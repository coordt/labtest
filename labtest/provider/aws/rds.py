# -*- coding: utf-8 -*-
from fabric.api import env, run
from fabric.context_managers import hide
import json
import click


def _get_client_sg():
    """
    @brief      Return the client security group, creating it if necessary

    @return     dict of the security group
    """

    # To get info about the running instance:
    # curl http://169.254.169.254/latest/meta-data/instance-id
    # curl http://169.254.169.254/latest/meta-data/security-groups
