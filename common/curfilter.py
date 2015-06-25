#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

__author__ = 'Lian Tian'
__email__ = "liantian@188.com"
__status__ = "Dev"


from datetime import timedelta
from google.appengine.ext.webapp import template
register = template.create_template_register()


def timezone(value, offset):
    return value + timedelta(hours=offset)

register.filter(timezone)