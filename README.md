# Aircraft Overhead Display (AOD)

AOD is a project combining Python and C++ that tracks airplanes overhead and displays/alerts based on their proximity and details. 

## Structure
- Python components handle the backend data collection/serving and media logic.
- C++ components (for microcontrollers) handle the LED display, local screens, and proximity alerting.

## Setup
### Python Server
1. Clone the project.
2. Rename `.env.example` to `.env` and fill in your details (IPs, locations, secret keys).
3. `pip install python-dotenv requests` etc.
4. Run the server: `python aod_server.py`.

### Microcontroller (C++)
1. Ensure you have the required Arduino/C++ board libraries installed.
2. Copy `config.example.h` to `config.h` in the root (or `lib/` directory depending on your setup) and put your WiFi / API details.
3. Build and upload using PlatformIO or Arduino IDE.