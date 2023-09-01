import re
import sys

from datetime import datetime

import mwparserfromhell as mwp
import pywikibot as pwb

from dyk_logger import DYKLogger

class Bot():
    SITE = pwb.Site()
    ACTIVATOR_LOC = f"User:{SITE.username()}/DYKRun"
    DYK_LOC = f"Template:Did you know"
    NEXQ_LOC = f"Template:Did you know/Queue/NexQ"
    CLEAR_LOC = f"Template:Did you know/Queue/Clear"
    TIMER_LOC = f"Template:Did you know/Queue/Time"
    ARCHIVE_LOC = f"Template:Did you know/Archives"
    CUR_DATEMONTH = "{now.day} {now:%B}".format(now=datetime.now())
    CUR_YEAR = str(datetime.now().year)
    CUR_QUEUE = 0
    NUM_QUEUES = 7

    def check_activator(self):
        activator = pwb.Page(self.SITE, self.ACTIVATOR_LOC)
        return activator.text == "1"

    def reset_activator(self):
        activator = pwb.Page(self.SITE, self.ACTIVATOR_LOC)
        activator.text = "0"
        activator.save("[BOT] Running DYK update")

    def get_next_queue(self):
        nexq = pwb.Page(self.SITE, self.NEXQ_LOC)
        nexq_text = str(mwp.parse(nexq.text).filter_text()[0])
        self.CUR_QUEUE = nexq_int = int(nexq_text)
        return pwb.Page(self.SITE, f"Template:Did you know/Queue/{nexq_int}")
    
    def update_next_queue(self):
        nexq = pwb.Page(self.SITE, self.NEXQ_LOC)
        nexq_number = 1 + (self.CUR_QUEUE % self.NUM_QUEUES)
        nexq.text = re.sub(r"\d+", str(nexq_number), nexq.text)
        nexq.save("[BOT] Incrementing next queue number")

    def get_hooks(self, queue):
        return re.search(r"== ?Hooks ?==((.|\n)*?)<!--\nSTOP", queue.text)[1]

    def clear_queue(self, queue):
        clear = pwb.Page(self.SITE, self.CLEAR_LOC)
        queue.text = clear.text
        queue.save("[BOT] Clearing DYK queue")

    def archive_dyk(self):
        dyk = pwb.Page(self.SITE, self.DYK_LOC)
        hooks = re.search(r"<div style=\"float:right;margin-left:0.5em;\">((.|\n)*?)\{\{-\}\}", dyk.text)[0]
        archive = pwb.Page(self.SITE, self.ARCHIVE_LOC)
        archive_count = int(re.search(r"adding a new set of hooks: (\d+)", archive.text)[1])
        archive.text = re.sub(r"\{\{-\}\}\n<!--#", f"{{{{-}}}}\n'''''~~~~~'''''\n{hooks}\n<!--#", archive.text)
        archive.text = re.sub(r"adding a new set of hooks: \d+", f"adding a new set of hooks: {str(archive_count + 1)}", archive.text)
        archive.save("[BOT] Archiving previous DYK")

    def update_dyk(self, hooks):
        dyk = pwb.Page(self.SITE, self.DYK_LOC)
        dyk.text = re.sub(r"== ?Current hooks ?==\n((.|\n)*?)\[\[Category:", f"==Current hooks==\n{hooks}[[Category:", dyk.text)
        dyk.save(f"[BOT] Updating DYK from Queue {self.CUR_QUEUE}")

    def update_timer(self):
        timer = pwb.Page(self.SITE, self.TIMER_LOC)
        timer.text = re.sub(r"</noinclude>((.|\n)*?)<noinclude>", "</noinclude>\n{{subst:#time:Y-m-d\\\TH:i:s\\\Z}}<noinclude>", timer.text)
        timer.save("[BOT] Updating DYK timer")

    def add_tp_banner(self, hooks):
        hook_array = re.findall("^:\{\{\*mp\}\}(.*)", hooks, flags=re.M)
        for hook in hook_array:
            talk_page = pwb.Page(self.SITE, re.search("'''('')?\[\[(.*?)(|(.*?))?\]\](.*?)('')?'''", hook)[2], ns=1)
            talk_page.text = f"{{{{dyktalk|{self.CUR_DATEMONTH}|{self.CUR_YEAR}}}}}" + talk_page.text
            talk_page.save("[BOT] Adding {{dyktalk}} to DYK-featured article")

    def run(self):
        try:
            if not self.check_activator():
                return
            activator = pwb.Page(self.SITE, self.ACTIVATOR_LOC)
            DYKLogger.log(f"DYK update run triggered by {next(activator.revisions()).user}.")
            self.reset_activator()
            queue = self.get_next_queue()
            hooks = self.get_hooks(queue)
            self.clear_queue(queue)
            self.update_next_queue()
            self.archive_dyk()
            self.update_dyk(hooks)
            self.update_timer()
            self.add_tp_banner(hooks)
            DYKLogger.log(f"DYK update finished.")
        except Exception as e:
            DYKLogger.log(f"{type(e).__name__}: {e}")
            sys.exit(1)
def main():
    bot = Bot()
    bot.run()

if __name__ == '__main__':
    main()
