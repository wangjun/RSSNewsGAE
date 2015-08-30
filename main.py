#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# import sys
# default_encoding = 'utf-8'
# if sys.getdefaultencoding() != default_encoding:
#     reload(sys)
#     sys.setdefaultencoding(default_encoding)

import webapp2
#


from controller import FetchFeed
from controller import DelOldEntry
from controller import InitGAE
from controller import CollectWord
from controller import PushOver, PushMsg
from views import MainHandler
# from views import TestPage
from views import EditProfile
from views import FilterEntry
from views import KeyWordEntry


app = webapp2.WSGIApplication([
    (r'/', MainHandler),
    (r'/key/(.*)/', KeyWordEntry),
    (r'/user/profile', EditProfile),
    (r'/user/filter', FilterEntry),

    (r'/admin/InitGAE', InitGAE),
    (r'/admin/PushOver', PushOver),

    (r'/cron/FetchFeed', FetchFeed),
    (r'/cron/DelOldEntry', DelOldEntry),
    (r'/cron/CollectWord', CollectWord),
    (r'/cron/PushMsg', PushMsg),

], debug=True)

