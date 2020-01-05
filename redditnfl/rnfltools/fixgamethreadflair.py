#!/usr/bin/env python

from praw import Reddit
import sys

# Pre and Post game threads have been set to "event-thread" rather than "game-thread"
# Go through as many as possible and fix that

r = Reddit()
sub = r.subreddit(sys.argv[1])

for q in ('author:nfl_gamethread title:"Pre Game Thread"', 'author:nfl_gamethread title:"Post Game Thread"'):
    for thread in sub.search(q, sort='new', syntax='lucene', time_filter='all', limit=None):
        print("%s - %s" % (thread.id, thread.title))
        for k in filter(lambda p: p.startswith('link_flair'), dir(thread)):
            v = getattr(thread, k, None)
            if v:
                print("  %s=%s" % (k, v))
        if thread.link_flair_css_class == 'event-thread' or not thread.link_flair_css_class:
            new_class = 'game-thread'
            new_text = thread.link_flair_text
            if not new_text or new_text == 'event':
                new_text = 'Pre Game Thread' if 'Pre Game' in q else 'Post Game Thread'
            print("!!%s -> %s (%s)" % (thread.link_flair_css_class, new_class, new_text))
            thread.mod.flair(text=new_text, css_class=new_class)
