"""ODPT identifiers used across the app."""

# Operators with passenger survey data in the challenge API (checked 2026-11-03).
# Code (as used in ODPT ids and our URLs) -> display name.
OPERATORS = {
    "JR-East": "JR East",
    "Tobu": "Tobu",
    "Tokyu": "Tokyu",
    "Seibu": "Seibu",
    "Keikyu": "Keikyu",
    "Keio": "Keio",
    "Odakyu": "Odakyu",
    "Sotetsu": "Sotetsu",
}
DEFAULT_OPERATOR = "JR-East"

STATION = "odpt:Station"
PASSENGER_SURVEY = "odpt:PassengerSurvey"
TRAIN = "odpt:Train"
TRAIN_INFORMATION = "odpt:TrainInformation"


def operator_id(code: str) -> str:
    return f"odpt.Operator:{code}"


def resolve_operator(code: str) -> str | None:
    """Canonical operator code for a case-insensitive match, or None if unsupported."""
    return next((c for c in OPERATORS if c.lower() == code.strip().lower()), None)
