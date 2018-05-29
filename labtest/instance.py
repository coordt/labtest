# -*- coding: utf-8 -*-
import os

from future.utils import iteritems
from future import standard_library
from builtins import str
import click
from fabric.api import env, sudo, run, task, execute, cd
from fabric.contrib.files import exists
from fabric.operations import put
from fabric.context_managers import settings, hide
from . import services

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
    sudo('mkdir -p {instance_path}'.format(**env), quiet=env.quiet)

    # Set up the permissions on all the paths
    sudo('chgrp -R docker /testing', quiet=env.quiet)
    sudo('chmod -R g+w /testing', quiet=env.quiet)


def _remove_path():
    """
    Remove the path o the remote server
    """
    click.echo('Checking for code path: {}'.format(env.instance_path))
    if exists(env.instance_path):
        click.echo('  Found. Removing...')
        sudo('rm -Rf {}'.format(env.instance_path), quiet=env.quiet)


def _checkout_code():
    """
    Check out the repository into the proper place, if it hasn't already been done
    """
    env.code_path = os.path.join(env.instance_path, 'code')
    if not exists(env.code_path):
        click.echo('Checking out code from: {code_repo_url}'.format(**env))
        with cd(env.instance_path):
            # All git commands must use the ec2-user since we have added credentials
            # and a key for the service.
            _git_cmd('git clone {code_repo_url} code --branch {branch_name} --depth 1')
            with settings(warn_only=True):
                _git_cmd('chgrp -R docker {instance_path}; chmod -R g+w {instance_path}')
    else:
        click.echo('Fetching most recent code from: {code_repo_url}'.format(**env))
        with cd(env.code_path):
            if 'branch_name' not in env:
                env.branch_name = _git_cmd('git rev-parse --abbrev-ref HEAD')
            _git_cmd('git fetch --depth 1; git reset --hard origin/{branch_name}; git clean -dfx')
            with settings(warn_only=True):
                _git_cmd('chgrp -R docker {instance_path}; chmod -R g+w {instance_path}')

    with cd(env.code_path):
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
    with settings(hide('running'), warn_only=True):
        with cd(env.instance_path):
            result = put(local_path=contents, remote_path='docker-build', mode=0o775)
    if result.failed:
        click.ClickException('Failed to put the docker-build command on remote host.')


def _image_build():
    """
    Build the container
    """
    _put_docker_build_cmd()
    click.echo('Building the Docker image.')
    with cd(env.instance_path):
        run('./docker-build -a {app_name} -i {instance_name}'.format(**env), quiet=env.quiet)


def _setup_backing_services():
    """
    Add the services to the env config and call the appropriate functions to
    create them
    """
    from itertools import chain
    from provider import service_providers, check_services_config

    check_services_config(env.services)
    additional_configs = []
    for service_name, config in iteritems(env.services):
        service = service_providers[config['provider']][config['service']]
        additional_configs.append(service.create(config, service_name))

    # De-dupe the additional configs
    keys = set(chain(*[x.keys() for x in additional_configs]))
    backing_service_configs = {}
    for key in keys:
        backing_service_configs[key] = set(chain(*[x.get(key, []) for x in additional_configs]))
    env.backing_service_configs = backing_service_configs


def _delete_backing_services():
    """
    Call the appropriate functions to delete any backing services
    """
    from provider import providers

    for service_name, config in iteritems(env.services):
        service = providers[config['provider']][config['service']]
        service.destroy(config, service_name)


def _setup_network():
    """
    Create a network for this experiment, if necessary
    """
    networks = run('docker network ls --filter name={network_name} --format "{{{{.ID}}}}"'.format(**env))
    if len(networks) == 0:
        click.echo('Setting up networking.')
        run('docker network create --driver bridge {network_name}'.format(**env), quiet=env.quiet)
        run('docker network connect {network_name} nginx_proxy'.format(**env), quiet=env.quiet)


