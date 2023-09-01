from datetime import datetime

import pywikibot as pwb

class DYKLogger():
    SITE = pwb.Site()
    LOG_LOC = f"User:{SITE.username()}/Log"

    @classmethod
    def log(self, message):
        log = pwb.Page(self.SITE, self.LOG_LOC)
        log.text = log.text + "\n*'''{now:%c}''': {message}".format(now=datetime.now(), message=message)
        log.save("[BOT] Logging bot run")