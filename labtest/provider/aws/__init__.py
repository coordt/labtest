# -*- coding: utf-8 -*-
from .state import S3State

service_provider = {}
state_provider = {'s3': S3State}

__all__ = ['state_provider', 'service_provider', ]
