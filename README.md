<p align="center">
  <img src="custom_components/tibber_scheduler/brand/logo.png" alt="Tibber Scheduler Logo" width="256">
</p>

# Tibber Scheduler Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A custom Home Assistant integration for the Tibber Scheduler. It exposes sensors, binary sensors, and buttons that let you monitor and control your Tibber schedules directly from the Home Assistant UI.

## Features

- **Sensors** – current schedule status and timing information
- **Binary sensors** – on/off state for active schedules
- **Buttons** – force-run and stop-force-run for each schedule

## Installation

### HACS (recommended)

1. Open **HACS** in Home Assistant.
2. Go to **Integrations**.
3. Click the **⋮** menu (top right) and select **Custom repositories**.
4. Enter the repository URL:
   ```
   https://github.com/RomanWilkening/tibber_scheduler_integration
   ```
5. Select **Integration** as the category and click **Add**.
6. Search for **Tibber Scheduler** and click **Download**.
7. Restart Home Assistant.

### Manual

1. Copy the `custom_components/tibber_scheduler` folder into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.

## Configuration

1. In Home Assistant go to **Settings → Devices & Services → Add Integration**.
2. Search for **Tibber Scheduler**.
3. Enter the base URL of your Tibber Scheduler instance and the desired scan interval.

## Links

- [Issues](https://github.com/RomanWilkening/tibber_scheduler_integration/issues)