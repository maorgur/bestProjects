# Light Show Controller

A comprehensive Python-based lighting orchestration engine that synchronizes LED effects across multiple devices. 

Designed to seamlessly broadcast and coordinate RGB patterns, it integrates physical LED strips (via Arduino), PC lights, screen rendering, smart bulbs (like Yeelight), and even network devices via UDP multicast.

## Features

- **Multi-Device Synchronization**: Continuously syncs lighting patterns to:
  - **Arduino**: Sends data over raw serial to drive LED strips (WS2812B/NeoPixels).
  - **PC Lights**: Native PC ambient lighting integration.
  - **Smart Bulbs**: Discovers and controls smart bulbs (Yeelight) on the network.
  - **Screen Preview**: Renders a live preview window of your current pattern.
  - **Network Receivers**: UDP multicast to sync multiple network-connected receiver nodes.
- **Custom Animation Engine**: Create complex effects and transitions using the `brain.py` frame generation engine, designed to match BPM (`keys.py`) for music visualization.
- **Terminal UI & Hotkeys**: Manage your lights natively via configurable keyboard hotkeys bindings and a built-in terminal visualizer.
- **Media Controller**: Includes hooks for media playback integration.

## Project Structure

- `brain.py` - The core engine for loading, modifying, and triggering LED transitions and effects.
- `broadcaster.py` & `receiver.py` - Network endpoints. The broadcaster sends synchronized UDP payloads, while the receiver decodes and relays them to subsequent endpoints.
- `raw_serial.py` - Serial bridge handling high-speed framing to an Arduino.
- `light_bulbs.py` - Module for discovering and commanding Wi-Fi smart bulbs using SSDP.
- `pc_lights.py` & `screen.py` - Handlers for PC illumination and real-time GUI preview.
- `config.py` - Global configuration.

## Setup & Configuration

1. **Install Dependencies**: Ensure you have Python installed along with the required networking and UI packages (e.g. `yeelight`, `pyserial`).
2. **Configure Ports**: Edit `config.py` and assign your custom ports and setup configuration:
   - Make sure `ARDUINO_PORT` is set correctly to your board (e.g., `'COM3'` / `'/dev/ttyUSB0'`).
   - Toggle features on or off by setting boolean flags (`SEND_TO_ARDUINO`, `SEND_TO_NETWORK`, `SEND_TO_BULBS`, etc.).
3. **Run**: 
   - Execute the main orchestrator `effects.py`.
   - Alternatively, run `receiver.py` on client machines you want to sync over the network.

