"""
EU Certification Fixer manual trigger.

Entry point for RunScript(script.eucert.fixer).
Triggers an immediate rating scan outside the normal schedule.

Logging:
    Logger: 'default'
    Key events:
        - manual.start (INFO): Manual scan triggered
        - manual.complete (INFO): Manual scan finished
"""
from resources.lib.utils import get_bool_setting, get_float_setting, get_logger, notify
from resources.lib.data.backfill import backfill, run_canaries, _build_enabled_scrapers
from resources.lib.data.media_types import MOVIE, TVSHOW

log = get_logger('default')


def main() -> None:
    log.info("Manual scan triggered", event="manual.start")

    verified_scrapers = run_canaries(
        _build_enabled_scrapers(),
        get_float_setting('rate_limit', 0.25),
    )

    media_types = [MOVIE, TVSHOW]
    stats = {}
    for media_type in media_types:
        result = backfill(media_type, verified_scrapers)
        stats[media_type.name] = result

    total = sum(
        s.get("tmdb_direct", 0) + s.get("tmdb_inferred", 0) +
        s.get("omdb", 0) + s.get("scraper", 0) + s.get("fallback", 0)
        for s in stats.values()
    )
    log.info("Manual scan complete", event="manual.complete",
             ratings_set=total)

    if get_bool_setting('show_notifications'):
        if total > 0:
            notify("Set {} rating{}".format(total, "s" if total != 1 else ""))
        else:
            notify("No new ratings found")


if __name__ == '__main__':
    main()
