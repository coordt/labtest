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


def test_yaml_config():
    """
    Make sure the YAML processing is working
    """
    c = config.get_config(os.path.join(FIXTURE_DIR, 'config.yml'))
    assert c.app_name == 'testing'
    assert c.hosts == ['10.2.3.4']
    assert c.use_ssh_config is True
    assert c.provider == 'aws'


def test_yaml_missing_labtest():
    """
    It should return an empty configuration
    """
    c = config.get_config(os.path.join(FIXTURE_DIR, 'config_missing_labtest.yml'))

    assert len(c.config.keys()) == 0


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
    assert c.app_name == 'testing'
    assert c.hosts == ['10.2.3.4']
    assert c.use_ssh_config is True
    assert c.provider == 'aws'


def test_json_missing_labtest():
    """
    It should return an empty configuration
    """
    c = config.get_config(os.path.join(FIXTURE_DIR, 'config_missing_labtest.json'))

    assert len(c.config.keys()) == 0


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
    assert c.app_name == 'testing'
    assert c.hosts == ['10.2.3.4']
    assert c.use_ssh_config is True
    assert c.provider == 'aws'


def test_ini_missing_labtest():
    """
    It should return an empty configuration
    """
    c = config.get_config(os.path.join(FIXTURE_DIR, 'config_missing_labtest.ini'))

    assert len(c.config.keys()) == 0


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
        "hosts": "kwarg",
        "use_ssh_config": False,
        "provider": "kwarg"
    }
    c = config.get_config(os.path.join(FIXTURE_DIR, 'config.yml'), **kw_overrides)
    assert c.app_name == kw_overrides['app_name']
    assert c.hosts == [kw_overrides['hosts']]
    assert c.use_ssh_config == kw_overrides['use_ssh_config']
    assert c.provider == kw_overrides['provider']
