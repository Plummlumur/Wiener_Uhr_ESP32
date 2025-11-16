"""
DS1302 RTC Driver for MicroPython on ESP32
===========================================
Driver for the DS1302 Real-Time Clock module using 3-wire serial interface.

The DS1302 is a low-cost RTC that uses a simple 3-wire serial interface (not I2C).
It requires 3 GPIO pins: CLK (clock), DAT (data), and CE/RST (chip enable).

Hardware Connection:
- DS1302 VCC -> ESP32 3.3V
- DS1302 GND -> ESP32 GND
- DS1302 CLK -> ESP32 GPIO (defined in config)
- DS1302 DAT -> ESP32 GPIO (defined in config)
- DS1302 CE/RST -> ESP32 GPIO (defined in config)
"""

import time
from machine import Pin


class DS1302:
    """
    Driver for DS1302 Real-Time Clock on ESP32

    The DS1302 uses a 3-wire serial interface with the following pins:
    - CLK: Serial clock input
    - DAT: Serial data I/O (bidirectional)
    - CE/RST: Chip Enable (active high)
    """

    # Register addresses (with read bit set to 0, write bit set to 0)
    REG_SECONDS = 0x80
    REG_MINUTES = 0x82
    REG_HOURS = 0x84
    REG_DATE = 0x86
    REG_MONTH = 0x88
    REG_DAY = 0x8A
    REG_YEAR = 0x8C
    REG_WP = 0x8E  # Write protect register
    REG_TRICKLE = 0x90  # Trickle charge register

    def __init__(self, clk_pin, dat_pin, ce_pin):
        """
        Initialize DS1302

        Args:
            clk_pin: GPIO pin number for CLK (e.g., 18)
            dat_pin: GPIO pin number for DAT (e.g., 21)
            ce_pin: GPIO pin number for CE/RST (e.g., 32)
        """
        self.clk = Pin(clk_pin, Pin.OUT)
        self.dat = Pin(dat_pin, Pin.OUT)
        self.ce = Pin(ce_pin, Pin.OUT)

        self.clk.value(0)
        self.ce.value(0)

    def _set_dat_output(self):
        """Set DAT pin as output"""
        self.dat.init(Pin.OUT)

    def _set_dat_input(self):
        """Set DAT pin as input"""
        self.dat.init(Pin.IN)

    def _write_byte(self, byte_value):
        """
        Write a byte to the DS1302 (LSB first)

        Args:
            byte_value: Byte to write (0-255)
        """
        self._set_dat_output()
        for i in range(8):
            self.dat.value((byte_value >> i) & 0x01)
            self.clk.value(1)
            self.clk.value(0)

    def _read_byte(self):
        """
        Read a byte from the DS1302 (LSB first)

        Returns:
            int: Byte read (0-255)
        """
        self._set_dat_input()
        byte_value = 0
        for i in range(8):
            bit = 1 if self.dat.value() else 0
            byte_value |= (bit << i)
            self.clk.value(1)
            self.clk.value(0)
        return byte_value

    def _write_register(self, register, value):
        """
        Write a value to a register

        Args:
            register: Register address
            value: Value to write (0-255)
        """
        self.ce.value(1)
        self._write_byte(register)
        self._write_byte(value)
        self.ce.value(0)

    def _read_register(self, register):
        """
        Read a value from a register

        Args:
            register: Register address

        Returns:
            int: Value read (0-255)
        """
        self.ce.value(1)
        self._write_byte(register | 0x01)  # Set read bit
        value = self._read_byte()
        self.ce.value(0)
        return value

    def _bcd_to_dec(self, bcd):
        """Convert BCD to decimal"""
        return ((bcd >> 4) * 10) + (bcd & 0x0F)

    def _dec_to_bcd(self, dec):
        """Convert decimal to BCD"""
        return ((dec // 10) << 4) | (dec % 10)

    def _disable_write_protect(self):
        """Disable write protection"""
        self._write_register(self.REG_WP, 0x00)

    def _enable_write_protect(self):
        """Enable write protection"""
        self._write_register(self.REG_WP, 0x80)

    def halt(self, halted=True):
        """
        Halt or resume the clock

        Args:
            halted: True to halt, False to resume
        """
        seconds = self._read_register(self.REG_SECONDS)
        if halted:
            seconds |= 0x80  # Set CH (Clock Halt) bit
        else:
            seconds &= 0x7F  # Clear CH bit
        self._disable_write_protect()
        self._write_register(self.REG_SECONDS, seconds)
        self._enable_write_protect()

    def is_halted(self):
        """
        Check if clock is halted

        Returns:
            bool: True if halted
        """
        seconds = self._read_register(self.REG_SECONDS)
        return (seconds & 0x80) != 0

    def set_datetime(self, year, month, day, hour, minute, second, weekday=None):
        """
        Set date and time

        Args:
            year: Year (2000-2099, e.g., 2025)
            month: Month (1-12)
            day: Day (1-31)
            hour: Hour (0-23)
            minute: Minute (0-59)
            second: Second (0-59)
            weekday: Day of week (1-7, Monday=1, optional)
        """
        # Calculate weekday if not provided (Zeller's congruence)
        if weekday is None:
            _month = month
            _year = year
            if _month < 3:
                _month += 12
                _year -= 1
            q = day
            m = _month
            k = _year % 100
            j = _year // 100
            h = (q + ((13 * (m + 1)) // 5) + k + (k // 4) + (j // 4) - (2 * j)) % 7
            weekday = ((h + 5) % 7) + 1  # Convert to 1=Monday format

        self._disable_write_protect()

        # Write registers (year is 0-99 for 2000-2099)
        year_bcd = year - 2000 if year >= 2000 else year
        self._write_register(self.REG_SECONDS, self._dec_to_bcd(second) & 0x7F)  # Clear CH bit
        self._write_register(self.REG_MINUTES, self._dec_to_bcd(minute))
        self._write_register(self.REG_HOURS, self._dec_to_bcd(hour) & 0x3F)  # 24-hour mode
        self._write_register(self.REG_DATE, self._dec_to_bcd(day))
        self._write_register(self.REG_MONTH, self._dec_to_bcd(month))
        self._write_register(self.REG_DAY, self._dec_to_bcd(weekday))
        self._write_register(self.REG_YEAR, self._dec_to_bcd(year_bcd))

        self._enable_write_protect()

    def get_datetime(self):
        """
        Get current date and time

        Returns:
            tuple: (year, month, day, hour, minute, second, weekday, yearday)
        """
        # Read all registers
        seconds = self._bcd_to_dec(self._read_register(self.REG_SECONDS) & 0x7F)
        minutes = self._bcd_to_dec(self._read_register(self.REG_MINUTES))
        hours = self._bcd_to_dec(self._read_register(self.REG_HOURS) & 0x3F)
        day = self._bcd_to_dec(self._read_register(self.REG_DATE))
        month = self._bcd_to_dec(self._read_register(self.REG_MONTH))
        weekday = self._bcd_to_dec(self._read_register(self.REG_DAY)) - 1  # 0=Monday
        year = self._bcd_to_dec(self._read_register(self.REG_YEAR)) + 2000

        # Calculate day of year
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        if is_leap:
            days_in_month[1] = 29
        yday = sum(days_in_month[:month - 1]) + day

        return (year, month, day, hours, minutes, seconds, weekday, yday)

    def get_time_components(self):
        """
        Get individual time components

        Returns:
            dict: Dictionary with year, month, day, hour, minute, second, weekday
        """
        dt = self.get_datetime()
        return {
            "year": dt[0],
            "month": dt[1],
            "day": dt[2],
            "hour": dt[3],
            "minute": dt[4],
            "second": dt[5],
            "weekday": dt[6]  # 0=Monday, 6=Sunday
        }

    def enable_trickle_charge(self, diodes=1, resistor=2):
        """
        Enable trickle charge for backup battery/supercap

        Args:
            diodes: Number of diodes (1 or 2)
            resistor: Resistor selection (0=none, 1=2kΩ, 2=4kΩ, 3=8kΩ)

        WARNING: Only use if you have a rechargeable battery or supercapacitor!
        Do NOT use with non-rechargeable CR2032 battery!
        """
        tcs = 0xA0  # Enable trickle charge
        if diodes == 1:
            tcs |= 0x04
        elif diodes == 2:
            tcs |= 0x08
        tcs |= (resistor & 0x03)

        self._disable_write_protect()
        self._write_register(self.REG_TRICKLE, tcs)
        self._enable_write_protect()

    def disable_trickle_charge(self):
        """Disable trickle charge (safe for CR2032 batteries)"""
        self._disable_write_protect()
        self._write_register(self.REG_TRICKLE, 0x00)
        self._enable_write_protect()


class DS1302Helper:
    """Helper class for DS1302 RTC operations on ESP32"""

    def __init__(self, clk_pin=18, dat_pin=21, ce_pin=32):
        """
        Initialize the DS1302 RTC

        Args:
            clk_pin: GPIO pin for CLK (default: 18)
            dat_pin: GPIO pin for DAT (default: 21)
            ce_pin: GPIO pin for CE/RST (default: 32)
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
            rtc.set_time(2025, 11, 16, 14, 30, 0)  # November 16, 2025, 2:30:00 PM
        """
        self.rtc.set_datetime(year, month, day, hour, minute, second)
        print(f"Time set to: {self.get_formatted_datetime()}")

    def get_datetime(self):
        """
        Get the current date and time

        Returns:
            tuple: (year, month, day, hour, minute, second, weekday, yearday)
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
        dt = self.rtc.get_datetime()
        year, month, day, hour, minute, second = dt[0], dt[1], dt[2], dt[3], dt[4], dt[5]

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
        weekday = self.rtc.get_datetime()[6]

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
        month = self.rtc.get_datetime()[1]

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
