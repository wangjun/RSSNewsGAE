#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'Liantian'
# __email__ = "liantian.me+code@gmail.com"
#
# Copyright 2015-2016 liantian
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# Stdlib imports
import os
import pytz
import datetime
import random
import string
# Third-party app imports

# Imports from your apps

# Create your models here.

random.seed = (os.urandom(1024))


class CommonSetting(object):
    SITE_URL = u"https://stocknews.liantian.me"
    ADMIN_EMAIL = u"liantian.me@gmail.com"
    TIME_FORMAT = u'%Y-%m-%d'
    TIME_ZONE  = pytz.timezone('Asia/Shanghai')
    PROCESS_TIME = datetime.datetime.now(tz  = TIME_ZONE)
    SECRET_KEY = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(32))
    CSRF_SESSION_KEY = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(32))



class Development(CommonSetting):
    DEBUG = True
    # Flask-DebugToolbar settings
    DEBUG_TB_PROFILER_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CSRF_ENABLED = True
    CACHE_TYPE = 'null'


class Production(CommonSetting):
    DEBUG = False
    CSRF_ENABLED = True
    CACHE_TYPE = 'gaememcached'
