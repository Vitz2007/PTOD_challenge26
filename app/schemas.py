from enum import Enum

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


class Health(BaseModel):
    status: str = "ok"
