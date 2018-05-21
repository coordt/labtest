# -*- coding: utf-8 -*-
import os
from io import BytesIO
from fabric.api import env, run, sudo
from fabric.contrib.files import exists
from fabric.operations import put, get
from fabric.context_managers import settings, hide
import json
import click
from labtest import services


def _get_initial_data_source(path):
    """
    If the path is a directory, get the latest file in it. If the path is a file
    return the path
    """
    out = run('stat -L --format=%F {}'.format(path), quiet=env.quiet)
    if out.succeeded:
        if out == 'regular file':
            return path
        elif out == 'directory':
            latest = run('ls -1td {}/* | head -1'.format(path.rstrip('/')), quiet=env.quiet)
            if latest.succeeded:
                return latest
            else:
                raise click.ClickException('The initial source directory ({}) is empty'.format(path))
        else:
            raise click.ClickException('LabTest doesn\'t understand the type of "{}": {}'.format(path, out))
    else:
        raise click.ClickException('The initial data source "{}" doesn\'t exist on the test server.'.format(path))


def _setup_initial_data_source(path):
    """
    Check for the real initial data source and symlink it to an ``initialdata``
    directory in the experiment's namespace
    """
    real_path = _get_initial_data_source(path)
    init_data_path = '{instance_path}/initialdata'.format(**env)
    _, filename = os.path.split(real_path)
    link_path = os.path.join(init_data_path, filename)

    if exists(init_data_path):
        # check to see if the link exists already
        if exists(link_path):
            return link_path
        else:
            # the initial data source must have changed, so clear it out
            run('rm -Rf {}'.format(init_data_path), quiet=env.quiet)
    else:
        run('mkdir -p {}'.format(init_data_path), quiet=env.quiet)
        run('chgrp docker {}'.format(init_data_path), quiet=env.quiet)
        run('ln -s {} {}'.format(real_path, link_path), quiet=env.quiet)
    click.echo('  Created a symlink from {} -> {}'.format(real_path, link_path))
    return link_path


def _setup_env_file(filepath, environment):
    """
    Write the templates to the appropriate places

    @param environment  A list of strings
    """
    contents = BytesIO()
    for item in environment:
        contents.write('{}\n'.format(item))
    with hide('running'):
        put(local_path=contents, remote_path=filepath)


def _setup_volume(config):
    """
    Create a volume if it doesn't exist for storing the mysql data
    """
    volumes = run('docker volume ls --filter name={volume_name} -q'.format(**config), quiet=env.quiet)
    if len(volumes) == 0:
        click.echo('  Creating a volume for storing MySQL data.')
        run('docker volume create --driver rexray/ebs:latest --opt=size=10 {volume_name}'.format(**config), quiet=env.quiet)


def _delete_volume(config):
    """
    Remove the volume, if it exists
    """
    volumes = run('docker volume ls --filter name={volume_name} -q'.format(**config), quiet=env.quiet)
    if len(volumes) != 0:
        click.echo('  Deleting volume {volume_name}.'.format(**config))
        run('docker volume rm {volume_name}'.format(**config), quiet=env.quiet)


def _setup_container(config):
    """
    Create a container.

    If an existing container is running, we need to stop and remove it.
    We also need to remember that so we can restart the new container when done.
    The Docker command is built dynamically, since there are optional parts.
    """
    click.echo('  Setting up the {service_name} container'.format(**config))

    containers = run('docker ps -a --filter name={service_name} --format "{{{{.ID}}}}"'.format(**config), quiet=env.quiet)
    if len(containers) > 0:
        click.echo('  Removing existing container.')
        with settings(warn_only=True):
            sudo('systemctl stop {service_name}'.format(**config), quiet=env.quiet)
        run('docker rm -f {service_name}'.format(**config), quiet=env.quiet)
        run('docker volume prune -f', quiet=env.quiet)

    cmd = [
        'docker create',
        '--name {service_name}',
        '--network {network_name}',
        '--net-alias {name}',
        '-v {volume_name}:/var/lib/mysql',
    ]

    if config['environment']:
        _setup_env_file(config['environment_file_path'], config['environment'])
        cmd.append('--env-file {environment_file_path}'.format(**config))

    if config.get('initial_data_source', ''):
        config['data_source_filename'] = os.path.basename(config['initial_data_source'])
        cmd.append('-v {initial_data_source}:/docker-entrypoint-initdb.d/{data_source_filename}')

    cmd.append('{image}')
    if 'commands' in config:
        cmd.extend(config['commands'])

    run(' '.join(cmd).format(**config), quiet=env.quiet)

    # If the container existed before, we need to start it again
    if len(containers) > 0:
        click.echo('  Starting new container.')
        with settings(warn_only=True):
            sudo('systemctl start {service_name}'.format(**config), quiet=env.quiet)


