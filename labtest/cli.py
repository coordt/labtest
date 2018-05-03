# -*- coding: utf-8 -*-

import click
from config import get_config, check_config
from dotenv import load_dotenv, find_dotenv
import instance


@click.group(invoke_without_command=True)
@click.option('--config', '-c', type=click.Path(exists=True), help='Alternate configuration file.')
@click.option('--verbose', '-v', is_flag=True, default=False, help='Show verbose output.')
@click.pass_context
def cli(ctx, config, **kwargs):
    """Console script for labtest"""
    cfg = get_config(config, **kwargs)
    if not cfg.validate():
        click.ClickException(cfg.validation_message())
    ctx.obj = cfg

cli.add_command(instance.create)
cli.add_command(check_config, 'check-config')

if __name__ == "__main__":
    load_dotenv(find_dotenv())
    cli(obj={}, auto_envvar_prefix='LABTEST')
