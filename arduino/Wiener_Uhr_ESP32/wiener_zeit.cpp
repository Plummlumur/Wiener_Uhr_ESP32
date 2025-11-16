/**
 * Wiener Zeit (Viennese Time) - Implementation
 * ==============================================
 */

#include "wiener_zeit.h"

// Minute names in German
const char* minutenInWorten[] = {
  "", "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben",
  "acht", "neun", "zehn", "elf", "zwölf", "dreizehn", "vierzehn"
};

// Hour names in German (capitalized for hour display)
const char* volleStundeAusgeschrieben[] = {
  "Eins", "Zwei", "Drei", "Vier", "Fünf", "Sechs", "Sieben",
  "Acht", "Neun", "Zehn", "Elf", "Zwölf",
  "Eins", "Zwei", "Drei", "Vier", "Fünf", "Sechs",
  "Sieben", "Acht", "Neun", "Zehn", "Elf", "Zwölf"
};

WienerZeit getWienerZeit(int hour, int minute) {
  WienerZeit result;
  int hourOffset = 0;

  // Gimmick: Bei 10, 20, 40, 50 Minuten zufällig alternative Formulierung
  // Use a pseudo-random approach based on current time
  randomSeed(hour * 100 + minute);
  bool useAlternative = (random(2) == 1);

  if (minute == 0) {
    result.bezeichner = "punkt";
    result.bezeichner2 = "";
  }
  else if (minute == 10 && useAlternative) {
    // Alternative: "zehn nach" statt "fünf vor viertel"
    result.bezeichner = "zehn nach ";
    result.bezeichner2 = "";
    hourOffset = 0;
  }
  else if (minute == 20 && useAlternative) {
    // Alternative: "zehn vor halb" statt "fünf nach viertel"
    result.bezeichner = "zehn vor ";
    result.bezeichner2 = "halb";
    hourOffset = 1;
  }
  else if (minute == 40 && useAlternative) {
    // Alternative: "zehn nach halb" statt "fünf vor dreiviertel"
    result.bezeichner = "zehn nach ";
    result.bezeichner2 = "halb";
    hourOffset = 1;
  }
  else if (minute == 50 && useAlternative) {
    // Alternative: "zehn vor" statt "fünf nach dreiviertel"
    result.bezeichner = "zehn vor";
    result.bezeichner2 = "";
    hourOffset = 1;
  }
  else if (minute < 15) {
    if (minute < 7) {
      result.bezeichner = String(minutenInWorten[minute]) + " nach ";
      result.bezeichner2 = "";
      hourOffset = 0;
    }
    else {
      int minutenAnzahl = 15 - minute;
      result.bezeichner = String(minutenInWorten[minutenAnzahl]) + " vor ";
      result.bezeichner2 = "viertel";
      hourOffset = 1;
    }
  }
  else if (minute == 15) {
    result.bezeichner = "viertel";
    result.bezeichner2 = "";
    hourOffset = 1;
  }
  else if (minute > 15 && minute < 30) {
    if (minute < 23) {
      int minutenAnzahl = minute - 15;
      result.bezeichner = String(minutenInWorten[minutenAnzahl]) + " nach ";
      result.bezeichner2 = "viertel";
      hourOffset = 1;
    }
    else {
      int minutenAnzahl = 30 - minute;
      result.bezeichner = String(minutenInWorten[minutenAnzahl]) + " vor ";
      result.bezeichner2 = "halb";
      hourOffset = 1;
    }
  }
  else if (minute == 30) {
    result.bezeichner = "halb";
    result.bezeichner2 = "";
    hourOffset = 1;
  }
  else if (minute > 30 && minute < 45) {
    if (minute < 38) {
      int minutenAnzahl = minute - 30;
      result.bezeichner = String(minutenInWorten[minutenAnzahl]) + " nach ";
      result.bezeichner2 = "halb";
      hourOffset = 1;
    }
    else {
      int minutenAnzahl = 45 - minute;
      result.bezeichner = String(minutenInWorten[minutenAnzahl]) + " vor ";
      result.bezeichner2 = "dreiviertel";
      hourOffset = 1;
    }
  }
  else if (minute == 45) {
    result.bezeichner = "dreiviertel";
    result.bezeichner2 = "";
    hourOffset = 1;
  }
  else { // minute > 45
    if (minute < 53) {
      int minutenAnzahl = minute - 45;
      result.bezeichner = String(minutenInWorten[minutenAnzahl]) + " nach ";
      result.bezeichner2 = "dreiviertel";
      hourOffset = 1;
    }
    else {
      int minutenAnzahl = 60 - minute;
      result.bezeichner = String(minutenInWorten[minutenAnzahl]) + " vor";
      result.bezeichner2 = "";
      hourOffset = 1;
    }
  }

  // Calculate the displayed hour
  int displayHour = (hour + hourOffset) % 24;
  if (displayHour == 0) displayHour = 24;

  // Convert to 1-24 range for array lookup (but array uses 12-hour format)
  int hourIndex = (displayHour - 1) % 24;
  result.stunde = String(volleStundeAusgeschrieben[hourIndex]);

  return result;
}

int getLineCount(const WienerZeit& zeit) {
  if (zeit.bezeichner2.length() > 2) {
    return 4;  // "Es ist", bezeichner, bezeichner2, stunde
  } else {
    return 3;  // "Es ist", bezeichner, stunde
  }
}

int getDisplayLines(const WienerZeit& zeit, String lines[]) {
  int lineCount = 0;

  lines[lineCount++] = "Es ist";
  lines[lineCount++] = zeit.bezeichner;

  if (zeit.bezeichner2.length() > 2) {
    lines[lineCount++] = zeit.bezeichner2;
  }

  lines[lineCount++] = zeit.stunde;

  return lineCount;
}
