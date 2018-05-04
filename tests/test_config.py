#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_config
----------------------------------

Tests for `config` module.
"""
import os
import pytest
from labtest import config

FIXTURE_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), 'fixtures'))


def check_config_result(config):
    """
    Easy way to make sure the configuration is what we think instead of doing it
    multiple times
    """
    assert config.validate() is True, config.validation_message()
    assert config.app_name == 'testing'
    assert config.host == '10.2.3.4'
    assert config.use_ssh_config is True
    assert len(config.environment) == 3


def test_single_environment_string():
    """
    Make sure an environment string without commas works
    """
    c = config.get_config(os.path.join(FIXTURE_DIR, 'config.yml'))
    c.environment = 'NUMBER=1'
    assert len(c.environment) == 1
    assert c.environment == ['NUMBER=1']


def test_yaml_config():
    """
    Make sure the YAML processing is working
    """
    c = config.get_config(os.path.join(FIXTURE_DIR, 'config.yml'))
    check_config_result(c)


def test_yaml_missing_labtest():
    """
    It should return an empty configuration
    """
    c = config.get_config(os.path.join(FIXTURE_DIR, 'config_missing_labtest.yml'))
    assert c.validate() is False


def test_yaml_missing_config():
    """
    It should return an empty configuration
    """
    with pytest.raises(IOError):
        c = config.get_config(os.path.join(FIXTURE_DIR, 'file_doesnt_exist.yml'))  # NOQA


def test_json_config():
    """
    Make sure the JSON processing is working
    """
    c = config.get_config(os.path.join(FIXTURE_DIR, 'config.json'))
    check_config_result(c)


def test_json_missing_labtest():
    """
    It should return an empty configuration
    """
    c = config.get_config(os.path.join(FIXTURE_DIR, 'config_missing_labtest.json'))

    assert c.validate() is False


def test_json_missing_config():
    """
    It should return an empty configuration
    """
    with pytest.raises(IOError):
        c = config.get_config(os.path.join(FIXTURE_DIR, 'file_doesnt_exist.json'))  # NOQA


def test_ini_config():
    """
    Make sure the INI processing is working
    """
    c = config.get_config(os.path.join(FIXTURE_DIR, 'config.ini'))
    check_config_result(c)


def test_ini_missing_labtest():
    """
    It should return an empty configuration
    """
    c = config.get_config(os.path.join(FIXTURE_DIR, 'config_missing_labtest.ini'))

    assert c.validate() is False


def test_ini_missing_config():
    """
    It should return an empty configuration
    """
    with pytest.raises(IOError):
        c = config.get_config(os.path.join(FIXTURE_DIR, 'file_doesnt_exist.ini'))  # NOQA


def test_overrides():
    """
    Test that passing overrides gets included in the config
    """
    kw_overrides = {
        "app_name": "kwarg",
        "host": "kwarg",
        "use_ssh_config": False,
        "provider": "kwarg"
    }
    c = config.get_config(os.path.join(FIXTURE_DIR, 'config.yml'), **kw_overrides)
    assert c.app_name == kw_overrides['app_name']
    assert c.host == kw_overrides['host']
    assert c.use_ssh_config == kw_overrides['use_ssh_config']
    assert c.provider == kw_overrides['provider']
