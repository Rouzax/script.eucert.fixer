"""
Kijkwijzer Ratings manual trigger.

Entry point for RunScript(script.kijkwijzer.ratings).
Triggers an immediate rating scan outside the normal schedule.

Logging:
    Logger: 'default'
    Key events:
        - manual.start (INFO): Manual scan triggered
        - manual.complete (INFO): Manual scan finished
"""
from resources.lib.utils import get_logger
from resources.lib.data.backfill import backfill
from resources.lib.data.media_types import MOVIE, TVSHOW

log = get_logger('default')


def main() -> None:
    log.info("Manual scan triggered", event="manual.start")

    media_types = [MOVIE, TVSHOW]
    stats = {}
    for media_type in media_types:
        result = backfill(media_type)
        stats[media_type.name] = result

    total = sum(
        s.get("tmdb_direct", 0) + s.get("tmdb_inferred", 0) +
        s.get("omdb", 0) + s.get("kijkwijzer", 0) + s.get("fallback", 0)
        for s in stats.values()
    )
    log.info("Manual scan complete", event="manual.complete",
             ratings_set=total)


if __name__ == '__main__':
    main()
