#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

__author__ = 'Lian Tian'
__email__ = "liantian@188.com"
__status__ = "Dev"

import os
import webapp2
import uuid
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from gaesessions import get_current_session

from models import EntryCollect
from models import UserProfile

PER_PAGE = 50

template.register_template_library('common.curfilter')


class MainHandler(webapp2.RequestHandler):
    def get(self):
        q = EntryCollect.query().order(-EntryCollect.published)
        top_entry = ndb.get_multi(q.fetch(PER_PAGE, keys_only=True))
        user = users.get_current_user()
        if user:
            profile = UserProfile.get_or_insert(user.user_id())
            user_key_word = profile.key_word
        else:
            user_key_word = None

        template_values = {
            'user': user,
            'ecs': top_entry,
            "logout": users.create_logout_url('/'),
            "login": users.create_login_url('/'),
            'user_key_word': user_key_word
        }
        path = os.path.join(os.path.dirname(__file__)+'/templates/', 'index.html')
        self.response.out.write(template.render(path, template_values))


class EditProfile(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.response.out.write('<html><body><a href="%s">Sign in or register</a>.</body></html>' % users.create_login_url('/'))
        session = get_current_session()
        # if session.is_active():
        # session.regenerate_id()
        csrf = str(uuid.uuid4())
        session['csrf'] = csrf
        profile = UserProfile.get_or_insert(user.user_id())
        template_values = {
            'user': user,
            "profile": profile,
            "csrf": csrf,
            "logout": users.create_logout_url('/'),
            "login": users.create_login_url('/'),
        }
        path = os.path.join(os.path.dirname(__file__)+'/templates/', 'profile.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        user = users.get_current_user()
        if not user:
            raise self.error(403)
        csrf = self.request.get("csrf", default_value="")
        session = get_current_session()
        if csrf != session['csrf']:
            raise self.error(403)
        # pushover_app_token = self.request.get("pushover_app_token", default_value="")
        pushover_user_token = self.request.get("pushover_user_token", default_value="")
        pushover_notice = bool(self.request.get("pushover_notice", default_value=""))
        key_word = self.request.get("key_word", default_value="")
        profile = UserProfile.get_by_id(user.user_id())
        # profile.pushover_app_token = pushover_app_token
        profile.pushover_user_token = pushover_user_token
        profile.pushover_notice = pushover_notice
        profile.key_word = filter(None, key_word.replace(' ', '').replace('\n', '').replace('\t', '').split(','))
        profile.put()
        session['csrf'] = None
        self.redirect("/")


class FilterEntry(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.response.out.write('<html><body><a href="%s">Sign in or register</a>.</body></html>' % users.create_login_url('/'))
        profile = UserProfile.get_or_insert(user.user_id())

        if len(profile.key_word) < 1:
            self.redirect("/")

        # keys = EntryCollect.query(EntryCollect.key_word.IN(profile.key_word)).order(-EntryCollect.published)
        # top_entry = ndb.get_multi(keys.fetch(20, keys_only=True))


        keys = EntryCollect.query().order(-EntryCollect.published)
        entrys = ndb.get_multi(keys.fetch(PER_PAGE*2, keys_only=True))
        top_entry = []
        for entry in entrys:
            if set(profile.key_word).intersection(set(entry.key_word)):
                top_entry.append(entry)

        template_values = {
            'user': user,
            'ecs': top_entry,
            "logout": users.create_logout_url('/'),
            "login": users.create_login_url('/'),
            'user_key_word': profile.key_word,

        }
        path = os.path.join(os.path.dirname(__file__)+'/templates/', 'index.html')
        self.response.out.write(template.render(path, template_values))


class KeyWordEntry(webapp2.RequestHandler):
    def get(self, keyword):

        user = users.get_current_user()
        if user:
            profile = UserProfile.get_or_insert(user.user_id())
            user_key_word = profile.key_word
        else:
            user_key_word = None

        # q = EntryCollect.query(EntryCollect.key_word == keyword).order(-EntryCollect.published)
        # top_entry = ndb.get_multi(q.fetch(50, keys_only=True))
        keys = EntryCollect.query().order(-EntryCollect.published)
        entrys = ndb.get_multi(keys.fetch(PER_PAGE*2, keys_only=True))
        top_entry = []
        for entry in entrys:
            if keyword.decode('utf-8') in entry.key_word:
                top_entry.append(entry)

        template_values = {
            'user': user,
            'ecs': top_entry,
            "logout": users.create_logout_url('/'),
            "login": users.create_login_url('/'),
            'user_key_word': user_key_word,
            'keyword': keyword
        }
        path = os.path.join(os.path.dirname(__file__)+'/templates/', 'index.html')
        self.response.out.write(template.render(path, template_values))