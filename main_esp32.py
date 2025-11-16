"""
Wiener Uhr (Viennese Clock) - ESP32 Version
============================================
Displays time in Viennese German dialect on a 64x64 RGB LED matrix.

Hardware Requirements:
- ESP32-WROOM32 board
- 64x64 HUB75 RGB LED Matrix
- DS1302 Real-Time Clock module
- 5V power supply (for LED matrix)

Author: Ported to ESP32 MicroPython
"""

import time
import random
from machine import Pin
from config_esp32 import (
    RGB_MATRIX_PINS,
    DS1302_PINS,
    DISPLAY_CONFIG,
    TIME_CONFIG,
    FONT_CONFIG,
    BACKGROUND_CONFIG,
    MONTH_NAMES,
    MATRIX_WIDTH,
    MATRIX_HEIGHT,
    WIFI_CONFIG,
    NTP_CONFIG
)
from hub75_esp32 import HUB75Matrix
from display_api import RGB_Api, DisplayManager
from ds1302_esp32 import DS1302Helper
from bdf_font import load_font
from wifi_time import WiFiTimeManager


# --------------------------------------------------------------
# Hilfsfunktionen (Helper Functions)
# --------------------------------------------------------------

def returnWienerZeit(Stunde, Minute):
    """
    Convert time to Viennese German time format

    Args:
        Stunde: Hour (0-23)
        Minute: Minute (0-59)

    Returns:
        tuple: (bezeichner, bezeichner2, volleStunde)
    """
    hourOffset = 0
    bezeichner = ""
    bezeichner2 = ""

    minutenInWorten = [
        "", "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben",
        "acht", "neun", "zehn", "elf", "zwölf", "dreizehn", "vierzehn"
    ]

    # Gimmick: Bei 10, 20, 40, 50 Minuten zufällig alternative Formulierung
    random.seed(Stunde * 100 + Minute)
    useAlternative = random.choice([True, False])

    if Minute == 0:
        bezeichner = "punkt"
        bezeichner2 = ""
    elif Minute == 10 and useAlternative:
        # Alternative: "zehn nach" statt "fünf vor viertel"
        bezeichner = "zehn nach "
        bezeichner2 = ""
        hourOffset = 0
    elif Minute == 20 and useAlternative:
        # Alternative: "zehn vor halb" statt "fünf nach viertel"
        bezeichner = "zehn vor "
        bezeichner2 = "halb"
        hourOffset = 1
    elif Minute == 40 and useAlternative:
        # Alternative: "zehn nach halb" statt "fünf vor dreiviertel"
        bezeichner = "zehn nach "
        bezeichner2 = "halb"
        hourOffset = 1
    elif Minute == 50 and useAlternative:
        # Alternative: "zehn vor" statt "fünf nach dreiviertel"
        bezeichner = "zehn vor"
        bezeichner2 = ""
        hourOffset = 1
    elif Minute < 15:
        if Minute < 7:
            bezeichner = minutenInWorten[Minute] + " nach "
            bezeichner2 = ""
            hourOffset = 0
        else:
            minutenAnzahl = 15 - Minute
            bezeichner = minutenInWorten[minutenAnzahl] + " vor "
            bezeichner2 = "viertel"
            hourOffset = 1
    elif Minute == 15:
        bezeichner = "viertel"
        bezeichner2 = ""
        hourOffset = 1
    elif 15 < Minute < 30:
        if Minute < 23:
            minutenAnzahl = Minute - 15
            bezeichner = minutenInWorten[minutenAnzahl] + " nach "
            bezeichner2 = "viertel"
            hourOffset = 1
        else:
            minutenAnzahl = 30 - Minute
            bezeichner = minutenInWorten[minutenAnzahl] + " vor "
            bezeichner2 = "halb"
            hourOffset = 1
    elif Minute == 30:
        bezeichner = "halb"
        bezeichner2 = ""
        hourOffset = 1
    elif 30 < Minute < 45:
        if Minute < 38:
            minutenAnzahl = Minute - 30
            bezeichner = minutenInWorten[minutenAnzahl] + " nach "
            bezeichner2 = "halb"
            hourOffset = 1
        else:
            minutenAnzahl = 45 - Minute
            bezeichner = minutenInWorten[minutenAnzahl] + " vor "
            bezeichner2 = "dreiviertel"
            hourOffset = 1
    elif Minute == 45:
        bezeichner = "dreiviertel"
        bezeichner2 = ""
        hourOffset = 1
    else:  # Minute > 45
        if Minute < 53:
            minutenAnzahl = Minute - 45
            bezeichner = minutenInWorten[minutenAnzahl] + " nach "
            bezeichner2 = "dreiviertel"
            hourOffset = 1
        else:
            minutenAnzahl = 60 - Minute
            bezeichner = minutenInWorten[minutenAnzahl] + " vor"
            bezeichner2 = ""
            hourOffset = 1

    volleStunde = (Stunde + hourOffset)
    volleStundeAusgeschrieben = [
        "Eins", "Zwei", "Drei", "Vier", "Fünf", "Sechs", "Sieben",
        "Acht", "Neun", "Zehn", "Elf", "Zwölf",
        "Eins", "Zwei", "Drei", "Vier", "Fünf", "Sechs",
        "Sieben", "Acht", "Neun", "Zehn", "Elf", "Zwölf"
    ]

    return bezeichner, bezeichner2, volleStundeAusgeschrieben[volleStunde - 1]


