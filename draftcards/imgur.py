#!/usr/bin/env python
from pprint import pprint
import json
from imgurpython import ImgurClient
import os.path
import webbrowser

CREDENTIALS_FILE = 'imgur_client_secret.json'


class Imgur:
    def __init__(self):
        with open(CREDENTIALS_FILE, 'r') as fp:
            data = json.load(fp)
        self.client = ImgurClient(data['client_id'], data['client_secret'])
        self.get_credentials()

    def get_credentials(self):
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'rnfl-draftcards-imgur.json')

        try:
            with open(credential_path) as fp:
                credentials = json.load(fp)
        except Exception:
            credentials = None
        
        if not credentials:
            authorization_url = self.client.get_auth_url('pin')
            try:
                webbrowser.open_new_tab(authorization_url)
            except Exception:
                print("Go to %s" % authorization_url)
            pin = input('Input PIN: ')
            credentials = self.client.authorize(pin, 'pin')
        with open(credential_path, 'w') as fp:
            json.dump(credentials, fp)
        self.client.set_user_auth(credentials['access_token'], credentials['refresh_token'])

    def get_or_make_album(self, albumtitle):
        for album in self.client.get_account_albums('rasher'):
            if album.title == albumtitle:
                return album.id
        ret = self.client.create_album({'title': albumtitle})
        return ret.id

    def upload(self, path, albumtitle, title=None):
        album_id = self.get_or_make_album(albumtitle)
        config = {'album': album_id}
        if title:
            config['title'] = title
        ret = self.client.upload_from_path(path, config, anon=False)
        pprint(ret)
        return ret

    def upload_url(self, url, albumtitle, title=None):
        album_id = self.get_or_make_album(albumtitle)
        config = {'album': album_id}
        if title:
            config['title'] = title
        ret = self.client.upload_from_url(url, config, anon=False)
        return ret


if __name__ == "__main__":
    import sys
    i = Imgur()
    path = sys.argv[1]
    albumtitle = sys.argv[2]
    i.upload(path, albumtitle)

