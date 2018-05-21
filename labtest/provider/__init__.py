# -*- coding: utf-8 -*-
from future.utils import iteritems
import click
from . import docker
from . import aws


providers = {
    'docker': docker.provider,
    'aws': aws.provider,
}


def check_services_config(services):
    """
    @brief      Make sure the services are configured correctly

    @param      services  The services confgiuration
    """
    for service_name, config in iteritems(services):
        if 'provider' not in config:
            raise click.ClickException('The service "{}" doesn\'t have a provider specified'.format(service_name))
        if 'service' not in config:
            raise click.ClickException('The service "{}" doesn\'t have a service specified'.format(service_name))
        if config['service'] not in providers[config['provider']]:
            raise click.ClickException('The {provider} provider doesn\'t have a registered service of "{service}".'.format(**config))

__all__ = ['providers', 'check_services_config']
