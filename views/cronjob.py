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

import datetime
from flask import send_file, request, render_template, redirect, url_for, flash, jsonify
from main import app
from google.appengine.api import taskqueue
from models import KeyWord
from google.appengine.ext import ndb
from models import get_enable_keyword, get_keyword, flush_keyword_cache
from models import get_quarterly_feed_key,get_hourly_feed_key,get_daily_feed_key


@app.route('/cron/feed_corn', methods=['get','post'])
def feed_corn():
    tasks = []
    feeds = get_quarterly_feed_key()
    now = datetime.datetime.now(tz  = app.config["TIME_ZONE"])
    if now.minute/15 == 3:
        feeds += get_hourly_feed_key()
    if now.hour == 9 and now.minute/15 == 1:
        feeds += get_daily_feed_key()
    for feed in feeds:
        task = taskqueue.add(queue_name='fetch-queue',
                      url=url_for("fetch_feed"),
                      method='POST',
                      params = {"key":feed.urlsafe()}
                      )
        tasks.append(task)
    return "Done",200


