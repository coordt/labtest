# -*- coding: utf-8 -*-


class BaseService(object):
    """
    Base class for managing a backing service

    :param service: The type of the service, like ``mysql`` or ``redis``
    :param create_function: The function to call to create the service
    :param destroy_function: The function to call to destroy the service
    :param check_config_function: The function to call to check for a valid configuration for this service
    """

    def __init__(self, service, create_function=None, destroy_function=None, check_config_function=None):
        self.service = service
        self.create_function = create_function
        self.destroy_function = destroy_function
        self.check_config_function = check_config_function

    def create(self, config, name):
        """
        Creates the service (if necessary)

        Example result::

            {
                'environment': [],  # Items to add to the environment of the container (--env)
                'links': [],  # links in the ``containername:localname`` format for --link
                'hosts': []  # Add hosts using the --add-host option
            }

        :param config:  The configuration for the service
        :param name:    The name of the service

        :return: dict
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

        :param      config:  The configuration of the service
        :param      name:    The name of the service
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

        If sub-classes don't provide a ``check_config_function``, it will always
        return ``True``.

        :param      self:    The object
        :param      config:  The configuration

        :return:     boolean
        """
        if self.check_config_function is None:
            return True
        else:
            return self.check_config_function(config)
