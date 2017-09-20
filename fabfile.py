import os
import posixpath
from contextlib import contextmanager

from fabric.api import env, run, task, execute
from fabric.context_managers import cd, prefix, settings as fabsettings
from fabric.contrib.files import exists
from fabric.operations import sudo

if os.path.exists(os.path.expanduser("~/.ssh/config")):
    env.use_ssh_config = True

env.VENV_RELATIVE_PATH = '/venv'
env.repopath = '~/flask-socketio-grid-game'
env.VENV_PATH = env.repopath + env.VENV_RELATIVE_PATH
env.user = 'root'
env.hosts = ['178.62.63.15']


@task
def deploy(requirements=True):
    for host in env.hosts:
        with fabsettings(host_string=host):
            path = env.VENV_PATH
            if not exists(env.repopath):
                print("Missing repository in %s. Cloning" % path)
                print("We need superpowers to create the repo in /var/www")
                sudo('mkdir "%s"' % path)
                sudo('chown {user}:{user} "{path}"'.format(
                    user=env.USER, path=path
                ))
                with cd(env.repopath):
                    run('git clone {repo} .'.format(repo=env.REPO))
                    execute(mkvirtualenv)

    execute(update_git)
    if requirements:
        execute(update_requirements)

    execute(update_assets)
    execute(restart)


@contextmanager
def virtualenv():
    """ Put fabric commands in a virtualenv """
    with prefix("source %s" % posixpath.join(env.VENV_PATH, "bin/activate")):
        yield


@task
def restart():
    print("Restarting the grid-game")
    run('service grid-game restart')


def update_requirements():
    with virtualenv():
        with cd(env.repopath):
            requirements_file = 'requirements.txt'
            run('pip install -q -U -r %s' % requirements_file)


def update_assets():
    with cd(env.repopath):
        with virtualenv():
            run('/.manage.py assets --parse-templates build ')


def update_git():
    print("Update GIT repo on {host}".format(
        host=", ".join(env.hosts))
    )
    with cd(env.repopath):
        run('git pull')


def mkvirtualenv():
    print("Creating virtualenv")
    with cd(env.repopath):
        run('virtualenv {env}'.format(env=env.VENV_PATH))
        with virtualenv():
            run('pip install -U pip')