def _delete_container(config):
    """
    Remove the container
    """
    containers = run('docker ps -a --filter name={service_name} --format "{{{{.ID}}}}"'.format(**config), quiet=env.quiet)
    if len(containers) > 0:
        click.echo('  Deleting the {service_name} container'.format(**config))
        with settings(warn_only=True):
            sudo('systemctl stop {service_name}'.format(**config), quiet=env.quiet)
        run('docker rm -f {service_name}'.format(**config), quiet=env.quiet)


def _write_config(config, config_path):
    """
    Write a JSON file to the test server to make it easy to see if things have changed
    """
    config = json.dumps(config)
    with hide('running'):
        put(local_path=BytesIO(config), remote_path=config_path)


def _delete_config(config_path):
    """
    Remove the JSON file
    """
    if exists(config_path):
        run('rm {}'.format(config_path), quiet=env.quiet)


def _has_config_changed(new_config):
    """
    Check a config file on the test server and see if it is different from the
    ``new_config``
    """
    config_path = new_config['config_path']
    if exists(config_path):
        existing_config_buffer = BytesIO()
        with hide('running'):
            get(local_path=existing_config_buffer, remote_path=config_path)
        try:
            existing_config = json.loads(unicode(existing_config_buffer.getvalue()))
            if new_config == existing_config:
                click.echo('  Configuration for existing MySQL service is unchanged. Skipping.')
                return False
            else:
                click.echo('  Configuration for existing MySQL service has changed. Re-creating it.')
                return True
        except Exception as e:
            click.echo('  Error: {}'.format(e))
            click.echo('  Configuration for existing MySQL service is unreadable. Re-creating it.')
            return True
    else:
        return True


def _get_service_config(config, name):
    """
    Return a dict with all the configuration used throughout this module
    """
    service_config = config.get('options', {})
    service_config['app_name'] = env.app_name
    service_config['instance_name'] = env.instance_name
    service_config['instance_path'] = env.instance_path
    service_config['name'] = name
    service_config['service_name'] = '{app_name}-{instance_name}-{name}'.format(name=name, **env)
    service_config['environment_file_path'] = '{instance_path}/{service_name}.env'.format(**service_config)
    service_config['volume_name'] = '{service_name}-data'.format(**service_config)
    service_config['config_path'] = '{instance_path}/{service_name}.conf.json'.format(**service_config)
    service_config['network_name'] = '{app_name}-{instance_name}-net'.format(name=name, **env)

    return service_config


def create(config, name):
    """
    Create the service

    Args:
        config:  The configuration
        name: The name of the service

    Returns:
        An empty``dict``. There is no additional information required for the experiment.
    """
    service_config = _get_service_config(config, name)

    click.echo('Creating MySQL service.')
    if 'initial_data_source' in service_config:
        click.echo('  Getting the initial data source.')
        service_config['initial_data_source'] = _setup_initial_data_source(config['options']['initial_data_source'])
        click.echo('    Initial data source: {}'.format(service_config['initial_data_source']))
    if 'image' not in service_config:
        service_config['image'] = 'mysql'

    # See if existing configuration file is on test server
    # if it is, see if anything changed with current config
    # Create the service only if the configuration is changed
    create_service = _has_config_changed(service_config)

    if create_service:
        click.echo('  Updating docker image "{}" for backing service.'.format(service_config['image']))
        run('docker pull {}'.format(service_config['image']), quiet=env.quiet)  # To make sure it is ready to go
        _setup_volume(service_config)
        _setup_container(service_config)

        systemd_template = os.path.join(os.path.dirname(__file__), 'templates', 'systemd-backing.conf.template')
        services.setup_service(service_config['service_name'], systemd_template, {'SERVICE_NAME': service_config['service_name']}, env.quiet)

        _write_config(service_config, service_config['config_path'])

    return {}


def destroy(config, name):
    """
    Destroy the service and clean up

    Args:
        config:  The service configuration
        name: The name for the service
    """
    service_config = _get_service_config(config, name)
    click.echo('Destroying MySQL service.')
    initial_data_path = '{instance_path}/initialdata'.format(**env)
    if exists(initial_data_path):
        run('rm -R {}'.format(initial_data_path), quiet=env.quiet)
    if exists(service_config['environment_file_path']):
        run('rm -R {}'.format(service_config['environment_file_path']), quiet=env.quiet)

    _delete_config(service_config['config_path'])
    services.delete_service(service_config['service_name'], env.quiet)
    _delete_container(service_config)
    _delete_volume(service_config)
    run('docker prune volume -f', quiet=env.quiet)
    run('docker prune container -f', quiet=env.quiet)


def check_config(config):
    """
    Make sure all the proper arguments are in there

    Args:
        config:  The configuration

    Returns:
       ``True`` if the configuration is correct, otherwise ``False``.
    """
    pass
