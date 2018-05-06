# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from future import standard_library
from future.utils import iteritems
from builtins import object
import click
standard_library.install_aliases()


class Config(object):
    # A mapping of extensions to method names to use when processing config files
    extension_map = {
        '.cfg': 'read_ini_config',
        '.ini': 'read_ini_config',
        '.json': 'read_json_config',
        '.yml': 'read_yaml_config',
        '.yaml': 'read_yaml_config',
    }

    # Where to automatically look for the configuration information
    default_config_files = [
        '.labtest.yml',
        'setup.cfg',
        'package.json',
    ]
    # namespace is the section under which it looks for the key/values
    # in the config file
    namespace = 'config'

    # required_attrs is are the configuration attributes required before continuing
    # It is used by the validation method
    required_attrs = []

    def __init__(self, **kwargs):
        self._config = {}
        self._validation_errors = {}

        for key, val in iteritems(kwargs):
            setattr(self, key, val)

    @property
    def config(self):
        """
        This returns the configuration as a dict.

        This method will use the logic in `__getattr__` to set the values.
        It doesn't just return the default `_config` dict.
        """
        cfg = {}
        for item in self.required_attrs:
            if item not in self._config:
                default_func = getattr(self, 'get_default_{}'.format(item), None)
                if default_func:
                    cfg[item] = default_func()
        for key, val in iteritems(self._config):
            cfg[key] = getattr(self, key)
        return cfg

    def validate_dependencies(self):
        """
        Subclasses should override this command to provide validation for options
        that are required based on other option's values
        """
        pass

    def validate(self):
        """
        Validate the configuration. Set the attribute `validation_errors`
        """
        self._validation_errors = {}
        is_valid = True
        config = self.config
        missing_attrs = []
        for attr in self.required_attrs:
            if attr not in config:
                is_valid = False
                missing_attrs.append(attr)

        missing_attrs.extend(self.validate_dependencies())

        if missing_attrs:
            self._validation_errors['Missing Attributes'] = missing_attrs
        return is_valid

    def validation_message(self):
        """
        Convenience method to format the validation errors, if any
        """
        msg = []
        if self._validation_errors:
            if 'Missing Attributes' in self._validation_errors:
                msg.append(click.style('The configuration is missing the following required attributes:', fg='red'))
                msg.append(', '.join(self._validation_errors['Missing Attributes']))
            return ' '.join(msg)
        else:
            return click.style('The configuration is valid.', fg='green')

    def __getattr__(self, name):
        """
        Get a configuration attribute via several methods

        1. Look for a `get_<attribute>` function and call it.
           This allows for some processing of the value if it needs to be
           stored one way, but used in another, or is a composite value.
        2. Look for the attribute in the `_config` dict.
           The `_config` attribute is the local storage of the configuration
           attributes.
        3. Look for a `get_default_<attribute>` function and call it.
           The value returned is set in the `_config` dict for next time before
           getting returned.
        4. Raise `AttributeError` if nothing is found
        """
        attr_name = 'get_{}'.format(name)
        attr_default_name = 'get_default_{}'.format(name)
        if name.startswith('get_'):
            raise AttributeError
        elif hasattr(self, attr_name):
            return getattr(self, attr_name)()
        elif name in self._config:
            return self._config[name]
        elif hasattr(self, attr_default_name):
            self._config[name] = getattr(self, attr_default_name)()
            return self._config[name]
        raise AttributeError('The configuration attribute "{}" is not set.'.format(name))

    def __setattr__(self, name, value):
        """
        Set the configuration attribute via a setter or directly in the `_config`

        1. Attributes starting with `_` are automatically set.
        2. If a `set_<attribute>` method exists, call it.
           This allows for processing of the value and validation. This function
           *must* update the attribute in `self._config`
        3. Set the attribute in `_config` to the value passed.
        """
        attr_name = 'set_{}'.format(name)
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        elif hasattr(self, attr_name):
            fn = getattr(self, attr_name)
            fn(value)
        else:
            self._config[name] = value

    def parse_default_config(self):
        """
        Look for the default config path from the `default_config_files`.
        """
        import os
        from dotenv import find_dotenv

        for option in self.default_config_files:
            path = find_dotenv(option, usecwd=True)
            if path:
                self.config_file_path = os.path.normpath(path)
                self.parse_file(path)
                break

    def parse_file(self, filepath):
        """
        Determine which method to use to parse the file, based on the file extension
        """
        import os

        name, ext = os.path.splitext(filepath)
        if ext in self.extension_map:
            getattr(self, self.extension_map[ext])(filepath)

    def read_ini_config(self, filepath):
        """
        Read a configuration from an INI file
        """
        import os
        import configparser

        if not os.path.exists(filepath):
            raise IOError()
        configparser = configparser.ConfigParser()
        configparser.read([filepath])
        if self.namespace in configparser.sections():
            for key, val in configparser.items(self.namespace):
                setattr(self, key, val)

    def read_json_config(self, filepath):
        """
        Read a configuration from a JSON file
        """
        import json
        with open(filepath, 'r') as f:
            config = json.loads(f.read())

        for key, val in iteritems(config.get(self.namespace, {})):
            setattr(self, key, val)

    def read_yaml_config(self, filepath):
        """
        Reads a configuration from a YAML file
        """
        import oyaml as yaml
        with open(filepath, 'r') as f:
            config = yaml.load(f)

        for key, val in iteritems(config.get(self.namespace, {})):
            setattr(self, key, val)
