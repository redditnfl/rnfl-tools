#!/usr/bin/env python
import traceback
import sys
from praw import Reddit

r = Reddit()
sub = r.subreddit(sys.argv[1])

for f in sub.flair(limit=None):
    print(f)
    try:
        if f['flair_css_class'] and 'party' in f['flair_css_class']:
            if 'Bandwagon' not in f['flair_text']:
                flair_text = "%s Bandwagon" % f['flair_text']
                print("%s: %s -> %s" % (f['user'].name, f['flair_text'], flair_text))
                sub.flair.set(f['user'], text=flair_text, css_class=f['flair_css_class'])
    except Exception as e:
        traceback.print_exc()
