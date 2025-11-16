/**
 * Wiener Uhr (Viennese Clock) - ESP32 Arduino Version
 * ====================================================
 * Displays time in Viennese German dialect on a 64x64 RGB LED matrix
 *
 * Hardware Requirements:
 * - ESP32-WROOM32 board
 * - 64x64 HUB75 RGB LED Matrix
 * - 5V power supply (for LED matrix, 3-5A recommended)
 * - Optional: DS1302 Real-Time Clock module (if not using WiFi/NTP)
 *
 * Required Libraries (install via Arduino Library Manager or PlatformIO):
 * - ESP32-HUB75-MatrixPanel-DMA by mrfaptastic
 * - Adafruit_GFX
 * - DS1302 by Timur Maksimov (optional, if using DS1302 RTC)
 *
 * Author: Arduino Port
 * Based on: MicroPython ESP32 version
 */

#include "config.h"
#include "display_manager.h"
#include "wifi_manager.h"
#include "wiener_zeit.h"

#if USE_DS1302
  #include <DS1302.h>
#endif

// Define MONTH_NAMES array (declared as extern in config.h)
const char* MONTH_NAMES[12] = {
  "januar", "februar", "maerz", "april", "mai", "juni",
  "juli", "august", "september", "oktober", "november", "dezember"
};

// Global objects
DisplayManager display;
WiFiTimeManager wifiTime;

#if USE_DS1302
  DS1302 rtc(DS1302_CE_PIN, DS1302_CLK_PIN, DS1302_DAT_PIN);
#endif

// State tracking
String lastDisplayedLines[4];
int lastDisplayedLineCount = 0;
unsigned long lastUpdateTime = 0;
unsigned long lastNTPCheckTime = 0;

// Update interval (1 second)
const unsigned long UPDATE_INTERVAL = 1000;

// NTP check interval (60 seconds)
const unsigned long NTP_CHECK_INTERVAL = 60000;

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  delay(1000);  // Wait for serial to initialize

  Serial.println();
  Serial.println("==================================================");
  Serial.println("   Wiener Uhr - ESP32 Arduino Version");
  Serial.println("==================================================");
  Serial.println();

  // IMPORTANT: Initialize WiFi BEFORE display to avoid DMA conflicts
  // The HUB75 DMA display can interfere with WiFi initialization
  #if WIFI_ENABLED
    Serial.println("Initializing WiFi...");
    if (wifiTime.connectWiFi()) {
      // Attempt initial NTP sync
      if (NTP_ENABLED) {
        wifiTime.syncNTP();
      }
    } else {
      Serial.println("WiFi connection failed");
      #if !USE_DS1302
        Serial.println("WARNING: No WiFi and no DS1302 RTC configured!");
        Serial.println("Time display may not work correctly.");
      #endif
    }

    // Print WiFi & NTP status
    wifiTime.printStatus();

    // Give WiFi a moment to stabilize and free up some memory
    Serial.println("\nWaiting for WiFi to stabilize...");
    delay(1000);
  #else
    Serial.println("WiFi disabled in configuration");
  #endif

  // Check available heap before display initialization
  Serial.print("\nFree heap before display init: ");
  Serial.print(ESP.getFreeHeap());
  Serial.println(" bytes");

  // Initialize display AFTER WiFi to avoid conflicts
  Serial.println();
  if (!display.begin()) {
    Serial.println("ERROR: Display initialization failed!");
    Serial.print("Free heap after failure: ");
    Serial.print(ESP.getFreeHeap());
    Serial.println(" bytes");
    Serial.println("\nTroubleshooting:");
    Serial.println("1. The display requires significant memory for DMA buffers");
    Serial.println("2. Try disabling WiFi temporarily in config.h");
    Serial.println("3. Check all pin connections");
    while (1) {
      delay(1000);
    }
  }

  Serial.print("Free heap after display init: ");
  Serial.print(ESP.getFreeHeap());
  Serial.println(" bytes");

  // Skip startup message due to potential text rendering conflicts with WiFi
  // Just clear the display and start the clock
  display.clear();
  delay(500);
  Serial.println("Display ready - starting clock...");

  // Initialize DS1302 RTC if enabled
  #if USE_DS1302
    Serial.println("\nInitializing DS1302 RTC...");
    rtc.writeProtect(false);
    rtc.halt(false);

    Time t = rtc.time();
    Serial.print("RTC initialized. Current time: ");
    Serial.print(t.yr);
    Serial.print("-");
    Serial.print(t.mon);
    Serial.print("-");
    Serial.print(t.date);
    Serial.print(" ");
    Serial.print(t.hr);
    Serial.print(":");
    Serial.print(t.min);
    Serial.print(":");
    Serial.println(t.sec);

    // Sync RTC with NTP if WiFi is connected and sync is enabled
    #if WIFI_ENABLED && NTP_ENABLED && NTP_SYNC_RTC
      if (wifiTime.isConnected()) {
        Serial.println("Syncing DS1302 RTC with NTP time...");
        int hour, minute, second, day, month, year;
        if (wifiTime.getLocalTime(hour, minute, second, day, month, year)) {
          Time ntpTime(year, month, day, hour, minute, second, Time::kSunday);
          rtc.time(ntpTime);
          Serial.println("RTC synchronized with NTP");
        }
      }
    #endif
  #endif

  Serial.println("\n==================================================");
  Serial.println("Setup complete! Starting main loop...");
  Serial.println("==================================================\n");

  display.clear();
  lastUpdateTime = millis();
  lastNTPCheckTime = millis();
}

