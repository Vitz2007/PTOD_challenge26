from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel


class BusyLevel(str, Enum):
    busy = "busy"
    normal = "normal"
    quiet = "quiet"


class LocalizedName(BaseModel):
    en: str | None = None
    ja: str | None = None


class Operator(BaseModel):
    code: str
    name: str


class StationSummary(BaseModel):
    id: str
    name: LocalizedName
    railway: str | None = None


class LineStatus(BaseModel):
    railway: str
    status: str | None = None  # Japanese only, as provided by ODPT
    text: str | None = None


class Congestion(BaseModel):
    passengers_per_day: int
    includes_alighting: bool  # True: people getting on and off; False: getting on only
    survey_year: int
    busy_level: BusyLevel
    live_delay_minutes: float | None = None


class Facility(BaseModel):
    kind: str
    description: str | None = None


class StationDetail(BaseModel):
    id: str
    operator: Operator
    name: LocalizedName
    railways: list[str]
    congestion: Congestion
    service_status: list[LineStatus]
    facilities: list[Facility] | None = None
    notes: list[str] = []


# GeoJSON, the format the frontend map (react-leaflet <GeoJSON>) reads directly


class PointGeometry(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: tuple[float, float]  # [longitude, latitude], GeoJSON order


class MapStationProperties(BaseModel):
    operator: str
    name: str  # use with /stations/{operator}/{name}
    name_en: str | None = None
    name_ja: str | None = None
    busy_level: BusyLevel | None = None  # None: no passenger survey for this station
    passengers_per_day: int | None = None


class StationFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: PointGeometry
    properties: MapStationProperties


class StationFeatureCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[StationFeature]


class FacilityFeatureCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[dict[str, Any]] = []
    note: str | None = None


class Health(BaseModel):
    status: str = "ok"
