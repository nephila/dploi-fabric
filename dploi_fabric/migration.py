from fabric.tasks import Task

from .utils import config


class MigrateTask(Task):
    name = 'migrate'

    def run(self):
        config.django_manage("migrate")


class SouthMigrateTask(MigrateTask):

    def run(self):
        config.django_manage("syncdb")
        config.django_manage("migrate")


migrate = MigrateTask()
south_migrate = SouthMigrateTask()
