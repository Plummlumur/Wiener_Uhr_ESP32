"""
WiFi and NTP Time Module for ESP32
===================================
Handles WiFi connection and NTP time synchronization for the Wiener Uhr.

Features:
- WiFi connection management with auto-reconnect
- NTP time synchronization
- Timezone support
- Fallback to RTC if WiFi is unavailable
- Periodic time synchronization

Author: ESP32 WiFi Module
"""

import network
import time
import ntptime
from machine import RTC


class WiFiTimeManager:
    """
    Manages WiFi connection and NTP time synchronization
    """

    def __init__(self, wifi_config, ntp_config):
        """
        Initialize WiFi Time Manager

        Args:
            wifi_config: Dictionary with WiFi configuration
            ntp_config: Dictionary with NTP configuration
        """
        self.wifi_config = wifi_config
        self.ntp_config = ntp_config
        self.wlan = network.WLAN(network.STA_IF)
        self.rtc = RTC()
        self.connected = False
        self.last_ntp_sync = 0
        self.time_source = "none"  # "ntp", "rtc", or "none"

        # Set NTP server if configured
        if ntp_config.get('server'):
            ntptime.host = ntp_config['server']

    def connect_wifi(self):
        """
        Connect to WiFi network

        Returns:
            bool: True if connected, False otherwise
        """
        if not self.wifi_config.get('enabled', False):
            print("WiFi is disabled in configuration")
            return False

        ssid = self.wifi_config.get('ssid', '')
        password = self.wifi_config.get('password', '')
        timeout = self.wifi_config.get('timeout', 10)

        if ssid == 'YOUR_WIFI_SSID' or not ssid:
            print("WiFi SSID not configured. Please update config_esp32.py")
            return False

        print(f"Connecting to WiFi: {ssid}...")

        # Activate WiFi interface
        self.wlan.active(True)

        # Check if already connected
        if self.wlan.isconnected():
            print(f"Already connected to WiFi")
            print(f"IP address: {self.wlan.ifconfig()[0]}")
            self.connected = True
            return True

        # Connect to network
        self.wlan.connect(ssid, password)

        # Wait for connection
        start_time = time.time()
        while not self.wlan.isconnected():
            if time.time() - start_time > timeout:
                print("WiFi connection timeout")
                self.connected = False
                return False
            time.sleep(0.5)
            print(".", end="")

        print("\nWiFi connected!")
        print(f"IP address: {self.wlan.ifconfig()[0]}")
        print(f"Subnet mask: {self.wlan.ifconfig()[1]}")
        print(f"Gateway: {self.wlan.ifconfig()[2]}")
        print(f"DNS: {self.wlan.ifconfig()[3]}")

        self.connected = True
        return True

    def disconnect_wifi(self):
        """Disconnect from WiFi"""
        if self.wlan.active():
            self.wlan.disconnect()
            self.wlan.active(False)
            self.connected = False
            print("WiFi disconnected")

    def is_connected(self):
        """
        Check if WiFi is connected

        Returns:
            bool: True if connected, False otherwise
        """
        self.connected = self.wlan.isconnected()
        return self.connected

    def sync_ntp(self):
        """
        Synchronize time with NTP server

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.ntp_config.get('enabled', False):
            print("NTP is disabled in configuration")
            return False

        if not self.is_connected():
            print("WiFi not connected, cannot sync NTP")
            return False

        try:
            print(f"Syncing time with NTP server: {self.ntp_config.get('server', 'pool.ntp.org')}...")
            ntptime.settime()

            # Get current time and apply timezone offset
            current_time = time.localtime()
            print(f"NTP time (UTC): {self._format_time(current_time)}")

            # Update last sync time
            self.last_ntp_sync = time.time()
            self.time_source = "ntp"

            print("NTP synchronization successful!")
            return True

        except Exception as e:
            print(f"NTP synchronization failed: {e}")
            return False

    def get_local_time(self):
        """
        Get current local time with timezone offset applied

        Returns:
            tuple: Time tuple (year, month, day, hour, minute, second, weekday, yearday)
        """
        # Get UTC time from RTC
        utc_time = time.localtime()

        # Apply timezone offset
        tz_offset = self.ntp_config.get('timezone_offset', 0)
        dst_offset = self.ntp_config.get('dst_offset', 0)
        total_offset = (tz_offset + dst_offset) * 3600  # Convert to seconds

        # Calculate local time
        local_timestamp = time.mktime(utc_time) + total_offset
        local_time = time.localtime(local_timestamp)

        return local_time

    def get_time_components(self):
        """
        Get time components in a dictionary format (compatible with DS1302Helper)

        Returns:
            dict: Time components with keys: year, month, day, hour, minute, second, weekday
        """
        local_time = self.get_local_time()

        return {
            'year': local_time[0],
            'month': local_time[1],
            'day': local_time[2],
            'hour': local_time[3],
            'minute': local_time[4],
            'second': local_time[5],
            'weekday': local_time[6] + 1,  # Convert 0-6 to 1-7
        }

    def should_sync(self):
        """
        Check if it's time to sync with NTP server

        Returns:
            bool: True if sync is needed, False otherwise
        """
        if not self.ntp_config.get('enabled', False):
            return False

        if not self.is_connected():
            return False

        sync_interval = self.ntp_config.get('sync_interval', 3600)
        current_time = time.time()

        # Sync if never synced or interval has elapsed
        if self.last_ntp_sync == 0 or (current_time - self.last_ntp_sync) >= sync_interval:
            return True

        return False

    def sync_rtc_from_ntp(self, ds1302_rtc):
        """
        Synchronize DS1302 RTC with NTP time

        Args:
            ds1302_rtc: DS1302Helper instance to synchronize

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.ntp_config.get('sync_rtc', False):
            return False

        if not self.is_connected():
            print("WiFi not connected, cannot sync RTC from NTP")
            return False

        try:
            # Sync NTP first
            if self.sync_ntp():
                # Get local time components
                comp = self.get_time_components()

                # Set DS1302 RTC
                ds1302_rtc.set_time(
                    comp['year'],
                    comp['month'],
                    comp['day'],
                    comp['hour'],
                    comp['minute'],
                    comp['second']
                )

                print(f"DS1302 RTC synchronized with NTP time")
                print(f"RTC time: {ds1302_rtc.get_formatted_datetime()}")
                return True
            else:
                return False

        except Exception as e:
            print(f"Failed to sync RTC from NTP: {e}")
            return False

    def _format_time(self, time_tuple):
        """
        Format time tuple to readable string

        Args:
            time_tuple: Time tuple from time.localtime()

        Returns:
            str: Formatted time string
        """
        return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            time_tuple[0], time_tuple[1], time_tuple[2],
            time_tuple[3], time_tuple[4], time_tuple[5]
        )

    def get_status(self):
        """
        Get WiFi and NTP status

        Returns:
            dict: Status dictionary
        """
        return {
            'wifi_enabled': self.wifi_config.get('enabled', False),
            'wifi_connected': self.is_connected(),
            'wifi_ssid': self.wifi_config.get('ssid', ''),
            'wifi_ip': self.wlan.ifconfig()[0] if self.is_connected() else 'N/A',
            'ntp_enabled': self.ntp_config.get('enabled', False),
            'ntp_server': self.ntp_config.get('server', 'N/A'),
            'ntp_last_sync': self.last_ntp_sync,
            'time_source': self.time_source,
            'timezone_offset': self.ntp_config.get('timezone_offset', 0),
        }

    def print_status(self):
        """Print WiFi and NTP status"""
        status = self.get_status()
        print("=" * 50)
        print("WiFi & NTP Status")
        print("=" * 50)
        print(f"WiFi Enabled: {status['wifi_enabled']}")
        print(f"WiFi Connected: {status['wifi_connected']}")
        print(f"WiFi SSID: {status['wifi_ssid']}")
        print(f"IP Address: {status['wifi_ip']}")
        print(f"NTP Enabled: {status['ntp_enabled']}")
        print(f"NTP Server: {status['ntp_server']}")
        print(f"Timezone Offset: UTC{status['timezone_offset']:+d}")
        print(f"Time Source: {status['time_source']}")
        if status['ntp_last_sync'] > 0:
            print(f"Last NTP Sync: {int(time.time() - status['ntp_last_sync'])}s ago")
        print("=" * 50)
