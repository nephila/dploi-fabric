from dploi_fabric.db.base import DownloadDatabase, DumpDatabaseTask
from fabric.tasks import Task


class PostgreDumpDatabaseTask(DumpDatabaseTask, Task):
    """
    Dump the database (PostgreSQL)
    """

    name = "dump"

    def get_command(self, env, file_name, **flags):
        return (
            "pg_dump --no-owner "
            + self.get_flags_string(**flags)
            + ' --username="%(db_username)s" "%(db_name)s" > ' % env
        ) + file_name


dump = PostgreDumpDatabaseTask()
download = DownloadDatabase(dump_task=dump)
