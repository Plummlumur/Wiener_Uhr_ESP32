/**
 * WiFi and NTP Time Manager - Implementation
 * ===========================================
 */

#include "wifi_manager.h"

WiFiTimeManager::WiFiTimeManager() {
  lastNTPSync = 0;
  wifiConnected = false;
}

bool WiFiTimeManager::connectWiFi() {
  if (!WIFI_ENABLED) {
    Serial.println("WiFi is disabled in configuration");
    return false;
  }

  String ssid = WIFI_SSID;
  if (ssid == "YOUR_WIFI_SSID" || ssid.length() == 0) {
    Serial.println("WiFi SSID not configured. Please update config.h");
    return false;
  }

  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);

  // Set WiFi mode
  WiFi.mode(WIFI_STA);

  // Check if already connected
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Already connected to WiFi");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    wifiConnected = true;
    return true;
  }

  // Connect to WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  // Wait for connection
  unsigned long startTime = millis();
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - startTime > WIFI_TIMEOUT) {
      Serial.println("\nWiFi connection timeout");
      wifiConnected = false;
      return false;
    }
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.print("Signal strength (RSSI): ");
  Serial.print(WiFi.RSSI());
  Serial.println(" dBm");

  wifiConnected = true;

  // Configure NTP if enabled
  if (NTP_ENABLED) {
    configureNTP();
  }

  return true;
}

bool WiFiTimeManager::isConnected() {
  wifiConnected = (WiFi.status() == WL_CONNECTED);
  return wifiConnected;
}

void WiFiTimeManager::disconnect() {
  WiFi.disconnect(true);
  WiFi.mode(WIFI_OFF);
  wifiConnected = false;
  Serial.println("WiFi disconnected");
}

void WiFiTimeManager::configureNTP() {
  // Configure NTP with timezone offset
  // ESP32 NTP uses seconds for timezone offset
  long gmtOffset_sec = NTP_TIMEZONE_OFFSET * 3600;
  long daylightOffset_sec = NTP_DST_OFFSET * 3600;

  configTime(gmtOffset_sec, daylightOffset_sec, NTP_SERVER);

  Serial.print("NTP server configured: ");
  Serial.println(NTP_SERVER);
  Serial.print("Timezone offset: UTC");
  if (NTP_TIMEZONE_OFFSET >= 0) Serial.print("+");
  Serial.println(NTP_TIMEZONE_OFFSET);
}

bool WiFiTimeManager::syncNTP() {
  if (!NTP_ENABLED) {
    Serial.println("NTP is disabled in configuration");
    return false;
  }

  if (!isConnected()) {
    Serial.println("WiFi not connected, cannot sync NTP");
    return false;
  }

  Serial.print("Syncing time with NTP server: ");
  Serial.println(NTP_SERVER);

  // Wait for NTP sync (max 10 seconds)
  struct tm timeinfo;
  int retries = 20;  // 20 * 500ms = 10 seconds
  while (retries > 0) {
    if (::getLocalTime(&timeinfo)) {
      lastNTPSync = millis();
      Serial.println("NTP synchronization successful!");
      Serial.print("Current time: ");
      Serial.println(getFormattedTime());
      return true;
    }
    delay(500);
    retries--;
    Serial.print(".");
  }

  Serial.println("\nNTP synchronization failed");
  return false;
}

bool WiFiTimeManager::shouldSync() {
  if (!NTP_ENABLED || !isConnected()) {
    return false;
  }

  // First sync
  if (lastNTPSync == 0) {
    return true;
  }

  // Check if sync interval has elapsed
  unsigned long currentTime = millis();
  unsigned long syncIntervalMs = (unsigned long)NTP_SYNC_INTERVAL * 1000;

  if (currentTime - lastNTPSync >= syncIntervalMs) {
    return true;
  }

  return false;
}

bool WiFiTimeManager::getLocalTime(int& hour, int& minute, int& second,
                                     int& day, int& month, int& year) {
  struct tm timeinfo;
  if (!::getLocalTime(&timeinfo)) {
    return false;
  }

  hour = timeinfo.tm_hour;
  minute = timeinfo.tm_min;
  second = timeinfo.tm_sec;
  day = timeinfo.tm_mday;
  month = timeinfo.tm_mon + 1;  // tm_mon is 0-11
  year = timeinfo.tm_year + 1900;  // tm_year is years since 1900

  return true;
}

String WiFiTimeManager::getFormattedTime() {
  struct tm timeinfo;
  if (!::getLocalTime(&timeinfo)) {
    return "Time not available";
  }

  char buffer[32];
  strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", &timeinfo);
  return String(buffer);
}

void WiFiTimeManager::printStatus() {
  Serial.println("==================================================");
  Serial.println("WiFi & NTP Status");
  Serial.println("==================================================");
  Serial.print("WiFi Enabled: ");
  Serial.println(WIFI_ENABLED ? "Yes" : "No");
  Serial.print("WiFi Connected: ");
  Serial.println(isConnected() ? "Yes" : "No");

  if (isConnected()) {
    Serial.print("WiFi SSID: ");
    Serial.println(WiFi.SSID());
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal Strength: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  }

  Serial.print("NTP Enabled: ");
  Serial.println(NTP_ENABLED ? "Yes" : "No");

  if (NTP_ENABLED) {
    Serial.print("NTP Server: ");
    Serial.println(NTP_SERVER);
    Serial.print("Timezone Offset: UTC");
    if (NTP_TIMEZONE_OFFSET >= 0) Serial.print("+");
    Serial.println(NTP_TIMEZONE_OFFSET);

    if (lastNTPSync > 0) {
      unsigned long timeSinceSync = (millis() - lastNTPSync) / 1000;
      Serial.print("Last NTP Sync: ");
      Serial.print(timeSinceSync);
      Serial.println(" seconds ago");
    }

    Serial.print("Current Time: ");
    Serial.println(getFormattedTime());
  }

  Serial.println("==================================================");
}
