from fabric import task

from .utils import config


@task
def update(c):
    """
    updates a virtualenv (pip install requirements.txt)
    """
    c.run('cd %(path)s; bin/pip install -r requirements.txt --upgrade --no-deps' % config.sites(c)["main"].deployment)


@task
def create(c):
    """
    creates a virtualenv and calls update
    """
    c.run('cd %(path)s; virtualenv . --system-site-packages --setuptools' % config.sites["main"].deployment)
    update(c)
    # this is ugly. I know. But it seems that on first run, pip does not
    # install the correct version of packages that are pulled directly from
    # git. Only the second time around it uses the correct one.
    update(c)
