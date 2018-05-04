# -*- coding: utf-8 -*-
import click
from fabric.api import env, sudo, run, task, execute, cd
from fabric.contrib.files import upload_template, exists
from fabric.operations import put, get
from fabric.context_managers import settings


def _git_cmd(cmd):
    """
    Convenience wrapper to do git commands
    """
    final_cmd = cmd.format(**env)
    return sudo(final_cmd, user='ec2-user', quiet=env.quiet)


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
        sudo('rm -Rf {}'.format(env.instance_path))


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
            _git_cmd('git fetch --depth 1; git reset --hard origin/{branch_name}; git clean -dfx')
            _git_cmd('chgrp -R docker {instance_path}; chmod -R g+w {instance_path}')


def _app_build():
    """
    Build the application
    """
    if env.app_build_command and env.app_build_image:
        msg = 'Building the application using {app_build_image} and {app_build_command}.'.format(**env)
        click.echo(msg)
        cmd = 'docker run --rm -ti -v {instance_path}:/build -w /build {app_build_image} {app_build_command}'.format(**env)
        run(cmd)


def _put_docker_build_cmd():
    """
    Put in the docker build command

    This wraps the `container_build_command` in a bash script
    """
    import os
    from StringIO import StringIO

    base_file = os.path.join(os.path.dirname(__file__), 'templates', 'docker-build')
    contents = StringIO()
    contents.write(open(base_file, 'r').read())
    contents.write(env.container_build_command)
    with cd(env.instance_path):
        result = put(local_path=contents, remote_path='docker-build', mode=0755)
    if result.failed:
        click.ClickException('Failed to put the docker-build command on remote host.')


def _container_build():
    """
    Build the container
    """
    _put_docker_build_cmd()

    with cd(env.instance_path):
        run('docker image prune -f')
        run('./docker-build -a {app_name} -i {instance_name}'.format(**env))


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
        sudo('mv {} {}'.format(systemd_tmp_dest, systemd_dest))
        sudo('systemctl enable {app_name}-{instance_name}.service'.format(**env))
        sudo('systemctl start {app_name}-{instance_name}.service'.format(**env))


def _remove_service():
    """
    Stop the service, and remove its configuration
    """
    systemd_dest = '/etc/systemd/system/{app_name}-{instance_name}.service'.format(**env)
    if exists(systemd_dest):
        sudo('systemctl disable {app_name}-{instance_name}.service'.format(**env))
        sudo('systemctl stop {app_name}-{instance_name}.service'.format(**env))
        sudo('rm {}'.format(systemd_dest))


def _setup_templates():
    """
    Write the templates to the appropriate places
    """
    from StringIO import StringIO

    env_dest = '/testing/{app_name}/{instance_name}/test.env'.format(**env)
    template = StringIO()
    contents = StringIO()
    if not exists(env_dest):
        with cd(env.instance_path):
            get(remote_path=env.env_template, local_path=template)
            contents.write(template.getvalue() % env.context)
            put(local_path=contents, remote_path=env_dest)


def _update_image():
    """
    Pull down the latest version of the image from the repository
    """
    # run("eval $(aws ecr get-login --no-include-email --region us-east-1) && "
    #     "docker pull {repository_url}:latest".format(**env))

    # Delete the container if it exists
    containers = run('docker ps -a --filter name={app_name}-{instance_name} --format "{{{{.ID}}}}"'.format(**env))
    if len(containers) > 0:
        with settings(warn_only=True):
            sudo('systemctl stop {app_name}-{instance_name}'.format(**env))
        run('docker rm -f {app_name}-{instance_name}'.format(**env))

    run('docker create --env-file /testing/{app_name}/{instance_name}/test.env --name {app_name}-{instance_name} {app_name}/{instance_name}:latest'.format(**env))

    # If the container existed before, we need to start it again
    if len(containers) > 0:
        with settings(warn_only=True):
            sudo('systemctl start {app_name}-{instance_name}'.format(**env))


def _setup_env_with_config(config):
    """
    Add config keys to the env
    """
    for key, val in config.config.items():
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
    with cd(env.instance_path):
        env.release = _git_cmd('git rev-parse --verify HEAD')
        env.context['RELEASE'] = env.release

    _app_build()
    _container_build()

    # How to determine if we need to deal with pulling from the repository
    # env.repository_url = aws._get_or_create_repository()
    # _upload_to_repository()

    _setup_templates()
    _update_image()
    _setup_service()


@click.command()
@click.argument('branch')
@click.option('--name', '-n', help='The URL-safe name for the test instance. Defaults to the branch name.')
@click.pass_context
def create(ctx, branch, name):
    """
    Create a test instance on the server
    """
    _setup_env_with_config(ctx.obj)

    env.instance_name = name
    env.branch_name = branch
    execute(create_instance, branch, name, hosts=ctx.obj.host)
