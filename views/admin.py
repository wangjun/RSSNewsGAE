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

from google.appengine.ext import ndb
from flask import request, render_template, redirect, url_for, flash, jsonify

from main import app
from models import KeyWord, Feed
from models import get_feed, flush_feed_cache
from models import get_keyword, flush_keyword_cache


@app.route('/admin/', methods=['GET'])
def admin():
    keyword_list = get_keyword()
    feed_list = get_feed()
    return render_template("admin.html", keyword_list=keyword_list, feed_list=feed_list)


@app.route('/admin/add_keyword', methods=['post'])
def add_keyword():
    word = request.form.get('word')
    if word is not None:
        key = KeyWord()
        key.word = word
        key.enable = True
        key.put()
        flash(u'KeyWord add successfully~', 'success')
        flush_keyword_cache()
    return redirect(url_for("admin"))


@app.route('/admin/del_keyword/<key>', methods=['get'])
def del_keyword(key):
    ndb.Key(urlsafe=key).delete()
    flush_keyword_cache()
    return redirect(url_for("admin"))


@app.route('/admin/keyword_switch', methods=['post'])
def keyword_switch():
    content = request.get_json(silent=True)
    if content is not None:
        action = content['action']
        key = content['key']
        keyword = ndb.Key(urlsafe=key).get()
        keyword.enable = not keyword.enable
        keyword.put()
        flush_keyword_cache()
        return jsonify(result=True, key=key, action=action)
    else:
        return jsonify(result=False)


@app.route('/admin/add_feed', methods=['post'])
def add_feed():
    title = request.form.get('title')
    url = request.form.get('url')
    delay = request.form.get('delay')
    feed = Feed()
    feed.url = url
    feed.title = title
    feed.delay = delay
    feed.latest_fetch = datetime.datetime.now()
    feed.put()
    flash(u'KeyWord add successfully~', 'success')
    flush_feed_cache()
    return redirect(url_for("admin"))


@app.route('/admin/del_feed/<key>', methods=['get'])
def del_feed(key):
    ndb.Key(urlsafe=key).delete()
    flush_feed_cache()
    return redirect(url_for("admin"))


@app.route('/admin/feed_switch', methods=['post'])
def feed_switch():
    content = request.get_json(silent=True)
    if content is not None:
        action = content['action']
        key = content['key']
        feed = ndb.Key(urlsafe=key).get()
        feed.enable = not feed.enable
        feed.put()
        flush_feed_cache()
        return jsonify(result=True, key=key, action=action)
    else:
        return jsonify(result=False)
