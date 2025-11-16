"""
Boot Configuration for Wiener Uhr ESP32
========================================
This file runs automatically when the ESP32 boots up.

It performs basic system initialization and optionally sets up Wi-Fi.
"""

import gc
import esp
import machine

# Disable ESP32 debug output
esp.osdebug(None)

# Run garbage collection
gc.collect()

print()
print("=" * 50)
print("Wiener Uhr - ESP32 Boot")
print("=" * 50)
print(f"Free memory: {gc.mem_free()} bytes")
print(f"Frequency: {machine.freq() // 1000000} MHz")
print("=" * 50)

# Optional: Set CPU frequency for better performance
# Uncomment to increase to 240 MHz (default is usually 160 MHz)
# machine.freq(240000000)

# Optional: Wi-Fi setup (uncomment and configure if needed)
"""
import network

def connect_wifi(ssid, password):
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Connecting to WiFi...')
        sta_if.active(True)
        sta_if.connect(ssid, password)
        timeout = 10
        while not sta_if.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
    if sta_if.isconnected():
        print('WiFi connected!')
        print('Network config:', sta_if.ifconfig())
        return True
    else:
        print('WiFi connection failed!')
        return False

# Uncomment and set your WiFi credentials
# WIFI_SSID = "YourNetworkName"
# WIFI_PASSWORD = "YourPassword"
# connect_wifi(WIFI_SSID, WIFI_PASSWORD)
"""

print("Boot complete. Starting main application...")
