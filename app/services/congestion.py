"""Pure congestion logic, kept free of I/O so it is easy to test and change."""

from bisect import bisect_right
from dataclasses import dataclass, field
from typing import Any

from app.schemas import BusyLevel

# Share of stations (by passenger count, busiest first) in each level
BUSY_SHARE = 0.2
QUIET_FROM = 0.6


@dataclass
class SurveyStat:
    operator: str  # e.g. "Keio"
    name: str  # lower-case station name, e.g. "shinjuku"
    station_ids: list[str] = field(default_factory=list)
    railways: list[str] = field(default_factory=list)
    passengers_per_day: int = 0
    survey_year: int = 0
    includes_alighting: bool = False
    busy_level: BusyLevel = BusyLevel.normal

    @property
    def comparable_passengers(self) -> int:
        """Passengers on a common basis across operators.

        JR East counts people getting on only; other operators count people
        getting on and off, so JR East's figure is doubled for ranking.
        """
        return self.passengers_per_day if self.includes_alighting else self.passengers_per_day * 2


def latest_survey(record: dict[str, Any]) -> tuple[int, int] | None:
    """(year, passengers) for the newest survey year, or None if there is none."""
    years = record.get("odpt:passengerSurveyObject") or []
    if not years:
        return None
    newest = max(years, key=lambda y: y["odpt:surveyYear"])
    return newest["odpt:surveyYear"], newest["odpt:passengerJourneys"]


def busy_level(busier_share: float) -> BusyLevel:
    """Level from the share of stations that are busier than this one."""
    if busier_share < BUSY_SHARE:
        return BusyLevel.busy
    if busier_share >= QUIET_FROM:
        return BusyLevel.quiet
    return BusyLevel.normal


def survey_key(record: dict[str, Any]) -> tuple[str, str]:
    """(operator, lower-case name) from an id like "odpt.PassengerSurvey:Keio.Shinjuku"."""
    operator, *_, name = record["owl:sameAs"].split(":", 1)[1].split(".")
    return operator, name.lower()


def rank_surveys(records: list[dict[str, Any]]) -> dict[tuple[str, str], SurveyStat]:
    """Index surveys by (operator, station name), each ranked against all stations.

    Some operators survey a station once per line; those are added together.
    """
    stats: dict[tuple[str, str], SurveyStat] = {}
    for record in records:
        latest = latest_survey(record)
        if latest is None:
            continue
        year, passengers = latest
        operator, name = survey_key(record)
        stat = stats.setdefault((operator, name), SurveyStat(operator=operator, name=name))
        stat.station_ids += record.get("odpt:station", [])
        stat.railways += [r for r in record.get("odpt:railway", []) if r not in stat.railways]
        stat.passengers_per_day += passengers
        stat.survey_year = max(stat.survey_year, year)
        stat.includes_alighting = bool(record.get("odpt:includeAlighting"))

    counts = sorted(s.comparable_passengers for s in stats.values())
    for stat in stats.values():
        busier = len(counts) - bisect_right(counts, stat.comparable_passengers)
        stat.busy_level = busy_level(busier / len(counts))
    return stats


def average_delay_minutes(trains: list[dict[str, Any]]) -> float | None:
    """Average live delay in minutes (ODPT reports seconds), or None with no trains."""
    if not trains:
        return None
    seconds = sum(t.get("odpt:delay") or 0 for t in trains)
    return round(seconds / len(trains) / 60, 1)
