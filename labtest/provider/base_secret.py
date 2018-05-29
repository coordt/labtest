# -*- coding: utf-8 -*-


class BaseSecret(object):
    """
    Base class for secret providers

    When initialized, the BaseSecret sets its ``config`` attribute and sets
    an attribute for each key, value in the config.

    Example:
        >>> state = BaseSecret({'dir': 'foo', 'length': 5})
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

    def encrypt(self, plaintext):
        """
        Encrypt the plaintext and return the result

        Args:
            plaintext: The text to encrypt
        Returns:
            The encrypted secret
        """
        raise NotImplemented()

    def decrypt(self, ciphertext):
        """
        Decrypt the ciphertext and return the result

        Args:
            ciphertext: The encrypted secret to decrypt
        Returns:
            The plaintext
        """
        raise NotImplemented()
