#!/usr/bin/env python3
import traceback

from progressbar import ProgressBar, ETA, FormatLabel, Bar
import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from praw import Reddit
from redditnfl.reddittools.reddittoken import ensure_scopes
import sys
import pytz

EST = pytz.timezone('America/New_York')
UTC = pytz.utc

def userage(u):
    return (datetime.now().date() - datetime.utcfromtimestamp(u.created_utc).date()).days

def get_comments(u):
    if not hasattr(u, '__vet_comments'):
        comments = []
        for comment in u.comments.new(limit=1000):
            comments.append(comment)
        u.__vet_comments = comments
    return u.__vet_comments

def topcomments_count(n):
    def f(u):
        s = {}
        c = 0
        for comment in get_comments(u):
            sub = comment.subreddit.display_name
            if sub not in s:
                s[sub] = 0
            s[sub] += 1
            c += 1
        top = sorted(s.items(), key=lambda n: n[1], reverse=True)[0:n]
        return ", ".join(["{s} ({p:.0f}%)".format(n=n, p=100.0*n/c, s=s) for s, n in top])
    return f

def subreddit_karma(sub):
    def f(u):
        karma = 0
        for comment in get_comments(u):
            if comment.subreddit.display_name == sub:
                karma += comment.score
        return karma
    return f

def modof(u):
    url = "https://old.reddit.com/user/%s/overview" % u.name
    headers = {
            'user-agent': 'applicantstats/0.1;r/nfl',
            }
    response = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response.content, 'html5lib')
    try:
        return ", ".join([a.string.replace('r/', '') for a in soup.find(text='MODERATOR OF').parent.parent.next_sibling.find_all('a')][0:5])
    except AttributeError as e:
        return ""

def hourly_breakdown(u):
    hours = dict((hour, 0) for hour in range(24))
    for comment in get_comments(u):
        utc_dt = UTC.localize(datetime.utcfromtimestamp(comment.created_utc))
        eastern = utc_dt.astimezone(EST)
        hours[eastern.hour] += 1
    return ",".join(map(str, hours.values()))
        

    

stats = {
        'Account age': userage,
        'username': lambda u: u.name,
        'Link karma': lambda u: u.link_karma,
        'Comment karma': lambda u: u.comment_karma,
        'Top-3 SR by comment count': topcomments_count(3),
        'NFL comment karma': subreddit_karma('nfl'),
        'Mod of (top 5)': modof,
        'Hourly Breakdown (EST)': hourly_breakdown,
        }

def main():
    r = Reddit('vet')
    ensure_scopes(r, 'read,history')

    infile = sys.argv[1]
    outfile = sys.argv[2]

    with open(outfile, 'w') as outf:
        out = csv.DictWriter(outf, ['inputname'] + list(stats.keys()))
        out.writeheader()
        
        users = []
        with open(infile, 'r') as fp:
            for line in fp:
                un = line.strip().replace('u/', '').replace('/', '')
                users.append(un)

        print("\nVetting %d users\n" % len(users))
        
        with ProgressBar(max_value=len(users), widgets=[ETA(), ' ', Bar(marker='=', left='[', right=']'), ' ', FormatLabel('%(value)d/%(max_value)d')]) as p:
            for i, un in enumerate(users):
                user = r.redditor(un)
                userstats = {'inputname': user}
                try:
                    user.created_utc
                    for k, f in stats.items():
                        try:
                            userstats[k] = f(user)
                        except Exception as e:
                            traceback.print_exc()
                            userstats[k] = ""
                except Exception as e:
                    traceback.print_exc()
                out.writerow(userstats)
                p.update(i)


if __name__ == '__main__':
    main()

