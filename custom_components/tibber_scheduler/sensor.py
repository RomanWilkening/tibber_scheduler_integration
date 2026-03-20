"""Sensor platform for Tibber Scheduler integration."""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_BASE_URL, DOMAIN
from .coordinator import TibberSchedulerCoordinator

SENSOR_DESCRIPTIONS: tuple[tuple[str, str], ...] = (
    ("next_start", "Next Start"),
    ("next_end", "Next End"),
    ("force_run_since", "Force Run Since"),
    ("force_run_end", "Force Run End"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tibber Scheduler sensors."""
    coordinator: TibberSchedulerCoordinator = hass.data[DOMAIN][entry.entry_id]
    base_url = entry.data[CONF_BASE_URL]

    entities = []
    for device_id, info in coordinator.discovery.items():
        for field, name_suffix in SENSOR_DESCRIPTIONS:
            entities.append(
                TibberSchedulerSensor(
                    coordinator=coordinator,
                    device_id=device_id,
                    field=field,
                    name=f"{info['name']} {name_suffix}",
                    base_url=base_url,
                )
            )
    async_add_entities(entities)


class TibberSchedulerSensor(CoordinatorEntity, SensorEntity):
    """Timestamp sensor for a Tibber Scheduler schedule."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
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
    def native_value(self) -> datetime | None:
        """Return the sensor state as a datetime."""
        device_state = self.coordinator.data.get(self._device_id)
        if device_state is None:
            return None
        raw = device_state.get(self._field)
        if raw is None:
            return None
        from homeassistant.util.dt import parse_datetime
        return parse_datetime(raw)

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
