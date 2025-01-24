"""Sample API Client."""

from __future__ import annotations

import socket
from typing import Any

import aiohttp
import async_timeout

from .const import LOGGER


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
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method, url=url, headers=headers
                )
                _verify_response_or_raise(response)

                mappings = [
                    "BEDIENUNG",
                    "BETRIEBSART",
                    "LEISTUNG",
                    "HELLIGKEIT",
                    "TEMPERATUR",
                    "SCHIEBER",
                    "FEINZUG",
                    "STATUS",
                    "ERRORS",
                    "LED",
                    "ABBRAND",
                    "LAUTSTAERKE",
                ]
                splitted_values = str(await response.text()).strip().split("\\n")
                splitted_values.pop(0)
                splitted_values.pop(-1)
                LOGGER.debug(f"Slitted values: {splitted_values}")

                res_dict = {}
                for i in range(len(mappings)):
                    res_dict[mappings[i]] = splitted_values[i]

                if res_dict["ABBRAND"] == "0":
                    res_dict["ABBRAND"] = "Gluterhalt"
                else:
                    res_dict["ABBRAND"] = "Glutabbrand"

                res_dict["BETRIEBSART"] = self.__str_map_betriebsart(
                    res_dict["BETRIEBSART"]
                )
                res_dict["STATUS"] = self.__str_mapping_status(res_dict["STATUS"])

                LOGGER.debug(f"Mapped values: {res_dict}")

                return res_dict

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

    def __str_mapping_status(self, str_to_be_mapped: str) -> str:
        sanitized_str = str_to_be_mapped.lower().strip()
        known_mappings = {
            "aus": "Standby",
            "gruen blinkt": "Anheizvorgang",
            "gruen": "Regelbetrieb",
            "gelb": "Holz nachlegen",
            "gelb blinkt": "Letzte Möglichkeit zum Holz nachlegen",
            "orange": "Glutabbrand",
            "violett blinkt": "Gluterhalt",
            "rot blinkt": "Fehlermeldung",
        }

        if sanitized_str in known_mappings:
            return known_mappings[sanitized_str]
        return sanitized_str

    def __str_map_betriebsart(self, str_to_be_mapped: str) -> str:
        known_mappings = {"2": "Eco", "3": "Normal", "4": "Power"}

        if str_to_be_mapped.lower() in known_mappings:
            return known_mappings[str_to_be_mapped]
        return str_to_be_mapped
