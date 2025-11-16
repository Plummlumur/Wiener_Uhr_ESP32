# Quick Start Guide - Wiener Uhr ESP32

## Hardware Checklist

- [ ] ESP32-WROOM32 board
- [ ] 64x64 HUB75 RGB LED matrix
- [ ] DS1302 RTC module with CR2032 battery
- [ ] 5V power supply (4-8A)
- [ ] Jumper wires
- [ ] USB cable for ESP32

## Quick Setup (5 Steps)

### 1. Wire Everything

**RGB Matrix to ESP32:**
```
R1→GPIO25  G1→GPIO26  B1→GPIO27
R2→GPIO14  G2→GPIO12  B2→GPIO13
A→GPIO23   B→GPIO19   C→GPIO5
D→GPIO17   E→GPIO16
CLK→GPIO22 LAT→GPIO4  OE→GPIO15
GND→GND
```

**DS1302 to ESP32:**
```
VCC→3.3V   GND→GND
CLK→GPIO18 DAT→GPIO21 CE→GPIO32
```

**Power:**
```
Matrix: 5V supply → HUB75 connector
ESP32: USB or 5V → VIN pin
All grounds connected together
```

### 2. Flash MicroPython

```bash
pip install esptool
esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-*.bin
```

Download firmware: https://micropython.org/download/esp32/

### 3. Upload Files

```bash
pip install adafruit-ampy

PORT=/dev/ttyUSB0

# Core files
ampy --port $PORT put boot.py
ampy --port $PORT put main_esp32.py main.py
ampy --port $PORT put config_esp32.py
ampy --port $PORT put ds1302_esp32.py
ampy --port $PORT put hub75_esp32.py
ampy --port $PORT put display_api.py
ampy --port $PORT put bmp_loader.py
ampy --port $PORT put bdf_font.py

# Font
ampy --port $PORT mkdir /fonts
ampy --port $PORT put lib/fonts/helvR12.bdf /fonts/helvR12.bdf

# Images (all months)
ampy --port $PORT put januar_8bit.bmp
ampy --port $PORT put februar_8bit.bmp
# ... repeat for all months
```

### 4. Set Time

```bash
screen /dev/ttyUSB0 115200
```

In REPL:
```python
from ds1302_esp32 import DS1302Helper
rtc = DS1302Helper()
rtc.set_time(2025, 11, 16, 14, 30, 0)  # year, month, day, hour, min, sec
```

Press Ctrl+A, K, Y to exit screen

### 5. Reboot

Press RESET button on ESP32 - Done!

## Test Checklist

- [ ] ESP32 boots (serial output visible)
- [ ] RTC time set correctly
- [ ] Matrix lights up
- [ ] Background image displays
- [ ] Text appears on matrix
- [ ] Time updates every minute
- [ ] Brightness changes day/night

## Common Issues

| Problem | Solution |
|---------|----------|
| Matrix doesn't light up | Check 5V power supply and connections |
| Display flickers badly | Normal for software driver, try lower brightness |
| RTC time resets | Replace CR2032 battery |
| Out of memory | Remove unused BMP files |
| GPIO 12 boot fail | Disconnect GPIO 12 during boot, reconnect after |

## Configuration Quick Reference

Edit `config_esp32.py`:

**Brightness:**
```python
'brightness_day': 0.3,     # 0.0 - 1.0
'brightness_night': 0.15,  # 0.0 - 1.0
```

**Night Mode Hours:**
```python
'night_start_hour': 16,    # 4 PM
'night_end_hour': 8,       # 8 AM
```

**Pin Changes:**
```python
RGB_MATRIX_PINS = { 'R1': 25, ... }
DS1302_PINS = { 'CLK': 18, ... }
```

## Files Overview

| File | Purpose |
|------|---------|
| `boot.py` | Runs on boot, initializes system |
| `main.py` | Main clock application (renamed from main_esp32.py) |
| `config_esp32.py` | All pin and settings configuration |
| `ds1302_esp32.py` | RTC driver |
| `hub75_esp32.py` | LED matrix driver |
| `display_api.py` | Graphics and display API |
| `bmp_loader.py` | Image loader |
| `bdf_font.py` | Font renderer |

## Troubleshooting Commands

Check free memory:
```python
import gc
print(gc.mem_free())
```

Check RTC:
```python
from ds1302_esp32 import DS1302Helper
rtc = DS1302Helper()
print(rtc.get_formatted_datetime())
print(rtc.is_running())
```

Force display update:
```python
# In main loop, already handled
```

Reset ESP32:
```python
import machine
machine.reset()
```

## Performance Tips

1. **Brightness**: Lower = better refresh rate
2. **Images**: Smaller BMPs = more free RAM
3. **Font**: Use default font if memory tight
4. **Refresh**: Call `display_manager.update()` frequently

## Next Steps

- Adjust brightness in config
- Add Wi-Fi for NTP time sync (see boot.py comments)
- Customize monthly images
- Modify time display phrases in `returnWienerZeit()`

---

Need help? Check README_ESP32.md for detailed documentation.
