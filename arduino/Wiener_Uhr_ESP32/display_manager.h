/**
 * Display Manager
 * ===============
 * Manages the HUB75 RGB LED matrix display
 */

#ifndef DISPLAY_MANAGER_H
#define DISPLAY_MANAGER_H

#include <Arduino.h>
#include <ESP32-HUB75-MatrixPanel-I2S-DMA.h>
#include "config.h"

class DisplayManager {
public:
  DisplayManager();

  /**
   * Initialize the display
   * @return true if successful
   */
  bool begin();

  /**
   * Clear the display
   */
  void clear();

  /**
   * Set display brightness
   * @param brightness Brightness value (0-255)
   */
  void setBrightness(uint8_t brightness);

  /**
   * Display text lines on the screen
   * @param lines Array of text lines to display
   * @param lineCount Number of lines
   * @param color Text color (RGB565)
   */
  void displayText(String lines[], int lineCount, uint16_t color = 0x0000);

  /**
   * Update the display (call this in loop)
   */
  void update();

  /**
   * Get the matrix panel instance for advanced usage
   * @return Pointer to MatrixPanel_I2S_DMA
   */
  MatrixPanel_I2S_DMA* getPanel();

private:
  MatrixPanel_I2S_DMA* matrix;
  uint8_t currentBrightness;

  /**
   * Draw centered text
   * @param text Text to draw
   * @param y Y position
   * @param color Text color
   */
  void drawCenteredText(String text, int y, uint16_t color);
};

#endif // DISPLAY_MANAGER_H
