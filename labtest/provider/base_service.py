# -*- coding: utf-8 -*-


class BaseService(object):
    """
    Base class for managing a backing service

    Args:
        service: The type of the service, like ``mysql`` or ``redis``
        create_function: The function to call to create the service
        destroy_function: The function to call to destroy the service
        check_config_function: The function to call to check for a valid configuration for this service
    """

    def __init__(self, service, create_function=None, destroy_function=None, check_config_function=None):
        self.service = service
        self.create_function = create_function
        self.destroy_function = destroy_function
        self.check_config_function = check_config_function

    def create(self, config, name):
        """
        Creates the service (if necessary)

        Args:
            config:  The configuration for the service
            name:    The name of the service

        Returns:
            A ``dict`` that may include ``environment`` or ``hosts`` keys. These
            are a method of communication back to the experiment to potentially
            alter its own container

            Example result::

                {
                    'environment': [],  # Items to add to the environment of the container (--env)
                    'hosts': []  # Add hosts using the --add-host option
                }
        """
        if config.get('provision_type', 'independent') != 'independent':
            return {}  # There is nothing to do if it isn't an independent provision
        if self.create_function is None:
            raise NotImplemented()
        else:
            return self.create_function(config, name)

    def destroy(self, config, name):
        """
        Removes the service, if it is still there, and cleans up

        Args:
            config:  The configuration of the service
            name:    The name of the service
        """
        if config.get('provision_type', 'independent') != 'independent':
            return  # There is nothing to do if it isn't an independent provision
        if self.destroy_function is None:
            raise NotImplemented()
        else:
            self.destroy_function(config, name)

    def check_config(self, config):
        """
        Check the configuration to make sure it is valid for this service.

        Note:
            If sub-classes don't provide a ``check_config_function``, it will always
            return ``True``.

        Args:
            self:    The object
            config:  The configuration

        Returns:
            ``True`` if the configuration is valid, otherwise ``False``.
        """
        if self.check_config_function is None:
            return True
        else:
            return self.check_config_function(config)
