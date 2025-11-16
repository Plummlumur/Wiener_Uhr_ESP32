/**
 * WiFi and NTP Time Manager
 * ==========================
 * Handles WiFi connection and NTP time synchronization
 */

#ifndef WIFI_MANAGER_H
#define WIFI_MANAGER_H

#include <Arduino.h>
#include <WiFi.h>
#include <time.h>
#include "config.h"

class WiFiTimeManager {
public:
  WiFiTimeManager();

  /**
   * Connect to WiFi network
   * @return true if connected successfully
   */
  bool connectWiFi();

  /**
   * Check if WiFi is connected
   * @return true if connected
   */
  bool isConnected();

  /**
   * Disconnect from WiFi
   */
  void disconnect();

  /**
   * Sync time with NTP server
   * @return true if successful
   */
  bool syncNTP();

  /**
   * Check if NTP sync is needed based on interval
   * @return true if sync is needed
   */
  bool shouldSync();

  /**
   * Get current local time
   * @param hour Output parameter for hour (0-23)
   * @param minute Output parameter for minute (0-59)
   * @param second Output parameter for second (0-59)
   * @param day Output parameter for day (1-31)
   * @param month Output parameter for month (1-12)
   * @param year Output parameter for year (e.g., 2025)
   * @return true if time is valid
   */
  bool getLocalTime(int& hour, int& minute, int& second, int& day, int& month, int& year);

  /**
   * Get formatted time string
   * @return String in format "YYYY-MM-DD HH:MM:SS"
   */
  String getFormattedTime();

  /**
   * Print WiFi and NTP status
   */
  void printStatus();

private:
  unsigned long lastNTPSync;
  bool wifiConnected;

  /**
   * Configure NTP client
   */
  void configureNTP();
};

#endif // WIFI_MANAGER_H
