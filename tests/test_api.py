import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_station_service
from app.cache import TTLCache
from app.config import Settings
from app.main import create_app
from app.odpt import vocab
from app.odpt.client import ODPTError
from app.services.stations import StationService

JR_LINE = "odpt.Railway:JR-East.Yamanote"
KEIO_LINE = "odpt.Railway:Keio.Keio"


def survey(operator: str, line: str, passengers: int) -> dict:
    return {
        "owl:sameAs": f"odpt.PassengerSurvey:{operator}.Shinjuku",
        "odpt:station": [f"odpt.Station:{operator}.{line.split('.')[-1]}.Shinjuku"],
        "odpt:railway": [line],
        "odpt:includeAlighting": operator != "JR-East",
        "odpt:passengerSurveyObject": [{"odpt:surveyYear": 2023, "odpt:passengerJourneys": passengers}],
    }


FAKE_SURVEYS = {
    vocab.operator_id("JR-East"): [survey("JR-East", JR_LINE, 650000)],
    vocab.operator_id("Keio"): [survey("Keio", KEIO_LINE, 700000)],
}
FAKE_STATIONS = [
    {
        "owl:sameAs": "odpt.Station:JR-East.Yamanote.Shinjuku",
        "dc:title": "新宿",
        "odpt:stationTitle": {"en": "Shinjuku"},
        "geo:lat": 35.69,
        "geo:long": 139.70,
    },
    # Same station on a second line: should give only one map point
    {
        "owl:sameAs": "odpt.Station:JR-East.ChuoRapid.Shinjuku",
        "dc:title": "新宿",
        "odpt:stationTitle": {"en": "Shinjuku"},
        "geo:lat": 35.69,
        "geo:long": 139.70,
    },
    # No passenger survey
    {
        "owl:sameAs": "odpt.Station:JR-East.Yamanote.Yoyogi",
        "dc:title": "代々木",
        "odpt:stationTitle": {"en": "Yoyogi"},
        "geo:lat": 35.68,
        "geo:long": 139.70,
    },
    # No coordinates: left off the map
    {"owl:sameAs": "odpt.Station:JR-East.Yamanote.Nowhere", "dc:title": "なし", "odpt:stationTitle": {"en": "Nowhere"}},
    {
        "owl:sameAs": "odpt.Station:Keio.Keio.Shinjuku",
        "dc:title": "新宿",
        "odpt:stationTitle": {"en": "Shinjuku"},
        "geo:lat": 35.69,
        "geo:long": 139.70,
    },
]
FAKE_TRAINS = [{"odpt:railway": JR_LINE, "odpt:delay": 180}, {"odpt:railway": KEIO_LINE, "odpt:delay": 60}]
FAKE_STATUS = [
    {"odpt:railway": JR_LINE, "odpt:trainInformationStatus": {"ja": "遅延"}, "odpt:trainInformationText": {"ja": "遅れ"}}
]


class FakeODPTClient:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[str] = []

    async def fetch(self, data_type: str, **filters: str) -> list[dict]:
        self.calls.append(data_type)
        if self.fail:
            raise ODPTError("ODPT returned 503 for " + data_type, 503)
        if data_type == vocab.PASSENGER_SURVEY:
            return FAKE_SURVEYS.get(filters["odpt:operator"], [])
        if data_type == vocab.STATION:
            if "owl:sameAs" in filters:
                return [s for s in FAKE_STATIONS if s["owl:sameAs"] == filters["owl:sameAs"]]
            code = filters["odpt:operator"].split(":")[1]
            return [s for s in FAKE_STATIONS if s["owl:sameAs"].startswith(f"odpt.Station:{code}.")]
        if data_type == vocab.TRAIN:
            code = filters["odpt:operator"].split(":")[1]
            return [t for t in FAKE_TRAINS if t["odpt:railway"].split(":")[1].startswith(code + ".")]
        return FAKE_STATUS


def make_client(fake: FakeODPTClient) -> TestClient:
    settings = Settings(odpt_consumer_key="test-key")
    app = create_app(settings)
    service = StationService(fake, TTLCache(), settings)
    app.dependency_overrides[get_station_service] = lambda: service
    return TestClient(app)


@pytest.fixture
def client() -> TestClient:
    return make_client(FakeODPTClient())


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_operators(client):
    codes = [o["code"] for o in client.get("/api/v1/operators").json()]
    assert codes == list(vocab.OPERATORS)


def test_station_detail(client):
    body = client.get("/api/v1/stations/jr-east/shinjuku").json()

    assert body["operator"] == {"code": "JR-East", "name": "JR East"}
    assert body["name"] == {"en": "Shinjuku", "ja": "新宿"}
    assert body["congestion"]["passengers_per_day"] == 650000
    assert body["congestion"]["includes_alighting"] is False
    assert body["congestion"]["live_delay_minutes"] == 3.0
    assert body["service_status"][0]["status"] == "遅延"
    assert body["facilities"] is None


def test_same_station_name_on_other_operator(client):
    body = client.get("/api/v1/stations/Keio/Shinjuku").json()

    assert body["id"] == "odpt.Station:Keio.Keio.Shinjuku"
    assert body["congestion"]["passengers_per_day"] == 700000
    assert body["congestion"]["live_delay_minutes"] == 1.0
    assert body["service_status"] == []


def test_station_not_found(client):
    assert client.get("/api/v1/stations/Keio/Nowhere").status_code == 404


def test_unknown_operator(client):
    response = client.get("/api/v1/stations/TokyoMetro/Ginza")
    assert response.status_code == 404
    assert "Supported" in response.json()["detail"]
    assert client.get("/api/v1/stations?operator=TokyoMetro").status_code == 404


def test_map_stations(client):
    body = client.get("/api/v1/map/stations").json()

    assert body["type"] == "FeatureCollection"
    points = {f["properties"]["name"]: f for f in body["features"]}
    assert set(points) == {"Shinjuku", "Yoyogi"}
    assert points["Shinjuku"]["geometry"] == {"type": "Point", "coordinates": [139.70, 35.69]}
    assert points["Shinjuku"]["properties"]["busy_level"] is not None
    assert points["Yoyogi"]["properties"]["busy_level"] is None


def test_map_stations_accepts_full_operator_id(client):
    body = client.get("/api/v1/map/stations?operator=odpt.Operator:Keio").json()
    assert [f["properties"]["operator"] for f in body["features"]] == ["Keio"]


def test_facilities_is_empty_geojson_with_note(client):
    body = client.get("/api/v1/facilities?operator=JR-East").json()
    assert body["type"] == "FeatureCollection"
    assert body["features"] == []
    assert "not yet published" in body["note"]
    assert client.get("/api/v1/facilities?operator=TokyoMetro").status_code == 404


def test_facilities_at_frontend_path(client):
    # Exact request made by frontend/src/hooks/useStationData.js
    response = client.get("/facilities?operator=odpt.Operator: JR East", headers={"Origin": "http://localhost:5173"})

    assert response.status_code == 200
    assert response.json()["type"] == "FeatureCollection"
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_surveys_are_cached():
    fake = FakeODPTClient()
    client = make_client(fake)
    client.get("/api/v1/stations/Keio/Shinjuku")
    client.get("/api/v1/stations/JR-East/Shinjuku")
    assert fake.calls.count(vocab.PASSENGER_SURVEY) == len(vocab.OPERATORS)


def test_odpt_failure_returns_502():
    response = make_client(FakeODPTClient(fail=True)).get("/api/v1/service-status")
    assert response.status_code == 502
    assert "test-key" not in response.text
