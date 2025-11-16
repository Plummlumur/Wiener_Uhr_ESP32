# Wiener Uhr (Viennese Clock) - Arduino ESP32 Port

Arduino port of the Wiener Uhr (Viennese Clock) for ESP32 with HUB75 RGB LED Matrix.

## Overview

This project displays the current time in Viennese German dialect on a 64x64 RGB LED matrix. The clock uses authentic Viennese time expressions like "viertel drei" (quarter past two), "halb vier" (half past three), and includes regional variations.

## Features

- **Viennese Time Format**: Displays time in authentic Viennese German dialect
- **WiFi & NTP Support**: Automatic time synchronization via internet
- **DS1302 RTC Support**: Optional hardware RTC for offline operation
- **64x64 RGB Matrix**: High-quality HUB75 LED matrix display
- **Day/Night Brightness**: Automatic brightness adjustment based on time
- **Alternative Phrases**: Random variations for certain times (10, 20, 40, 50 minutes)

## Hardware Requirements

### Required Components

1. **ESP32-WROOM32** or compatible ESP32 development board
2. **64x64 HUB75 RGB LED Matrix Panel** (P2.5, P3, or P4)
3. **5V Power Supply** (3-5A recommended, depending on brightness)
4. **Jumper Wires** for connections

### Optional Components

5. **DS1302 Real-Time Clock Module** (optional, only needed if not using WiFi/NTP)

### Wiring Diagram

#### HUB75 Matrix to ESP32

| HUB75 Pin | ESP32 GPIO | Description          |
|-----------|------------|----------------------|
| R1        | 25         | Red - Upper half     |
| G1        | 26         | Green - Upper half   |
| B1        | 27         | Blue - Upper half    |
| R2        | 14         | Red - Lower half     |
| G2        | 12         | Green - Lower half   |
| B2        | 13         | Blue - Lower half    |
| A         | 23         | Address A            |
| B         | 19         | Address B            |
| C         | 5          | Address C            |
| D         | 17         | Address D            |
| E         | 16         | Address E (64x64)    |
| CLK       | 22         | Clock                |
| LAT       | 4          | Latch/Strobe         |
| OE        | 15         | Output Enable        |
| GND       | GND        | Ground               |

**Note**: Connect the matrix power (5V and GND) to your 5V power supply, **not** to the ESP32. The ESP32 should be powered separately via USB or the power supply's 5V rail through a voltage regulator.

#### DS1302 RTC to ESP32 (Optional)

| DS1302 Pin | ESP32 GPIO |
|------------|------------|
| VCC        | 3.3V       |
| GND        | GND        |
| CLK        | 18         |
| DAT        | 21         |
| CE/RST     | 32         |

## Software Requirements

### Arduino IDE

1. **Arduino IDE** 1.8.19 or newer (or Arduino IDE 2.x)
2. **ESP32 Board Support**: Install via Boards Manager
   - Add to Boards Manager URLs: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Install "ESP32 by Espressif Systems"

### Required Libraries

Install the following libraries via Arduino Library Manager (**Tools → Manage Libraries**):

1. **ESP32-HUB75-MatrixPanel-DMA** by mrfaptastic (v3.0.0 or newer)
   - Search: "ESP32 HUB75"
   - This is the most critical library for the LED matrix

2. **Adafruit GFX Library** (dependency for matrix library)
   - Search: "Adafruit GFX"

3. **DS1302** by Timur Maksimov (optional, only if using DS1302 RTC)
   - Search: "DS1302"
   - Only needed if `USE_DS1302` is set to `true` in config.h

### PlatformIO (Alternative)

If using PlatformIO, use the provided `platformio.ini` file. All dependencies will be installed automatically.

## Installation & Setup

### 1. Clone or Download

```bash
cd arduino/Wiener_Uhr_ESP32
```

### 2. Configure WiFi and Settings

Edit `config.h` and update the following:

```cpp
// WiFi credentials
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// Timezone (CET = 1, CEST = 2, PST = -8, etc.)
#define NTP_TIMEZONE_OFFSET 1

// Enable/disable DS1302 RTC
#define USE_DS1302 false  // Set to true if you have a DS1302 connected
```

### 3. Install Libraries

**Arduino IDE:**
- Open **Tools → Manage Libraries**
- Install the required libraries listed above

**PlatformIO:**
- Libraries will be installed automatically based on `platformio.ini`

### 4. Upload to ESP32

1. Connect ESP32 via USB
2. Select the correct board: **Tools → Board → ESP32 Dev Module**
3. Select the correct port: **Tools → Port → (your port)**
4. Click **Upload**

### 5. Monitor Serial Output