def _delete_network():
    """
    Delete the network for this experiment, if necessary
    """
    networks = run('docker network ls --filter name={network_name} --format "{{{{.ID}}}}"'.format(**env))
    if len(networks) != 0:
        click.echo('Removing network.')
        run('docker network disconnect {network_name} nginx_proxy'.format(**env), quiet=env.quiet)
        run('docker network rm {network_name}'.format(**env), quiet=env.quiet)


def _setup_templates():
    """
    Write the templates to the appropriate places
    """
    import re
    from io import StringIO
    encrypt_pattern = re.compile(r'^(.*)ENC\[([A-Za-z0-9+=/]+)\](.*)$')

    env_dest = u'{instance_path}/test.env'.format(**env)
    click.echo('Writing the experiment\'s environment file.')
    contents = StringIO()
    with cd(env.instance_path):
        env.virtual_host = _virtual_host_name()
        contents.write(u'VIRTUAL_HOST={}\n'.format(env.virtual_host))
        for key, val in iteritems(env.context):
            contents.write(u'{}={}\n'.format(key, val))
        for item in env.environment:
            match = encrypt_pattern.match(item)
            if match:
                contents.write(unicode(match.group(1)))
                contents.write(unicode(env.config.secrets.decrypt(match.group(2))))
                contents.write(unicode(match.group(3)))
            else:
                contents.write(u'{}\n'.format(item))
        if 'backing_service_configs' in env:
            for item in env.backing_service_configs.get('environment', []):
                match = encrypt_pattern.match(item)
                if match:
                    contents.write(unicode(match.group(1)))
                    contents.write(unicode(env.config.secrets.decrypt(match.group(2))))
                    contents.write(unicode(match.group(3)))
                else:
                    contents.write(u'{}\n'.format(item))
        with hide('running'):
            put(local_path=contents, remote_path=env_dest)


def _update_container():
    """
    Pull down the latest version of the image from the repository
    """
    # Delete the container if it exists
    cmd = [
        'docker ps -a',
        '--filter name={service_name}',
        '--filter ancestor={docker_image}',
        '--format "{{{{.ID}}}}"'
    ]
    containers = run(' '.join(cmd).format(**env), quiet=env.quiet)
    if len(containers) > 0:
        click.echo('Removing the existing container.')
        with settings(warn_only=True):
            sudo('systemctl stop {service_name}'.format(**env), quiet=env.quiet)
        run('docker rm -f {service_name}'.format(**env), quiet=env.quiet)

    cmd = [
        'docker create',
        '--env-file {instance_path}/test.env',
        '--name {service_name}',
        '--network {network_name}',
    ]

    # Note that the enviornment variables were added in _setup_templates
    if 'backing_service_configs' in env:
        for host in env.backing_service_configs.get('hosts', []):
            cmd.append('--add-host {}'.format(host))

    cmd.append('{docker_image}')

    click.echo('Creating the Docker container.')

    run(' '.join(cmd).format(**env), quiet=env.quiet)
    # If the container existed before, we need to start it again
    if len(containers) > 0:
        click.echo('Starting the new container.')
        with settings(warn_only=True):
            sudo('systemctl start {app_name}-{instance_name}'.format(**env), quiet=env.quiet)


def _setup_env_with_config(config):
    """
    Add config keys to the env
    """
    env.config = config
    for key, val in iteritems(config.config):
        setattr(env, key, val)
    env.quiet = not config.verbose


def _setup_default_env(instance_name, branch_name=''):
    """
    Provide a basic setup of the env for values needed throughout the code

    Assumes ``app_name`` is already set.

    Args:
        instance_name: The name of the instance we are dealing with
        branch_name: If we know it, include it. This is not guaranteed
    """
    env.instance_name = instance_name
    env.app_path = '/testing/{app_name}'.format(**env)
    env.instance_path = '/testing/{app_name}/{instance_name}'.format(**env)
    env.service_name = '{app_name}-{instance_name}'.format(**env)
    env.network_name = '{service_name}-net'.format(**env)
    env.context = {
        'APP_NAME': env.app_name,
        'INSTANCE_NAME': env.instance_name,
    }
    if branch_name:
        env.branch_name = branch_name
        env.context['BRANCH_NAME'] = branch_name
    env.docker_image = env.docker_image_pattern % env.context


