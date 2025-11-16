"""
DS1302 RTC Driver for CircuitPython
====================================
Driver for the DS1302 Real-Time Clock module using 3-wire serial interface.

The DS1302 is a low-cost RTC that uses a simple 3-wire serial interface (not I2C).
It requires 3 GPIO pins: CLK (clock), DAT (data), and CE/RST (chip enable).
"""

import time
from digitalio import DigitalInOut, Direction


class DS1302:
    """
    Driver for DS1302 Real-Time Clock

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
            clk_pin: Board pin for CLK (e.g., board.GP6)
            dat_pin: Board pin for DAT (e.g., board.GP7)
            ce_pin: Board pin for CE/RST (e.g., board.GP14)
        """
        self.clk = DigitalInOut(clk_pin)
        self.dat = DigitalInOut(dat_pin)
        self.ce = DigitalInOut(ce_pin)

        self.clk.direction = Direction.OUTPUT
        self.ce.direction = Direction.OUTPUT

        self.clk.value = False
        self.ce.value = False

    def _set_dat_output(self):
        """Set DAT pin as output"""
        self.dat.direction = Direction.OUTPUT

    def _set_dat_input(self):
        """Set DAT pin as input"""
        self.dat.direction = Direction.INPUT

    def _write_byte(self, byte_value):
        """
        Write a byte to the DS1302 (LSB first)

        Args:
            byte_value: Byte to write (0-255)
        """
        self._set_dat_output()
        for i in range(8):
            self.dat.value = (byte_value >> i) & 0x01
            self.clk.value = True
            self.clk.value = False

    def _read_byte(self):
        """
        Read a byte from the DS1302 (LSB first)

        Returns:
            int: Byte read (0-255)
        """
        self._set_dat_input()
        byte_value = 0
        for i in range(8):
            bit = 1 if self.dat.value else 0
            byte_value |= (bit << i)
            self.clk.value = True
            self.clk.value = False
        return byte_value

    def _write_register(self, register, value):
        """
        Write a value to a register

        Args:
            register: Register address
            value: Value to write (0-255)
        """
        self.ce.value = True
        self._write_byte(register)
        self._write_byte(value)
        self.ce.value = False

    def _read_register(self, register):
        """
        Read a value from a register

        Args:
            register: Register address

        Returns:
            int: Value read (0-255)
        """
        self.ce.value = True
        self._write_byte(register | 0x01)  # Set read bit
        value = self._read_byte()
        self.ce.value = False
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
            if month < 3:
                month += 12
                year -= 1
            q = day
            m = month
            k = year % 100
            j = year // 100
            h = (q + ((13 * (m + 1)) // 5) + k + (k // 4) + (j // 4) - (2 * j)) % 7
            weekday = ((h + 5) % 7) + 1  # Convert to 1=Monday format
            # Restore month/year
            if month > 12:
                month -= 12
                year += 1

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
            time.struct_time: Current date and time
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

        return time.struct_time((year, month, day, hours, minutes, seconds, weekday, yday, -1))

    def get_time_components(self):
        """
        Get individual time components

        Returns:
            dict: Dictionary with year, month, day, hour, minute, second, weekday
        """
        dt = self.get_datetime()
        return {
            "year": dt.tm_year,
            "month": dt.tm_mon,
            "day": dt.tm_mday,
            "hour": dt.tm_hour,
            "minute": dt.tm_min,
            "second": dt.tm_sec,
            "weekday": dt.tm_wday  # 0=Monday, 6=Sunday
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
