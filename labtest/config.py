# -*- coding: utf-8 -*-
from configobj import Config
import click


class LabTestConfig(Config):
    default_config_files = [
        '.labtest.yml',
        'setup.cfg',
        'package.json',
    ]
    namespace = 'labtest'
    required_attrs = [
        'code_repo_url',
        'host',
        'app_name',
        'provider',
        'env_template',
    ]

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

    for key, val in kwargs.items():
        setattr(config, key, val)
    return config


@click.command()
@click.pass_context
def check_config(ctx):
    """
    Check the configuration and output any errors
    """
    ctx.obj.validate()
    click.echo(ctx.obj.validation_message())
    click.echo('')
    click.echo('Configuration:')
    for key, val in ctx.obj.config.items():
        click.echo('  {}: {}'.format(key, val))
