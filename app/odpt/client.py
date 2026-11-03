import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class ODPTError(Exception):
    """ODPT could not be reached or returned an error."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ODPTClient:
    """Thin wrapper around the ODPT API that adds the consumer key.

    Errors are re-raised without the request URL, because it contains the key.
    """

    def __init__(self, http: httpx.AsyncClient, consumer_key: str) -> None:
        self._http = http
        self._key = consumer_key

    async def fetch(self, data_type: str, **filters: str) -> list[dict[str, Any]]:
        params = {"acl:consumerKey": self._key, **filters}
        try:
            response = await self._http.get(f"/{data_type}", params=params)
        except httpx.HTTPError as exc:
            logger.warning("ODPT request for %s failed: %s", data_type, type(exc).__name__)
            raise ODPTError(f"Could not reach ODPT for {data_type}") from None

        if response.status_code != 200:
            logger.warning("ODPT returned %s for %s", response.status_code, data_type)
            raise ODPTError(f"ODPT returned {response.status_code} for {data_type}", response.status_code)
        return response.json()
