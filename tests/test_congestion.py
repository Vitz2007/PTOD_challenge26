from app.odpt.vocab import resolve_operator
from app.schemas import BusyLevel
from app.services.congestion import average_delay_minutes, busy_level, latest_survey, rank_surveys, survey_key


def survey(name: str, passengers: int, operator: str = "Keio", year: int = 2023, line: str = "Line") -> dict:
    return {
        "owl:sameAs": f"odpt.PassengerSurvey:{operator}.{name}",
        "odpt:station": [f"odpt.Station:{operator}.{line}.{name}"],
        "odpt:railway": [f"odpt.Railway:{operator}.{line}"],
        "odpt:includeAlighting": operator != "JR-East",
        "odpt:passengerSurveyObject": [
            {"odpt:surveyYear": year - 1, "odpt:passengerJourneys": 1},
            {"odpt:surveyYear": year, "odpt:passengerJourneys": passengers},
        ],
    }


def test_latest_survey_picks_newest_year():
    assert latest_survey(survey("A", 500, year=2024)) == (2024, 500)
    assert latest_survey({"odpt:passengerSurveyObject": []}) is None


def test_survey_key():
    assert survey_key(survey("Shinjuku", 1, operator="JR-East")) == ("JR-East", "shinjuku")


def test_busy_level_thresholds():
    assert busy_level(0.0) is BusyLevel.busy
    assert busy_level(0.2) is BusyLevel.normal
    assert busy_level(0.6) is BusyLevel.quiet


def test_rank_surveys_orders_stations_by_passengers():
    stats = rank_surveys([survey(f"S{i}", (i + 1) * 100) for i in range(10)])  # S9 busiest

    assert stats[("Keio", "s9")].busy_level is BusyLevel.busy
    assert stats[("Keio", "s5")].busy_level is BusyLevel.normal
    assert stats[("Keio", "s0")].busy_level is BusyLevel.quiet


def test_same_name_on_different_operators_stays_separate():
    stats = rank_surveys([survey("Shinjuku", 100, operator="Keio"), survey("Shinjuku", 200, operator="Odakyu")])
    assert set(stats) == {("Keio", "shinjuku"), ("Odakyu", "shinjuku")}


def test_lines_of_one_station_are_added_together():
    stats = rank_surveys([survey("Shibuya", 600, operator="Tokyu", line="A"), survey("Shibuya", 400, operator="Tokyu", line="B")])
    stat = stats[("Tokyu", "shibuya")]

    assert stat.passengers_per_day == 1000
    assert len(stat.railways) == 2


def test_jr_east_boardings_are_doubled_for_ranking():
    # JR East counts getting on only, so 300 boardings ranks above 500 on+off
    stats = rank_surveys([survey("A", 300, operator="JR-East")] + [survey(f"K{i}", 500 - i) for i in range(9)])

    assert stats[("JR-East", "a")].passengers_per_day == 300
    assert stats[("JR-East", "a")].busy_level is BusyLevel.busy


def test_rank_surveys_skips_stations_without_data():
    stats = rank_surveys([survey("A", 100), {"owl:sameAs": "odpt.PassengerSurvey:Keio.B", "odpt:passengerSurveyObject": []}])
    assert list(stats) == [("Keio", "a")]


def test_average_delay_minutes():
    assert average_delay_minutes([]) is None
    assert average_delay_minutes([{"odpt:delay": 120}, {"odpt:delay": None}]) == 1.0


def test_resolve_operator_accepts_all_forms():
    for form in ["JR-East", "jr east", "odpt.Operator:JR-East", "odpt.Operator: JR East"]:
        assert resolve_operator(form) == "JR-East"
    assert resolve_operator("TokyoMetro") is None
