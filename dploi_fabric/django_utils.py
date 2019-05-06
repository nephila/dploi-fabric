from fabric import task
from patchwork.files import exists

try:
    import configparser
    import io
except ImportError:
    import io as StringIO
    import configparser as ConfigParser

import os
import posixpath
from pprint import pformat

# from fabric.api import env, get, put
# from fabric.contrib.files import exists
# from fabric.decorators import task
# from fabric.operations import run

from .utils import DATA_DIRECTORY, STATIC_COLLECTED, config


@task
def django_exec(c, dictionary={}, tool="buildout"):
    # TODO: Remove this and change dependants to use utils.config
    env = c.config
    config = configparser.RawConfigParser()
    config_file = os.path.join(env['path'], "config.ini")
    django_base = "."  # default to current dir
    if exists(config_file):
        output = io.StringIO()
        c.get("%s" % config_file, output)
        output.seek(0)
        config.readfp(output)

        try:
            tool = config.get("checkout", "tool")
        except (configparser.NoSectionError, configparser.NoOptionError):
            tool = "buildout"  # default to buildout

        try:
            django_base = config.get("django", "base")
        except (configparser.NoSectionError, configparser.NoOptionError):
            pass
    if django_base == ".":
        django_base = ""
    if tool == "buildout":
        cmd = os.path.join(env['path'], django_base, "bin/django")
        django_settings = os.path.join(env['path'], django_base, "settings.py")
    else:
        cmd = "%s %s" % (os.path.join(env['path'], "bin/python"), os.path.join(env['path'], django_base, "manage.py"))
        django_settings = os.path.join(env['path'], django_base, "settings.py")
    dictionary['django_exec'] = cmd
    dictionary['django_settings'] = django_settings
    dictionary['checkout_tool'] = tool
    return dictionary


@task
def django_settings_file(c, dictionary={}):  # TODO: Remove this and change dependants to use utils.config
    return django_exec(c).get("django_settings")


@task
def manage(c, *args):
    """
    Proxy for manage.py
    """
    config.django_manage(c, " ".join(args))


@task
def collectstatic(c, staticdir='static'):  # As defined in puppet config
    # TODO: Use utils.config
    env = c.config
    c.run(('cd %(path)s; mkdir -p ' + staticdir) % env)
    manage(c, "collectstatic", "--noinput", "--link")


@task
def load_fixture(c, file_path):
    remote_path = c.put(file_path, '~/tmp/')[0]
    manage('loaddata %s' % remote_path)
    c.run('rm %s' % remote_path)


@task
def append_settings(c):
    # TODO: make it work with multisites!
    env = c.config
    append = config.sites(c)["main"].get("django").get("append_settings", False)
    if append:
        site_config = config.sites(c)["main"]
        settings_file_path = django_settings_file(c)
        print(("Appending auto generated settings to", settings_file_path))
        output = io.StringIO()
        c.get("%s" % os.path.join(env['path'], "../config/django.py"), output)
        output.seek(0)
        manual_settings = output.read()

        # START OF DIRTY DATABASE HACK

        additional_settings = """if "DATABASES" in locals():\n"""
        # DATABASES
        # additional_settings = "DATABASES = %s\n" % pformat(config.sites(c)["main"].get("deployment").get("databases"))
        additional_settings += "    DATABASES = %s\n" % pformat(
            config.sites(c)["main"].get("deployment").get("databases")
        )

        db_old_dict = config.sites(c)["main"].get("deployment").get("databases")["default"]
        db_old_dict["ENGINE"] = db_old_dict["ENGINE"].replace("django.db.backends.", "")
        additional_settings += """else:
    DATABASE_ENGINE = "%(ENGINE)s"
    DATABASE_NAME = "%(NAME)s"
    DATABASE_USER = "%(USER)s"
    DATABASE_PASSWORD = "%(PASSWORD)s"
    DATABASE_HOST = "%(HOST)s"
""" % db_old_dict

        # // END OF DIRTY DATABASE HACK

        # CACHES
        processes = config.sites(c)["main"].get("processes")
        cache_dict = {
            'default': {
                'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
                'LOCATION': 'unix:%s' % [processes[x] for x in processes if processes[x]["type"] == "memcached"][0].get(
                    "socket"),
            }
        }
        additional_settings += "CACHES = %s\n" % pformat(cache_dict)

        # PATHS
        additional_settings += """
STATIC_ROOT = "%(static_root)s"
MEDIA_ROOT = "%(media_root)s"
""" % {
            'static_root': posixpath.join(site_config.get("deployment").get("path"), STATIC_COLLECTED),
            'media_root': posixpath.join(site_config.get("deployment").get("path"), DATA_DIRECTORY, 'media/'),
        }

        output = io.StringIO()
        c.get(settings_file_path, output)
        output.seek(0)
        settings_file = output.read()

        c.run("mkdir -p %s" % posixpath.join(site_config.get("deployment").get("path"), "_gen/"))
        c.put(io.StringIO("%s\n%s\n%s" % (settings_file, additional_settings, manual_settings)),
              site_config.get("deployment").get("generated_settings_path"))
        c.put(io.StringIO(""), posixpath.join(site_config.get("deployment").get("path"), "_gen/__init__.py"))
