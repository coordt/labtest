# -*- coding: utf-8 -*-
"""
A collection of common functions to setup and destroy OS services
"""
from fabric.api import run, sudo
from fabric.contrib.files import upload_template, exists
from fabric.context_managers import hide
import click


def start_service(service_name, quiet=False):
    """
    Make sure the service is running
    """
    status = run('systemctl is-active {}'.format(service_name), quiet=quiet)
    if status == 'inactive':
        sudo('systemctl start {}'.format(service_name), quiet=quiet)
    elif status == 'unknown':
        click.ClickException(click.style('There was an issue starting the service. The test server doesn\'t recognize it.'), fg='red')


def delete_service(service_name, quiet=False):
    """
    Remove the service and clean up

    Args:
        service_name: The name of the service
        quiet: Set to ``True`` to suppress Fabric output
    """
    systemd_dest = '/etc/systemd/system/{}.service'.format(service_name)
    if exists(systemd_dest):
        click.echo('Deleting the OS service: {}'.format(service_name))
        sudo('systemctl stop {}.service'.format(service_name), quiet=quiet)
        sudo('systemctl disable {}.service'.format(service_name), quiet=quiet)
        sudo('rm {}'.format(systemd_dest), quiet=quiet)


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
    systemd_tmp_dest = '/tmp/{}.service'.format(service_name)
    systemd_dest = '/etc/systemd/system/{}.service'.format(service_name)
    if not exists(systemd_dest):
        click.echo('Creating the OS service.')
        with hide('running'):
            upload_template(systemd_template, systemd_tmp_dest, context)
        sudo('mv {} {}'.format(systemd_tmp_dest, systemd_dest), quiet=quiet)
        sudo('systemctl enable {}.service'.format(service_name), quiet=quiet)
        click.echo('Starting the OS service: {}'.format(service_name))
        sudo('systemctl start {}.service'.format(service_name), quiet=quiet)
    else:
        start_service(service_name, quiet)  # Just to make sure the service is running
