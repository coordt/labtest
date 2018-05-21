# -*- coding: utf-8 -*-
from __future__ import absolute_import
from future.utils import iteritems
from past.builtins import basestring
from .configobj import Config
import click


class LabTestConfig(Config):
    default_config_files = [
        '.labtest.yml',
        '.labtest.yaml',
        'setup.cfg',
        'package.json',
    ]
    namespace = 'labtest'
    required_attrs = [
        'host',
        'app_name',
        'test_domain',
        'container_provider',
        'build_provider',
        'host_name_pattern',
        'environment',
        'docker_image_pattern',
        'services',
    ]
    dependencies = {
        'build_provider': {
            'default': [
                'code_repo_url', 'app_build_image', 'app_build_command',
                'container_build_command', 'container_provider',
            ]
        }
    }

    def get_default_services(self):
        """
        The services the experiment requires. Defaults to an empty dict
        """
        return {}

    def get_default_build_provider(self):
        """
        The default provider of the build
        """
        return 'default'

    def get_default_docker_image_pattern(self):
        """
        Return the default docker image name pattern
        """
        return '%(APP_NAME)s/%(INSTANCE_NAME)s:latest'

    def get_default_host_name_pattern(self):
        """
        Return the default host name pattern
        """
        return '%(APP_NAME)s-%(INSTANCE_NAME)s'

    def set_use_ssh_config(self, value):
        """
        Make sure the value is converted to a boolean
        """
        if isinstance(value, basestring):
            self._config['use_ssh_config'] = (value.lower() in ['1', 'true', 'yes', ])
        elif isinstance(value, int):
            self._config['use_ssh_config'] = (value == 1)
        elif isinstance(value, bool):
            self._config['use_ssh_config'] = value
        else:
            self._config['use_ssh_config'] = False

    def get_default_use_ssh_config(self):
        return False

    def set_environment(self, value):
        """
        Make sure the environment is a list
        """
        if isinstance(value, basestring):
            self._config['environment'] = value.split(',')
        elif isinstance(value, (list, tuple)):
            self._config['environment'] = list(value)  # convert tuples to list

    def get_default_environment(self):
        """
        Return an empty list as the default environment
        """
        return []

    def get_default_app_build_image(self):
        """
        Make the app build image config optional
        """
        return ''

    def get_default_app_build_command(self):
        """
        Make the app build image command optional
        """
        return ''

    def get_default_container_provider(self):
        """
        Where are the images stored by default?
        """
        return 'local'

    def get_default_container_build_command(self):
        return 'docker build -t $APP_NAME/$INSTANCE_NAME --build-arg RELEASE=$RELEASE --build-arg APP_NAME=$APP_NAME --build-arg BRANCH_NAME=$BRANCH_NAME --build-arg INSTANCE_NAME=$INSTANCE_NAME .'

    def get_default_app_name(self):
        """
        The default app_name is the name of the directory containing the .git directory
        """
        import os
        import subprocess
        out = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'])
        dirname, name = os.path.split(out.strip())
        return name

    def validate_dependencies(self):
        """
        Make sure extra options are set, if necessary
        """
        config = self.config
        missing_attrs = []

        for option, dependency in iteritems(self.dependencies):
            for dep_option in dependency.get(config[option], []):
                if dep_option not in config:
                    default_func = getattr(self, 'get_default_{}'.format(dep_option), None)
                    if default_func:
                        setattr(self, dep_option, default_func())
                    else:
                        missing_attrs.append(dep_option)
        return missing_attrs


def get_config(filepath='', **kwargs):
    """
    Get the configuration based off all the ways you can pass it

    Can raise IOError if the filepath passed in doesn't exist

    Precedence:
        1. Command-line arguments
        2. Configuration file
    """
    config = LabTestConfig()
    if not filepath:
        config.parse_default_config()
    else:
        config.parse_file(filepath)

    for key, val in iteritems(kwargs):
        setattr(config, key, val)
    return config


def _format_config(val, key='', indent=0, indent_amt=2):
    """
    recursive dict/list formatter
    """
    spaces = ' ' * indent * indent_amt
    if indent > 10:
        click.ClickException('WHATSGOINGON!')
    if isinstance(val, (list, tuple)):
        if key:
            click.echo(spaces, nl=False)
            click.echo(click.style('{}:'.format(key), bold=True))
            indent += 1
        for item in val:
            _format_config(item, '', indent, indent_amt)
        if key:
            indent -= 1
    elif isinstance(val, dict):
        if key:
            click.echo(spaces, nl=False)
            click.echo(click.style('{}:'.format(key), bold=True))
            indent += 1
        for subkey, subval in iteritems(val):
            # indent += 1
            _format_config(subval, subkey, indent, indent_amt)
    else:
        if key:
            click.echo(spaces, nl=False)
            click.echo(click.style('{}:'.format(key), bold=True), nl=False)
            click.echo(' {}'.format(val))
        else:
            click.echo('{}{}'.format(spaces, val))


@click.command()
@click.pass_context
def check_config(ctx):
    """
    Check the configuration and output any errors
    """
    ctx.obj.validate()
    click.echo(ctx.obj.validation_message())
    click.echo('')
    _format_config(ctx.obj.config, 'Configuration')
