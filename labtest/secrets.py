# -*- coding: utf-8 -*-

import click
from future.utils import iteritems
from fabric.api import env, task, execute


def _setup_env_with_config(config):
    """
    Add config keys to the env
    """
    env.config = config
    for key, val in iteritems(config.config):
        setattr(env, key, val)
    env.quiet = not config.verbose


@task
def encrypt_task(plaintext):
    """
    Encrypt a secret with the configured secret provider

    Args:
        plaintext: The text to encrypt

    Returns:
        The encrypted ciphertext
    """
    sec_provider = env.config.secrets
    return sec_provider.encrypt(plaintext)


@click.command()
@click.argument('plaintext')
@click.pass_context
def encrypt(ctx, plaintext):
    """
    Encrypt a secret
    """
    _setup_env_with_config(ctx.obj)
    do_parts = False
    key = ''
    val = plaintext
    if '=' in plaintext:
        key, val = plaintext.split('=')
        do_parts = click.confirm('Did you want to encrypt "{}" for key "{}"? (No will encrypt the entire string)'.format(val, key))
        if not do_parts:
            key = ''
            val = plaintext
    result = execute(encrypt_task, val, hosts=ctx.obj.host)
    ciphertext = result[ctx.obj.host]
    click.echo('')
    if key:
        click.echo('Add this to the appropriate environment configuration section:')
        click.echo('')
        click.echo('{}=ENC[{}]'.format(key, ciphertext))
    else:
        click.echo('Your value is encrypted. Add this appropriate environment configuration section:')
        click.echo('')
        click.echo('ENC[{}]'.format(ciphertext))
