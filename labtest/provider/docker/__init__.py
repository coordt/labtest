# -*- coding: utf-8 -*-
from . import mysql
from ..base_service import BaseService


provider = {
    'mysql': BaseService('mysql', mysql.create, mysql.destroy)
}

__all__ = ['provider']
