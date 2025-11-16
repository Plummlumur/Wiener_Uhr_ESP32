"""
BDF Font Loader for MicroPython ESP32
======================================
Loads and renders BDF (Glyph Bitmap Distribution Format) fonts.

BDF is a simple bitmap font format used in X11 and many embedded systems.
"""

import framebuf


class BDFGlyph:
    """Represents a single character glyph"""

    def __init__(self, char, width, height, x_offset, y_offset, x_advance, bitmap):
        self.char = char
        self.width = width
        self.height = height
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.x_advance = x_advance
        self.bitmap = bitmap


class BDFFont:
    """BDF Font renderer"""

    def __init__(self, filename):
        """
        Load a BDF font file

        Args:
            filename: Path to .bdf font file
        """
        self.glyphs = {}
        self.font_height = 0
        self.font_ascent = 0
        self.font_descent = 0
        self._load_font(filename)

    def _load_font(self, filename):
        """Load BDF font from file"""
        with open(filename, 'r') as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Parse font properties
            if line.startswith('FONT_ASCENT'):
                self.font_ascent = int(line.split()[1])
            elif line.startswith('FONT_DESCENT'):
                self.font_descent = int(line.split()[1])
                self.font_height = self.font_ascent + self.font_descent

            # Parse character definition
            elif line.startswith('STARTCHAR'):
                i = self._load_glyph(lines, i)
                continue

            i += 1

    def _load_glyph(self, lines, start_index):
        """Load a single glyph from BDF data"""
        i = start_index
        char_name = None
        encoding = None
        width = 0
        height = 0
        x_offset = 0
        y_offset = 0
        x_advance = 0
        bitmap = []

        while i < len(lines):
            line = lines[i].strip()

            if line.startswith('STARTCHAR'):
                char_name = line.split(None, 1)[1]
            elif line.startswith('ENCODING'):
                encoding = int(line.split()[1])
            elif line.startswith('BBX'):
                parts = line.split()
                width = int(parts[1])
                height = int(parts[2])
                x_offset = int(parts[3])
                y_offset = int(parts[4])
            elif line.startswith('DWIDTH'):
                parts = line.split()
                x_advance = int(parts[1])
            elif line.startswith('BITMAP'):
                i += 1
                # Read bitmap data
                while i < len(lines) and not lines[i].strip().startswith('ENDCHAR'):
                    hex_str = lines[i].strip()
                    if hex_str:
                        bitmap.append(int(hex_str, 16))
                    i += 1
                break

            i += 1

        # Store glyph
        if encoding is not None and width > 0 and height > 0:
            try:
                char = chr(encoding)
                glyph = BDFGlyph(char, width, height, x_offset, y_offset, x_advance, bitmap)
                self.glyphs[char] = glyph
            except ValueError:
                pass  # Skip invalid encodings

        return i

    def get_glyph(self, char):
        """Get glyph for character, return space if not found"""
        return self.glyphs.get(char, self.glyphs.get(' ', None))

    def draw_char(self, fb, char, x, y, color, bg_color=None):
        """
        Draw a character on framebuffer

        Args:
            fb: Framebuffer to draw on
            char: Character to draw
            x: X position
            y: Y position
            color: Foreground color (RGB565)
            bg_color: Background color (RGB565), None for transparent
        """
        glyph = self.get_glyph(char)
        if not glyph:
            return 0

        # Calculate actual draw position
        draw_x = x + glyph.x_offset
        draw_y = y - glyph.y_offset - glyph.height

        # Draw each row of the glyph
        for row in range(glyph.height):
            if row >= len(glyph.bitmap):
                break

            bitmap_row = glyph.bitmap[row]
            for col in range(glyph.width):
                # Check if bit is set (MSB first)
                bit_index = glyph.width - 1 - col
                if bitmap_row & (1 << bit_index):
                    fb.pixel(draw_x + col, draw_y + row, color)
                elif bg_color is not None:
                    fb.pixel(draw_x + col, draw_y + row, bg_color)

        return glyph.x_advance

    def draw_text(self, fb, text, x, y, color, bg_color=None):
        """
        Draw text string on framebuffer

        Args:
            fb: Framebuffer to draw on
            text: Text string to draw
            x: X position
            y: Y position
            color: Foreground color (RGB565)
            bg_color: Background color (RGB565), None for transparent

        Returns:
            int: Total width of drawn text
        """
        cursor_x = x
        for char in text:
            advance = self.draw_char(fb, char, cursor_x, y, color, bg_color)
            cursor_x += advance

        return cursor_x - x

    def measure_text(self, text):
        """
        Measure width of text string

        Args:
            text: Text to measure

        Returns:
            int: Width in pixels
        """
        width = 0
        for char in text:
            glyph = self.get_glyph(char)
            if glyph:
                width += glyph.x_advance
        return width


class DefaultFont:
    """Default built-in font (8x8)"""

    def __init__(self):
        self.font_height = 8
        self.font_ascent = 8
        self.font_descent = 0

    def draw_text(self, fb, text, x, y, color, bg_color=None):
        """Draw text using framebuffer's built-in font"""
        fb.text(text, x, y, color)
        return len(text) * 8

    def measure_text(self, text):
        """Measure text width"""
        return len(text) * 8


def load_font(filename):
    """
    Load a BDF font file

    Args:
        filename: Path to .bdf file

    Returns:
        BDFFont: Loaded font
    """
    try:
        return BDFFont(filename)
    except Exception as e:
        print(f"Error loading font {filename}: {e}")
        print("Using default font")
        return DefaultFont()
