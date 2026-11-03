from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_station_service
from app.odpt import vocab
from app.schemas import LineStatus, Operator, StationDetail, StationSummary
from app.services.stations import StationNotFound, StationService, UnknownOperator

router = APIRouter(tags=["stations"])
Service = Annotated[StationService, Depends(get_station_service)]


def unknown_operator(operator: str) -> HTTPException:
    supported = ", ".join(vocab.OPERATORS)
    return HTTPException(404, f"Unknown operator '{operator}'. Supported: {supported}")


@router.get("/operators", response_model=list[Operator])
async def list_operators(service: Service):
    """Operators the app supports (those with passenger counts in ODPT)."""
    return service.operators()


@router.get("/stations", response_model=list[StationSummary])
async def list_stations(service: Service, operator: str = vocab.DEFAULT_OPERATOR):
    """All stations for an operator, e.g. `?operator=Keio` (JR East by default)."""
    try:
        return await service.list_stations(operator)
    except UnknownOperator:
        raise unknown_operator(operator) from None


@router.get("/stations/{operator}/{name}", response_model=StationDetail)
async def get_station(operator: str, name: str, service: Service):
    """Congestion and live status for one station, e.g. `/stations/Keio/Shinjuku`."""
    try:
        return await service.get_station(operator, name)
    except UnknownOperator:
        raise unknown_operator(operator) from None
    except StationNotFound:
        raise HTTPException(404, f"No {operator} station called '{name}'") from None


@router.get("/service-status", response_model=list[LineStatus])
async def service_status(service: Service):
    """Live operating status for every line ODPT reports on."""
    return await service.service_status()
