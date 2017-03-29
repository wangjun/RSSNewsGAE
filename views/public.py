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

from flask import render_template
from main import app

from models import get_latest_news, get_pure_keyword, get_important_news


@app.route('/', methods=['GET'])
def index():
    news_list = get_latest_news()
    user_key_word = get_pure_keyword()
    return render_template("index.html", news_list=news_list, user_key_word=user_key_word)


@app.route('/important', methods=['GET'])
def important():
    news_list = get_important_news()
    user_key_word = get_pure_keyword()
    return render_template("index.html", news_list=news_list, user_key_word=user_key_word)
