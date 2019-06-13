from fabric.api import task
from fabric.operations import run as do_run

from .utils import config


@task
def update():
    """
    updates a virtualenv (pip install requirements.txt)
    """
    print("Updating virtualenv!")
    do_run('cd %(path)s; bin/pip install -r requirements.txt --upgrade --no-deps' % config.sites["main"].deployment)
    print("Finished to update virtualenv!")


@task
def create():
    """
    creates a virtualenv and calls update
    """
    print("Create virtualenv!")
    do_run('cd %(path)s; virtualenv . --system-site-packages --setuptools' % config.sites["main"].deployment)
    update()
    # this is ugly. I know. But it seems that on first run, pip does not
    # install the correct version of packages that are pulled directly from
    # git. Only the second time around it uses the correct one.
    update()