@task
def test_task():
    _setup_default_env('labtest', 'labtest')
    # _setup_path()
    print "Starting string to encrypt"
    pt = 'This is my secret. Keep it safe'
    print pt
    ct = env.config.secrets.encrypt(pt)
    print 'Ciphertext:'
    print ct
    new_pt = env.config.secrets.decrypt(ct)
    print 'Decrypted ciphertext'
    print new_pt


@task
def create_instance(branch, name=''):
    """
    The Fabric tasks that create a test instance
    """
    if not name:
        name = branch
    _setup_default_env(name, branch)

    _setup_path()
    _checkout_code()

    _app_build()
    _image_build()
    _setup_network()

    # TODO: How to determine if we need to deal with pulling from the repository
    # env.repository_url = aws._get_or_create_repository()
    # _upload_to_repository()

    _setup_backing_services()

    _setup_templates()
    _update_container()

    systemd_template = os.path.join(os.path.dirname(__file__), 'templates', 'systemd-test.conf.template')
    services.setup_service(env.service_name, systemd_template, env.context, env.quiet)
    click.echo('')
    click.secho('Your experiment is available at: http://{}'.format(env.virtual_host), fg='green')


@task
def delete_instance(name):
    """
    The Fabric task to delete an instance
    """
    _setup_default_env(name)

    _remove_path()
    services.delete_service(env.service_name, env.quiet)
    run('docker container prune -f', quiet=env.quiet)
    run('docker volume prune -f', quiet=env.quiet)

    cmd = [
        'docker ps -a',
        '--filter name={service_name}',
        '--filter ancestor={docker_image}',
        '--format "{{{{.ID}}}}"'
    ]
    containers = run(' '.join(cmd).format(**env), quiet=env.quiet)
    if len(containers) > 0:
        run('docker rm -f {service_name}'.format(**env), quiet=env.quiet)

    env.docker_image = env.docker_image_pattern % env.context
    images = run('docker image ls {docker_image} -q'.format(**env), quiet=env.quiet)
    if len(images) > 0:
        run('docker image rm {docker_image}'.format(**env), quiet=env.quiet)

    _delete_backing_services()
    _delete_network()
    click.echo('')
    click.secho('Your experiment has been deleted.', fg='green')


@task
def update_instance(name):
    """
    The Fabric task to update an instance
    """
    _setup_default_env(name)
    _setup_path()
    _checkout_code()

    _app_build()
    _image_build()
    _setup_backing_services()
    _setup_templates()
    _update_container()
    services.start_service('{app_name}-{instance_name}'.format(**env), env.quiet)
    click.echo('')
    click.secho('Your experiment updated and available at: http://{}'.format(env.virtual_host), fg='green')


@task
def list_instances(app_name=''):
    """
    Return a list of test instances on the server
    """
    if app_name:
        find_cmd = 'find /testing/{}/ -mindepth 1 -maxdepth 1 -type d -print '.format(app_name)
    else:
        find_cmd = 'find /testing/ -mindepth 2 -maxdepth 2 -type d -print'
    output = run('{} | sed -e "s;/testing/;;g;s;/;-;g"'.format(find_cmd), quiet=env.quiet)
    click.echo(output)


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


@click.command()
@click.argument('app_name', default='')
@click.pass_context
def list(ctx, app_name):
    """
    Delete a test instance on the server
    """
    _setup_env_with_config(ctx.obj)
    execute(list_instances, app_name=app_name, hosts=ctx.obj.host)


@click.command()
@click.pass_context
def test(ctx):
    """
    for testing
    """
    _setup_env_with_config(ctx.obj)
    execute(test_task, hosts=ctx.obj.host)
