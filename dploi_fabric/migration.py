from fabric.api import env, run
from fabric.tasks import Task

from .utils import config


class SouthMigrateTask(Task):

    name = 'migrate'

    def run(self):
        config.django_manage("syncdb")
        config.django_manage("migrate")


class MigrateTask(Task):
    name = 'migrate'

    def run(self):
        config.django_manage('migrate')


south_migrate = SouthMigrateTask()
migrate = MigrateTask()
