from nflapi import NFL
from nflapi.shield import shield, WeekOrderBy, OrderByDirection
from redditnfl.nfltools.nflteams import get_team

from sgqlc.operation import Operation

from pprint import pprint


def division_standings(teams):
    standings = {}
    for team, record in teams:
        div = (team.conference_abbr, team.division_full_name.split(' ')[1])
        if div not in standings:
            standings[div] = []
        standings[div].append((team, record))

    for div in standings:
        standings[div].sort(key=lambda t: t[1].division.rank)

    return standings


def fmt_record(standings):
    ret = '{s.overall.wins}-{s.overall.losses}'.format(s=standings)
    if standings.overall.ties:
        ret += '-{s.overall.ties}'.format(s=standings)
    return ret


def fmt_playoffs(standings):
    symbols = [
        ("playoff", "x"),
        ("division", "y"),
        ("wild_card", "z"),
        ("home_field", "*"),
        ("eliminated", "†"),
    ]
    ret = ""
    for attr, s in symbols:
        if getattr(standings.clinched, attr, False):
            ret += s
    return "^" + ret if ret else ret


def run(reddit_session, **config):
    nfl = NFL(ua='nfl scores sidebar')
    ret = config['header']
    records = nfl.standings.current()

    standings = division_standings(records)

    for conference in ('AFC', 'NFC'):
        for left_division, right_division in (('North', 'South'), ('East', 'West')):
            ret += "|{c}|{ld}|{c}|{rd}|\n".format(c=conference, ld=left_division, rd=right_division)
            ret += "|--:|:--|--:|:--|\n"
            for p in range(4):
                lteam, lstandings = standings[(conference, left_division)][p]
                rteam, rstandings = standings[(conference, right_division)][p]
                lteam = get_team(lteam.abbreviation)
                rteam = get_team(rteam.abbreviation)
                ret += "|[*{lt}*]({lsr})|{lr}{lleg}|[*{rt}*]({rsr})|{rr}{rleg}|\n".format(
                    lt=lteam['short'],
                    lsr=lteam['subreddit'],
                    lr=fmt_record(lstandings),
                    lleg=fmt_playoffs(lstandings),
                    rt=rteam['short'],
                    rsr=rteam['subreddit'],
                    rr=fmt_record(rstandings),
                    rleg=fmt_playoffs(rstandings)
                )
            ret += '\n'
    return ret + config['footer']


if __name__ == '__main__':
    print(run(None, header='', footer=''))
