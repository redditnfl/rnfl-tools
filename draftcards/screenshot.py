#!/usr/bin/env python
from selenium import webdriver
from pathlib import Path

class Screenshot:

    def __init__(self, w, h):
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(w, h)

    def sshot(self, fn, outfn):
        p = Path(fn)
        if not p.exists():
            return None
        self.driver.get('file://' + str(p.resolve()))
        self.driver.save_screenshot(outfn)

    def sshot_url_to_png(self, url):
        self.driver.get(url)
        return self.driver.get_screenshot_as_png()

if __name__ == "__main__":
    import sys
    s = Screenshot()
    s.sshot(sys.argv[1], sys.argv[2])
