
This is a utility for transferring RSS feeds to zenobase. A new zenobase event is created
in a specified bucket for every item in the RSS feed. The link and publication date of a
feed item is used to prevent duplicate events.

It can be run from the command line like so:

python rss_to_zenobase.py \
       "http://ws.audioscrobbler.com/1.0/user/berniecode/recenttracks.rss" \
       "https://api.zenobase.com/buckets/<bucket id>/?code=<api key>"

This can be run as a cron job on any always-on computer.

Alternatively, it can be run from Google AppEngine. You'll need to create an application,
on appspot.com, edit app.yaml to insert the correct application id, inastall the requirements
as described in requirements.txt and deploy the app. This is not the whole story. I don't
suggest trying this unless you know your way around appengine or are willing to spend some
time reading docs and tinkering, as there are gotchas.
