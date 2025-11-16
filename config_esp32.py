"""
ESP32-WROOM32 Pin Configuration for Wiener Uhr
===============================================
Pin mapping for ESP32-WROOM32 board with HUB75 RGB LED matrix and DS1302 RTC.

ESP32 Pin Constraints:
- GPIO 0: Boot mode selection (pulled up, avoid for critical signals)
- GPIO 2: Onboard LED, strapping pin (pulled down at boot)
- GPIO 5: Strapping pin (pulled up)
- GPIO 12: Strapping pin (pulled down, must be LOW during boot)
- GPIO 15: Strapping pin (pulled up)
- GPIO 34-39: Input only (no pull-up/pull-down)
- Avoid GPIO 6-11 (connected to SPI flash on most modules)
"""

# =============================================================================
# RGB LED Matrix (HUB75 Interface) - 64x64 pixels
# =============================================================================
# The HUB75 interface requires the following pins:

# RGB Data Pins (6 pins for upper and lower half)
RGB_MATRIX_PINS = {
    'R1': 25,   # Red - Upper half
    'G1': 26,   # Green - Upper half
    'B1': 27,   # Blue - Upper half
    'R2': 14,   # Red - Lower half
    'G2': 12,   # Green - Lower half (Note: GPIO 12 strapping pin - ensure LOW at boot)
    'B2': 13,   # Blue - Lower half

    # Address pins (5 pins for 64x64 matrix = 32 rows addressable)
    'A': 23,    # Address A
    'B': 19,    # Address B
    'C': 5,     # Address C (strapping pin, but OK for output)
    'D': 17,    # Address D
    'E': 16,    # Address E (needed for 64x64 matrix)

    # Control pins
    'CLK': 22,  # Clock
    'LAT': 4,   # Latch / Strobe
    'OE': 15,   # Output Enable (active LOW, strapping pin)
}

# Matrix configuration
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 64
MATRIX_CHAIN = 1  # Number of chained panels

# =============================================================================
# DS1302 Real-Time Clock
# =============================================================================
DS1302_PINS = {
    'CLK': 18,  # Clock pin
    'DAT': 21,  # Data pin (bidirectional)
    'CE': 32,   # Chip Enable / Reset pin
}

# =============================================================================
# Display Settings
# =============================================================================
DISPLAY_CONFIG = {
    'brightness_day': 0.3,      # Brightness during day hours
    'brightness_night': 0.15,   # Brightness during night hours
    'update_interval': 60,      # Update interval in seconds
    'text_x': 1,                # Text X position
    'text_y': 8,                # Text Y position
    'text_scale': 1,            # Text scale factor
    'line_spacing': 1.5,        # Line spacing multiplier
    'text_color': 0x000000,     # Black text (RGB888)
    'rotation': 180,            # Display rotation in degrees
}

# =============================================================================
# Time Display Settings
# =============================================================================
TIME_CONFIG = {
    'use_alternative_phrases': True,  # Random alternative phrases
    'night_start_hour': 16,           # Night mode starts at 16:00
    'night_end_hour': 8,              # Night mode ends at 08:00
}

# =============================================================================
# Font Settings
# =============================================================================
FONT_CONFIG = {
    'font_path': '/fonts/helvR12.bdf',  # BDF font file path
}

# =============================================================================
# Background Images
# =============================================================================
BACKGROUND_CONFIG = {
    'use_monthly_backgrounds': True,
    'image_path': '/',
    'image_pattern': '{month}_8bit.bmp',
}

# Month names (for background image filenames)
MONTH_NAMES = [
    "januar", "februar", "maerz", "april", "mai", "juni",
    "juli", "august", "september", "oktober", "november", "dezember"
]

# =============================================================================
# WiFi and NTP Time Configuration
# =============================================================================
WIFI_CONFIG = {
    'enabled': True,                        # Enable WiFi connection
    'ssid': 'YOUR_WIFI_SSID',              # Replace with your WiFi SSID
    'password': 'YOUR_WIFI_PASSWORD',       # Replace with your WiFi password
    'timeout': 10,                          # Connection timeout in seconds
    'retry_interval': 60,                   # Retry connection interval in seconds
}

NTP_CONFIG = {
    'enabled': True,                        # Enable NTP time synchronization
    'server': 'pool.ntp.org',              # NTP server address
    'timezone_offset': 1,                   # Timezone offset in hours (CET = UTC+1)
    'dst_offset': 0,                        # Daylight saving time offset in hours
    'sync_interval': 3600,                  # Sync interval in seconds (1 hour)
    'sync_rtc': True,                       # Sync DS1302 RTC with NTP time
}

# =============================================================================
# Pin Assignment Summary for Easy Reference
# =============================================================================
"""
ESP32-WROOM32 Pin Assignment Summary:
====================================

RGB Matrix (HUB75):
  R1  -> GPIO 25    B1  -> GPIO 27    R2  -> GPIO 14
  G1  -> GPIO 26    B2  -> GPIO 13    G2  -> GPIO 12
  A   -> GPIO 23    C   -> GPIO 5     E   -> GPIO 16
  B   -> GPIO 19    D   -> GPIO 17
  CLK -> GPIO 22    LAT -> GPIO 4     OE  -> GPIO 15

DS1302 RTC:
  CLK -> GPIO 18
  DAT -> GPIO 21
  CE  -> GPIO 32

Available for future expansion:
  GPIO 33, 34, 35, 36, 39 (34-39 are input only)

Note: Ensure GPIO 12 (G2) is LOW during boot (matrix will be off at boot)
"""
