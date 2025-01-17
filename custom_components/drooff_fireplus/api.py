"""Sample API Client."""

from __future__ import annotations

import socket
from typing import Any

import aiohttp
import async_timeout


class DrooffFireplusApiClientError(Exception):
    """Exception to indicate a general API error."""


class DrooffFireplusApiClientCommunicationError(
    DrooffFireplusApiClientError,
):
    """Exception to indicate a communication error."""


class DrooffFireplusApiClientAuthenticationError(
    DrooffFireplusApiClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise DrooffFireplusApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


class DrooffFireplusApiClient:
    """Sample API Client."""

    def __init__(self, session: aiohttp.ClientSession, ip: str) -> None:
        """Sample API Client."""
        self._ip = ip
        self._session = session

    async def async_get_data(self) -> Any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="get",
            url=f"http://{self._ip}/php/easpanel.php",
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
      #  data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers
                )
                _verify_response_or_raise(response)
                return await response.text()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise DrooffFireplusApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise DrooffFireplusApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}, {self._ip}"
            raise DrooffFireplusApiClientError(
                msg,
            ) from exception
