# WiFi and NTP Time Setup for Wiener Uhr ESP32

This guide explains how to configure and use WiFi connectivity with NTP (Network Time Protocol) time synchronization on the Wiener Uhr ESP32 clock.

## Overview

The Wiener Uhr ESP32 now supports two time sources:

1. **DS1302 RTC** (Real-Time Clock) - Hardware clock module
2. **NTP Time Server** - Internet-based time synchronization via WiFi

The system can use either source independently or both together, with NTP as the primary source and DS1302 as a fallback.

## Features

- **Automatic WiFi Connection** - Connects to your WiFi network on startup
- **NTP Time Synchronization** - Gets accurate time from internet time servers
- **Timezone Support** - Configure your timezone offset (e.g., CET = UTC+1)
- **RTC Synchronization** - Automatically sync DS1302 RTC with NTP time
- **Periodic Updates** - Keeps time accurate with periodic NTP synchronization
- **Fallback Mode** - Uses DS1302 RTC if WiFi is unavailable
- **Status Monitoring** - Displays WiFi and NTP status on startup

## Configuration

### Step 1: Edit WiFi Configuration

Open `config_esp32.py` and update the WiFi settings:

```python
WIFI_CONFIG = {
    'enabled': True,                        # Set to False to disable WiFi
    'ssid': 'YOUR_WIFI_SSID',              # Replace with your WiFi network name
    'password': 'YOUR_WIFI_PASSWORD',       # Replace with your WiFi password
    'timeout': 10,                          # Connection timeout in seconds
    'retry_interval': 60,                   # Retry connection interval in seconds
}
```

**Important:** Replace `'YOUR_WIFI_SSID'` and `'YOUR_WIFI_PASSWORD'` with your actual WiFi credentials.

### Step 2: Configure NTP Settings

In the same file, configure NTP settings:

```python
NTP_CONFIG = {
    'enabled': True,                        # Enable NTP time synchronization
    'server': 'pool.ntp.org',              # NTP server address
    'timezone_offset': 1,                   # Timezone offset in hours (CET = UTC+1)
    'dst_offset': 0,                        # Daylight saving time offset in hours
    'sync_interval': 3600,                  # Sync interval in seconds (1 hour)
    'sync_rtc': True,                       # Sync DS1302 RTC with NTP time
}
```

#### Timezone Configuration

Set the `timezone_offset` according to your location:

- **CET (Central European Time)**: `1` (UTC+1)
- **CEST (Central European Summer Time)**: Set `dst_offset` to `1`
- **EST (Eastern Standard Time)**: `-5` (UTC-5)
- **PST (Pacific Standard Time)**: `-8` (UTC-8)
- **JST (Japan Standard Time)**: `9` (UTC+9)
- **AEST (Australian Eastern Standard Time)**: `10` (UTC+10)

#### NTP Server Options

You can use different NTP servers:

- `'pool.ntp.org'` - Global pool (default)
- `'europe.pool.ntp.org'` - European servers
- `'north-america.pool.ntp.org'` - North American servers
- `'asia.pool.ntp.org'` - Asian servers
- `'time.google.com'` - Google's NTP servers
- `'time.nist.gov'` - NIST time servers

## Usage Modes

### Mode 1: WiFi/NTP Only (Recommended)

The ESP32 connects to WiFi and uses NTP for time. The DS1302 RTC is synchronized with NTP time as a backup.

```python
WIFI_CONFIG = {
    'enabled': True,
    'ssid': 'MyWiFi',
    'password': 'MyPassword',
}

NTP_CONFIG = {
    'enabled': True,
    'sync_rtc': True,  # Keep RTC synced for fallback
}
```

**Advantages:**
- Most accurate time (internet-based)
- Automatic timezone handling
- No manual time setting required

### Mode 2: DS1302 RTC Only

WiFi is disabled, system uses only the DS1302 RTC.

```python
WIFI_CONFIG = {
    'enabled': False,  # Disable WiFi
}
```

**Advantages:**
- Works without internet connection
- Lower power consumption
- Reliable if battery-backed RTC is set

### Mode 3: Hybrid (WiFi with RTC Fallback)

