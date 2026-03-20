"""DataUpdateCoordinator for Tibber Scheduler."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_DEVICES, API_DISCOVERY, DOMAIN

_LOGGER = logging.getLogger(__name__)


class TibberSchedulerCoordinator(DataUpdateCoordinator):
    """Coordinator that polls /api/ha/devices and provides device states."""

    def __init__(
        self, hass: HomeAssistant, base_url: str, scan_interval: int
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.discovery: dict[str, dict] = {}  # device_id -> HADeviceInfo

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def async_fetch_discovery(self) -> None:
        """Fetch discovery data (once on setup / reload)."""
        session = async_get_clientsession(self.hass)
        url = self.base_url + API_DISCOVERY
        try:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
        except Exception as err:
            raise UpdateFailed(f"Error fetching discovery data: {err}") from err

        self.discovery = {d["device_id"]: d for d in data.get("devices", [])}

    async def _async_update_data(self) -> dict[str, dict]:
        """Fetch all device states from /api/ha/devices."""
        session = async_get_clientsession(self.hass)
        url = self.base_url + API_DEVICES
        try:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
        except Exception as err:
            raise UpdateFailed(f"Error fetching device states: {err}") from err

        return {d["device_id"]: d for d in data.get("devices", [])}

    async def async_force_run(self, schedule_id: int) -> None:
        """POST force_run for the given schedule."""
        session = async_get_clientsession(self.hass)
        url = f"{self.base_url}/api/ha/devices/{schedule_id}/force_run"
        async with session.post(
            url, timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            resp.raise_for_status()

    async def async_stop_force_run(self, schedule_id: int) -> None:
        """POST stop_force_run for the given schedule."""
        session = async_get_clientsession(self.hass)
        url = f"{self.base_url}/api/ha/devices/{schedule_id}/stop_force_run"
        async with session.post(
            url, timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            resp.raise_for_status()
