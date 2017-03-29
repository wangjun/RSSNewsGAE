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


from google.appengine.ext import ndb
from google.appengine.api import memcache

from main import app

feed_delay_choice = ('daily', 'hourly', 'quarterly')


class Feed(ndb.Model):
    enable = ndb.BooleanProperty(default=True)
    title = ndb.StringProperty(indexed=False)
    url = ndb.StringProperty(indexed=False)
    latest_fetch = ndb.DateTimeProperty(indexed=False)
    delay = ndb.StringProperty(choices=feed_delay_choice)


class NewsEntry(ndb.Model):
    published = ndb.DateTimeProperty()
    title = ndb.TextProperty()
    link = ndb.TextProperty()
    summary = ndb.TextProperty()
    feed = ndb.TextProperty()
    key_word = ndb.TextProperty(repeated=True, indexed=False)
    important = ndb.BooleanProperty(default=False)


class KeyWord(ndb.Model):
    word = ndb.StringProperty(indexed=False)
    enable = ndb.BooleanProperty(default=True)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def get_keyword():
    data = memcache.get(key="keyword")
    if data is None:
        q = KeyWord.query()
        data = ndb.get_multi(q.fetch(keys_only=True))
        memcache.add(key="keyword", value=data, time=86400 * 30)
    return data


def get_enable_keyword():
    data = memcache.get(key="enable_keyword")
    if data is None:
        q = KeyWord.query(KeyWord.enable == True)
        data = ndb.get_multi(q.fetch(keys_only=True))
        memcache.add(key="enable_keyword", value=data, time=86400 * 30)
    return data

def get_pure_keyword():
    data = memcache.get(key="pure_keyword")
    if data is None:
        data = []
        q = KeyWord.query(KeyWord.enable == True)
        key_words = ndb.get_multi(q.fetch(keys_only=True))
        for key_word in key_words:
            data.append(key_word.word)
        memcache.add(key="pure_keyword", value=data, time=86400 * 30)
    return data



def flush_keyword_cache():
    return memcache.delete_multi(keys=["enable_keyword", "keyword",'pure_keyword'])


def get_feed():
    data = memcache.get(key="feed")
    if data is None:
        q = Feed.query()
        data = ndb.get_multi(q.fetch(keys_only=True))
        memcache.add(key="feed", value=data, time=86400 * 30)
    return data


def get_daily_feed():
    data = memcache.get(key="daily_feed")
    if data is None:
        q = Feed.query(Feed.delay == "daily", Feed.enable == True)
        data = ndb.get_multi(q.fetch(keys_only=True))
        memcache.add(key="daily_feed", value=data, time=86400 * 30)
    return data


def get_hourly_feed():
    data = memcache.get(key="hourly_feed")
    if data is None:
        q = Feed.query(Feed.delay == "hourly", Feed.enable == True)
        data = ndb.get_multi(q.fetch(keys_only=True))
        memcache.add(key="hourly_feed", value=data, time=86400 * 30)
    return data


def get_quarterly_feed():
    data = memcache.get(key="quarterly_feed")
    if data is None:
        q = Feed.query(Feed.delay == "quarterly", Feed.enable == True)
        data = ndb.get_multi(q.fetch(keys_only=True))
        memcache.add(key="quarterly_feed", value=data, time=86400 * 30)
    return data


def flush_feed_cache():
    return memcache.delete_multi(keys=["feed", "daily_feed", "hourly_feed", "quarterly_feed"])


def get_daily_feed_key():
    return Feed.query(Feed.delay == "daily", Feed.enable == True).fetch(keys_only=True)


def get_hourly_feed_key():
    return Feed.query(Feed.delay == "hourly", Feed.enable == True).fetch(keys_only=True)


def get_quarterly_feed_key():
    return Feed.query(Feed.delay == "quarterly", Feed.enable == True).fetch(keys_only=True)


def get_latest_news():
    data = memcache.get(key="latest_news")
    if data is None:
        q = NewsEntry.query().order(-NewsEntry.published)
        data = ndb.get_multi(q.fetch(limit=app.config["PER_PAGE"],keys_only=True))
        memcache.add(key="latest_news", value=data, time=app.config["INDEX_CACHE_TIME"])
    return data


def get_important_news():
    data = memcache.get(key="important_news")
    if data is None:
        q = NewsEntry.query(NewsEntry.important==True).order(-NewsEntry.published)
        data = ndb.get_multi(q.fetch(limit=app.config["PER_PAGE"],keys_only=True))
        memcache.add(key="important_news", value=data, time=app.config["INDEX_CACHE_TIME"])
    return data