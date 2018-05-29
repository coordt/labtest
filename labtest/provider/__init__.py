# -*- coding: utf-8 -*-
from future.utils import iteritems
import click
from . import docker
from . import aws
from . import local


service_providers = {
    'docker': docker.service_provider,
}

state_providers = {
    'aws': aws.state_provider,
    'local': local.state_provider,
}

secret_providers = {
    'aws': aws.secret_provider
}


def check_services_config(services):
    """
    Make sure the services are configured correctly

    Args:
        services:  The services confgiuration to check
    Raises:
        ClickException: If there is an error
    """
    for service_name, config in iteritems(services):
        if 'provider' not in config:
            raise click.ClickException('The service "{}" doesn\'t have a provider specified'.format(service_name))
        if 'service' not in config:
            raise click.ClickException('The service "{}" doesn\'t have a service specified'.format(service_name))
        if config['service'] not in service_providers[config['provider']]:
            raise click.ClickException('The {provider} provider doesn\'t have a registered service of "{service}".'.format(**config))

__all__ = ['secret_providers', 'service_providers', 'state_providers', 'check_services_config']
