from fabric.api import env, task
from fabric.operations import run as do_run


@task
def run():
    """
    runs buildout
    """
    # TODO: Refactor to use utils.config
    do_run("cd %(path)s;./bin/buildout -c %(buildout_cfg)s" % env)
