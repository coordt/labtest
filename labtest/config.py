# -*- coding: utf-8 -*-
from __future__ import absolute_import
from future.utils import iteritems
from past.builtins import basestring
from .configobj import Config
import click

from fabric.api import task, execute
from fabric.context_managers import hide
from fabric.contrib.files import exists
from .filesystem import get_file_contents


@task
def get_state():
    """
    Task to get the state provider from the remote server and return a State object

    Returns:
        A subclass instance of :class:`BaseState` or ``None``
    """
    import json
    from labtest.provider import state_providers

    remote_path = '/testing/state.json'
    if exists(remote_path):
        try:
            state_config = json.loads(get_file_contents(remote_path).getvalue())
        except Exception as e:
            raise click.ClickException('There was an issue reading the state config: {}'.format(e))

        if state_config['provider'] not in state_providers:
            raise click.ClickException('The state provider "{}" is does not exist in this version of LabTest.'.format(state_config['provider']))
        elif state_config.get('service') not in state_providers[state_config['provider']]:
            raise click.ClickException('The state provider "{}" is does not have a state service of "{}" in this version of LabTest.'.format(state_config['provider'], state_config['service']))
        else:
            return state_providers[state_config['provider']][state_config['service']](state_config.get('options', {}))
    else:
        return None


class LabTestConfig(Config):
    default_config_files = [
        '.labtest.yml',
        '.labtest.yaml',
        'setup.cfg',
        'package.json',
    ]
    namespace = 'labtest'
    required_attrs = [
        'app_build_command',
        'app_build_image',
        'app_name',
        'build_provider',
        'container_provider',
        'docker_image_pattern',
        'environment',
        'host',
        'host_name_pattern',
        'services',
        'test_domain',
        'verbose',
    ]
    dependencies = {
        'build_provider': {
            'default': [
                'code_repo_url', 'app_build_image', 'app_build_command',
                'container_build_command', 'container_provider',
            ]
        }
    }

    def get_default_app_build_command(self):
        """
        Make the app build image command optional
        """
        return ''

    def get_default_app_build_image(self):
        """
        Make the app build image config optional
        """
        return ''

    def get_default_app_name(self):
        """
        The default app_name is the name of the directory containing the .git directory
        """
        import os
        import subprocess
        out = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'])
        dirname, name = os.path.split(out.strip())
        return name

    def get_default_build_provider(self):
        """
        The default provider of the build
        """
        return 'default'

    def get_default_container_provider(self):
        """
        Where are the images stored by default?
        """
        return 'local'

    def get_default_container_build_command(self):
        return 'docker build -t $APP_NAME/$INSTANCE_NAME --build-arg RELEASE=$RELEASE --build-arg APP_NAME=$APP_NAME --build-arg BRANCH_NAME=$BRANCH_NAME --build-arg INSTANCE_NAME=$INSTANCE_NAME .'

    def get_default_docker_image_pattern(self):
        """
        Return the default docker image name pattern
        """
        return '%(APP_NAME)s/%(INSTANCE_NAME)s:latest'

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

    def get_default_host_name_pattern(self):
        """
        Return the default host name pattern
        """
        return '%(APP_NAME)s-%(INSTANCE_NAME)s'

    def get_default_services(self):
        """
        The services the experiment requires. Defaults to an empty dict
        """
        return {}

    def get_state(self):
        """
        Retrieves the state object and caches it
        """
        if 'state' not in self._config:
            with hide('running'):
                self._config['state'] = execute(get_state, hosts=self.host)[self.host]

        return self._config['state']

    def get_secrets(self):
        """
        Retrieves the secret provider from state and caches it
        """
        import json
        from labtest.provider import secret_providers

        if 'secrets' not in self._config:
            secret_config = json.loads(self.state.get('/secrets'))
            if not isinstance(secret_config, dict):
                raise click.ClickException('The secret provider configuration is not recognized.')
            elif secret_config.get('provider') not in secret_providers:
                raise click.ClickException('The secret provider "{}" is not configured in this version of LabTest'.format(secret_config.get('provider')))
            elif secret_config.get('service') not in secret_providers[secret_config['provider']]:
                raise click.ClickException('The secret provider "{}" is does not have a service of "{}" in this version of LabTest.'.format(secret_config['provider'], secret_config.get('service')))
            else:
                self._config['secrets'] = secret_providers[secret_config['provider']][secret_config['service']](secret_config.get('options', {}))

        return self._config['secrets']

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

    def get_default_verbose(self):
        return False

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
