# -*- coding: utf-8 -*-


class BaseState(object):
    """
    Base class for state providers

    When initialized, the BaseState sets its ``config`` attribute and sets
    an attribute for each key, value in the config.

    Example:
        >>> state = BaseState({'dir': 'foo', 'length': 5})
        >>> state.config
        {'dir': 'foo', 'length': 5}
        >>> state.dir
        'foo'
        >>> state.length
        5

    Args:
        config: The configuration for the state
    """
    default_config = None

    def __init__(self, config):
        if self.default_config is not None:
            self.config = self.default_config.copy()
            self.config.update(config)
        else:
            self.config = config

        for key, val in self.config.items():
            setattr(self, key, val)

    def _calc_search_paths(self, key):
        """
        Figure out the paths to search for a key

        Args:
            key: The key as a ``/`` delimited path

        Returns:
            A list of strings in the order that they should be searched, including the original key
        """
        paths = [key]

        bits = key.strip('/').split('/')
        for i in range(len(bits), 0, -1):
            paths.append('/{}/default'.format('/'.join(bits[0:i])))
        paths.append('/default')
        return paths

    def get(self, key):
        """
        Get the ``key`` from state

        It should search the state in the following manner for key=/a/b/c:

        1. ``/a/b/c``
        2. ``/a/b/c/default``
        3. ``/a/b/default``
        4. ``/a/default``
        5. ``/default``

        Args:
            key: The key to get the value for

        Returns:
            The value of the key or ``None``
        """
        raise NotImplemented()
