import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
import argparse
import logging

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
SECRET_FILE = 'client_secret.json'
APP_NAME = 'Google Calendar API Python Quickstart'
CREDENTIAL_FILE = 'google-calendar.json'

logging.getLogger('googleapiclient.discovery').setLevel(logging.ERROR)

class Calendar:

    def __init__(self, scopes=None, app_name=None, secret_file=None, credential_file=None):
        self.scopes = scopes or SCOPES
        self.app_name = app_name or APP_NAME
        self.secret_file = secret_file or SECRET_FILE
        self.credential_file = credential_file or CREDENTIAL_FILE

    def get_service(self):
        credentials = self._get_credentials()
        http = credentials.authorize(httplib2.Http())
        return discovery.build('calendar', 'v3', http=http, cache_discovery=False)

    def get_calendar(self, summary):
        for c in self.get_service().calendarList().list().execute()['items']:
            this_summary = c['summaryOverride'] if 'summaryOverride' in c else c['summary']
            if summary == this_summary:
                return c
    
    def get_events(self, calendar, **kwargs):
        s = self.get_service()
        return s.events().list(calendarId=calendar['id'], **kwargs).execute()['items']

    def _get_credentials(self):
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, self.credential_file)

        store = Storage(credential_path)
        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.secret_file, self.scopes)
            flow.user_agent = self.app_name
            flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args(['--noauth_local_webserver'])
            credentials = tools.run_flow(flow, store, flags)
        return credentials

def is_url(s):
    from urllib.parse import urlparse
    return urlparse(s).scheme != ""
            
def run(reddit_session, **config):
    import pendulum
    name = config['calendar']
    secret_file = config.get('secret_file')
    c = Calendar(secret_file=secret_file)
    calendar = c.get_calendar(name)
    now = pendulum.now()
    tz = pendulum.timezone(config['tz'])
    events = c.get_events(calendar, orderBy='startTime', singleEvents=True, timeMin=now.to_rfc3339_string())
    if len(events) == 0:
        return config.get('no_events', 'No upcoming events')
    ret = config.get('header', "| Time | Event |\n|:-----|:------|\n")
    for event in events:
        start = event['start']
        if 'date' in start:
            # All-day events
            date = pendulum.parse(event['start']['date'])
            fmt = config.get('fmt_date', 'M/D')
        else:
            date = pendulum.parse(event['start']['dateTime']).in_timezone(tz)
            fmt = config.get('fmt_datetime', 'M/D h:mmA')

        if 'location' in event and is_url(event['location']):
            title = "[{0[summary]}]({0[location]})".format(event)
        else:
            title = event['summary']

        desc = '*%s*' % event['description'].replace("\n", " ") if 'description' in event else ''

        ret += config['row'].format(title=title, desc=desc, date=date, fmt=fmt)

    ret += config.get('footer', '')
    return ret
