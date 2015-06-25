# -*- coding: utf-8 -*-

__author__ = 'Lian Tian'
__email__ = "liantian@188.com"
__status__ = "Dev"

from google.appengine.ext import ndb


class Feed(ndb.Model):
    title = ndb.StringProperty(indexed=False)
    url = ndb.StringProperty(indexed=False)
    # delay = ndb.IntegerProperty()


class EntryCollect(ndb.Model):
    # id = ndb.TextProperty()
    published = ndb.DateTimeProperty()
    title = ndb.TextProperty()
    link = ndb.TextProperty()
    summary = ndb.TextProperty()
    feed = ndb.StringProperty(indexed=False)
    need_collect_word = ndb.BooleanProperty(default=True)
    # need_collect_word = ndb.BooleanProperty(default=True, indexed=False)
    key_word = ndb.StringProperty(repeated=True, indexed=False)
    # need_notice = ndb.BooleanProperty(default=False, indexed=False)
    need_notice = ndb.BooleanProperty(default=False)


class UserProfile(ndb.Model):
    key_word = ndb.StringProperty(repeated=True, indexed=False)
    pushover_notice = ndb.BooleanProperty(default=False, indexed=False)
    pushover_user_token = ndb.StringProperty(default="pushover_user_token", indexed=False)
    pushover_app_token = ndb.StringProperty(default="pushover_app_token", indexed=False)