from datetime import datetime
import pendulum
from nflapi import NFL
from redditnfl.nfltools.nflteams import get_team

def run(reddit_session, **config):
    nfl = NFL(ua='nfl scores sidebar')
    cw = nfl.schedule.current_week()
    games = nfl.game.week(cw)
    ret = config['header'].format(w=cw)
    tz = pendulum.timezone(config.get('tz', 'US/Eastern'))
    for g in games:
        home = get_team(g.homeTeam.abbr)
        away = get_team(g.visitorTeam.abbr)
        time = g.gameTime.astimezone(tz)
        ret += config['row'].format(g=g, time=time, home=home, away=away)

    return ret + config['footer'] 
