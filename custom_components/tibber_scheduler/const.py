"""Constants for the Tibber Scheduler integration."""

DOMAIN = "tibber_scheduler"

CONF_BASE_URL = "base_url"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 30  # seconds

API_DISCOVERY = "/api/ha/discovery"
API_DEVICES = "/api/ha/devices"
API_FORCE_RUN = "/api/ha/devices/{schedule_id}/force_run"
API_STOP_FORCE_RUN = "/api/ha/devices/{schedule_id}/stop_force_run"
