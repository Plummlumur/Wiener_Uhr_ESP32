"""
DS1302 RTC Helper Functions
============================
High-level utility functions for working with the DS1302 Real-Time Clock.

Hardware Connection (3-wire serial):
- DS1302 VCC -> Pico 3.3V or 5V (Pin 36 for 3.3V)
- DS1302 GND -> Pico GND (Pin 38 or any GND)
- DS1302 CLK -> Pico GP6 (or any available GPIO)
- DS1302 DAT -> Pico GP7 (or any available GPIO)
- DS1302 CE/RST -> Pico GP14 (or any available GPIO)
"""

import board
import time
from ds1302 import DS1302


class DS1302Helper:
    """Helper class for DS1302 RTC operations"""

    def __init__(self, clk_pin=board.GP6, dat_pin=board.GP7, ce_pin=board.GP14):
        """
        Initialize the DS1302 RTC

        Args:
            clk_pin: GPIO pin for CLK (default: GP6)
            dat_pin: GPIO pin for DAT (default: GP7)
            ce_pin: GPIO pin for CE/RST (default: GP14)
        """
        self.rtc = DS1302(clk_pin, dat_pin, ce_pin)

        # Ensure clock is running
        if self.rtc.is_halted():
            print("WARNING: RTC clock is halted. Starting clock...")
            self.rtc.halt(False)

        # Disable trickle charge by default (safe for CR2032)
        self.rtc.disable_trickle_charge()

    def set_time(self, year, month, day, hour, minute, second):
        """
        Set the RTC time

        Args:
            year: Year (2000-2099, e.g., 2025)
            month: Month (1-12)
            day: Day (1-31)
            hour: Hour (0-23)
            minute: Minute (0-59)
            second: Second (0-59)

        Example:
            rtc.set_time(2025, 10, 18, 14, 30, 0)  # October 18, 2025, 2:30:00 PM
        """
        self.rtc.set_datetime(year, month, day, hour, minute, second)
        print(f"Time set to: {self.get_formatted_datetime()}")

    def set_time_from_struct(self, time_struct):
        """
        Set the RTC time from a time.struct_time object

        Args:
            time_struct: time.struct_time object
        """
        self.rtc.set_datetime(
            time_struct.tm_year,
            time_struct.tm_mon,
            time_struct.tm_mday,
            time_struct.tm_hour,
            time_struct.tm_min,
            time_struct.tm_sec
        )
        print(f"Time set to: {self.get_formatted_datetime()}")

    def get_datetime(self):
        """
        Get the current date and time as a struct_time object

        Returns:
            time.struct_time: Current date and time
        """
        return self.rtc.get_datetime()

    def get_formatted_datetime(self, format_str="default"):
        """
        Get formatted date and time string

        Args:
            format_str: Format type
                - "default": "YYYY-MM-DD HH:MM:SS"
                - "date": "YYYY-MM-DD"
                - "time": "HH:MM:SS"
                - "german_date": "DD.MM.YYYY"
                - "german_datetime": "DD.MM.YYYY HH:MM:SS"
                - "time_12h": "HH:MM:SS AM/PM"

        Returns:
            str: Formatted date/time string
        """
        current_time = self.rtc.get_datetime()
        year = current_time.tm_year
        month = current_time.tm_mon
        day = current_time.tm_mday
        hour = current_time.tm_hour
        minute = current_time.tm_min
        second = current_time.tm_sec

        if format_str == "default":
            return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
        elif format_str == "date":
            return f"{year:04d}-{month:02d}-{day:02d}"
        elif format_str == "time":
            return f"{hour:02d}:{minute:02d}:{second:02d}"
        elif format_str == "german_date":
            return f"{day:02d}.{month:02d}.{year:04d}"
        elif format_str == "german_datetime":
            return f"{day:02d}.{month:02d}.{year:04d} {hour:02d}:{minute:02d}:{second:02d}"
        elif format_str == "time_12h":
            am_pm = "AM" if hour < 12 else "PM"
            hour_12 = hour % 12
            if hour_12 == 0:
                hour_12 = 12
            return f"{hour_12:02d}:{minute:02d}:{second:02d} {am_pm}"
        else:
            return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"

    def get_time_components(self):
        """
        Get individual time components

        Returns:
            dict: Dictionary with year, month, day, hour, minute, second, weekday
        """
        return self.rtc.get_time_components()

    def get_weekday_name(self, language="en"):
        """
        Get the name of the current weekday

        Args:
            language: "en" for English, "de" for German

        Returns:
            str: Name of the weekday
        """
        weekday = self.rtc.get_datetime().tm_wday

        if language == "de":
            days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        else:
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        return days[weekday]

    def get_month_name(self, language="en"):
        """
        Get the name of the current month

        Args:
            language: "en" for English, "de" for German

        Returns:
            str: Name of the month
        """
        month = self.rtc.get_datetime().tm_mon

        if language == "de":
            months = ["", "Januar", "Februar", "März", "April", "Mai", "Juni",
                     "Juli", "August", "September", "Oktober", "November", "Dezember"]
        else:
            months = ["", "January", "February", "March", "April", "May", "June",
                     "July", "August", "September", "October", "November", "December"]

        return months[month]

    def is_running(self):
        """
        Check if the RTC clock is running

        Returns:
            bool: True if running, False if halted
        """
        return not self.rtc.is_halted()

    def start_clock(self):
        """Start the RTC clock if halted"""
        self.rtc.halt(False)
        print("RTC clock started")

    def stop_clock(self):
        """Stop the RTC clock"""
        self.rtc.halt(True)
        print("RTC clock stopped")


# Standalone helper functions for quick use
def initialize_rtc(clk_pin=board.GP6, dat_pin=board.GP7, ce_pin=board.GP14):
    """
    Quick initialization of DS1302 RTC

    Args:
        clk_pin: GPIO pin for CLK (default: GP6)
        dat_pin: GPIO pin for DAT (default: GP7)
        ce_pin: GPIO pin for CE/RST (default: GP14)

    Returns:
        DS1302Helper: Initialized RTC helper object
    """
    return DS1302Helper(clk_pin, dat_pin, ce_pin)


def print_current_time(rtc_helper):
    """
    Print the current time to console

    Args:
        rtc_helper: DS1302Helper instance
    """
    print("Current Date/Time:", rtc_helper.get_formatted_datetime())
    print("German format:", rtc_helper.get_formatted_datetime("german_datetime"))
    print("Weekday:", rtc_helper.get_weekday_name("de"))
    print("Month:", rtc_helper.get_month_name("de"))
    print("Clock running:", rtc_helper.is_running())
