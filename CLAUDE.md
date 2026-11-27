# FridgePaper notes

## Pinterest pins

Pins reach Pinterest automatically through RSS feeds, one feed per board, in feeds/.
Pinterest is connected to each feed (Pinterest settings, Import content, Auto-publish).

To add a new pin:
1. Put a 1000 x 1500 PNG in pins/.
2. Add an entry to pins.json with image, board, title, description, link, and optionally date (YYYY-MM-DD).
3. Run: python3 scripts/build_feeds.py
4. Commit pins/, pins.json and feeds/ together.

There are two pin styles. The first style has a serif headline over a colored top band. The second style (files ending -2.png) is made by scripts/make_pins_v2.py from scripts/pins_v2.json, using headless Chrome and the Fredoka fonts: either the on-fridge photo with a colored headline panel, or a numbered tip list. Use the second style's layouts for new pins so that the two styles alternate.
Pins are released slowly, about 3 a day. A pin whose date is later than today (Chicago time) stays out of the feeds until that day. A GitHub Actions workflow (.github/workflows/daily-pins.yml) runs every morning, rebuilds the feeds with scripts/build_feeds.py, and commits them if they changed. When you add new pins, give them dates after the last date already queued in pins.json, 3 per day, and send seasonal pins out before their season.
Give every pins.json entry a date, so that the pubDate of existing pins never changes when "updated" changes.

Keep each pin's image file name unchanged after it is published. The file name is the item's guid, so renaming it makes Pinterest post it again.
A pin for a new board name creates a new feed file, and that feed must be connected in Pinterest by hand.

The p:domain_verify meta tag in index.html is the Pinterest website claim. Leave it in place.
