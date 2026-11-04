from fastapi import Request

from app.services.stations import StationService


def get_station_service(request: Request) -> StationService:
    return request.app.state.station_service
