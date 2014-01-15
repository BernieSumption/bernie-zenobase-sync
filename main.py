""" main.py is the top level script.

Return "Hello World" at the root URL.
"""


from __future__ import unicode_literals

import os
import sys
import logging
import time
import itertools
import datetime
import .settings

from google.appengine.api.logservice import logservice

from rss_to_zenobase import copy_new_feed_items_to_zenobase

# sys.path includes 'server/lib' due to appengine_config.py
from flask import Flask
from flask import render_template, redirect, request
app = Flask(__name__.split('.')[0])



@app.route('/')
def index():
    loglines = []
    req_logs = logservice.fetch(minimum_log_level=logservice.LOG_LEVEL_INFO,
                include_app_logs=True, include_incomplete=True)
    req_logs= list(itertools.islice(req_logs, 0, 10))
    return render_template('hello.html', req_logs=req_logs)

@app.route('/poll-now')
def poll_now():
    if request.headers.get('X-AppEngine-Cron'):
        logging.info("Starting cron poll...")
    else:
        logging.info("Starting manually initiated poll...")
    copy_new_feed_items_to_zenobase(settings.RSS_URL, settings.BUCKET_URL)
    return redirect('/')

def isodate(timestamp):
    """ Convert a timestamp to an ISO date """
    return datetime.datetime.fromtimestamp(timestamp).isoformat()

app.jinja_env.filters["isodate"] = isodate