WiFi/NTP is primary, but DS1302 RTC is used if WiFi is unavailable.

```python
WIFI_CONFIG = {
    'enabled': True,
}

NTP_CONFIG = {
    'enabled': True,
    'sync_rtc': True,  # Sync RTC when WiFi available
}
```

**Advantages:**
- Best of both worlds
- Continues working if WiFi goes down
- RTC automatically updates when WiFi available

## How It Works

### Startup Sequence

1. **WiFi Connection**
   - ESP32 attempts to connect to configured WiFi network
   - Connection timeout: 10 seconds (configurable)
   - If connection fails, continues with DS1302 RTC only

2. **NTP Synchronization**
   - Once connected, performs initial NTP sync
   - Applies timezone offset to get local time
   - If `sync_rtc` is enabled, updates DS1302 RTC

3. **Time Source Selection**
   - If WiFi connected and NTP enabled: Uses NTP time
   - If WiFi disconnected: Falls back to DS1302 RTC
   - Display shows `[NTP]` or `[RTC]` to indicate source

### Periodic Updates

- **NTP Sync Interval**: 3600 seconds (1 hour) by default
- **Check Interval**: Every 60 seconds
- **RTC Sync**: Automatically synced when NTP updates (if enabled)

### Display Output

The system shows which time source is being used:

```
Updating display [NTP]: Es ist halb Drei
```

or

```
Updating display [RTC]: Es ist halb Drei
```

## Troubleshooting

### WiFi Not Connecting

**Problem:** WiFi connection fails on startup

