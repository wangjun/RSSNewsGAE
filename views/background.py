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

import json
import re
import urllib
from datetime import datetime
from time import mktime

from google.appengine.api import taskqueue
from google.appengine.api import urlfetch
from google.appengine.ext import ndb

import feedparser
from flask import request, url_for
from main import app
from models import NewsEntry
from models import get_pure_keyword
from models import get_quarterly_feed_key, get_hourly_feed_key, get_daily_feed_key


def clean_html(html):
    return re.sub('<[^<]+?>', '', html)


def url2parser(url):
    try:
        result = urlfetch.fetch(url, headers={'User-Agent': app.config['USER_AGENT']}, deadline=app.config['DEADLINE'])
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


@app.route('/background/launch_fetch/', methods=['get', 'post'])
def launch_fetch():
    feeds = get_quarterly_feed_key()
    now = datetime.now(tz=app.config["TIME_ZONE"])
    if now.minute / 15 == 3:
        feeds += get_hourly_feed_key()
    if now.hour == 9 and now.minute / 15 == 1:
        feeds += get_daily_feed_key()
    for feed in feeds:
        taskqueue.add(queue_name='fetch-queue',
                      url=url_for("fetch_one_feed"),
                      method='POST',
                      params={"key": feed.urlsafe()}
                      )
    return "Done", 200


@app.route('/background/fetch_one_feed/', methods=['post'])
def fetch_one_feed():
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
        feed.put()
        news_key_list = ndb.put_multi(list_of_news_entities)
        for news_key in news_key_list:
            taskqueue.add(queue_name='collect-queue',
                          url=url_for("collect_keyword_for_one_news"),
                          method='POST',
                          params={"key": news_key.urlsafe()}
                          )
        return "Done", 200
    else:
        return "parser is None", 200


@app.route('/background/collect_keyword_for_one_news/', methods=['post'])
def collect_keyword_for_one_news():
    user_key_word = get_pure_keyword()
    key = request.values.get('key')
    news = ndb.Key(urlsafe=key).get()
    form_fields = {
        "text": news.summary.encode("utf-8"),
        "topK": app.config["TOP_KEYWORD"],
        "withWeight": 0
    }
    form_data = urllib.urlencode(form_fields)
    result = urlfetch.fetch(url=app.config["JIEBA_API"],
                            payload=form_data,
                            method=urlfetch.POST,
                            headers={'Content-Type': 'application/x-www-form-urlencoded'},
                            follow_redirects=False)
    json_content = json.loads(result.content)
    key_words = json_content["result"]
    del news.key_word[:]
    news.key_word = key_words
    tmp = [val for val in key_words if val in user_key_word]
    if tmp:
        news.important = True
    if tmp and app.config["PUSHOVER"]:
        taskqueue.add(queue_name='push-msg-queue',
                      url=url_for("push_important_news"),
                      method='POST',
                      params={"key": key})
    news.put()
    return "Done", 200


@app.route('/background/push_important_news/', methods=['post'])
def push_important_news():
    key = request.values.get('key')
    news = ndb.Key(urlsafe=key).get()
    form_fields = {
        "token": app.config["PUSHOVER_APP_KEY"],
        "user": app.config["PUSHOVER_USER_KEY"],
        "message": news.summary.encode("utf-8"),
        "url": news.link.encode("utf-8"),
        "url_title": u"点击访问正文".encode("utf-8"),
        "title": news.title.encode("utf-8"),
    }
    form_data = urllib.urlencode(form_fields)
    urlfetch.fetch(url=app.config["PUSH_OVER_URL"],
                   payload=form_data,
                   method=urlfetch.POST,
                   headers={'Content-Type': 'application/x-www-form-urlencoded'},
                   follow_redirects=False,
                   validate_certificate=False)
    return "Done", 200


@app.route('/background/delete_old_news/', methods=['post', 'get'])
def delete_old_news():
    q = NewsEntry.query(NewsEntry.important == True).order(-NewsEntry.published)
    ndb.delete_multi(q.fetch(offset=app.config["PER_PAGE"], keys_only=True))
    q = NewsEntry.query(NewsEntry.important == False).order(-NewsEntry.published)
    ndb.delete_multi(q.fetch(offset=app.config["PER_PAGE"], keys_only=True))
    return "Done", 200
