# -*- coding: utf-8 -*-
from fabric.api import run
from labtest.provider.base_state import BaseState


class ScriptState(BaseState):
    """
    Implements retrieval of state information from filesystem documents
    """
    default_config = {}

    def get(self, key):
        """
        Get the value of ``key`` from ``bucket`` navigating the hierarchy of the key path

        Args:
            key:     The key, as a ``/`` delimited path.

        Returns:
            The value or ``None``
        """
        response = run('{} {}'.format(self.command, key))

        if response != '':
            return response
        return None