**Solutions:**
1. Verify SSID and password are correct
2. Check that WiFi network is 2.4 GHz (ESP32 doesn't support 5 GHz)
3. Ensure WiFi network is within range
4. Check if MAC address filtering is blocking ESP32
5. Try increasing timeout in `WIFI_CONFIG`

**Diagnostic Output:**
```
Connecting to WiFi: MyWiFi...
WiFi connection timeout
WiFi connection failed, will use DS1302 RTC only
```

### NTP Sync Fails

**Problem:** WiFi connects but NTP sync fails

**Solutions:**
1. Check internet connectivity of your WiFi network
2. Verify NTP server address is correct
3. Check if firewall is blocking NTP (UDP port 123)
4. Try different NTP server (e.g., `'time.google.com'`)

**Diagnostic Output:**
```
Syncing time with NTP server: pool.ntp.org...
NTP synchronization failed: [error message]
```

### Wrong Time Displayed

**Problem:** Time is off by several hours

**Solutions:**
1. Check `timezone_offset` in `NTP_CONFIG`
2. Adjust `dst_offset` if daylight saving time is active
3. Verify the offset calculation:
   - If clock shows 14:00 but it's 15:00, increase offset by 1
   - If clock shows 16:00 but it's 15:00, decrease offset by 1

### RTC Not Syncing

**Problem:** DS1302 RTC doesn't update from NTP

**Solutions:**
1. Verify `sync_rtc: True` in `NTP_CONFIG`
2. Check that NTP sync is successful first
3. Ensure DS1302 write protection is disabled
4. Check DS1302 connections (CLK, DAT, CE pins)

## Status Monitoring

### WiFi & NTP Status Display

On startup, the system displays status information:

```
==================================================
WiFi & NTP Status
==================================================
WiFi Enabled: True
WiFi Connected: True
WiFi SSID: MyWiFi
IP Address: 192.168.1.100
NTP Enabled: True
NTP Server: pool.ntp.org
Timezone Offset: UTC+1
Time Source: ntp
Last NTP Sync: 0s ago
==================================================
```

### Time Source Indicator

In the main loop, each time update shows the source:

```
Updating display [NTP]: Es ist punkt Drei
```

- `[NTP]` - Time from NTP server (most accurate)
- `[RTC]` - Time from DS1302 RTC (fallback)

## Advanced Configuration

### Custom NTP Sync Interval

For more or less frequent updates:

```python
NTP_CONFIG = {
    'sync_interval': 1800,  # 30 minutes (more frequent)
    # or
    'sync_interval': 7200,  # 2 hours (less frequent)
}
```

**Note:** More frequent syncs use more power and bandwidth.

### Disable RTC Sync

If you want to use NTP only without updating the RTC:

```python
NTP_CONFIG = {
    'sync_rtc': False,  # Don't update DS1302 RTC
}
```

**Use case:** Testing NTP without affecting RTC, or if RTC is used for other purposes.

### Connection Retry

If WiFi connection fails, the system will:
1. Continue with DS1302 RTC
2. Not retry automatically (to avoid blocking)

To manually retry, you can:
- Press the reset button on ESP32
- Power cycle the device

## Security Considerations

### WiFi Credentials

**Important:** The `config_esp32.py` file contains your WiFi password in plain text.

**Best Practices:**
1. Don't share your `config_esp32.py` file
2. Add `config_esp32.py` to `.gitignore` if using version control
3. Create a `config_esp32_example.py` template without real credentials
4. Consider using WPA2-Enterprise if available

### NTP Security

- NTP protocol is unencrypted (potential for spoofing)
- Use trusted NTP servers (pool.ntp.org, time.google.com, etc.)
- For critical applications, consider NTS (NTP with TLS) in the future

## Example Configurations

### Example 1: Home Use (Vienna, Austria)

```python
WIFI_CONFIG = {
    'enabled': True,
    'ssid': 'HomeWiFi',
    'password': 'MySecurePassword',
    'timeout': 15,
}

NTP_CONFIG = {
    'enabled': True,
    'server': 'europe.pool.ntp.org',
    'timezone_offset': 1,      # CET (Winter)
    'dst_offset': 1,           # Add 1 hour in summer (CEST)
    'sync_interval': 3600,
    'sync_rtc': True,
}
```

### Example 2: Office Use (New York, USA)

```python
WIFI_CONFIG = {
    'enabled': True,
    'ssid': 'OfficeNetwork',
    'password': 'OfficePass123',
}

NTP_CONFIG = {
    'enabled': True,
    'server': 'north-america.pool.ntp.org',
    'timezone_offset': -5,     # EST (Winter)
    'dst_offset': 1,           # EDT (Summer)
    'sync_interval': 1800,     # 30 minutes
    'sync_rtc': True,
}
```

### Example 3: Portable/Demo Mode

```python
WIFI_CONFIG = {
    'enabled': False,  # No WiFi
}

# DS1302 RTC only - set time manually:
# rtc.set_time(2025, 11, 16, 14, 30, 0)
```

## Technical Details

### WiFi Module

- **Library:** `network` (MicroPython built-in)
- **Mode:** Station (STA) mode
- **Security:** WPA/WPA2 PSK
- **Frequency:** 2.4 GHz only

### NTP Module

- **Library:** `ntptime` (MicroPython built-in)
- **Protocol:** NTP v4
- **Port:** UDP 123
- **Accuracy:** ±1 second typically

### Time Synchronization

- **Initial sync:** On WiFi connection
- **Periodic sync:** Every hour (configurable)
- **RTC update:** Optional, on each NTP sync
- **Timezone:** Applied on top of UTC time

## Compatibility

- **ESP32 boards:** ESP32-WROOM32, ESP32-DevKitC, and compatible
- **MicroPython:** v1.19 or later
- **WiFi:** 802.11 b/g/n (2.4 GHz)
- **RTC:** DS1302 (still supported as fallback)

## Future Enhancements

Potential future improvements:

- [ ] Web interface for WiFi configuration
- [ ] Automatic daylight saving time detection
- [ ] Multiple NTP server fallback
- [ ] WiFi signal strength indicator
- [ ] NTP over TLS (NTS) support
- [ ] OTA (Over-The-Air) firmware updates

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Verify your configuration in `config_esp32.py`
3. Review the status output on serial console
4. Check the main documentation in `README_ESP32.md`

## Summary

The WiFi/NTP feature provides:

- ✅ Automatic internet time synchronization
- ✅ No manual time setting required
- ✅ Timezone support
- ✅ Fallback to RTC if WiFi unavailable
- ✅ Periodic automatic updates
- ✅ Easy configuration

Enjoy your always-accurate Wiener Uhr!
