/**
 * Wiener Uhr (Viennese Clock) - ESP32 Arduino Configuration
 * ===========================================================
 * Pin mapping and configuration for ESP32 with HUB75 RGB LED matrix and DS1302 RTC
 *
 * Hardware Requirements:
 * - ESP32-WROOM32 board
 * - 64x64 HUB75 RGB LED Matrix
 * - DS1302 Real-Time Clock module (optional, if WiFi/NTP not used)
 * - 5V power supply (for LED matrix)
 */

#ifndef CONFIG_H
#define CONFIG_H

// =============================================================================
// RGB LED Matrix (HUB75 Interface) - 64x64 pixels
// =============================================================================

// Matrix dimensions
#define MATRIX_WIDTH 64
#define MATRIX_HEIGHT 64
#define MATRIX_CHAIN 1  // Number of chained panels

// HUB75 Pin Configuration
// These pins are used by the ESP32-HUB75-MatrixPanel-DMA library
#define R1_PIN 25   // Red - Upper half
#define G1_PIN 26   // Green - Upper half
#define B1_PIN 27   // Blue - Upper half
#define R2_PIN 14   // Red - Lower half
#define G2_PIN 12   // Green - Lower half (Note: GPIO 12 strapping pin)
#define B2_PIN 13   // Blue - Lower half

#define A_PIN  23   // Address A
#define B_PIN  19   // Address B
#define C_PIN  5    // Address C
#define D_PIN  17   // Address D
#define E_PIN  16   // Address E (needed for 64x64 matrix)

#define LAT_PIN 4   // Latch / Strobe
#define OE_PIN  15  // Output Enable (active LOW)
#define CLK_PIN 22  // Clock

// =============================================================================
// DS1302 Real-Time Clock (Optional if using WiFi/NTP)
// =============================================================================
#define DS1302_CLK_PIN 18  // Clock pin
#define DS1302_DAT_PIN 21  // Data pin (bidirectional)
#define DS1302_CE_PIN  32  // Chip Enable / Reset pin

// Set to false if you don't have a DS1302 and only want to use WiFi/NTP
#define USE_DS1302 true

// =============================================================================
// Display Settings
// =============================================================================
#define BRIGHTNESS_DAY   80    // Brightness during day (0-255)
#define BRIGHTNESS_NIGHT 40    // Brightness during night (0-255)
#define NIGHT_START_HOUR 16    // Night mode starts at 16:00
#define NIGHT_END_HOUR   8     // Night mode ends at 08:00

// Text positioning
#define TEXT_X_OFFSET 1
#define TEXT_Y_OFFSET 8
#define TEXT_COLOR 0x0000      // Black text (works with colored backgrounds)
#define LINE_SPACING  13       // Pixels between lines

// =============================================================================
// WiFi and NTP Configuration
// =============================================================================
#define WIFI_ENABLED true
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"
#define WIFI_TIMEOUT 10000     // Connection timeout in milliseconds

#define NTP_ENABLED true
#define NTP_SERVER "pool.ntp.org"
#define NTP_TIMEZONE_OFFSET 1  // Timezone offset in hours (CET = UTC+1)
#define NTP_DST_OFFSET 0       // Daylight saving time offset
#define NTP_SYNC_INTERVAL 3600 // Sync interval in seconds (1 hour)
#define NTP_SYNC_RTC true      // Sync DS1302 RTC with NTP time

// =============================================================================
// Background Images
// =============================================================================
// Set to true to load monthly background images from SD card or SPIFFS
#define USE_MONTHLY_BACKGROUNDS false

// If using backgrounds, define the path pattern
// Month names: januar, februar, maerz, april, mai, juni, juli, august,
//              september, oktober, november, dezember
#define BG_IMAGE_PATH "/backgrounds/"
#define BG_IMAGE_EXTENSION ".bmp"

// =============================================================================
// Font Settings
// =============================================================================
// Use Adafruit_GFX built-in fonts
// Options: NULL (default 5x7), &FreeSans9pt7b, &FreeSans12pt7b, etc.
// For BDF fonts, you'll need to convert them to GFX format first
#define USE_CUSTOM_FONT false

// =============================================================================
// Month Names (German)
// =============================================================================
const char* MONTH_NAMES[] = {
  "januar", "februar", "maerz", "april", "mai", "juni",
  "juli", "august", "september", "oktober", "november", "dezember"
};

#endif // CONFIG_H
