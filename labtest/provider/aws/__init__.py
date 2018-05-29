# -*- coding: utf-8 -*-
from .state import S3State
from .secrets import KMSSecret

service_provider = {}
state_provider = {'s3': S3State}
secret_provider = {'kms': KMSSecret}

__all__ = ['state_provider', 'service_provider', 'secret_provider', ]
