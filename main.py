import board
import displayio
import framebufferio
import rgbmatrix
from digitalio import DigitalInOut, Direction
import adafruit_display_text.label
import terminalio
from adafruit_bitmap_font import bitmap_font
import adafruit_imageload
import time
from ds1302_helper import DS1302Helper
import random
# --------------------------------------------------------------
# Hardware & Display Setup
# --------------------------------------------------------------
rtc = DS1302Helper()
#rtc.set_time(2025, 11, 15, 14, 37, 30)
bit_depth_value = 6
unit_width = 64
unit_height = 64
chain_width = 1
chain_height = 1
serpentine_value = True

width_value = unit_width * chain_width
height_value = unit_height * chain_height

displayio.release_displays()

matrix = rgbmatrix.RGBMatrix(
    width=width_value,
    height=height_value,
    bit_depth=bit_depth_value,
    rgb_pins=[board.GP2, board.GP3, board.GP4, board.GP5, board.GP8, board.GP9],
    addr_pins=[board.GP10, board.GP16, board.GP18, board.GP20, board.GP22],
    clock_pin=board.GP11,
    latch_pin=board.GP12,
    output_enable_pin=board.GP13,
    tile=chain_height,
    serpentine=serpentine_value,
    doublebuffer=True
)

DISPLAY = framebufferio.FramebufferDisplay(matrix, auto_refresh=True, rotation=180)


# --------------------------------------------------------------
# RGB_Api-Klasse
# --------------------------------------------------------------
class RGB_Api:
    def __init__(self):
        self.txt_lines = ["", "", ""]
        self.txt_color = 0xFFFFFF
        self.txt_font = terminalio.FONT
        self.txt_scale = 1
        self.line_spacing = 1
        self.txt_x = 1
        self.txt_y = 10
        self.txt_bg_color = 0x000000
        self.txt_bg_opacity = False
        self.group = displayio.Group()
        self.has_background = False

    # ----------------------------------------------------------
    # Hintergrund laden (8-Bit BMP mit Palette)
    # ----------------------------------------------------------
    def load_background(self, path="/bild.bmp"):
        """Lädt ein 8-Bit-palettiertes BMP."""
        try:
            self.bg_bitmap, self.bg_palette = adafruit_imageload.load(
                path,
                bitmap=displayio.Bitmap,
                palette=displayio.Palette
            )
            self._bg_palette_orig = [self.bg_palette[i] for i in range(len(self.bg_palette))]
            self.has_background = True
            self.bg_path = path
        except Exception as e:
            print("Fehler beim Laden des Hintergrundbilds:", e)
            self.has_background = False

    # ----------------------------------------------------------
    # Hilfsfunktionen
    # ----------------------------------------------------------
    def _show_group(self, *elements):
        group = displayio.Group()

        if self.has_background:
            bg_copy = displayio.TileGrid(
                self.bg_bitmap,
                pixel_shader=self.bg_palette,
                x=0, y=0
            )
            group.append(bg_copy)

        for e in elements:
            group.append(e)

        DISPLAY.root_group = group
        self.group = group

    def _make_multiline_text(self):
        text_group = displayio.Group()
        line_height = 10 * self.txt_scale * self.line_spacing
        y_offset = self.txt_y

        for i, line in enumerate(self.txt_lines):
            lbl = adafruit_display_text.label.Label(
                self.txt_font,
                text=line,
                color=self.txt_color,
                scale=self.txt_scale,
            )
            lbl.x = self.txt_x
            lbl.y = int(y_offset + i * line_height)
            text_group.append(lbl)

        return text_group

    # ----------------------------------------------------------
    # Dimmen durch Paletten-Skalierung
    # ----------------------------------------------------------
    def _dim_color(self, color, factor: float):
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        return (r << 16) | (g << 8) | b

    def set_brightness(self, factor: float):
        """Dimmt den Hintergrund (0.0 = dunkel, 1.0 = hell)."""
        if not self.has_background:
            return

        f = max(0.0, min(1.0, factor))
        for i in range(len(self.bg_palette)):
            orig = self._bg_palette_orig[i]
            self.bg_palette[i] = self._dim_color(orig, f)

        if not hasattr(self, "_txt_color_orig"):
            self._txt_color_orig = self.txt_color
        self.txt_color = self._dim_color(self._txt_color_orig, f)

    # ----------------------------------------------------------
    # Text aktualisieren
    # ----------------------------------------------------------
    def update_text(self):
        text_group = self._make_multiline_text()
        self._show_group(text_group)


# --------------------------------------------------------------
# Hilfsfunktionen
# --------------------------------------------------------------

