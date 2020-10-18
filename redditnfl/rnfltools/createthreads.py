#!/usr/bin/env python3
import argparse
import datetime
import random
import re
import sys
import traceback
from pathlib import Path
from typing import List, Dict

import jinja2
import pendulum
from nflapi import NFL
from nflapi.shield import Game, Week, WeekType, Team
from pendulum import TUESDAY, WEDNESDAY, THURSDAY
from praw import Reddit
from redditnfl.nfltools import nflteams
from redditnfl.reddittools.reddittoken import ensure_scopes

NFL_TZ = pendulum.timezone("America/New_York")

RECURRING_THREADS = [
    ('wagers.post', lambda day: day.day_of_week == TUESDAY, {}),
    ('complaints.post', lambda day: day.day_of_week == WEDNESDAY, {}),
    ('trashtalk.post', lambda day: day.day_of_week == THURSDAY,
     {'random_minutes': random.randint(0, 8 * 60)}),
]


class Filters:
    @staticmethod
    def format_week(cw: Week) -> str:
        if cw.week_type == WeekType.HOF:
            return "Hall of Fame Week"
        elif cw.week_type == WeekType.PRE:
            return "Pre-season Week {cw.week_value}".format(cw=cw)
        elif cw.week_type == WeekType.REG:
            return "Week {cw.week_value}".format(cw=cw)
        elif cw.week_type == WeekType.WC:
            return "Wild-card Weekend"
        elif cw.week_type == WeekType.DIV:
            return "Divisional Round"
        elif cw.week_type == WeekType.CONF:
            return "Conference Playoffs"
        elif cw.week_type == WeekType.PRO:
            return "Pro Bowl"
        elif cw.week_type == WeekType.SB:
            return "Super Bowl"
        return ""

    @staticmethod
    def team_sr(team: Team) -> str:
        info = nflteams.get_team(team.abbreviation)
        if info:
            return info.get('subreddit', 'nfl')
        else:
            return 'nfl'


def games_on_day(day):
    def f(game):
        if not game.game_time:
            return False
        kickoff = pendulum.instance(game.game_time).in_timezone(NFL_TZ)
        return day.date() == kickoff.date()

    return f


def find_start_times(games: List[Game]) -> Dict:
    start_times = {}
    for game in games:
        start_times[game.game_time] = 1 + start_times.get(game.game_time, 0)
    return start_times


def dir_path(p):
    path = Path(p)
    if path.exists() and path.is_dir():
        return path
    else:
        raise argparse.ArgumentTypeError(f"{path.absolute()} is not a valid path")


def date_string(s):
    try:
        return pendulum.parse(s).set(tz=NFL_TZ)
    except Exception as e:
        raise argparse.ArgumentTypeError(f"{s} could not be parsed as a date: " + str(e))


class ThreadCreator:
    def __init__(self):
        parser = argparse.ArgumentParser(description="r/nfl thread scheduler")
        parser.add_argument('-s', '--site', dest='site', help="Reddit 'site' (praw.ini section) to use")
        parser.add_argument('-d', '--date', dest='today', type=date_string, default=pendulum.today(),
                            help="Date to generate threads for (default: today)")
        parser.add_argument('sr_name', help="Name of subreddit to send notice to")
        parser.add_argument('template_dir', type=dir_path, help="Root directory for templates")
        parser.add_argument('output_dir', type=dir_path, help="Output directory")

        self.args = parser.parse_args()
        self.r = Reddit(self.args.site)
        ensure_scopes(self.r, ['privatemessages'])
        self.sub = self.r.subreddit(self.args.sr_name)

        self.env = jinja2.Environment(loader=jinja2.loaders.FileSystemLoader(str(self.args.template_dir)),
                                      undefined=jinja2.StrictUndefined)
        self.env.filters['format_week'] = Filters.format_week
        self.env.filters['team_sr'] = Filters.team_sr
        self.scheduled = []

    def main(self):
        today = self.args.today
        print("Today is {}".format(today))

        nfl = NFL('rnfl thread creator')
        current_week = nfl.schedule.current_week()
        hour = datetime.timedelta(hours=1)

        week_games = nfl.game.week_games(week=current_week.week_value, season_type=current_week.season_type,
                                         season=current_week.season_value)

        if len(week_games) > 0:
            for tpl, should_post, ctx in RECURRING_THREADS:
                if should_post(today):
                    self.schedule(tpl, today=today, cw=current_week, hours=hour, **ctx)

        games_today = list(filter(games_on_day(today), week_games))
        for game in games_today:
            game.game_time = pendulum.instance(game.game_time).in_timezone(NFL_TZ)
        start_times = find_start_times(games_today)

        if len(games_today) > 0:
            print("Need day after")
            self.schedule('dayafter.post', cw=current_week, today=today, games=games_today, hours=hour)

        # Is there a time when 3 or more games start?
        # If so, create a highlights thread and comments starting from the first kickoff of the day
        # Also create a redzone thread
        if len(games_today) > 0 and max(start_times.values()) >= 3:
            first_kickoff = sorted(games_today, key=lambda g: g.game_time)[0].game_time
            first_kickoff = pendulum.instance(first_kickoff).in_timezone(NFL_TZ)

            print("Need redzone")
            self.schedule('redzone.post', cw=current_week, first_kickoff=first_kickoff, hours=hour, today=today)

            print("Need highlights")
            highlights_submission = self.schedule('highlights.post', cw=current_week, first_kickoff=first_kickoff,
                                                  hours=hour, today=today)
            for game in games_today:
                print("  Highlights comment for %s" % game)
                self.schedule('highlights_game.comment', cw=current_week, game=game, parent=highlights_submission,
                              hours=hour)

    def schedule(self, template_name: str, **kwargs) -> str:
        print("Scheduling %s" % template_name)
        tpl = self.env.get_template(template_name)
        output = tpl.render(**kwargs)
        headers, body = re.split('\n *\n', output, maxsplit=1, flags=re.M)
        headers = dict([(k.lower(), v) for k, v in [tuple(re.split(" *: *", line, 1)) for line in headers.split("\n")]])

        if 'filename' not in headers:
            raise Exception("No filename found in template " + template_name)
        filename = self.args.output_dir / headers['filename']
        with open(filename, 'w') as fp:
            print("Saving %s" % filename)
            fp.write(output)
        self.scheduled.append((filename, headers, body))
        return filename

    def send_modmail(self):
        if len(self.scheduled) > 0:
            tpl = self.env.get_template('modmail.md')
            message = tpl.render(scheduled=self.scheduled, pendulum=pendulum)
            self.sub.message("Scheduled posts for today", message)

    def send_error(self, exc_info, *users):
        for user in users:
            subject = "Error scheduling threads!"
            tb = "".join(traceback.format_exception(*exc_info))
            indented = "\n".join(["    " + l for l in tb.splitlines()])
            message = "Exception when generating threads:\n\n" + indented
            self.r.redditor(user).message(subject, message)


def main():
    tc = ThreadCreator()
    try:
        tc.main()
        tc.send_modmail()
    except Exception as e:
        exc_info = sys.exc_info()
        tc.send_error(exc_info, 'rasherdk')


if __name__ == '__main__':
    main()