def monatsHintergrund(month, rgb):
    """
    Load monthly background image

    Args:
        month: Month number (1-12)
        rgb: RGB_Api instance
    """
    if 1 <= month <= 12:
        month_name = MONTH_NAMES[month - 1]
        path = BACKGROUND_CONFIG['image_path'] + BACKGROUND_CONFIG['image_pattern'].format(month=month_name)
        rgb.load_background(path)


# --------------------------------------------------------------
# Hardware & Display Setup
# --------------------------------------------------------------

def setup_hardware():
    """Initialize all hardware components"""
    print("=" * 50)
    print("Wiener Uhr - ESP32 Version")
    print("=" * 50)

    # Initialize WiFi Time Manager
    print("Initializing WiFi Time Manager...")
    wifi_time = WiFiTimeManager(WIFI_CONFIG, NTP_CONFIG)

    # Try to connect to WiFi if enabled
    if WIFI_CONFIG.get('enabled', False):
        if wifi_time.connect_wifi():
            # Attempt initial NTP sync
            wifi_time.sync_ntp()
        else:
            print("WiFi connection failed, will use DS1302 RTC only")
    else:
        print("WiFi disabled, using DS1302 RTC only")

    # Initialize RTC (always initialize as fallback)
    print("Initializing DS1302 RTC...")
    rtc = DS1302Helper(
        clk_pin=DS1302_PINS['CLK'],
        dat_pin=DS1302_PINS['DAT'],
        ce_pin=DS1302_PINS['CE']
    )
    print(f"RTC initialized. Current time: {rtc.get_formatted_datetime()}")

    # Sync RTC with NTP if WiFi is connected and sync_rtc is enabled
    if wifi_time.is_connected() and NTP_CONFIG.get('sync_rtc', False):
        print("Syncing DS1302 RTC with NTP time...")
        wifi_time.sync_rtc_from_ntp(rtc)

    # Uncomment to manually set time (example):
    # rtc.set_time(2025, 11, 16, 14, 30, 0)

    # Print WiFi & NTP status
    wifi_time.print_status()

    # Initialize RGB Matrix
    print("Initializing RGB Matrix...")
    matrix = HUB75Matrix(MATRIX_WIDTH, MATRIX_HEIGHT, RGB_MATRIX_PINS)
    print(f"Matrix initialized: {MATRIX_WIDTH}x{MATRIX_HEIGHT}")

    # Initialize Display Manager
    print("Initializing Display Manager...")
    display_manager = DisplayManager(matrix, refresh_rate=100)
    display_manager.start()

    # Initialize Graphics API
    print("Initializing Graphics API...")
    rgb = RGB_Api(matrix, MATRIX_WIDTH, MATRIX_HEIGHT)

    # Load font
    print("Loading font...")
    try:
        font_path = FONT_CONFIG['font_path']
        rgb.txt_font = load_font(font_path)
        print(f"Font loaded: {font_path}")
    except Exception as e:
        print(f"Font loading failed: {e}")
        print("Using default font")

    # Configure text settings
    rgb.txt_color = DISPLAY_CONFIG['text_color']
    rgb.txt_scale = DISPLAY_CONFIG['text_scale']
    rgb.line_spacing = DISPLAY_CONFIG['line_spacing']
    rgb.txt_x = DISPLAY_CONFIG['text_x']
    rgb.txt_y = DISPLAY_CONFIG['text_y']

    print("Hardware setup complete!")
    print("=" * 50)

    return rtc, matrix, display_manager, rgb, wifi_time


