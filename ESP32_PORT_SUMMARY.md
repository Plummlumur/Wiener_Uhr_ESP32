# ESP32 Port Summary

## Overview

This codebase has been successfully ported from **CircuitPython on Raspberry Pi Pico** to **MicroPython on ESP32-WROOM32**.

## File Mapping

### Original CircuitPython Files (Pico)

| Original File | Purpose | Status |
|--------------|---------|--------|
| `main.py` | Main application for Pico | Keep for reference |
| `ds1302.py` | DS1302 driver for CircuitPython | Keep for reference |
| `ds1302_helper.py` | DS1302 helper for CircuitPython | Keep for reference |
| `settings.toml` | CircuitPython settings | Not used on ESP32 |
| `lib/` | CircuitPython libraries | Not needed on ESP32 |

### New ESP32 MicroPython Files

| ESP32 File | Purpose | Required |
|-----------|---------|----------|
| `boot.py` | Boot configuration | ✅ Yes |
| `main_esp32.py` | Main application (rename to `main.py`) | ✅ Yes |
| `config_esp32.py` | Pin and configuration settings | ✅ Yes |
| `ds1302_esp32.py` | DS1302 driver for MicroPython | ✅ Yes |
| `hub75_esp32.py` | HUB75 RGB matrix driver | ✅ Yes |
| `display_api.py` | Graphics and display API | ✅ Yes |
| `bmp_loader.py` | BMP image loader | ✅ Yes |
| `bdf_font.py` | BDF font renderer | ✅ Yes |

### Documentation Files

| File | Description |
|------|-------------|
| `README_ESP32.md` | Complete documentation for ESP32 port |
| `QUICK_START_ESP32.md` | Quick setup guide |
| `ESP32_PORT_SUMMARY.md` | This file |

### Shared Files (Use with both platforms)

| File | Description | Format |
|------|-------------|--------|
| `januar_8bit.bmp` | January background | 8-bit BMP |
| `februar_8bit.bmp` | February background | 8-bit BMP |
| `maerz_8bit.bmp` | March background | 8-bit BMP |
| `april_8bit.bmp` | April background | 8-bit BMP |
| `mai_8bit.bmp` | May background | 8-bit BMP |
| `juni_8bit.bmp` | June background | 8-bit BMP |
| `juli_8bit.bmp` | July background | 8-bit BMP |
| `august_8bit.bmp` | August background | 8-bit BMP |
| _(rest of months)_ | September-December | 8-bit BMP |
| `lib/fonts/helvR12.bdf` | Font file | BDF format |

## Key Differences: CircuitPython vs ESP32

### Hardware Platform

| Aspect | CircuitPython (Pico) | MicroPython (ESP32) |
|--------|---------------------|---------------------|
| MCU | RP2040 | ESP32-WROOM32 |
| GPIO Pins | GP2, GP3, etc. | GPIO 25, 26, etc. |
| Voltage | 3.3V | 3.3V |
| Flash | 2MB | 4MB |
| RAM | 264KB | 520KB |
| Cores | Dual Cortex-M0+ | Dual Xtensa LX6 |

### Software Changes

| Component | CircuitPython | ESP32 MicroPython |
|-----------|--------------|------------------|
| Board module | `import board` | `from machine import Pin` |
| Display driver | `rgbmatrix` built-in | Custom `hub75_esp32.py` |
| Pin access | `board.GP2` | `Pin(25)` |
| Digital I/O | `digitalio.DigitalInOut` | `machine.Pin` |
| Config file | `settings.toml` | `config_esp32.py` |
| Image loading | `adafruit_imageload` | Custom `bmp_loader.py` |
| Font rendering | `adafruit_bitmap_font` | Custom `bdf_font.py` |

### Pin Mapping Changes

**RGB Matrix:**
- Pico: GP2-GP22 (various pins)
- ESP32: GPIO 4-27 (avoiding strapping pins)

**DS1302 RTC:**
- Pico: GP6 (CLK), GP7 (DAT), GP14 (CE)
- ESP32: GPIO 18 (CLK), GPIO 21 (DAT), GPIO 32 (CE)

## Installation Summary

### For ESP32 (New Port):

1. Flash MicroPython firmware
2. Upload ESP32-specific Python files (`*_esp32.py`, `boot.py`, etc.)
3. Upload shared assets (BMP images, fonts)
4. Rename `main_esp32.py` to `main.py`
5. Configure time and reboot

### For Raspberry Pi Pico (Original):

1. Install CircuitPython firmware
2. Copy original files (`main.py`, `ds1302.py`, etc.)
3. Copy `lib/` folder with Adafruit libraries
4. Copy BMP images and fonts
5. Edit `settings.toml` for configuration

## Feature Comparison

