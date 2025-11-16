# ESP32 Port - Complete Checklist

## ✅ Pre-Installation Checklist

### Hardware
- [ ] ESP32-WROOM32 development board
- [ ] 64x64 HUB75 RGB LED matrix panel
- [ ] DS1302 RTC module
- [ ] CR2032 battery for RTC
- [ ] 5V power supply (4-8A minimum)
- [ ] USB cable for ESP32
- [ ] Jumper wires (male-to-female, ~30 pieces)
- [ ] Breadboard (optional)
- [ ] Level shifters 74HCT245 (optional but recommended)

### Software Tools
- [ ] Python 3.x installed
- [ ] `esptool` installed (`pip install esptool`)
- [ ] `ampy` or `mpremote` installed (`pip install adafruit-ampy`)
- [ ] MicroPython firmware downloaded (esp32-*.bin)
- [ ] Serial terminal (screen, minicom, or Thonny)

### Files Required

#### ESP32 Python Files
- [ ] `boot.py` - Boot configuration
- [ ] `main_esp32.py` - Main application
- [ ] `config_esp32.py` - Configuration
- [ ] `ds1302_esp32.py` - RTC driver
- [ ] `hub75_esp32.py` - Matrix driver
- [ ] `display_api.py` - Display API
- [ ] `bmp_loader.py` - Image loader
- [ ] `bdf_font.py` - Font renderer

#### Asset Files
- [ ] `januar_8bit.bmp`
- [ ] `februar_8bit.bmp`
- [ ] `maerz_8bit.bmp`
- [ ] `april_8bit.bmp`
- [ ] `mai_8bit.bmp`
- [ ] `juni_8bit.bmp`
- [ ] `juli_8bit.bmp`
- [ ] `august_8bit.bmp`
- [ ] `september_8bit.bmp` (if exists)
- [ ] `oktober_8bit.bmp`
- [ ] `november_8bit.bmp`
- [ ] `dezember_8bit.bmp`
- [ ] `lib/fonts/helvR12.bdf` - Font file

## ✅ Wiring Checklist

### RGB Matrix Connections
- [ ] R1 → GPIO 25
- [ ] G1 → GPIO 26
- [ ] B1 → GPIO 27
- [ ] R2 → GPIO 14
- [ ] G2 → GPIO 12 (note: strapping pin!)
- [ ] B2 → GPIO 13
- [ ] A → GPIO 23
- [ ] B → GPIO 19
- [ ] C → GPIO 5
- [ ] D → GPIO 17
- [ ] E → GPIO 16
- [ ] CLK → GPIO 22
- [ ] LAT → GPIO 4
- [ ] OE → GPIO 15
- [ ] GND → ESP32 GND

### DS1302 RTC Connections
- [ ] VCC → ESP32 3.3V
- [ ] GND → ESP32 GND
- [ ] CLK → GPIO 18
- [ ] DAT → GPIO 21
- [ ] CE → GPIO 32
- [ ] CR2032 battery installed in RTC module

### Power Connections
- [ ] 5V power supply connected to matrix power connector
- [ ] ESP32 powered (USB or VIN pin)
- [ ] All grounds connected together
- [ ] Power supply rated for at least 4A

### Safety Checks
- [ ] No short circuits visible
- [ ] Polarity correct on all connections
- [ ] GPIO 12 will be LOW at boot (matrix off initially)
- [ ] Wires not loose or touching

## ✅ Software Installation Checklist

### 1. Flash MicroPython
- [ ] ESP32 connected via USB
- [ ] Port identified (e.g., /dev/ttyUSB0 or COM3)
- [ ] Flash erased: `esptool.py --port PORT erase_flash`
- [ ] MicroPython flashed: `esptool.py --chip esp32 --port PORT write_flash -z 0x1000 firmware.bin`
- [ ] ESP32 reboots successfully
- [ ] REPL accessible via serial terminal

### 2. File Upload
- [ ] All Python files uploaded
- [ ] `main_esp32.py` renamed to `main.py`
- [ ] `/fonts` directory created
- [ ] Font file uploaded to `/fonts/helvR12.bdf`
- [ ] All 12 month BMP files uploaded
- [ ] File upload verified with `ampy ls`

### 3. Configuration
- [ ] `config_esp32.py` pins match your wiring
- [ ] Brightness settings adjusted
- [ ] Night mode hours configured
- [ ] RTC pin configuration correct

