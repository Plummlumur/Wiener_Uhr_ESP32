# Wiener Uhr (Viennese Clock)

A beautiful clock that displays time in traditional Viennese German dialect on a 64x64 RGB LED matrix.

![Wiener Uhr](https://img.shields.io/badge/Platform-ESP32%20%7C%20Raspberry%20Pi%20Pico-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Language](https://img.shields.io/badge/Language-MicroPython%20%7C%20CircuitPython%20%7C%20Arduino-yellow)

## 🕐 What is Wiener Uhr?

Wiener Uhr displays the current time in the traditional Viennese way of telling time. Instead of saying "2:15", Viennese people say "viertel drei" (quarter three). This project brings that charming tradition to life on an LED matrix!

### Example Time Displays:
- 14:00 → "Es ist punkt Zwei"
- 14:15 → "Es ist viertel Drei"
- 14:30 → "Es ist halb Drei"
- 14:45 → "Es ist dreiviertel Drei"
- 14:52 → "Es ist acht vor Drei"

## 🎯 Features

- **Authentic Viennese Time**: Displays time in traditional Viennese German dialect
- **Monthly Backgrounds**: Different background image for each month
- **Automatic Brightness**: Day and night modes with adjustable brightness
- **Real-Time Clock**: Uses DS1302 RTC for accurate timekeeping with battery backup
- **Alternative Phrases**: Random variations for certain time expressions (10, 20, 40, 50 minutes)
- **Custom Fonts**: BDF font support for beautiful text rendering

## 🔧 Three Platform Options

This project supports **three hardware platforms**:

### Option 1: ESP32 (Arduino)
- **Recommended for**: Arduino ecosystem, easy setup, C++ performance
- **Documentation**: [arduino/README.md](arduino/README.md)
- **Quick Start**: [arduino/QUICK_START_ARDUINO.md](arduino/QUICK_START_ARDUINO.md)
- **Features**: Wi-Fi time sync, automatic brightness, optimized performance

### Option 2: ESP32-WROOM32 (MicroPython)
- **Recommended for**: Python development, flexible scripting, ESP32 ecosystem
- **Documentation**: [README_ESP32.md](README_ESP32.md)
- **Quick Start**: [QUICK_START_ESP32.md](QUICK_START_ESP32.md)

### Option 3: Raspberry Pi Pico (CircuitPython)
- **Recommended for**: Better display performance, lower cost, CircuitPython ecosystem
- **Files**: `main.py`, `ds1302.py`, `ds1302_helper.py`, `settings.toml`
- **Libraries**: Requires Adafruit CircuitPython libraries in `lib/` folder

See [ESP32_PORT_SUMMARY.md](ESP32_PORT_SUMMARY.md) for a detailed comparison.

## 📦 Quick Start

### For ESP32 (Arduino):
See [arduino/QUICK_START_ARDUINO.md](arduino/QUICK_START_ARDUINO.md)

### For ESP32 (MicroPython):
See [QUICK_START_ESP32.md](QUICK_START_ESP32.md)

### For Raspberry Pi Pico (CircuitPython):
1. Install CircuitPython on Pico
2. Copy `main.py`, `ds1302*.py`, `settings.toml` to CIRCUITPY drive
3. Copy `lib/` folder with Adafruit libraries
4. Copy all `*_8bit.bmp` images and fonts
5. Configure RTC time and reboot

## 🛠️ Hardware Requirements

### Common Components (Both Platforms):
- 64x64 HUB75 RGB LED Matrix Panel
- DS1302 Real-Time Clock Module
- CR2032 battery for RTC
- 5V power supply (4-8A)
- Jumper wires

### Platform-Specific:
- **ESP32 (Arduino/MicroPython)**: ESP32-WROOM32 development board
- **Pico**: Raspberry Pi Pico board

## 📂 Repository Structure

```
Wiener_Uhr_ESP32/
│
├── README.md                    # This file
├── .gitignore                   # Git ignore file
│
├── Arduino Version (C++)
│   ├── arduino/
│   │   ├── README.md            # Arduino documentation
│   │   ├── QUICK_START_ARDUINO.md  # Quick setup guide
│   │   └── Wiener_Uhr_ESP32/    # Arduino sketch folder
│   │       ├── Wiener_Uhr_ESP32.ino  # Main sketch
│   │       ├── config.h         # Configuration
│   │       ├── wifi_manager.*   # WiFi & NTP
│   │       ├── display_manager.* # Display driver
│   │       └── wiener_zeit.*    # Time logic
│
├── ESP32 Version (MicroPython)
│   ├── README_ESP32.md          # ESP32 documentation
│   ├── QUICK_START_ESP32.md     # Quick setup guide
│   ├── ESP32_CHECKLIST.md       # Installation checklist
│   ├── ESP32_PORT_SUMMARY.md    # Port comparison
│   ├── boot.py                  # ESP32 boot config
│   ├── main_esp32.py            # Main application
│   ├── config_esp32.py          # Configuration
│   ├── ds1302_esp32.py          # RTC driver
│   ├── hub75_esp32.py           # Matrix driver
│   ├── display_api.py           # Display API
│   ├── bmp_loader.py            # Image loader
│   └── bdf_font.py              # Font renderer
│
├── Pico Version (CircuitPython)
│   ├── main.py                  # Main application
│   ├── ds1302.py                # RTC driver
│   ├── ds1302_helper.py         # RTC helper
│   ├── settings.toml            # Configuration
│   └── lib/                     # Adafruit libraries
│
└── Shared Assets
    ├── januar_8bit.bmp          # January background
    ├── februar_8bit.bmp         # February background
    ├── maerz_8bit.bmp           # March background
    ├── april_8bit.bmp           # April background
    ├── mai_8bit.bmp             # May background
    ├── juni_8bit.bmp            # June background
    ├── juli_8bit.bmp            # July background
    ├── august_8bit.bmp          # August background
    ├── oktober_8bit.bmp         # October background
    ├── november_8bit.bmp        # November background
    ├── dezember_8bit.bmp        # December background
    └── lib/fonts/
        └── helvR12.bdf          # Font file
```

## 🚀 Getting Started

1. **Choose your platform**: ESP32 (Arduino or MicroPython) or Raspberry Pi Pico
2. **Read the docs**:
   - ESP32 Arduino: [arduino/README.md](arduino/README.md)
   - ESP32 MicroPython: [README_ESP32.md](README_ESP32.md)
   - Pico: Check CircuitPython documentation
3. **Gather hardware**: See requirements above
4. **Follow the guide**: Use the quick start or detailed setup
5. **Enjoy your Wiener Uhr!** 🎉

## 🎨 Customization

### Change Backgrounds
Replace the `*_8bit.bmp` files with your own 64x64, 8-bit indexed BMP images.

### Modify Time Phrases
Edit the time logic in:
- Arduino: `wiener_zeit.cpp`
- MicroPython: `main_esp32.py`
- CircuitPython: `main.py`

### Adjust Brightness
Edit brightness values in:
- Arduino: `config.h`
- ESP32 MicroPython: `config_esp32.py`
- Pico: `settings.toml`

### Use Different Fonts
Add BDF font files to the `fonts/` directory and update configuration.

## 🔍 Platform Comparison

| Feature | ESP32 (Arduino) | ESP32 (MicroPython) | Raspberry Pi Pico |
|---------|-----------------|---------------------|-------------------|
| Language | C++ | Python | Python |
| Display Performance | Excellent | Good (software) | Excellent (PIO) |
| Color Depth | 6-bit (64 colors) | 1-bit (upgradable) | 6-bit (64 colors) |
| Wi-Fi | ✅ Yes | ✅ Yes | ❌ No |
| Bluetooth | ✅ Yes | ✅ Yes | ❌ No |
| Setup Difficulty | Easy | Moderate | Moderate |
| Development Speed | Fast (compiled) | Medium (interpreted) | Medium (interpreted) |
| Cost | ~$6-10 | ~$6-10 | ~$4-6 |
| Power Usage | Higher | Higher | Lower |
| CPU Power | Dual 240MHz | Dual 240MHz | Dual 133MHz |
| RAM | 520KB | 520KB | 264KB |

## 📖 Documentation

### Arduino Version:
- [arduino/README.md](arduino/README.md) - Complete Arduino setup and documentation
- [arduino/QUICK_START_ARDUINO.md](arduino/QUICK_START_ARDUINO.md) - Quick Arduino setup guide

### MicroPython Version:
- [README_ESP32.md](README_ESP32.md) - Complete ESP32 MicroPython documentation
- [QUICK_START_ESP32.md](QUICK_START_ESP32.md) - Quick 5-step ESP32 setup
- [ESP32_PORT_SUMMARY.md](ESP32_PORT_SUMMARY.md) - Detailed platform comparison
- [ESP32_CHECKLIST.md](ESP32_CHECKLIST.md) - Complete installation checklist

## 🐛 Troubleshooting

### Common Issues:

**Display not working?**
- Check power supply (5V, adequate current)
- Verify all pin connections
- Check ground connections

**RTC time wrong?**
- Install CR2032 battery
- Set time via REPL
- Verify clock is running

**Out of memory?**
- Remove unused BMP files
- Use default font instead of BDF
- Reduce image sizes

See platform-specific documentation for more troubleshooting tips.

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Share your custom backgrounds or fonts

## 📄 License

This project is released under the MIT License.

## 🙏 Acknowledgments

- Viennese culture for the unique time-telling tradition
- Arduino community and ecosystem
- Adafruit for CircuitPython libraries and HUB75 library
- MicroPython community
- HUB75 LED matrix community

## 📧 Support

- **Issues**: Open an issue on GitHub
- **Questions**: Check the documentation first
- **Arduino specific**: See [arduino/README.md](arduino/README.md)
- **ESP32 MicroPython specific**: See [README_ESP32.md](README_ESP32.md)

---

**Viel Spaß mit deiner Wiener Uhr!** 🕐🇦🇹

*Made with ❤️ for Vienna's timeless tradition*
