import asyncio
from typing import Any

from app.cache import TTLCache
from app.config import Settings
from app.odpt import vocab
from app.odpt.client import ODPTClient
from app.schemas import (
    Congestion,
    FacilityFeatureCollection,
    LineStatus,
    LocalizedName,
    MapStationProperties,
    Operator,
    PointGeometry,
    StationDetail,
    StationFeature,
    StationFeatureCollection,
    StationSummary,
)
from app.services.congestion import SurveyStat, average_delay_minutes, rank_surveys

FACILITIES_NOTE = "Station facility data is not yet published by the ODPT challenge API."
CONGESTION_NOTE = (
    "Busy level compares yearly passenger counts across all supported operators; "
    "delays and line status are live."
)


class StationNotFound(Exception):
    pass


class UnknownOperator(Exception):
    pass


def _name(record: dict[str, Any]) -> LocalizedName:
    return LocalizedName(en=(record.get("odpt:stationTitle") or {}).get("en"), ja=record.get("dc:title"))


def _operator(code: str) -> str:
    resolved = vocab.resolve_operator(code)
    if resolved is None:
        raise UnknownOperator(code)
    return resolved


class StationService:
    """Combines ODPT data into what the app shows for a station."""

    def __init__(self, client: ODPTClient, cache: TTLCache, settings: Settings) -> None:
        self._client = client
        self._cache = cache
        self._settings = settings

    async def _fetch(self, ttl: int, data_type: str, **filters: str) -> list[dict[str, Any]]:
        key = data_type + "?" + "&".join(f"{k}={v}" for k, v in sorted(filters.items()))
        return await self._cache.get_or_set(key, ttl, lambda: self._client.fetch(data_type, **filters))

    async def _surveys(self) -> dict[tuple[str, str], SurveyStat]:
        async def load() -> dict[tuple[str, str], SurveyStat]:
            # One request per operator: ODPT caps a response at 1,000 rows
            results = await asyncio.gather(
                *(
                    self._client.fetch(vocab.PASSENGER_SURVEY, **{"odpt:operator": vocab.operator_id(code)})
                    for code in vocab.OPERATORS
                )
            )
            return rank_surveys([record for records in results for record in records])

        return await self._cache.get_or_set("surveys", self._settings.static_cache_seconds, load)

    @staticmethod
    def operators() -> list[Operator]:
        return [Operator(code=code, name=name) for code, name in vocab.OPERATORS.items()]

    async def list_stations(self, operator: str = vocab.DEFAULT_OPERATOR) -> list[StationSummary]:
        code = _operator(operator)
        records = await self._fetch(
            self._settings.static_cache_seconds, vocab.STATION, **{"odpt:operator": vocab.operator_id(code)}
        )
        return [StationSummary(id=r["owl:sameAs"], name=_name(r), railway=r.get("odpt:railway")) for r in records]

    async def map_stations(self, operator: str = vocab.DEFAULT_OPERATOR) -> StationFeatureCollection:
        """Stations as map points, each with its busy level when there is a survey."""
        code = _operator(operator)
        records, surveys = await asyncio.gather(
            self._fetch(self._settings.static_cache_seconds, vocab.STATION, **{"odpt:operator": vocab.operator_id(code)}),
            self._surveys(),
        )

        features: dict[str, StationFeature] = {}  # one point per station, even with several lines
        for record in records:
            name = record["owl:sameAs"].split(".")[-1]
            if name.lower() in features or record.get("geo:lat") is None or record.get("geo:long") is None:
                continue
            stat = surveys.get((code, name.lower()))
            features[name.lower()] = StationFeature(
                geometry=PointGeometry(coordinates=(record["geo:long"], record["geo:lat"])),
                properties=MapStationProperties(
                    operator=code,
                    name=name,
                    name_en=_name(record).en,
                    name_ja=_name(record).ja,
                    busy_level=stat.busy_level if stat else None,
                    passengers_per_day=stat.passengers_per_day if stat else None,
                ),
            )
        return StationFeatureCollection(features=list(features.values()))

    @staticmethod
    def facilities(operator: str = vocab.DEFAULT_OPERATOR) -> FacilityFeatureCollection:
        """Step-free paths and facilities as GeoJSON. Empty until ODPT publishes the data."""
        _operator(operator)
        return FacilityFeatureCollection(note=FACILITIES_NOTE)

    async def service_status(self, railways: set[str] | None = None) -> list[LineStatus]:
        records = await self._fetch(self._settings.live_cache_seconds, vocab.TRAIN_INFORMATION)
        return [
            LineStatus(
                railway=r["odpt:railway"],
                status=(r.get("odpt:trainInformationStatus") or {}).get("ja"),
                text=(r.get("odpt:trainInformationText") or {}).get("ja"),
            )
            for r in records
            if r.get("odpt:railway") and (railways is None or r["odpt:railway"] in railways)
        ]

    async def get_station(self, operator: str, name: str) -> StationDetail:
        code = _operator(operator)
        stat = (await self._surveys()).get((code, name.strip().lower()))
        if stat is None:
            raise StationNotFound(name)

        railways = set(stat.railways)
        info, trains, status = await asyncio.gather(
            self._fetch(self._settings.static_cache_seconds, vocab.STATION, **{"owl:sameAs": stat.station_ids[0]}),
            self._fetch(self._settings.live_cache_seconds, vocab.TRAIN, **{"odpt:operator": vocab.operator_id(code)}),
            self.service_status(railways),
        )

        return StationDetail(
            id=stat.station_ids[0],
            operator=Operator(code=code, name=vocab.OPERATORS[code]),
            name=_name(info[0]) if info else LocalizedName(en=name),
            railways=stat.railways,
            congestion=Congestion(
                passengers_per_day=stat.passengers_per_day,
                includes_alighting=stat.includes_alighting,
                survey_year=stat.survey_year,
                busy_level=stat.busy_level,
                live_delay_minutes=average_delay_minutes([t for t in trains if t.get("odpt:railway") in railways]),
            ),
            service_status=status,
            facilities=None,
            notes=[CONGESTION_NOTE, FACILITIES_NOTE],
        )
