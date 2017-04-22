from render import Render
from sheets import GoogleSheetsData
from pprint import pprint
from screenshot import Screenshot
from pathlib import Path

def height_from_in(k, v):
    feet, inches = divmod(int(v), 12)
    s = '{0}\' {1}"'.format(feet, inches)
    return 'Height', s

CONVERSIONS = {
        'Height (in)': height_from_in
}

class DraftCards:

    def __init__(self, sheet_id, range_def, template):
        self.sheet_id = sheet_id
        self.range_def = range_def
        self.template = template
        self.sheet = GoogleSheetsData(sheet_id)
        self.sshot = Screenshot(300, 400)
        self.render = Render()

    def fn(self, player):
        safename = player['Name'].replace(" ", "_").replace("'", "_").lower()
        return str(Path('output') / (safename + ".html"))

    def massage_values(self, player):
        ret = {}
        for key, value in player.items():
            ret[key] = value
            if key in CONVERSIONS:
                nk, nv = CONVERSIONS[key](key, value)
                ret[nk] = nv
        return ret

    def main(self):
        for player in self.sheet.get_range_dict(self.range_def):
            player = self.massage_values(player)
            print(player['Name'], end='... ')
            fn = self.fn(player)
            with open(fn, 'w') as fp:
                fp.write(self.render.render(self.template, {'p':player}))
            self.sshot.sshot(fn, '%s.png' % fn)
            print("done")
                

if __name__ == "__main__":
    import sys
    # Popping because the Google API reads args
    sheet_id = sys.argv.pop(1)
    range_def = sys.argv.pop(1)
    template = sys.argv.pop(1)
    dc = DraftCards(sheet_id, range_def, template)
    dc.main()
