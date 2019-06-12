import datetime
import os

from fabric import task


@task
def dump_db(c, reason='unknown', compress=False, **flags):
    env = c.config  # getting env
    file_name = _get_path(env, reason)
    command = _get_command(env, file_name, **flags)
    c.run(command)
    if compress:
        c.run('gzip ' + file_name)
        file_name += '.gz'
    return file_name


@task
def download_db(c, path='tmp', **flags):
    file_name = dump_db(c, reason='for_download', compress=True, **flags)
    c.get(file_name, path)


def _get_command(env, file_name, **flags):
    return ('pg_dump --no-owner ' + _get_flags_string(
        **flags) + ' --username="%(db_username)s" "%(db_name)s" > ' % env) + file_name


def _get_path(env, reason):
    mytimestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
    reason = reason.replace(' ', '_')
    return os.path.join('%(backup_dir)s' % env, '%(db_name)s-' % env + mytimestamp + '-' + reason + '.sql')


def _get_flags_string(**flags):
    flag_list = []
    for k, v in list(flags.items()):
        result = ('-' if len(k) == 1 else '--') + k
        if v:
            result += (' ' if len(k) == 1 else '=') + v
        flag_list.append(result)
    return ' '.join(flag_list)