# --------------------------------------------------------------
# Main Program
# --------------------------------------------------------------

def main():
    """Main program loop"""
    # Setup hardware
    rtc, matrix, display_manager, rgb, wifi_time = setup_hardware()

    # State tracking
    buffer = None
    last_update_time = 0
    last_ntp_check_time = 0
    refresh_counter = 0

    print("Starting main loop...")

    while True:
        # Refresh display (non-blocking, call frequently)
        display_manager.update()
        refresh_counter += 1

        # Periodic NTP sync check (every 60 seconds)
        current_tick = time.ticks_ms()
        if time.ticks_diff(current_tick, last_ntp_check_time) >= 60000:
            last_ntp_check_time = current_tick

            # Check if NTP sync is needed
            if wifi_time.should_sync():
                print("Performing periodic NTP sync...")
                if wifi_time.sync_ntp():
                    # Sync RTC if configured
                    if NTP_CONFIG.get('sync_rtc', False):
                        wifi_time.sync_rtc_from_ntp(rtc)

        # Check if it's time to update the clock (every second, but only update text when needed)
        if time.ticks_diff(current_tick, last_update_time) >= 1000:
            last_update_time = current_tick

            # Get current time - use WiFi/NTP if available, otherwise use DS1302 RTC
            if wifi_time.is_connected() and NTP_CONFIG.get('enabled', False):
                comp = wifi_time.get_time_components()
                time_source = "NTP"
            else:
                comp = rtc.get_time_components()
                time_source = "RTC"

            Stunde = comp["hour"]
            Minute = comp["minute"]
            Monat = comp["month"]

            # Determine Viennese time
            bezeichner, bezeichner2, volleStunde = returnWienerZeit(Stunde, Minute)

            # Assemble text content
            if len(bezeichner2) > 2:
                txt_lines = ["Es ist", bezeichner, bezeichner2, volleStunde]
            else:
                txt_lines = ["Es ist", bezeichner, volleStunde]

            # Only update if text has changed
            if txt_lines != buffer:
                print(f"Updating display [{time_source}]: {' '.join(txt_lines)}")

                # Load monthly background
                if BACKGROUND_CONFIG['use_monthly_backgrounds']:
                    monatsHintergrund(Monat, rgb)

                # Apply brightness based on time of day
                night_start = TIME_CONFIG['night_start_hour']
                night_end = TIME_CONFIG['night_end_hour']

                if Stunde >= night_start or Stunde < night_end:
                    # Night mode
                    rgb.set_brightness(DISPLAY_CONFIG['brightness_night'])
                else:
                    # Day mode
                    rgb.set_brightness(DISPLAY_CONFIG['brightness_day'])

                # Update text lines
                rgb.txt_lines = txt_lines
                rgb.update_text()

                buffer = txt_lines

                # Force some display refreshes after update
                for _ in range(50):
                    matrix.refresh()

        # Small delay to prevent CPU overload
        time.sleep_ms(1)


# --------------------------------------------------------------
# Entry Point
# --------------------------------------------------------------

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
        import sys
        sys.print_exception(e)
