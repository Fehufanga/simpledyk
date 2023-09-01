from datetime import datetime

import pywikibot as pwb

class DYKLogger():
    SITE = pwb.Site()
    LOG_LOC = f"User:{SITE.username}/Log"

    @classmethod
    def log(self, message):
        log = pwb.Page(self.SITE, self.LOG_LOC)
        log.text = log.text + "*{now:%c} {message}\n".format(now=datetime.now(), message=message)