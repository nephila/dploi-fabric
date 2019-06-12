import posixpath

# from fabric.api import env, local, task
# from fabric.contrib.files import exists
# from fabric.operations import prompt, run
from fabric import task
from patchwork.files import exists

from .django_utils import append_settings
from .messages import CAUTION


@task
def update(c):
    env = c.config  # getting env
    test = c.run("cd %(path)s; git --no-pager diff --stat" % env)
    if "files changed" in test.stdout.strip():
        print(CAUTION)
        print(("You have local file changes to the git repository on the server. Run 'fab %s git.reset' to "
              "remove them, or keep them by applying the diff locally with the command "
              "'git apply filename.diff' and upload it to your git host" % env['identifier']))
        print()
        print("You now have the following options:")
        print()
        print("[D]ownload diff")
        print("Continue and [R]eset changes")
        print("[E]xit")
        download_diff = str((input("What do you want to do?")))
        if download_diff.lower() == "d":
            diff = c.run(("cd %(path)s; git diff --color .") % env)
            for i in range(1, 50):
                print()
            print(diff)
            for i in range(1, 5):
                print()
            exit()
        elif download_diff.lower() == "e":
            exit()
    c.run("cd %(path)s; find . -iname '*.pyc' -delete" % env)
    c.run("cd %(path)s; git fetch origin" % env, pty=True)
    c.run("cd %(path)s; git reset --hard" % env)
    c.run("cd %(path)s; git checkout %(branch)s" % env)
    c.run("cd %(path)s; git pull origin %(branch)s" % env, pty=True)
    if exists(posixpath.join(env['path'], ".gitmodules")):
        c.run("cd %(path)s; git submodule init" % env)
        c.run("cd %(path)s; git submodule update" % env)
    append_settings(c)


@task
def diff(c, what=''):
    env = c.config
    c.run(("cd %(path)s; git --no-pager diff " + what) % env)


@task
def status(c):
    env = c.config
    c.run("cd %(path)s; git status" % env)


@task
def reset(c):
    """
    discard all non-committed changes
    """
    env = c.config
    c.run("cd %(path)s; find . -iname '*.pyc' -delete" % env)
    c.run("cd %(path)s; git reset --hard HEAD" % env)


@task
def incoming(c, remote='origin', branch=None):
    """
    Displays incoming commits 
    """
    env = c.config
    if not branch:
        branch = env['branch']
    c.run(("cd %(path)s; git fetch " + remote +
           " && git log --oneline --pretty=format:'%%C(yellow)%%h%%C(reset) - %%s %%C(bold blue)<%%an>%%C(reset)' .." +
           remote + '/' + branch) % env)


def local_branch_is_dirty(ignore_untracked_files=True):
    untracked_files = '--untracked-files=no' if ignore_untracked_files else ''
    git_status = local(
        'git status %s --porcelain' % untracked_files, capture=True)
    return git_status != ''


def local_branch_matches_remote():
    local_branch = local(
        'git rev-parse --symbolic-full-name --abbrev-ref HEAD',
        capture=True).strip()
    target_branch = env.branch.strip()
    return local_branch == target_branch
