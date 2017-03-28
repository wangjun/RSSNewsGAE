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
from models import KeyWord
from google.appengine.ext import ndb
from models import get_enable_keyword, get_keyword, flush_keyword_cache
from models import get_quarterly_feed,get_hourly_feed,get_daily_feed


import re
from time import mktime
from datetime import datetime
import feedparser

from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from models import NewsEntry

from models import Feed

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0"
DEADLINE = 1


def clean_html(html):
    return re.sub('<[^<]+?>', '', html)


def url2parser(url):
    try:
        result = urlfetch.fetch(url, headers={'User-Agent': USER_AGENT}, deadline=DEADLINE)
        if result.status_code == 200:
            parser = feedparser.parse(result.content)
            return parser
        else:
            return None
    except:
        return None


def check_entry(entry):
    try:
        if not entry.published:
            return False
        elif not entry.title:
            return False
        elif not entry.link:
            return False
        elif not entry.summary:
            return False
        else:
            return True
    except:
        return False



@app.route('/queue/fetch_feed/', methods=['post'])
def fetch_feed():
    key = request.values.get('key')
    feed = ndb.Key(urlsafe=key).get()
    parser = url2parser(feed.url)
    if parser is not None:
        the_last_fetch = feed.latest_fetch
        feed.latest_fetch = datetime.now()
        list_of_news_entities = []
        ndb.put_multi(list_of_news_entities)
        for entry in parser.entries:
            if check_entry(entry):
                entry.published = datetime.fromtimestamp(mktime(entry.published_parsed))
                if entry.published > the_last_fetch:
                    news_entry = NewsEntry()
                    news_entry.published = entry.published
                    news_entry.title = entry.title
                    news_entry.link = entry.link
                    news_entry.summary = clean_html(entry.summary)
                    news_entry.feed = feed.title
                    list_of_news_entities.append(news_entry)
        list_of_news_entities.append(feed)
        ndb.put_multi(list_of_news_entities)
        return "Done",200
    else:
        return None