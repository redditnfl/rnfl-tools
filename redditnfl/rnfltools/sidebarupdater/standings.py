from nflapi import NFL
from nflapi.shield import shield, WeekOrderBy, OrderByDirection
from redditnfl.nfltools.nflteams import get_team

from sgqlc.operation import Operation


def division(div):
    return div[0:3], div[4:].title()


def division_standings(teams):
    standings = {}
    for team, record in teams:
        div = division(team.division)
        if div not in standings:
            standings[div] = []
        standings[div].append((team, record))

    for div in standings:
        standings[div].sort(key=lambda t: (1 - t[1].overall_pct, t[1].division_rank, t[0].full_name))
    return standings


def fmt_record(standings):
    ret = '{s.overall_win}-{s.overall_loss}'.format(s=standings)
    if standings.overall_tie:
        ret += '-{s.overall_tie}'.format(s=standings)
    return ret


def fmt_playoffs(standings):
    symbols = [
        ("clinch_playoff", "x"),
        ("clinch_division", "y"),
        ("clinch_wc", "z"),
        ("clinch_division_and_homefield", "*"),
        ("eliminated_from_postseason", "†"),
    ]
    ret = ""
    for attr, s in symbols:
        if getattr(standings, attr, False):
            ret += s
    return "^" + ret if ret else ret


def run(reddit_session, **config):
    nfl = NFL(ua='nfl scores sidebar')
    ret = config['header']

    op = Operation(shield.Viewer)
    standings = op.viewer.teams_group.standings(first=1, week_season_value=0, order_by=WeekOrderBy.week__weekOrder,
                                                order_by_direction=OrderByDirection.DESC)
    standing = standings.edges.node
    record = standing.team_records
    record.team_id()
    record.overall_win()
    record.overall_loss()
    record.overall_tie()
    record.overall_pct()
    record.division_rank()
    record.clinch_playoff()
    record.clinch_division()
    record.clinch_wc()
    record.clinch_division_and_homefield()
    record.eliminated_from_postseason()

    res = nfl.query(op)
    records = res.viewer.teams_group.standings.edges[0].node.team_records
    records = {r.team_id: r for r in records}

    def team_fun(t: shield.Team):
        t.id()
        t.abbreviation()
        t.division()
        t.full_name()

    teams = nfl.team.by_ids(records.keys(), select_fun=team_fun)
    teams = [(t, records[t.id]) for t in teams]
    standings = division_standings(teams)

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
