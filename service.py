"""
Kijkwijzer Ratings background service.

Runs automatically when Kodi starts. Periodically scans the library
for movies and TV shows with missing age ratings and fills them using
TMDB, OMDB, and kijkwijzer.nl.

Logging:
    Logger: 'service'
    Key events:
        - service.start (INFO): Service started
        - service.stop (INFO): Service shutting down
        - service.scan_trigger (INFO): Periodic scan triggered
        - service.scan_skip (DEBUG): Scan skipped (interval not reached)
"""
from resources.lib.service.daemon import run

if __name__ == '__main__':
    run()
