"""Button platform for Tibber Scheduler integration."""
from __future__ import annotations

import logging

import aiohttp

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_BASE_URL, DOMAIN
from .coordinator import TibberSchedulerCoordinator

_LOGGER = logging.getLogger(__name__)

BUTTON_DESCRIPTIONS: tuple[tuple[str, str, str], ...] = (
    ("force_run", "Force Run", "force_run"),
    ("stop_force_run", "Stop Force Run", "stop_force_run"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tibber Scheduler buttons."""
    coordinator: TibberSchedulerCoordinator = hass.data[DOMAIN][entry.entry_id]
    base_url = entry.data[CONF_BASE_URL]

    entities = []
    for device_id, info in coordinator.discovery.items():
        for action_key, name_suffix, action_type in BUTTON_DESCRIPTIONS:
            entities.append(
                TibberSchedulerButton(
                    coordinator=coordinator,
                    device_id=device_id,
                    schedule_id=info["schedule_id"],
                    action_type=action_type,
                    name=f"{info['name']} {name_suffix}",
                    base_url=base_url,
                )
            )
    async_add_entities(entities)


class TibberSchedulerButton(CoordinatorEntity, ButtonEntity):
    """Button to trigger force_run or stop_force_run for a schedule."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TibberSchedulerCoordinator,
        device_id: str,
        schedule_id: int,
        action_type: str,
        name: str,
        base_url: str,
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._schedule_id = schedule_id
        self._action_type = action_type
        self._base_url = base_url.rstrip("/")
        self._attr_name = name
        self._attr_unique_id = f"{device_id}_{action_type}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            if self._action_type == "force_run":
                await self.coordinator.async_force_run(self._schedule_id)
            else:
                await self.coordinator.async_stop_force_run(self._schedule_id)
        except aiohttp.ClientResponseError as err:
            if err.status == 409:
                raise HomeAssistantError(
                    f"Cannot execute '{self._action_type}': condition not met "
                    f"(HTTP 409)"
                ) from err
            raise HomeAssistantError(
                f"Error executing '{self._action_type}': {err}"
            ) from err
        except Exception as err:
            raise HomeAssistantError(
                f"Error executing '{self._action_type}': {err}"
            ) from err

        # Refresh state after action
        await self.coordinator.async_request_refresh()

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra attributes."""
        attrs: dict = {}
        info = self.coordinator.discovery.get(self._device_id, {})
        detail_url = info.get("detail_url", "")
        if detail_url:
            attrs["detail_url"] = self._base_url + detail_url
        return attrs