def returnWienerZeit(Stunde, Minute):
    hourOffset = 0
    bezeichner = ""
    bezeichner2 = ""
    
    minutenInWorten = [
        "", "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben",
        "acht", "neun", "zehn", "elf", "zwölf", "dreizehn", "vierzehn"
    ]
    
    # Gimmick: Bei 10, 20, 40, 50 Minuten zufällig alternative Formulierung
    random.seed(Stunde * 100 + Minute)
    useAlternative = random.choice([True, False])
    
    if Minute == 0:
        bezeichner = "punkt"
        bezeichner2 = ""
    elif Minute == 10 and useAlternative:
        # Alternative: "zehn nach" statt "fünf vor viertel"
        bezeichner = "zehn nach "
        bezeichner2 = ""
        hourOffset = 0
    elif Minute == 20 and useAlternative:
        # Alternative: "zehn vor halb" statt "fünf nach viertel"
        bezeichner = "zehn vor "
        bezeichner2 = "halb"
        hourOffset = 1
    elif Minute == 40 and useAlternative:
        # Alternative: "zehn nach halb" statt "fünf vor dreiviertel"
        bezeichner = "zehn nach "
        bezeichner2 = "halb"
        hourOffset = 1
    elif Minute == 50 and useAlternative:
        # Alternative: "zehn vor" statt "fünf nach dreiviertel"
        bezeichner = "zehn vor"
        bezeichner2 = ""
        hourOffset = 1
    elif Minute < 15:
        if Minute < 7:
            bezeichner = minutenInWorten[Minute] + " nach "
            bezeichner2 = ""
            hourOffset = 0
        else:
            minutenAnzahl = 15 - Minute
            bezeichner = minutenInWorten[minutenAnzahl] + " vor "
            bezeichner2 = "viertel"
            hourOffset = 1
    elif Minute == 15:
        bezeichner = "viertel"
        bezeichner2 = ""
        hourOffset = 1
    elif 15 < Minute < 30:
        if Minute < 23:
            minutenAnzahl = Minute - 15
            bezeichner = minutenInWorten[minutenAnzahl] + " nach "
            bezeichner2 = "viertel"
            hourOffset = 1
        else:
            minutenAnzahl = 30 - Minute
            bezeichner = minutenInWorten[minutenAnzahl] + " vor "
            bezeichner2 = "halb"
            hourOffset = 1
    elif Minute == 30:
        bezeichner = "halb"
        bezeichner2 = ""
        hourOffset = 1
    elif 30 < Minute < 45:
        if Minute < 38:
            minutenAnzahl = Minute - 30
            bezeichner = minutenInWorten[minutenAnzahl] + " nach "
            bezeichner2 = "halb"
            hourOffset = 1
        else:
            minutenAnzahl = 45 - Minute
            bezeichner = minutenInWorten[minutenAnzahl] + " vor "
            bezeichner2 = "dreiviertel"
            hourOffset = 1
    elif Minute == 45:
        bezeichner = "dreiviertel"
        bezeichner2 = ""
        hourOffset = 1
    else:  # Minute > 45
        if Minute < 53:
            minutenAnzahl = Minute - 45
            bezeichner = minutenInWorten[minutenAnzahl] + " nach "
            bezeichner2 = "dreiviertel"
            hourOffset = 1
        else:
            minutenAnzahl = 60 - Minute
            bezeichner = minutenInWorten[minutenAnzahl] + " vor"
            bezeichner2 = ""
            hourOffset = 1
    
    volleStunde = (Stunde + hourOffset)
    volleStundeAusgeschrieben = [
        "Eins", "Zwei", "Drei", "Vier", "Fünf", "Sechs", "Sieben",
        "Acht", "Neun", "Zehn", "Elf", "Zwölf",
        "Eins", "Zwei", "Drei", "Vier", "Fünf", "Sechs",
        "Sieben", "Acht", "Neun", "Zehn", "Elf", "Zwölf"
    ]
    
    return bezeichner, bezeichner2, volleStundeAusgeschrieben[volleStunde - 1]


def monatsHintergrund(month, rgb):
    monate = [
        "januar", "februar", "maerz", "april", "mai", "juni",
        "juli", "august", "september", "oktober", "november", "dezember"
    ]
    if 1 <= month <= 12:
        path = f"/{monate[month-1]}_8bit.bmp"
        rgb.load_background(path)


# --------------------------------------------------------------
# Hauptprogramm
# --------------------------------------------------------------
if __name__ == "__main__":
    RGB = RGB_Api()
    RGB.txt_font = bitmap_font.load_font("/lib/fonts/helvR12.bdf")
    RGB.txt_color = 0x000000
    RGB.txt_scale = 1
    RGB.line_spacing = 1.5
    RGB.txt_x = 1
    RGB.txt_y = 8
    buffer = ""

    while True:
        comp = rtc.get_time_components()
        Stunde = comp["hour"]
        Minute = comp["minute"]
        Monat = comp["month"]

        # Hintergrundbild passend zum Monat laden


        # Wiener Zeit bestimmen
        bezeichner, bezeichner2, volleStunde = returnWienerZeit(Stunde, Minute)

        # Textinhalt zusammenstellen
        RGB.txt_lines = (
            ["Es ist", bezeichner, bezeichner2, volleStunde]
            if len(bezeichner2) > 2 else
            ["Es ist", bezeichner, volleStunde]
        )

        # Nur aktualisieren, wenn sich der Text geändert hat
        if RGB.txt_lines != buffer:
            monatsHintergrund(Monat, RGB)
            # Nachtmodus: dimmen
            if Stunde in [0, 1, 2, 3, 4, 5, 6, 7, 16, 17, 18, 19, 20, 21, 22, 23]:
                RGB.set_brightness(0.15)
            else:
                RGB.set_brightness(0.3)

            RGB.update_text()
            buffer = RGB.txt_lines  # neuen Zustand merken

        time.sleep(60)