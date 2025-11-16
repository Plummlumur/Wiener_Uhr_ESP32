/**
 * Display Manager - Implementation
 * =================================
 */

#include "display_manager.h"

DisplayManager::DisplayManager() {
  matrix = nullptr;
  currentBrightness = BRIGHTNESS_DAY;
}

bool DisplayManager::begin() {
  Serial.println("Initializing RGB Matrix...");

  // Create matrix configuration
  HUB75_I2S_CFG mxconfig(
    MATRIX_WIDTH,   // Module width
    MATRIX_HEIGHT,  // Module height
    MATRIX_CHAIN    // Chain length
  );

  // Custom pin mapping
  mxconfig.gpio.r1 = R1_PIN;
  mxconfig.gpio.g1 = G1_PIN;
  mxconfig.gpio.b1 = B1_PIN;
  mxconfig.gpio.r2 = R2_PIN;
  mxconfig.gpio.g2 = G2_PIN;
  mxconfig.gpio.b2 = B2_PIN;
  mxconfig.gpio.a = A_PIN;
  mxconfig.gpio.b = B_PIN;
  mxconfig.gpio.c = C_PIN;
  mxconfig.gpio.d = D_PIN;
  mxconfig.gpio.e = E_PIN;
  mxconfig.gpio.lat = LAT_PIN;
  mxconfig.gpio.oe = OE_PIN;
  mxconfig.gpio.clk = CLK_PIN;

  // WiFi-friendly configuration with reduced memory usage
  // CRITICAL: After WiFi init, memory is limited. Use minimal DMA buffers.
  mxconfig.double_buff = false;  // Disable double buffering to save memory
  mxconfig.clkphase = false;     // Better WiFi compatibility

  // Reduce latch blanking to save memory (default is often too high)
  mxconfig.latch_blanking = 1;   // Minimal blanking time

  // Use minimal color depth to reduce memory (2-bit = 4 brightness levels per color)
  mxconfig.min_refresh_rate = 60; // Reduce refresh rate slightly to save CPU

  // Create matrix instance
  matrix = new MatrixPanel_I2S_DMA(mxconfig);

  // Check if allocation succeeded
  if (!matrix) {
    Serial.println("*** Failed to allocate matrix object ***");
    return false;
  }

  // Initialize matrix
  if (!matrix->begin()) {
    Serial.println("*** Matrix initialization failed ***");
    delete matrix;
    matrix = nullptr;
    return false;
  }

  Serial.println("Matrix initialized successfully");
  Serial.print("Matrix size: ");
  Serial.print(MATRIX_WIDTH);
  Serial.print("x");
  Serial.println(MATRIX_HEIGHT);

  // Set initial brightness
  matrix->setBrightness8(currentBrightness);

  // Clear display
  clear();

  return true;
}

void DisplayManager::clear() {
  if (matrix) {
    matrix->clearScreen();
    matrix->flipDMABuffer();
  }
}

void DisplayManager::setBrightness(uint8_t brightness) {
  currentBrightness = brightness;
  if (matrix) {
    matrix->setBrightness8(brightness);
  }
}

void DisplayManager::displayText(String lines[], int lineCount, uint16_t color) {
  if (!matrix) {
    Serial.println("ERROR: Matrix not initialized in displayText");
    return;
  }

  if (lineCount <= 0 || lineCount > 10) {
    Serial.println("ERROR: Invalid line count");
    return;
  }

  // Clear screen first
  matrix->clearScreen();

  // Calculate starting Y position for centered text
  int totalHeight = lineCount * LINE_SPACING;
  int startY = (MATRIX_HEIGHT - totalHeight) / 2 + TEXT_Y_OFFSET;

  // Draw each line with error checking
  for (int i = 0; i < lineCount; i++) {
    if (lines[i].length() > 0) {
      int y = startY + (i * LINE_SPACING);
      drawCenteredText(lines[i], y, color);
    }
  }

  // Update display
  matrix->flipDMABuffer();
}

void DisplayManager::update() {
  // For DMA-based display, no continuous update needed
  // The display is automatically refreshed by DMA
}

MatrixPanel_I2S_DMA* DisplayManager::getPanel() {
  return matrix;
}

void DisplayManager::drawCenteredText(String text, int y, uint16_t color) {
  if (!matrix) {
    Serial.println("ERROR: Matrix null in drawCenteredText");
    return;
  }

  if (text.length() == 0) {
    return;  // Nothing to draw
  }

  // Calculate text width (approximate, 6 pixels per character with default font)
  int textWidth = text.length() * 6;
  int x = (MATRIX_WIDTH - textWidth) / 2;

  // Ensure text stays within bounds
  if (x < 0) x = TEXT_X_OFFSET;
  if (y < 0 || y >= MATRIX_HEIGHT) {
    Serial.println("ERROR: Y position out of bounds");
    return;
  }

  // Use const char* instead of String to avoid potential issues
  const char* cstr = text.c_str();

  // Set text properties with bounds checking
  matrix->setTextColor(color);
  matrix->setTextWrap(false);
  matrix->setCursor(x, y);

  // Draw text using C string
  matrix->print(cstr);
}
