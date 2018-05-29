# -*- coding: utf-8 -*-

from __future__ import absolute_import
import click
from .config import get_config, check_config
from dotenv import load_dotenv, find_dotenv
from . import instance
from . import secrets


@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), help='Alternate configuration file.')
@click.option('--verbose', '-v', is_flag=True, default=False, help='Show verbose output.')
@click.pass_context
def main(ctx, config, **kwargs):
    """Console script for labtest"""
    cfg = get_config(config, **kwargs)
    if not cfg.validate():
        click.ClickException(cfg.validation_message())
    ctx.obj = cfg


@main.command()
def version():
    """
    Display the current labtest client version
    """
    from labtest import __version__
    click.echo(__version__)


main.add_command(instance.create)
main.add_command(instance.update)
main.add_command(instance.delete)
main.add_command(instance.list)
main.add_command(instance.test)
main.add_command(secrets.encrypt)
main.add_command(check_config, 'check-config')

if __name__ == "__main__":
    load_dotenv(find_dotenv())
    main(obj={}, auto_envvar_prefix='LABTEST')
