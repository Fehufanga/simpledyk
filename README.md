# Simple English Wikipedia DYK Bot
## About
This bot performs some of the required tasks needed to update Simple English Wikipedia's ''[Did You Know?](https://simple.wikipedia.org/wiki/Template:Did_you_know)'' template:
* Move DYK hooks from the next queue to the main template
* Clear the aforementioned queue
* Update the next queue counter
* Reset the DYK timer
* Archive the previous DYK
* Add the `{{dyktalk}}` template to talk pages of recently promoted articles.

## Activating
The bot checks for changes to User:[Bot's username]/DYKRun every hour. Replace the contents of this page with `1` to activate the bot. 