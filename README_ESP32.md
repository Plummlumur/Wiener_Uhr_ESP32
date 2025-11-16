# Wiener Uhr - ESP32 Port

A Viennese dialect clock that displays time in traditional Viennese German on a 64x64 RGB LED matrix, now ported to ESP32-WROOM32!

## 📋 Table of Contents

- [Features](#features)
- [Hardware Requirements](#hardware-requirements)
- [Pin Connections](#pin-connections)
- [Software Setup](#software-setup)
- [File Structure](#file-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Performance Notes](#performance-notes)

## ✨ Features

- **Viennese Time Display**: Shows time in traditional Viennese German dialect (e.g., "Es ist viertel drei")
- **Monthly Backgrounds**: Different background images for each month
- **Automatic Brightness**: Day/night mode with adjustable brightness
- **RTC Support**: Uses DS1302 Real-Time Clock for accurate timekeeping
- **Alternative Phrases**: Random variations for certain time expressions

## 🔧 Hardware Requirements

### Required Components:

1. **ESP32-WROOM32 Development Board**
   - Any ESP32-WROOM32 board (e.g., DevKit V1, NodeMCU-32S)
   - Minimum 4MB flash recommended

2. **64x64 RGB LED Matrix Panel**
   - HUB75 interface (6-pin RGB, 5-pin address)
   - 1/32 scan rate
   - Indoor P3 or P4 recommended

3. **DS1302 Real-Time Clock Module**
   - 3-wire serial interface
   - CR2032 battery backup

4. **Power Supply**
   - 5V, 4-8A (depending on brightness)
   - Recommended: Mean Well LRS-350-5 or similar

5. **Additional Components**
   - Jumper wires
   - Breadboard or custom PCB (optional)
   - Level shifters 3.3V to 5V (optional, recommended for reliability)

### Optional Components:

- Level shifters (74HCT245 or similar) for signal integrity
- Decoupling capacitors (1000µF for matrix power)

## 🔌 Pin Connections

### RGB Matrix (HUB75) Connections

| Matrix Pin | ESP32 GPIO | Description      |
|------------|------------|------------------|
| R1         | GPIO 25    | Red - Upper      |
| G1         | GPIO 26    | Green - Upper    |
| B1         | GPIO 27    | Blue - Upper     |
| R2         | GPIO 14    | Red - Lower      |
| G2         | GPIO 12    | Green - Lower    |
| B2         | GPIO 13    | Blue - Lower     |
| A          | GPIO 23    | Address A        |
| B          | GPIO 19    | Address B        |
| C          | GPIO 5     | Address C        |
| D          | GPIO 17    | Address D        |
| E          | GPIO 16    | Address E        |
| CLK        | GPIO 22    | Clock            |
| LAT        | GPIO 4     | Latch            |
| OE         | GPIO 15    | Output Enable    |
| GND        | GND        | Ground           |

### DS1302 RTC Connections

| DS1302 Pin | ESP32 GPIO | Description      |
|------------|------------|------------------|
| VCC        | 3.3V       | Power (3.3V)     |
| GND        | GND        | Ground           |
| CLK        | GPIO 18    | Serial Clock     |
| DAT        | GPIO 21    | Serial Data      |
| CE/RST     | GPIO 32    | Chip Enable      |

### Power Connections

- **Matrix Power**: Connect 5V power supply directly to matrix HUB75 connector
- **ESP32 Power**: Can be powered via USB or from 5V supply through VIN pin
- **Ground**: Connect all grounds together (ESP32, matrix, power supply, RTC)

**⚠️ Important**: Ensure GPIO 12 is LOW during ESP32 boot (matrix will be off at boot).

## 💾 Software Setup

### 1. Install MicroPython on ESP32

Download and flash MicroPython firmware:

```bash
# Install esptool
pip install esptool

# Erase flash (optional but recommended)
esptool.py --port /dev/ttyUSB0 erase_flash

# Flash MicroPython firmware (download from micropython.org)
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-*.bin
```

Download ESP32 firmware from: https://micropython.org/download/esp32/

### 2. Install Required Tools

Install `ampy` or `mpremote` for file transfer:

```bash
# Using pip
pip install adafruit-ampy

# Or use mpremote (newer)
pip install mpremote
```

### 3. Install rshell (Alternative)

```bash
pip install rshell
```

## 📁 File Structure

```
Wiener_Uhr_ESP32/
├── boot.py                 # Boot configuration
├── main_esp32.py          # Main application (rename to main.py)
├── config_esp32.py        # Pin and configuration settings
├── ds1302_esp32.py        # DS1302 RTC driver
├── hub75_esp32.py         # HUB75 matrix driver
├── display_api.py         # Graphics API
├── bmp_loader.py          # BMP image loader
├── bdf_font.py            # BDF font renderer
├── fonts/                 # Font files directory
│   └── helvR12.bdf       # Default font (copy from lib/fonts/)
├── januar_8bit.bmp        # January background
├── februar_8bit.bmp       # February background
├── maerz_8bit.bmp         # March background
├── ... (all month BMPs)
└── README_ESP32.md        # This file
```

## 🚀 Installation

### Step 1: Prepare Files

1. Copy all ESP32-specific Python files to your computer
2. Copy all month BMP files (januar_8bit.bmp, etc.)
3. Copy the font file from `lib/fonts/helvR12.bdf`

### Step 2: Upload Files to ESP32

Using `ampy`:

```bash
# Set your port
PORT=/dev/ttyUSB0

# Upload Python files
ampy --port $PORT put boot.py
ampy --port $PORT put config_esp32.py
ampy --port $PORT put ds1302_esp32.py
ampy --port $PORT put hub75_esp32.py
ampy --port $PORT put display_api.py
ampy --port $PORT put bmp_loader.py
ampy --port $PORT put bdf_font.py

# Rename and upload main file
ampy --port $PORT put main_esp32.py main.py

# Create and upload fonts directory
ampy --port $PORT mkdir /fonts
ampy --port $PORT put helvR12.bdf /fonts/helvR12.bdf

# Upload BMP files (all months)
ampy --port $PORT put januar_8bit.bmp
ampy --port $PORT put februar_8bit.bmp
ampy --port $PORT put maerz_8bit.bmp
ampy --port $PORT put april_8bit.bmp
ampy --port $PORT put mai_8bit.bmp
ampy --port $PORT put juni_8bit.bmp
ampy --port $PORT put juli_8bit.bmp
ampy --port $PORT put august_8bit.bmp
# ... upload remaining months
```

Using `rshell`:

```bash
rshell --port /dev/ttyUSB0

# Inside rshell:
cp boot.py /pyboard/
cp *.py /pyboard/
cp fonts/helvR12.bdf /pyboard/fonts/
cp *_8bit.bmp /pyboard/
```

### Step 3: Set RTC Time

Connect to ESP32 REPL and set the time:

```bash
# Using screen
screen /dev/ttyUSB0 115200

# Or using mpremote
mpremote connect /dev/ttyUSB0
```

In REPL:

```python
from ds1302_esp32 import DS1302Helper
rtc = DS1302Helper(18, 21, 32)

# Set time: year, month, day, hour, minute, second
rtc.set_time(2025, 11, 16, 14, 30, 0)

# Verify
print(rtc.get_formatted_datetime())
```

### Step 4: Reboot

Press the RESET button on your ESP32 or:

```python
import machine
machine.reset()
```

## ⚙️ Configuration

Edit `config_esp32.py` to customize:

### Pin Configuration

```python
# Change GPIO pins if needed
RGB_MATRIX_PINS = {
    'R1': 25,
    'G1': 26,
    # ...
}

DS1302_PINS = {
    'CLK': 18,
    'DAT': 21,
    'CE': 32,
}
```

### Display Settings

```python
DISPLAY_CONFIG = {
    'brightness_day': 0.3,      # 0.0 to 1.0
    'brightness_night': 0.15,   # Lower for night
    'update_interval': 60,      # Seconds
    'text_color': 0x000000,     # Black (RGB888)
}
```

### Time Settings

```python
TIME_CONFIG = {
    'night_start_hour': 16,     # Night mode starts at 16:00
    'night_end_hour': 8,        # Night mode ends at 08:00
}
```

## 🎯 Usage

### Normal Operation

Once uploaded and configured, the clock will:
1. Boot automatically on power-up
2. Initialize hardware
3. Load the current month's background
4. Display time in Viennese dialect
5. Update automatically every minute
6. Adjust brightness based on time of day

### Manual Time Update

Connect to REPL and run:

```python
from ds1302_esp32 import DS1302Helper
rtc = DS1302Helper()
rtc.set_time(2025, 11, 16, 14, 30, 0)
```

### Brightness Adjustment

Modify in `config_esp32.py`:

```python
DISPLAY_CONFIG = {
    'brightness_day': 0.5,    # Increase for brighter display
    'brightness_night': 0.1,  # Decrease for dimmer night mode
}
```

## 🔧 Troubleshooting

### Display Not Working

1. **Check power supply**: Matrix needs 5V with sufficient current
2. **Check pin connections**: Verify all HUB75 pins are connected correctly
3. **GPIO 12 issue**: Ensure GPIO 12 is LOW at boot (disconnect or use pull-down)
4. **Memory issues**: ESP32 may run out of RAM with large images

### RTC Not Keeping Time

1. **Check battery**: DS1302 needs CR2032 battery for backup
2. **Clock halted**: Run `rtc.start_clock()` in REPL
3. **Connections**: Verify CLK, DAT, CE pins

### Display Flickering

1. **Refresh rate**: The software driver is limited; consider hardware improvements
2. **Power issues**: Ensure stable 5V supply
3. **Signal integrity**: Use level shifters for longer wires

### Out of Memory

1. **Reduce image size**: Use smaller BMP files or remove unused months
2. **Simplify font**: Use built-in font instead of BDF
3. **Free memory**: Call `gc.collect()` periodically

### Wrong Time Display

1. **Set time correctly**: Use 24-hour format
2. **Check RTC**: Verify RTC is running with `rtc.is_running()`
3. **Battery**: Replace CR2032 if time resets on power loss

## ⚡ Performance Notes

### Software vs Hardware Driver

This port uses a **software-based HUB75 driver**, which has limitations:

- **Refresh rate**: ~100 Hz (may flicker on camera)
- **Color depth**: Limited to 1-bit per color (8 colors total) in basic version
- **CPU usage**: High CPU usage for display refresh

### Improvements for Production

For better performance, consider:

1. **ESP32-HUB75-MatrixPanel-DMA Library** (C++, requires Arduino framework)
2. **I2S DMA-based driver** for hardware-accelerated refresh
3. **Dual-core optimization** (use Core 0 for display, Core 1 for logic)

### Memory Optimization

- Current memory usage: ~150-200KB
- BMP images: ~8KB each (64x64 8-bit)
- Font files: ~5-10KB

## 📝 License

This is a port of the original Wiener Uhr project to ESP32.

## 🙏 Acknowledgments

- Original CircuitPython project
- MicroPython community
- HUB75 LED matrix documentation

## 📞 Support

For issues specific to the ESP32 port, check:
- Pin connections in `config_esp32.py`
- Serial output during boot
- Memory usage with `gc.mem_free()`

---

**Viel Spaß mit deiner Wiener Uhr!** 🕐🇦🇹