void loop() {
  unsigned long currentTime = millis();

  // Periodic NTP sync check (every 60 seconds)
  #if WIFI_ENABLED && NTP_ENABLED
    if (currentTime - lastNTPCheckTime >= NTP_CHECK_INTERVAL) {
      lastNTPCheckTime = currentTime;

      if (wifiTime.shouldSync()) {
        Serial.println("Performing periodic NTP sync...");
        if (wifiTime.syncNTP()) {
          // Sync RTC if configured
          #if USE_DS1302 && NTP_SYNC_RTC
            int hour, minute, second, day, month, year;
            if (wifiTime.getLocalTime(hour, minute, second, day, month, year)) {
              Time ntpTime(year, month, day, hour, minute, second, Time::kSunday);
              rtc.time(ntpTime);
              Serial.println("RTC synchronized with NTP");
            }
          #endif
        }
      }
    }
  #endif

  // Update clock display (every second)
  if (currentTime - lastUpdateTime >= UPDATE_INTERVAL) {
    lastUpdateTime = currentTime;

    int hour, minute, second, day, month, year;
    bool timeValid = false;
    String timeSource = "NONE";

    // Try to get time from WiFi/NTP first, then DS1302
    #if WIFI_ENABLED && NTP_ENABLED
      if (wifiTime.isConnected()) {
        if (wifiTime.getLocalTime(hour, minute, second, day, month, year)) {
          timeValid = true;
          timeSource = "NTP";
        }
      }
    #endif

    // Fallback to DS1302 RTC if WiFi/NTP not available
    #if USE_DS1302
      if (!timeValid) {
        Time t = rtc.time();
        hour = t.hr;
        minute = t.min;
        second = t.sec;
        day = t.date;
        month = t.mon;
        year = t.yr;
        timeValid = true;
        timeSource = "RTC";
      }
    #endif

    if (!timeValid) {
      Serial.println("ERROR: No valid time source available!");
      return;
    }

    // Get Viennese time representation
    WienerZeit zeit = getWienerZeit(hour, minute);

    // Get display lines
    String lines[4];
    int lineCount = getDisplayLines(zeit, lines);

    // Check if display needs updating
    bool needsUpdate = (lineCount != lastDisplayedLineCount);
    if (!needsUpdate) {
      for (int i = 0; i < lineCount; i++) {
        if (lines[i] != lastDisplayedLines[i]) {
          needsUpdate = true;
          break;
        }
      }
    }

    // Update display if needed
    if (needsUpdate) {
      Serial.print("Updating display [");
      Serial.print(timeSource);
      Serial.print("]: ");
      for (int i = 0; i < lineCount; i++) {
        Serial.print(lines[i]);
        Serial.print(" ");
      }
      Serial.println();

      // Apply brightness based on time of day
      if (hour >= NIGHT_START_HOUR || hour < NIGHT_END_HOUR) {
        display.setBrightness(BRIGHTNESS_NIGHT);
      } else {
        display.setBrightness(BRIGHTNESS_DAY);
      }

      // Yield to WiFi task before display update
      yield();
      delay(10);

      // Update display
      Serial.println("Calling displayText...");
      display.displayText(lines, lineCount, TEXT_COLOR);
      Serial.println("displayText complete");

      // Save current state
      lastDisplayedLineCount = lineCount;
      for (int i = 0; i < lineCount; i++) {
        lastDisplayedLines[i] = lines[i];
      }
    }
  }

  // Allow WiFi stack to process
  yield();
  delay(10);
}