| Feature | Pico (CircuitPython) | ESP32 (MicroPython) |
|---------|---------------------|---------------------|
| Viennese time display | ✅ | ✅ |
| Monthly backgrounds | ✅ | ✅ |
| Day/night brightness | ✅ | ✅ |
| DS1302 RTC support | ✅ | ✅ |
| Custom BDF fonts | ✅ | ✅ |
| 64x64 RGB matrix | ✅ | ✅ |
| Hardware refresh | ✅ (PIO) | ⚠️ (Software) |
| Color depth | 6-bit (64 colors) | 1-bit (8 colors)* |
| Wi-Fi capability | ❌ | ✅ (optional) |
| Bluetooth | ❌ | ✅ (optional) |

*Can be improved with BCM implementation

## Performance Notes

### CircuitPython (Pico):
- **Refresh**: Hardware-accelerated via PIO
- **Colors**: Full 6-bit (RGB222)
- **CPU Usage**: Low (offloaded to PIO)
- **Flicker**: Minimal

### MicroPython (ESP32):
- **Refresh**: Software bit-banging
- **Colors**: 1-bit per color (basic version)
- **CPU Usage**: High (~80%)
- **Flicker**: Moderate (acceptable for static display)

### Recommendations:

**Use CircuitPython/Pico if:**
- You need high refresh rates
- You want full color depth
- You have Pico hardware already

**Use MicroPython/ESP32 if:**
- You need Wi-Fi/Bluetooth
- You want more processing power
- You prefer ESP32 ecosystem
- You're okay with software refresh

## Upgrading ESP32 Performance

For better performance on ESP32, consider:

1. **Use C/C++ ESP-IDF framework** with ESP32-HUB75-MatrixPanel-DMA library
2. **Implement I2S DMA driver** for hardware-accelerated refresh
3. **Use dual-core optimization** (display on Core 0, app on Core 1)
4. **Add Binary Code Modulation (BCM)** for better color depth

## Migration Path

### From Pico to ESP32:

1. Keep all BMP and font files
2. Replace Python files with `*_esp32.py` versions
3. Update pin connections to ESP32 GPIO
4. Transfer configuration from `settings.toml` to `config_esp32.py`
5. Flash MicroPython instead of CircuitPython

### From ESP32 to Pico:

1. Keep all BMP and font files
2. Use original `main.py`, `ds1302.py` files
3. Update pin connections to Pico GP pins
4. Create `settings.toml` from `config_esp32.py` settings
5. Flash CircuitPython and install Adafruit libraries

## Directory Structure

```
Wiener_Uhr_ESP32/
│
├── CircuitPython (Original - Pico)
│   ├── main.py
│   ├── ds1302.py
│   ├── ds1302_helper.py
│   ├── settings.toml
│   └── lib/
│       ├── adafruit_bitmap_font/
│       ├── adafruit_display_text/
│       └── adafruit_imageload/
│
├── MicroPython (New - ESP32)
│   ├── boot.py
│   ├── main_esp32.py (→ main.py)
│   ├── config_esp32.py
│   ├── ds1302_esp32.py
│   ├── hub75_esp32.py
│   ├── display_api.py
│   ├── bmp_loader.py
│   └── bdf_font.py
│
├── Shared Assets
│   ├── *_8bit.bmp (12 month images)
│   └── fonts/
│       └── helvR12.bdf
│
└── Documentation
    ├── README_ESP32.md
    ├── QUICK_START_ESP32.md
    └── ESP32_PORT_SUMMARY.md
```

## What to Upload Where

### To Raspberry Pi Pico:
```
/
├── main.py (original)
├── ds1302.py (original)
├── ds1302_helper.py (original)
├── settings.toml
├── lib/ (entire folder with Adafruit libraries)
├── *_8bit.bmp (all months)
└── fonts/ (optional, can be in lib/)
```

### To ESP32:
```
/
├── boot.py
├── main.py (renamed from main_esp32.py)
├── config_esp32.py
├── ds1302_esp32.py
├── hub75_esp32.py
├── display_api.py
├── bmp_loader.py
├── bdf_font.py
├── *_8bit.bmp (all months)
└── fonts/
    └── helvR12.bdf
```

## Quick Command Reference

### ESP32 Upload:
```bash
# Single command to upload all ESP32 files
for f in boot.py config_esp32.py ds1302_esp32.py hub75_esp32.py \
         display_api.py bmp_loader.py bdf_font.py; do
    ampy --port /dev/ttyUSB0 put $f
done

# Rename and upload main
ampy --port /dev/ttyUSB0 put main_esp32.py main.py
```

### Pico Upload:
```bash
# Copy files to CIRCUITPY drive
cp main.py ds1302*.py settings.toml /media/CIRCUITPY/
cp -r lib /media/CIRCUITPY/
cp *_8bit.bmp /media/CIRCUITPY/
```

## Support

- **ESP32 Issues**: Check `README_ESP32.md`
- **Pico Issues**: Check original CircuitPython documentation
- **General Questions**: See respective platform documentation

---

**Port completed successfully!** ✅

Both CircuitPython (Pico) and MicroPython (ESP32) versions are now available.
