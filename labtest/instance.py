# -*- coding: utf-8 -*-
from future.utils import iteritems
from future import standard_library
from builtins import str
import click
from fabric.api import env, sudo, run, task, execute, cd
from fabric.contrib.files import upload_template, exists
from fabric.operations import put
from fabric.context_managers import settings
standard_library.install_aliases()


def _git_cmd(cmd):
    """
    Convenience wrapper to do git commands
    """
    final_cmd = cmd.format(**env)
    return sudo(final_cmd, user='ec2-user', quiet=env.quiet)


def _virtual_host_name():
    """
    Calculate the virtual host name from the test domain and the host name pattern
    """
    host_name = env.host_name_pattern % env.context
    return '.'.join([host_name, env.test_domain])


def _setup_path():
    """
    Set up the path on the remote server
    """
    sudo('mkdir -p {app_path}'.format(**env), quiet=env.quiet)

    # Set up the permissions on all the paths
    sudo('chgrp -R docker /testing', quiet=env.quiet)
    sudo('chmod -R g+w /testing', quiet=env.quiet)


def _remove_path():
    """
    Remove the path o the remote server
    """
    if exists(env.instance_path):
        sudo('rm -Rf {}'.format(env.instance_path), quiet=env.quiet)


def _checkout_code():
    """
    Check out the repository into the proper place, if it hasn't already been done
    """
    if not exists(env.instance_path):
        with cd(env.app_path):
            # All git commands must use the ec2-user since we have added credentials
            # and a key for the service.
            _git_cmd('git clone {code_repo_url} {instance_name} --branch {branch_name} --depth 1')
            _git_cmd('chgrp -R docker {instance_path}; chmod -R g+w {instance_path}')
    else:
        with cd(env.instance_path):
            if 'branch_name' not in env:
                env.branch_name = _git_cmd('git rev-parse --abbrev-ref HEAD')
            _git_cmd('git fetch --depth 1; git reset --hard origin/{branch_name}; git clean -dfx')
            _git_cmd('chgrp -R docker {instance_path}; chmod -R g+w {instance_path}')

    with cd(env.instance_path):
        env.release = _git_cmd('git rev-parse --verify HEAD')
        env.context['RELEASE'] = env.release


def _app_build():
    """
    Build the application
    """
    if env.app_build_command and env.app_build_image:
        msg = 'Building the application using {app_build_image} and {app_build_command}.'.format(**env)
        click.echo(msg)
        cmd = 'docker run --rm -ti -v {instance_path}:/build -w /build {app_build_image} {app_build_command}'.format(**env)
        run(cmd, quiet=env.quiet)


def _put_docker_build_cmd():
    """
    Put in the docker build command

    This wraps the `container_build_command` in a bash script
    """
    import os
    from io import StringIO

    base_file = os.path.join(os.path.dirname(__file__), 'templates', 'docker-build')
    contents = StringIO()
    contents.write(str(open(base_file, 'r').read()))
    contents.write(str(env.container_build_command))
    with cd(env.instance_path):
        result = put(local_path=contents, remote_path='docker-build', mode=0o755)
    if result.failed:
        click.ClickException('Failed to put the docker-build command on remote host.')


def _container_build():
    """
    Build the container
    """
    _put_docker_build_cmd()

    with cd(env.instance_path):
        run('docker image prune -f', quiet=env.quiet)
        run('./docker-build -a {app_name} -i {instance_name}'.format(**env), quiet=env.quiet)


def _setup_service():
    """
    Set up the service
    """
    import os

    systemd_template = os.path.join(os.path.dirname(__file__), 'templates', 'systemd-test.conf.template')
    systemd_tmp_dest = '/tmp/{app_name}-{instance_name}.service'.format(**env)
    systemd_dest = '/etc/systemd/system/{app_name}-{instance_name}.service'.format(**env)
    if not exists(systemd_dest):
        upload_template(systemd_template, systemd_tmp_dest, env.context)
        sudo('mv {} {}'.format(systemd_tmp_dest, systemd_dest), quiet=env.quiet)
        sudo('systemctl enable {app_name}-{instance_name}.service'.format(**env), quiet=env.quiet)
        sudo('systemctl start {app_name}-{instance_name}.service'.format(**env), quiet=env.quiet)


def _remove_service():
    """
    Stop the service, and remove its configuration
    """
    systemd_dest = '/etc/systemd/system/{app_name}-{instance_name}.service'.format(**env)
    if exists(systemd_dest):
        sudo('systemctl disable {app_name}-{instance_name}.service'.format(**env), quiet=env.quiet)
        sudo('systemctl stop {app_name}-{instance_name}.service'.format(**env), quiet=env.quiet)
        sudo('rm {}'.format(systemd_dest), quiet=env.quiet)


def _setup_templates():
    """
    Write the templates to the appropriate places
    """
    from io import StringIO

    env_dest = u'{instance_path}/test.env'.format(**env)
    contents = StringIO()
    with cd(env.instance_path):
        env.virtual_host = _virtual_host_name()
        contents.write(u'VIRTUAL_HOST={}\n'.format(env.virtual_host))
        for key, val in iteritems(env.context):
            contents.write(u'{}={}\n'.format(key, val))
        for item in env.environment:
            contents.write(u'{}\n'.format(item))
        put(local_path=contents, remote_path=env_dest)


