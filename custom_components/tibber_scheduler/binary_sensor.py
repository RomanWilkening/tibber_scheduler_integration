"""Binary sensor platform for Tibber Scheduler integration."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_BASE_URL, DOMAIN
from .coordinator import TibberSchedulerCoordinator

BINARY_SENSOR_DESCRIPTIONS: tuple[tuple[str, str], ...] = (
    ("is_active", "Active"),
    ("force_run_active", "Force Run Active"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tibber Scheduler binary sensors."""
    coordinator: TibberSchedulerCoordinator = hass.data[DOMAIN][entry.entry_id]
    base_url = entry.data[CONF_BASE_URL]

    entities = []
    for device_id, info in coordinator.discovery.items():
        for field, name_suffix in BINARY_SENSOR_DESCRIPTIONS:
            entities.append(
                TibberSchedulerBinarySensor(
                    coordinator=coordinator,
                    device_id=device_id,
                    field=field,
                    name=f"{info['name']} {name_suffix}",
                    base_url=base_url,
                )
            )
    async_add_entities(entities)


class TibberSchedulerBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for a Tibber Scheduler schedule."""

    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TibberSchedulerCoordinator,
        device_id: str,
        field: str,
        name: str,
        base_url: str,
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._field = field
        self._base_url = base_url.rstrip("/")
        self._attr_name = name
        self._attr_unique_id = f"{device_id}_{field}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        device_state = self.coordinator.data.get(self._device_id)
        if device_state is None:
            return None
        return bool(device_state.get(self._field))

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra attributes."""
        attrs: dict = {}
        info = self.coordinator.discovery.get(self._device_id, {})
        detail_url = info.get("detail_url", "")
        if detail_url:
            attrs["detail_url"] = self._base_url + detail_url
        device_state = self.coordinator.data.get(self._device_id, {})
        attrs["enabled"] = device_state.get("enabled")
        return attrs
