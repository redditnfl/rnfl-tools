from nflapi import NFL
from redditnfl.nfltools.nflteams import get_team

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

def run(reddit_session, **config):
    nfl = NFL(ua='nfl scores sidebar')
    ret = config['header']
    teams, _ = nfl.standings.current()

    standings = division_standings(teams)

    for conference in ('AFC', 'NFC'):
        for left_division, right_division in (('North', 'South'),('East', 'West')):
            ret += "|{c}|{ld}|{c}|{rd}|\n".format(c=conference, ld=left_division, rd=right_division)
            ret += "|--:|:--|--:|:--|\n"
            for p in range(4):
                lteam, lstandings = standings[(conference, left_division)][p]
                rteam, rstandings = standings[(conference, right_division)][p]
                lteam = get_team(lteam.abbr)
                rteam = get_team(rteam.abbr)
                ret += "|[*{lt}*]({lsr})|{lr}|[*{rt}*]({rsr})|{rr}|\n".format(
                        lt=lteam['short'],
                        lsr=lteam['subreddit'],
                        lr=record(lstandings),
                        rt=rteam['short'],
                        rsr=rteam['subreddit'],
                        rr=record(rstandings)
                        )
            ret += '\n'
    return ret + config['footer'] 

if __name__ == '__main__':
    print(run(None, header='', footer=''))