def _update_image():
    """
    Pull down the latest version of the image from the repository
    """
    # run("eval $(aws ecr get-login --no-include-email --region us-east-1) && "
    #     "docker pull {repository_url}:latest".format(**env))

    # Delete the container if it exists
    containers = run('docker ps -a --filter name={app_name}-{instance_name} --format "{{{{.ID}}}}"'.format(**env), quiet=env.quiet)
    if len(containers) > 0:
        with settings(warn_only=True):
            sudo('systemctl stop {app_name}-{instance_name}'.format(**env), quiet=env.quiet)
        run('docker rm -f {app_name}-{instance_name}'.format(**env), quiet=env.quiet)

    env.docker_image = env.docker_image_pattern % env.context
    run('docker create --env-file /testing/{app_name}/{instance_name}/test.env --name {app_name}-{instance_name} {docker_image}'.format(**env), quiet=env.quiet)

    # If the container existed before, we need to start it again
    if len(containers) > 0:
        with settings(warn_only=True):
            sudo('systemctl start {app_name}-{instance_name}'.format(**env), quiet=env.quiet)


def _setup_env_with_config(config):
    """
    Add config keys to the env
    """
    for key, val in iteritems(config.config):
        setattr(env, key, val)
    env.quiet = not config.verbose


@task
def create_instance(branch, name=''):
    """
    The Fabric tasks that create a test instance
    """
    if not name:
        name = branch
    env.instance_name = name
    env.branch_name = branch
    env.app_path = '/testing/{app_name}'.format(**env)
    env.instance_path = '/testing/{app_name}/{instance_name}'.format(**env)
    env.context = {
        'APP_NAME': env.app_name,
        'INSTANCE_NAME': env.instance_name,
        'BRANCH_NAME': env.branch_name
    }
    _setup_path()
    _checkout_code()

    _app_build()
    _container_build()

    # TODO: How to determine if we need to deal with pulling from the repository
    # env.repository_url = aws._get_or_create_repository()
    # _upload_to_repository()

    _setup_templates()
    _update_image()
    _setup_service()
    click.echo('')
    click.secho('Your experiment is available at: {}'.format(env.virtual_host), fg='green')


@task
def delete_instance(name):
    """
    The Fabric task to delete an instance
    """
    env.instance_name = name
    env.app_path = '/testing/{app_name}'.format(**env)
    env.instance_path = '/testing/{app_name}/{instance_name}'.format(**env)
    env.context = {
        'APP_NAME': env.app_name,
        'INSTANCE_NAME': env.instance_name,
    }
    _remove_path()
    _remove_service()
    run('docker container prune -f', quiet=env.quiet)
    run('docker image prune -f', quiet=env.quiet)
    containers = run('docker ps -a --filter name={app_name}-{instance_name} --format "{{{{.ID}}}}"'.format(**env), quiet=env.quiet)
    if len(containers) > 0:
        run('docker rm -f {app_name}-{instance_name}'.format(**env), quiet=env.quiet)

    env.docker_image = env.docker_image_pattern % env.context
    images = run('docker image ls {docker_image} -q'.format(**env), quiet=env.quiet)
    if len(images) > 0:
        run('docker image rm {docker_image}'.format(**env), quiet=env.quiet)


@task
def update_instance(name):
    """
    The Fabric task to update an instance
    """
    env.instance_name = name
    env.app_path = '/testing/{app_name}'.format(**env)
    env.instance_path = '/testing/{app_name}/{instance_name}'.format(**env)
    env.context = {
        'APP_NAME': env.app_name,
        'INSTANCE_NAME': env.instance_name,
    }
    _setup_path()
    _checkout_code()

    _app_build()
    _container_build()
    _setup_templates()
    _update_image()
    status = run('systemctl is-active {app_name}-{instance_name}'.format(**env), quiet=env.quiet)
    if status == 'inactive':
        sudo('systemctl start {app_name}-{instance_name}'.format(**env), quiet=env.quiet)
    elif status == 'unknown':
        click.ClickException(click.style('There was an issue restarting the service. The test server doesn\'t recognize it.'), fg='red')


@click.command()
@click.argument('branch')
@click.option('--name', '-n', help='The URL-safe name for the test instance. Defaults to the branch name.')
@click.pass_context
def create(ctx, branch, name):
    """
    Create a test instance on the server
    """
    _setup_env_with_config(ctx.obj)
    execute(create_instance, branch, name, hosts=ctx.obj.host)


@click.command()
@click.argument('name')
@click.pass_context
def delete(ctx, name):
    """
    Delete a test instance on the server
    """
    _setup_env_with_config(ctx.obj)
    execute(delete_instance, name, hosts=ctx.obj.host)


@click.command()
@click.argument('name')
@click.pass_context
def update(ctx, name):
    """
    Delete a test instance on the server
    """
    _setup_env_with_config(ctx.obj)
    execute(update_instance, name, hosts=ctx.obj.host)
