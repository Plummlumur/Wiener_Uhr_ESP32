/**
 * Wiener Zeit (Viennese Time) - Time Format Conversion
 * ======================================================
 * Converts standard time to Viennese German dialect time expressions
 */

#ifndef WIENER_ZEIT_H
#define WIENER_ZEIT_H

#include <Arduino.h>

/**
 * Structure to hold Viennese time representation
 */
struct WienerZeit {
  String bezeichner;   // First time description (e.g., "fünf nach")
  String bezeichner2;  // Second time description (e.g., "viertel", "halb")
  String stunde;       // Hour name (e.g., "Drei", "Vier")
};

/**
 * Convert time to Viennese German time format
 *
 * @param hour Hour (0-23)
 * @param minute Minute (0-59)
 * @return WienerZeit structure with Viennese time representation
 */
WienerZeit getWienerZeit(int hour, int minute);

/**
 * Get number of text lines needed for display
 *
 * @param zeit WienerZeit structure
 * @return Number of lines (3 or 4)
 */
int getLineCount(const WienerZeit& zeit);

/**
 * Get text lines for display
 *
 * @param zeit WienerZeit structure
 * @param lines Array to store text lines (must have space for 4 strings)
 * @return Number of lines filled
 */
int getDisplayLines(const WienerZeit& zeit, String lines[]);

#endif // WIENER_ZEIT_H
