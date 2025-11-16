"""
HUB75 RGB LED Matrix Driver for ESP32 MicroPython
==================================================
Driver for HUB75/HUB75E RGB LED matrix panels on ESP32.

This is a software-based driver for 64x64 RGB matrices.
For better performance, consider using a compiled driver or ESP32-HUB75-MatrixPanel-DMA.

Hardware Requirements:
- ESP32-WROOM32 or similar
- 64x64 HUB75 RGB LED Matrix Panel
- Proper power supply (5V, several amps depending on brightness)

Note: This driver uses bit-banging which may limit refresh rates.
For production use, consider using a native C extension or I2S DMA-based driver.
"""

from machine import Pin
import framebuf
import time


class HUB75Matrix:
    """
    Software driver for HUB75 RGB LED Matrix panels

    Supports 64x64 panels (1/32 scan) with or without E address line
    """

    def __init__(self, width, height, pin_config):
        """
        Initialize HUB75 matrix

        Args:
            width: Panel width in pixels (e.g., 64)
            height: Panel height in pixels (e.g., 64)
            pin_config: Dictionary with pin assignments:
                'R1', 'G1', 'B1': Upper half RGB
                'R2', 'G2', 'B2': Lower half RGB
                'A', 'B', 'C', 'D', 'E': Address lines
                'CLK': Clock
                'LAT': Latch
                'OE': Output Enable
        """
        self.width = width
        self.height = height
        self.rows = height // 2  # HUB75 drives upper/lower half simultaneously

        # Initialize pins
        self.r1 = Pin(pin_config['R1'], Pin.OUT)
        self.g1 = Pin(pin_config['G1'], Pin.OUT)
        self.b1 = Pin(pin_config['B1'], Pin.OUT)
        self.r2 = Pin(pin_config['R2'], Pin.OUT)
        self.g2 = Pin(pin_config['G2'], Pin.OUT)
        self.b2 = Pin(pin_config['B2'], Pin.OUT)

        self.addr_a = Pin(pin_config['A'], Pin.OUT)
        self.addr_b = Pin(pin_config['B'], Pin.OUT)
        self.addr_c = Pin(pin_config['C'], Pin.OUT)
        self.addr_d = Pin(pin_config['D'], Pin.OUT)
        self.addr_e = Pin(pin_config['E'], Pin.OUT) if 'E' in pin_config else None

        self.clk = Pin(pin_config['CLK'], Pin.OUT)
        self.lat = Pin(pin_config['LAT'], Pin.OUT)
        self.oe = Pin(pin_config['OE'], Pin.OUT)

        # Initialize to safe state
        self.oe.value(1)  # Disable output (active LOW)
        self.lat.value(0)
        self.clk.value(0)

        # Create framebuffer (RGB565 format, 2 bytes per pixel)
        # For 64x64: 64 * 64 * 2 = 8192 bytes
        self.buffer = bytearray(width * height * 2)
        self.fb = framebuf.FrameBuffer(self.buffer, width, height, framebuf.RGB565)

        # Brightness control (0-255)
        self._brightness = 64  # Default medium brightness

        # Clear display
        self.fill(0x0000)

    def _select_row(self, row):
        """Select row address (0 to rows-1)"""
        self.addr_a.value(row & 0x01)
        self.addr_b.value((row >> 1) & 0x01)
        self.addr_c.value((row >> 2) & 0x01)
        self.addr_d.value((row >> 3) & 0x01)
        if self.addr_e:
            self.addr_e.value((row >> 4) & 0x01)

    def _clock_pulse(self):
        """Generate a clock pulse"""
        self.clk.value(1)
        self.clk.value(0)

    def _latch_pulse(self):
        """Generate a latch pulse"""
        self.lat.value(1)
        self.lat.value(0)

    def _rgb565_to_rgb888(self, color):
        """Convert RGB565 to RGB888 components"""
        r = ((color >> 11) & 0x1F) << 3
        g = ((color >> 5) & 0x3F) << 2
        b = (color & 0x1F) << 3
        return r, g, b

    def _apply_brightness(self, value):
        """Apply brightness scaling to a color component"""
        return (value * self._brightness) >> 8

    def refresh(self):
        """
        Refresh the display by scanning all rows
        This should be called repeatedly in a loop
        """
        for row in range(self.rows):
            self._select_row(row)
            self.oe.value(1)  # Disable output while shifting data

            # Shift out data for this row (both upper and lower half)
            for col in range(self.width):
                # Get pixel colors from framebuffer
                # Upper half (top 32 rows)
                pixel_offset_upper = (row * self.width + col) * 2
                color_upper = (self.buffer[pixel_offset_upper + 1] << 8) | self.buffer[pixel_offset_upper]
                r1, g1, b1 = self._rgb565_to_rgb888(color_upper)

                # Lower half (bottom 32 rows)
                pixel_offset_lower = ((row + self.rows) * self.width + col) * 2
                color_lower = (self.buffer[pixel_offset_lower + 1] << 8) | self.buffer[pixel_offset_lower]
                r2, g2, b2 = self._rgb565_to_rgb888(color_lower)

                # Apply brightness
                r1 = self._apply_brightness(r1)
                g1 = self._apply_brightness(g1)
                b1 = self._apply_brightness(b1)
                r2 = self._apply_brightness(r2)
                g2 = self._apply_brightness(g2)
                b2 = self._apply_brightness(b2)

                # Simple 1-bit output (for basic operation)
                # For PWM/grayscale, you'd need BCM (Binary Code Modulation)
                self.r1.value(1 if r1 > 127 else 0)
                self.g1.value(1 if g1 > 127 else 0)
                self.b1.value(1 if b1 > 127 else 0)
                self.r2.value(1 if r2 > 127 else 0)
                self.g2.value(1 if g2 > 127 else 0)
                self.b2.value(1 if b2 > 127 else 0)

                self._clock_pulse()

            self._latch_pulse()
            self.oe.value(0)  # Enable output
            time.sleep_us(100)  # Display time per row

    def set_brightness(self, brightness):
        """
        Set display brightness

        Args:
            brightness: 0-255 (0=off, 255=full brightness)
        """
        self._brightness = max(0, min(255, brightness))

    def fill(self, color):
        """Fill entire display with color (RGB565 format)"""
        self.fb.fill(color)

    def pixel(self, x, y, color):
        """Set pixel at (x, y) to color (RGB565 format)"""
        self.fb.pixel(x, y, color)

    def text(self, string, x, y, color):
        """Draw text at (x, y) with color (RGB565 format)"""
        self.fb.text(string, x, y, color)

    def line(self, x1, y1, x2, y2, color):
        """Draw line from (x1, y1) to (x2, y2) with color"""
        self.fb.line(x1, y1, x2, y2, color)

    def rect(self, x, y, w, h, color, fill=False):
        """Draw rectangle"""
        if fill:
            self.fb.fill_rect(x, y, w, h, color)
        else:
            self.fb.rect(x, y, w, h, color)

    def blit(self, source_fb, x, y, key=-1):
        """Blit a framebuffer onto this display"""
        self.fb.blit(source_fb, x, y, key)

    @staticmethod
    def rgb888_to_rgb565(r, g, b):
        """Convert RGB888 (r, g, b) to RGB565 format"""
        r = (r >> 3) & 0x1F
        g = (g >> 2) & 0x3F
        b = (b >> 3) & 0x1F
        return (r << 11) | (g << 5) | b

    @staticmethod
    def color(r, g, b):
        """Create RGB565 color from r, g, b values (0-255)"""
        return HUB75Matrix.rgb888_to_rgb565(r, g, b)


