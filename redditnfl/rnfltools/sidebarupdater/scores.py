from collections import namedtuple

import pendulum
from nflapi import NFL
from nflapi.shield import shield, WeekType
from redditnfl.nfltools.nflteams import get_team
from sgqlc.operation import Operation

dgd = namedtuple('DefaultGameDetails', ['home_points_total', 'visitor_points_total'])


def week_name(cw):
    return {
        WeekType.HOF: "Hall of Fame Week",
        WeekType.PRE: "Pre Season Week {cw.week_value}",
        WeekType.WC: "Wildcard Weekend",
        WeekType.DIV: "Divisional Round",
        WeekType.CONF: "Conference Championships",
        WeekType.PRO: "Probowl Week",
        WeekType.SB: "Super Bowl",
        WeekType.REG: "Week {cw.week_value}",
    }.get(cw.week_type, "Week {cw.week_value}").format(cw=cw)


def run(reddit_session, **config):
    default_gd = dgd(0, 0)

    nfl = NFL(ua='nfl scores sidebar')
    cw = nfl.schedule.current_week()
    games = nfl.game.week_games(cw.week_value, cw.season_type, cw.season_value)

    ids = [game.game_detail_id for game in games if hasattr(game, 'game_detail_id') and game.game_detail_id]
    op = Operation(shield.Viewer)
    gd = op.viewer.league.game_details_by_ids(ids=ids)
    gd.__fields__('id', 'home_points_total', 'visitor_points_total')
    details = nfl.query(op).viewer.league.game_details_by_ids
    details = {gd.id: gd for gd in details}

    ret = config['header'].format(w=cw, wn=week_name(cw))
    tz = pendulum.timezone(config.get('tz', 'US/Eastern'))
    for g in games:
        home = get_team(g.home_team.abbreviation)
        away = get_team(g.away_team.abbreviation)
        time = g.game_time.astimezone(tz)
        gd = details.get(g.game_detail_id, default_gd)
        ret += config['row'].format(g=g, gd=gd, time=time, home=home, away=away)

    return ret + config['footer']


if __name__ == "__main__":
    print(run(None, **{
        'header': '# {wn} Schedule\n\nTime|Away||@||Home\n|:--|:--:|--:|:--:|:--|:--:|\n',
        'row': '{time:%a %I:%M%p}|[*{away[short]}*]({away[subreddit]})|{gd.visitor_points_total}|@|{gd.home_points_total}|[*{home[short]}*]({home[subreddit]})\n',
        'footer': ''
    }))
