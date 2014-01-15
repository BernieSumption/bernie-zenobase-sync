#!/usr/bin/python

#
# This is a script that copies entries from an RSS feed to zenobase. It can be run
# on a cron job and will populate a zenobase bucket with any 
#

from __future__ import unicode_literals

import feedparser, requests, json, re, datetime, email.utils, dateutil.parser, logging, re

from collections import namedtuple


RssItem = namedtuple('RssItem', 'title link published')


def get_last_event(bucket_url):
    response = requests.get(bucket_url, params={"offset": 0, "limit": 1}).json()
    if response["total"] == 0:
        return None
    event = response["events"][0]
    timestamp = dateutil.parser.parse(event["timestamp"])
    if "resource" in event:
        return RssItem(event["resource"]["title"], event["resource"]["url"], timestamp)
    return RssItem(None, None, timestamp)


def get_rss_items(feed_url):
    feed = feedparser.parse(feed_url)
    parse_rss_item = lambda item: RssItem(
        title = item["title"],
        link = item["link"],
        published = dateutil.parser.parse(item["published"])
    )
    return map(parse_rss_item, feed["items"])


def post_to_zenobase(item, bucket_url):
    # hack around a bug where zenobase requires timestamp seconds to have a decimal point
    # i.e. "2012-3-24T13:10:00.000-07:00" is valid, "2012-3-24T13:10:00-07:00" is not
    if item.published.microsecond == 0:
        timestamp_with_explicit_ms = item.published.replace(microsecond=999999).isoformat().replace("999999", "000")
    else:
        timestamp_with_explicit_ms = item.published.isoformat()
    
    data = json.dumps({
        "resource" : {
            "title" : item.title,
            "url" : item.link
        },
        "timestamp": timestamp_with_explicit_ms
    })
    req = requests.post(bucket_url, headers={"Content-Type": "application/json"}, data=data)


def copy_new_feed_items_to_zenobase(feed_url, bucket_url):
    last_event = get_last_event(bucket_url)
    items = get_rss_items(feed_url)
    if len(items) > 0 and items[0].link == last_event.link:
        # Check if the next item link has changed. This prevents duplicates for feeds that don't
        # hold the most recent published date constant, e.g. last.fm
        logging.info(u"Most recent of %s items is still %s, skipping all." % (len(items), items[0].link))
        return 0
    count = 0
    for item in items:
        if last_event == None or (item.published > last_event.published):
            safename = re.sub(r'[^\x00-\x7F]+','?', item.title)
            logging.info(u"posting rss item %s (%s, %s)" % (safename, item.link, item.published))
            post_to_zenobase(item, bucket_url)
            count += 1
    logging.info(u"Copied %s items to zenobase, skipping %s old items" % (count, len(items) - count))
    return count


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) != 3:
        print >> sys.stderr, ("Usage: python %s feed_url, bucket_url" % sys.argv[0])
        print >> sys.stderr, ("    where bucket_url is https://api.zenobase.com/buckets/<bucket>/?code=<api key>")
        exit()
    script, feed_url, bucket_url = sys.argv
    copy_new_feed_items_to_zenobase(feed_url, bucket_url)
    
    