class HUB75Display:
    """
    Higher-level display interface compatible with the original RGB_Api
    """

    def __init__(self, pin_config, width=64, height=64):
        """
        Initialize HUB75 display

        Args:
            pin_config: Pin configuration dictionary
            width: Display width (default 64)
            height: Display height (default 64)
        """
        self.matrix = HUB75Matrix(width, height, pin_config)
        self.width = width
        self.height = height
        self._running = False

    def start_refresh(self):
        """Start continuous refresh in background (requires threading)"""
        # Note: MicroPython threading support varies by build
        # For simple use, call refresh() in main loop
        self._running = True

    def stop_refresh(self):
        """Stop continuous refresh"""
        self._running = False

    def refresh_once(self):
        """Refresh display once (call this in a loop)"""
        self.matrix.refresh()

    def set_brightness(self, factor):
        """
        Set brightness as a factor (0.0 to 1.0)

        Args:
            factor: Brightness factor (0.0 = off, 1.0 = full)
        """
        brightness = int(factor * 255)
        self.matrix.set_brightness(brightness)

    def fill(self, color):
        """Fill display with color (RGB888 format 0xRRGGBB)"""
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        rgb565 = HUB75Matrix.rgb888_to_rgb565(r, g, b)
        self.matrix.fill(rgb565)

    def get_framebuffer(self):
        """Get the underlying framebuffer"""
        return self.matrix.fb

    def show(self):
        """Update display (compatibility method)"""
        # In continuous refresh mode, this would be automatic
        # For manual mode, user should call refresh_once() in loop
        pass