### 4. RTC Setup
- [ ] Connected to REPL
- [ ] Imported DS1302Helper
- [ ] Current time set correctly
- [ ] Time verified with `get_formatted_datetime()`
- [ ] Clock running verified with `is_running()`

### 5. First Boot
- [ ] ESP32 reset/rebooted
- [ ] Boot messages appear in serial
- [ ] "Wiener Uhr - ESP32 Version" banner visible
- [ ] Hardware initialization messages shown
- [ ] No error messages
- [ ] Main loop started

## ✅ Functional Testing

### Display Tests
- [ ] Matrix powers on
- [ ] Background image loads
- [ ] Text appears on display
- [ ] Text is readable
- [ ] Colors look correct
- [ ] No excessive flickering
- [ ] Display refreshes smoothly

### Time Display Tests
- [ ] Time shown in Viennese format
- [ ] "Es ist" appears
- [ ] Hour and minute words correct
- [ ] Updates every minute
- [ ] Matches RTC time

### Brightness Tests
- [ ] Day mode brightness appropriate
- [ ] Night mode brightness lower
- [ ] Transitions at configured hours
- [ ] Manual brightness adjustment works

### RTC Tests
- [ ] Time keeps running
- [ ] Time persists after power cycle (with battery)
- [ ] Time updates correctly
- [ ] Month detection correct
- [ ] Correct monthly background loads

## ✅ Optimization Checklist

### Performance
- [ ] Display refresh rate acceptable (minimal flicker)
- [ ] No lag in time updates
- [ ] Memory usage checked (`gc.mem_free()`)
- [ ] CPU not overheating
- [ ] Power consumption reasonable

### Fine-Tuning
- [ ] Brightness adjusted to preference
- [ ] Text position optimal
- [ ] Font size appropriate
- [ ] Background images look good
- [ ] Night mode hours set correctly

## ✅ Documentation Review

- [ ] Read README_ESP32.md
- [ ] Reviewed QUICK_START_ESP32.md
- [ ] Understood ESP32_PORT_SUMMARY.md
- [ ] Troubleshooting section reviewed
- [ ] Pin mapping confirmed
- [ ] Configuration options understood

## ✅ Troubleshooting Completed

If you encountered issues, check these:

### Display Issues
- [ ] Power supply adequate
- [ ] All HUB75 pins connected
- [ ] Ground connections solid
- [ ] GPIO 12 not causing boot problems
- [ ] Brightness not set to 0

### RTC Issues
- [ ] Battery installed
- [ ] Connections secure
- [ ] Clock started (not halted)
- [ ] Time set correctly

### Software Issues
- [ ] All files uploaded
- [ ] No import errors
- [ ] Sufficient free memory
- [ ] Correct file paths

## ✅ Advanced Features (Optional)

- [ ] Wi-Fi configured (boot.py)
- [ ] NTP time sync enabled
- [ ] Remote access set up
- [ ] Custom backgrounds created
- [ ] Alternative phrases customized
- [ ] Additional fonts tested

## ✅ Maintenance Schedule

### Daily
- [ ] Verify time is correct
- [ ] Check display is working

### Weekly
- [ ] Check free memory
- [ ] Verify all months' backgrounds still load

### Monthly
- [ ] RTC battery check (if time drifts)
- [ ] Clean dust from matrix
- [ ] Check wire connections

### Yearly
- [ ] Replace RTC battery (CR2032)
- [ ] Update MicroPython firmware
- [ ] Review and update time phrases

## Success Criteria ✨

Your ESP32 Wiener Uhr is fully operational when:

✅ Matrix displays current time in Viennese dialect
✅ Background changes each month automatically
✅ Brightness adjusts for day/night automatically
✅ Time updates every minute precisely
✅ RTC keeps time even after power loss
✅ No error messages in serial output
✅ Display is readable and flicker-free
✅ System runs reliably 24/7

## 🎉 Congratulations!

If all items are checked, your Wiener Uhr ESP32 port is complete!

**Viel Spaß mit deiner Wiener Uhr!** 🕐🇦🇹

---

**Need Help?**
- Hardware issues → Check wiring in ESP32_CHECKLIST.md
- Software issues → See README_ESP32.md Troubleshooting
- Quick fixes → Consult QUICK_START_ESP32.md
