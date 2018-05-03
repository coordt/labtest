# -*- coding: utf-8 -*-


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

        for key, val in kwargs.items():
            setattr(self, key, val)

    @property
    def config(self):
        """
        This returns the configuration as a dict.

        This method will use the logic in `__getattr__` to set the values.
        It doesn't just return the default `_config` dict.
        """
        cfg = {}
        for key, val in self._config.items():
            cfg[key] = getattr(self, key)
        return cfg

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
                msg.append('The configuration is missing the following required attributes:')
                msg.append(', '.join(self._validation_errors['Missing Attributes']))
            return ' '.join(msg)
        else:
            return 'The configuration is valid.'

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
        raise AttributeError

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
        from dotenv import find_dotenv

        for option in self.default_config_files:
            path = find_dotenv(option)
            if path:
                self.parse_file(path)

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
        import ConfigParser

        if not os.path.exists(filepath):
            raise IOError()
        configparser = ConfigParser.ConfigParser()
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

        for key, val in config.get(self.namespace, {}).items():
            setattr(self, key, val)

    def read_yaml_config(self, filepath):
        """
        Reads a configuration from a YAML file
        """
        import oyaml as yaml
        with open(filepath, 'r') as f:
            config = yaml.load(f)

        for key, val in config.get(self.namespace, {}).items():
            setattr(self, key, val)