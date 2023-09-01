import re
import sys

import mwparserfromhell as mwp
import pywikibot as pwb

class Bot():
    SITE = pwb.Site()
    ACTIVATOR_LOC = f"User:{SITE.username()}/DYKRun"
    DYK_LOC = f"User:{SITE.username()}/TestDYK"
    NEXQ_LOC = f"User:{SITE.username()}/TestQueue/NexQ"
    CLEAR_LOC = f"User:{SITE.username()}/TestQueue/Clear"
    TIMER_LOC = f"User:{SITE.username()}/TestQueue/Time"
    ARCHIVE_LOC = f"User:{SITE.username()}/Archives"
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
        return pwb.Page(self.SITE, f"User:{self.SITE.username()}/TestQueue/{nexq_int}")
    
    def update_next_queue(self):
        nexq = pwb.Page(self.SITE, self.NEXQ_LOC)
        nexq_number = 1 + (self.CUR_QUEUE % self.NUM_QUEUES)
        nexq.text = re.sub(r"%d+", str(nexq_number), nexq.text)

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
        timer.text = re.sub(r"</noinclude>((.|\n)*?)<noinclude>", "</noinclude>\n{{subst:#time:Y-m-d\\\TH:i:s\\\Z}}</noinclude>", timer.text)

    def run(self):
        if not self.check_activator():
            return
        #self.reset_activator()
        queue = None
        try:
            queue = self.get_next_queue()
        except ValueError:
            sys.exit(1)
        hooks = self.get_hooks(queue)
        self.clear_queue(queue)
        self.update_next_queue()
        self.archive_dyk()
        self.update_dyk(hooks)
        self.update_timer()
        
def main():
    bot = Bot()
    bot.run()

if __name__ == '__main__':
    main()
