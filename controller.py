# -*- coding: utf-8 -*-

__author__ = 'Lian Tian'
__email__ = "liantian@188.com"
__status__ = "Dev"

import os
import pprint
import webapp2
import re
import datetime
import logging
from feedparser import feedparser
from dateutil import parser

from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue


from models import Feed
from models import EntryCollect
from models import UserProfile

import json
import urllib


COLLECT_DAYS = 0
COLLECT_HOURS = 2
ENTRY_SAVE_DAYS = 2
JIEBA_URL = "http://localhost:8080/analyse"
# JIEBA_URL = "http://2b359e.appspot.com/analyse"
PUSH_OVER_URL = "https://api.pushover.net/1/messages.json"
PUSH_OVER_APP = ""

CONT = 5


def clean_html(html):
    return re.sub('<[^<]+?>', '', html)


class FetchFeed(webapp2.RequestHandler):
    def get(self):
        self.rpc_fetch()
        self.response.out.write("It's done!")

    @staticmethod
    def rpc_fetch():
        q = Feed.query()
        results = ndb.get_multi(q.fetch(keys_only=True))

        rpcs = []
        for f in results:
            rpc = urlfetch.create_rpc()
            urlfetch.make_fetch_call(rpc, f.url)
            rpcs.append(rpc)

        for rpc in rpcs:
            rpc.wait()
            result = rpc.get_result()
            d = feedparser.parse(result.content)
            for e in d['entries']:
                dt = parser.parse(e["published"]).replace(tzinfo=None)
                dy = (datetime.datetime.utcnow() - datetime.timedelta(days=COLLECT_DAYS, seconds=COLLECT_HOURS*3600)).replace(tzinfo=None)
                if dt > dy:
                    obj = EntryCollect.get_or_insert(e["id"])
                    if obj.published and obj.published >= dt:
                        pass
                    else:
                        logging.info("new entry : %s" % e["id"])
                        obj.published = dt
                        obj.title = e["title"]
                        obj.link = e["link"]
                        obj.summary = clean_html(e["summary"])
                        obj.feed = d['feed']['title']
                        obj.need_collect_word = True
                        obj.need_notice = True
                        obj.put()


class DelOldEntry(webapp2.RequestHandler):
    def get(self):
        self.del_old_entry()
        self.response.out.write("It's done!")

    @staticmethod
    def del_old_entry():
        earliest = datetime.datetime.now() - datetime.timedelta(days=ENTRY_SAVE_DAYS)
        keys = EntryCollect.query(EntryCollect.published <= earliest).fetch(keys_only=True)
        ndb.delete_multi(keys)


class InitGAE(webapp2.RequestHandler):
    def get(self):
        self.init_gae()
        self.response.out.write("It's done!")

    @staticmethod
    def init_gae():
        f = Feed()
        f.url = 'http://money.163.com/special/00252EQ2/yaowenrss.xml'
        f.title = '要闻综合-网易财经'
        f.put()


class CollectWord(webapp2.RequestHandler):
    def get(self):
        entrys = EntryCollect.query(EntryCollect.need_collect_word == True).order(-EntryCollect.published).fetch()
        # q = EntryCollect.query().order(-EntryCollect.published)
        # entrys = ndb.get_multi(q.fetch(CONT*2, keys_only=True))
        for entry in entrys:
            if entry.need_collect_word:
                self.collect_word(entry)
        self.response.out.write("It's done!")

    # @staticmethod
    # def collect_word_all(self):
    #     q = EntryCollect.query(EntryCollect.need_collect_word == True).order(-EntryCollect.published)
    #     entrys = ndb.get_multi(q.fetch(20, keys_only=True))
    #     for entry in entrys:
    #         self.collect_word(entry)

    @staticmethod
    def collect_word(entry):
        # try:
        form_fields = {
            "text": entry.summary.encode("utf-8"),
            "topK": 20
        }
        form_data = urllib.urlencode(form_fields)
        result = urlfetch.fetch(url=JIEBA_URL,
                                payload=form_data,
                                method=urlfetch.POST,
                                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                follow_redirects=False)

        pprint.pprint( result.content)
        result = json.loads(result.content)
        key_words = result["result"]

        del entry.key_word[:]
        entry.need_notice = True
        entry.key_word = key_words
        # except:
        #     entry.need_notice = False
        entry.need_collect_word = False
        entry.put()
        return True


class PushOver(webapp2.RequestHandler):
    def get(self):
        self.handle_requests()

    def post(self):
        self.handle_requests()

    def handle_requests(self):
        form_fields = {
            "token": PUSH_OVER_APP,
            "user": self.request.get("user", default_value=""),
            "message": self.request.get("message", default_value="").encode("utf-8"),
            "url": self.request.get("url", default_value="").encode("utf-8"),
            # "url_title": self.request.get("url_title", default_value="").encode("utf-8"),
            "url_title": u"点击访问正文".encode("utf-8"),
            "title": self.request.get("title", default_value="").encode("utf-8"),
        }
        form_data = urllib.urlencode(form_fields)
        result = urlfetch.fetch(url=PUSH_OVER_URL,
                                payload=form_data,
                                method=urlfetch.POST,
                                headers={'Content-Type': 'application/x-www-form-urlencoded'})
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(result.content)


class PushMsg(webapp2.RequestHandler):
    def get(self):
        entrys = EntryCollect.query(EntryCollect.need_notice == True).order(-EntryCollect.published).fetch()
        # q_entry = EntryCollect.query().order(-EntryCollect.published)
        # entrys = ndb.get_multi(q_entry.fetch(CONT*2, keys_only=True))
        for entry in entrys:
            if entry.need_notice and len(entry.key_word) > 0:
                self.push_msg(entry)
        self.response.out.write("It's done!")

    @staticmethod
    def push_msg(entry):
        key = UserProfile.query()
        all_users = ndb.get_multi(key.fetch(keys_only=True))
        for one_user in all_users:
            if set(one_user.key_word).intersection(set(entry.key_word)):
                params = {"user": one_user.pushover_user_token,
                          "message": entry.summary,
                          "title": entry.title,
                          "url": entry.link,
                          "url_title": entry.title}
                taskqueue.add(url='/admin/PushOver', params=params)
        entry.need_notice = False
        entry.put()