# -*- coding: utf-8 -*-
"""
A collection of common functions to setup and destroy OS services
"""
from fabric.api import run, sudo
from fabric.contrib.files import upload_template, exists
from fabric.context_managers import hide, settings
import click


def start_service(service_name, quiet=False):
    """
    Make sure the service is running
    """
    with settings(warn_only=True):
        status = run(f'systemctl is-active {service_name}', quiet=quiet)
    status = status.strip()
    if status == 'inactive':
        sudo(f'systemctl start {service_name}', quiet=quiet)
    elif status != 'active':
        raise click.ClickException(click.style('There was an issue starting the service. The test server doesn\'t recognize it.', fg='red'))


def delete_service(service_name, quiet=False):
    """
    Remove the service and clean up

    Args:
        service_name: The name of the service
        quiet: Set to ``True`` to suppress Fabric output
    """
    systemd_dest = f'/etc/systemd/system/{service_name}.service'
    if exists(systemd_dest):
        click.echo(f'Deleting the OS service: {service_name}')
        sudo(f'systemctl stop {service_name}.service', quiet=quiet)
        sudo(f'systemctl disable {service_name}.service', quiet=quiet)
        sudo(f'rm {systemd_dest}', quiet=quiet)


def setup_service(service_name, local_template_path, context, quiet=False):
    """
    Setup a service using a template and context to render the correct service file

    Args:
        service_name: The name of the service
        local_template_path: The path to the template to use to render the service
        context: A ``dict`` containing values to use in the rendering of the template
        quiet: Set to ``True`` to suppress Fabric output
    """
    systemd_template = local_template_path
    systemd_tmp_dest = f'/tmp/{service_name}.service'
    systemd_dest = f'/etc/systemd/system/{service_name}.service'
    if not exists(systemd_dest):
        click.echo('Creating the OS service.')
        with hide('running'):
            upload_template(systemd_template, systemd_tmp_dest, context)
        sudo(f'mv {systemd_tmp_dest} {systemd_dest}', quiet=quiet)
        sudo(f'systemctl enable {service_name}.service', quiet=quiet)
        click.echo(f'Starting the OS service: {service_name}')
        sudo(f'systemctl start {service_name}.service', quiet=quiet)
    else:
        start_service(service_name, quiet)  # Just to make sure the service is running