Open **Tools → Serial Monitor** (115200 baud) to see:
- WiFi connection status
- NTP synchronization
- Current time updates

## Configuration Options

All configuration is done in `config.h`:

### Display Settings

```cpp
#define BRIGHTNESS_DAY   80    // Day brightness (0-255)
#define BRIGHTNESS_NIGHT 40    // Night brightness (0-255)
#define NIGHT_START_HOUR 16    // Night mode starts at 16:00
#define NIGHT_END_HOUR   8     // Night mode ends at 08:00
```

### WiFi & NTP

```cpp
#define WIFI_ENABLED true
#define NTP_ENABLED true
#define NTP_SERVER "pool.ntp.org"
#define NTP_TIMEZONE_OFFSET 1  // Hours offset from UTC
#define NTP_SYNC_INTERVAL 3600 // Seconds between NTP syncs
```

### Text Appearance

```cpp
#define TEXT_COLOR 0x0000      // Black text (for colored backgrounds)
#define LINE_SPACING 13        // Pixels between lines
```

## Time Display Examples

The clock displays time in Viennese German dialect:

| Time  | Display                              |
|-------|--------------------------------------|
| 13:00 | Es ist / punkt / Eins                |
| 13:15 | Es ist / viertel / Zwei              |
| 13:30 | Es ist / halb / Zwei                 |
| 13:45 | Es ist / dreiviertel / Zwei          |
| 13:05 | Es ist / fünf nach / Eins            |
| 13:10 | Es ist / fünf vor / viertel / Zwei   |
| 13:25 | Es ist / fünf vor / halb / Zwei      |
| 13:40 | Es ist / fünf vor / dreiviertel / Zwei |

## Troubleshooting

### Display shows nothing or garbage

1. Check power supply to matrix (5V, sufficient amperage)
2. Verify all HUB75 pin connections
3. Check that E pin is connected (required for 64x64 panels)
4. Try reducing brightness in config.h

### WiFi connection fails

1. Verify SSID and password in config.h
2. Check WiFi signal strength
3. Monitor serial output for error messages
4. Make sure WiFi is 2.4GHz (ESP32 doesn't support 5GHz)

### Time is incorrect

1. Check timezone offset in config.h
2. Verify NTP server is accessible
3. If using DS1302, check RTC battery and connections
4. Monitor serial output for NTP sync status

### Compilation errors

1. Ensure all required libraries are installed
2. Update ESP32 board support to latest version
3. Check that you're using Arduino IDE 1.8.19 or newer
4. For "time.h" errors, make sure you have ESP32 board support installed

### Matrix is dim or colors are wrong

1. Adjust brightness settings in config.h
2. Check power supply voltage (should be stable 5V)
3. Verify all color pins (R1, G1, B1, R2, G2, B2) are connected correctly

## Advanced Usage

### Adding Background Images

1. Set `USE_MONTHLY_BACKGROUNDS true` in config.h
2. Prepare 64x64 BMP images for each month
3. Upload images to SPIFFS or SD card
4. Update background path in config.h

### Custom Fonts

The project uses Adafruit GFX built-in fonts. To use custom fonts:

1. Convert your font to Adafruit GFX format
2. Include the font header file
3. Modify `display_manager.cpp` to use the custom font

### Modifying Pin Assignments

All pins can be changed in `config.h`. However, avoid these ESP32 pins:
- GPIO 0, 2, 5, 12, 15 (strapping pins - use with caution)
- GPIO 6-11 (connected to flash on most modules)
- GPIO 34-39 (input only, no pull-up/down)

## Project Structure

```
arduino/Wiener_Uhr_ESP32/
├── Wiener_Uhr_ESP32.ino    # Main Arduino sketch
├── config.h                 # Configuration file
├── wiener_zeit.h            # Viennese time logic (header)
├── wiener_zeit.cpp          # Viennese time logic (implementation)
├── wifi_manager.h           # WiFi & NTP manager (header)
├── wifi_manager.cpp         # WiFi & NTP manager (implementation)
├── display_manager.h        # Display manager (header)
├── display_manager.cpp      # Display manager (implementation)
└── platformio.ini           # PlatformIO configuration (optional)
```

## Credits

- **Original Project**: Wiener Uhr for Raspberry Pi Pico
- **MicroPython ESP32 Port**: ESP32 MicroPython version
- **Arduino Port**: Arduino C++ implementation

## License

This project is open source. See main repository for license information.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## See Also

- [MicroPython ESP32 Version](../README_ESP32.md)
- [Original Raspberry Pi Pico Version](../README.md)
- [ESP32-HUB75-MatrixPanel-DMA Library](https://github.com/mrfaptastic/ESP32-HUB75-MatrixPanel-DMA)
