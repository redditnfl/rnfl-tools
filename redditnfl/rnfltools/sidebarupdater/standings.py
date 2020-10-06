from nflapi import NFL
from redditnfl.nfltools.nflteams import get_team
import requests
import json


def division(abbr):
    return ({'AC': 'AFC',
             'NC': 'NFC'}[abbr[0:2]],
            {'E': 'East',
             'N': 'North',
             'S': 'South',
             'W': 'West'}[abbr[2]])

def division_standings(teams):
    standings = {}
    for team in teams:
        if team.standings[0].divisionRank is None:
            raise Exception('No rank in data. Aborting')
        div = division(team.division.abbr)
        if div not in standings:
            standings[div] = []
        standings[div].append((team, team.standings[0]))
    for div in standings:
        standings[div].sort(key=lambda t: (1-t[1].overallWinPct, t[1].divisionRank, t[0].fullName))
    return standings

def record(standings):
    ret = '{s.overallWins}-{s.overallLosses}'.format(s=standings)
    if standings.overallTies:
        ret += '-{s.overallTies}'.format(s=standings)
    return ret

def playoff_status(season):
    url = 'http://www.nfl.com/static/content/playoff-picture/%d/playoff-picture.json' % season
    resp = requests.get(url, headers={'User-Agent': 'nfl scores sidebar'})
    status = json.loads(resp.text)
    ret = {}
    for conference in status['standings']:
        for key in ['eliminated', 'hunt', 'wild', 'leaders']:
            if 'team' not in conference[key]:
                continue
            teams = conference[key]['team']
            if not isinstance(teams, list):
                teams = [teams]
            for team in teams:
                if key == 'eliminated':
                    team['leg'] += '\u2020'
                if team['id'] == 'NO' and not team['leg']:
                    team['leg'] = 'y'
                ret[team['id']] = '^' + team['leg'] if team['leg'] else ''
    return ret


def run(reddit_session, **config):
    nfl = NFL(ua='nfl scores sidebar')
    ret = config['header']
    teams, week = nfl.standings.current()

    standings = division_standings(teams)
    try:
        playoffs = playoff_status(week.season)
    except Exception as e:
        playoffs = {}

    for conference in ('AFC', 'NFC'):
        for left_division, right_division in (('North', 'South'),('East', 'West')):
            ret += "|{c}|{ld}|{c}|{rd}|\n".format(c=conference, ld=left_division, rd=right_division)
            ret += "|--:|:--|--:|:--|\n"
            for p in range(4):
                lteam, lstandings = standings[(conference, left_division)][p]
                rteam, rstandings = standings[(conference, right_division)][p]
                lteam = get_team(lteam.abbr)
                rteam = get_team(rteam.abbr)
                ret += "|[*{lt}*]({lsr})|{lr}{lleg}|[*{rt}*]({rsr})|{rr}{rleg}|\n".format(
                        lt=lteam['short'],
                        lsr=lteam['subreddit'],
                        lr=record(lstandings),
                        lleg=playoffs.get(lteam['short'], ''),
                        rt=rteam['short'],
                        rsr=rteam['subreddit'],
                        rr=record(rstandings),
                        rleg=playoffs.get(rteam['short'], '')
                        )
            ret += '\n'
    return ret + config['footer'] 

if __name__ == '__main__':
    print(run(None, header='', footer=''))
