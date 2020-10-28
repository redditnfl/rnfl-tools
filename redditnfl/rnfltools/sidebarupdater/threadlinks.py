
def run(reddit_session, **config):
    i = 1
    results = []
    while '{}_query'.format(i) in config:
        print(repr(dir(reddit_session)))
        sub = reddit_session.subreddit(config['%d_sub' % i])
        q = config['%d_query' % i]
        sort = config.get('%i_sort' % i, 'relevance')
        limit = int(config.get('%i_limit' % i, 5))
        results += list(sub.search(q, sort=sort, limit=limit))
        i += 1
    return "\n".join([config['link'].format(thread=r) for r in results])


if __name__ == "__main__":
    from praw import Reddit
    r = Reddit()
    print(run(r, **{
        '1_sub': 'nfl',
        '1_query': 'author:NFL_Mod AND flair:"Free Talk"',
        '1_sort': 'new',
        '1_limit': '7',
        'link': ' * [{thread.permalink}]({thread.title})',
    }))
