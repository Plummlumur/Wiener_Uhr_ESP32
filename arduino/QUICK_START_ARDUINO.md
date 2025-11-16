# Quick Start Guide - Arduino ESP32 Port

Get your Wiener Uhr running in 5 easy steps!

## What You Need

### Hardware
- ESP32-WROOM32 development board
- 64x64 HUB75 RGB LED Matrix Panel
- 5V Power Supply (3-5A)
- USB cable for ESP32
- Jumper wires

### Software
- Arduino IDE 1.8.19+ or Arduino IDE 2.x
- ESP32 board support
- Required libraries (see below)

## Step 1: Install Arduino IDE & ESP32 Support

1. **Download Arduino IDE**: https://www.arduino.cc/en/software

2. **Add ESP32 Board Support**:
   - Open Arduino IDE
   - Go to **File → Preferences**
   - Add to "Additional Boards Manager URLs":
     ```
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
     ```
   - Click OK
   - Go to **Tools → Board → Boards Manager**
   - Search for "esp32"
   - Install "ESP32 by Espressif Systems"

## Step 2: Install Required Libraries

Open **Tools → Manage Libraries** and install:

1. **ESP32 HUB75 LED MATRIX PANEL DMA Display** by mrfaptastic
2. **Adafruit GFX Library**

Search for each library name and click "Install".

## Step 3: Wire Your Hardware

### Matrix Power (IMPORTANT!)
- Connect matrix **5V** and **GND** to your 5V power supply
- **DO NOT** power the matrix from ESP32!
- Connect ESP32 GND to power supply GND (common ground)

### HUB75 Connections

Connect the HUB75 connector to ESP32:

| Matrix | ESP32 | Matrix | ESP32 |
|--------|-------|--------|-------|
| R1     | 25    | B2     | 13    |
| G1     | 26    | A      | 23    |
| B1     | 27    | B      | 19    |
| R2     | 14    | C      | 5     |
| G2     | 12    | D      | 17    |
| CLK    | 22    | E      | 16    |
| LAT    | 4     | OE     | 15    |

## Step 4: Configure WiFi

1. Open `Wiener_Uhr_ESP32.ino` in Arduino IDE
2. Click on the `config.h` tab
3. Edit WiFi credentials:

```cpp
#define WIFI_SSID "YourWiFiName"
#define WIFI_PASSWORD "YourWiFiPassword"
```

4. Set your timezone (CET = 1, CEST = 2, EST = -5, PST = -8, etc.):

```cpp
#define NTP_TIMEZONE_OFFSET 1  // Change this
```

5. Save the file

## Step 5: Upload and Run

1. **Connect ESP32** via USB
2. **Select Board**: Tools → Board → ESP32 Dev Module
3. **Select Port**: Tools → Port → (your port)
   - Windows: Usually COM3, COM4, etc.
   - Mac: Usually /dev/cu.usbserial-*
   - Linux: Usually /dev/ttyUSB0
4. Click **Upload** button (→)
5. Wait for compilation and upload
6. Open **Serial Monitor** (Tools → Serial Monitor, 115200 baud)

You should see:
```
==================================================
   Wiener Uhr - ESP32 Arduino Version
==================================================

Initializing RGB Matrix...
Matrix initialized successfully
Connecting to WiFi: YourWiFiName...
WiFi connected!
Syncing time with NTP server: pool.ntp.org
NTP synchronization successful!
```

Your clock should now display the time in Viennese German!

## Common Issues

### "Matrix initialization failed"
- Check all HUB75 pin connections
- Verify matrix power supply (5V, sufficient amperage)
- Make sure E pin is connected (needed for 64x64 panels)

### "WiFi connection timeout"
- Double-check SSID and password in config.h
- Make sure you're using 2.4GHz WiFi (not 5GHz)
- Move ESP32 closer to WiFi router

### Display is too bright/dim
Edit in `config.h`:
```cpp
#define BRIGHTNESS_DAY   80    // Lower this (0-255)
#define BRIGHTNESS_NIGHT 40    // Lower this (0-255)
```

### Compilation errors about libraries
- Make sure you installed both required libraries
- Try updating to the latest versions
- Restart Arduino IDE

## Next Steps

- **Adjust brightness**: Edit `BRIGHTNESS_DAY` and `BRIGHTNESS_NIGHT` in config.h
- **Change day/night hours**: Edit `NIGHT_START_HOUR` and `NIGHT_END_HOUR`
- **Disable WiFi**: Set `WIFI_ENABLED false` (requires DS1302 RTC)
- **Add DS1302 RTC**: For offline operation without WiFi

## PlatformIO Users

If you prefer PlatformIO:

```bash
cd arduino/Wiener_Uhr_ESP32
pio run --target upload
pio device monitor
```

Libraries will be installed automatically!

## Need Help?

- Check the full [Arduino README](README.md)
- Review serial monitor output for error messages
- Check all wiring connections
- Verify power supply voltage and current capacity

## Success!

If everything works, you should see the time displayed in Viennese German dialect:

```
Es ist
viertel
Drei
```

(for 14:15 / 2:15 PM)

Enjoy your Wiener Uhr! 🕐
