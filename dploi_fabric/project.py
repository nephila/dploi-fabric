from fabric.api import env, prompt, put, run, task

from . import django_utils, git
from .nginx import update_config_file as nginx_update_config_file
from .redis import update_config_file as redis_update_config_file
from .supervisor import restart as supervisor_restart, update_config_file as supervisor_update_config_file
from .utils import config

env.use_ssh_config = True
env.forward_agent = True


@task
def init():
    run("mkdir -p %(path)s" % env)
    run("mkdir -p %(logdir)s" % env)
    run("mkdir -p %(path)s../tmp" % env)
    run("mkdir -p %(path)s../config" % env)
    if env.repo.startswith("git"):
        run("cd %(path)s; git clone -b %(branch)s %(repo)s ." % env)
        git.update()
    elif env.repo.startswith("ssh+svn"):
        run("cd %(path)s; svn co %(repo)s" % env)

    update_configuration()

    tool = config.sites["main"].get("checkout", {}).get("tool")
    if tool == "buildout":
        run("cd %(path)s; sh init.sh -c %(buildout_cfg)s" % env)
        django_utils.append_settings()
    elif tool == "virtualenv":
        from . import virtualenv

        virtualenv.create()
        django_utils.append_settings()
        django_utils.manage("migrate --fake")
    else:
        print(
            "WARNING: Couldnt find [checkout] tool - please set it to either virtualenv or buildout in your config.ini"
        )
        print("Got tool: %s" % tool)
        django_utils.append_settings()


@task
def upload_ssl():
    """
    Upload the SSL key and certificate to the directories and with the filenames
    specified in your settings.
    """
    for site, site_dict in config.sites.items():
        ssl_key_path = prompt("SSL Key path (%s):" % site)
        ssl_cert_path = prompt("SSL Certificate path (%s):" % site)
        put(ssl_key_path, site_dict.get("deployment").get("ssl_key_path"))
        put(ssl_cert_path, site_dict.get("deployment").get("ssl_cert_path"))


@task
def update_configuration():
    if config.sites["main"]["redis"]["enabled"]:
        redis_update_config_file()

    supervisor_update_config_file()

    if config.sites["main"]["nginx"]["enabled"] == True:
        nginx_update_config_file()
    supervisor_restart()
