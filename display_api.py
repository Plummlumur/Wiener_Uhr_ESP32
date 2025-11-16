"""
Display Graphics API for ESP32 Wiener Uhr
==========================================
High-level graphics API compatible with the original CircuitPython RGB_Api.

This module provides an interface similar to the original project but adapted
for MicroPython on ESP32.
"""

import framebuf
import time
from hub75_esp32 import HUB75Matrix
from bmp_loader import load_bmp
from bdf_font import load_font, DefaultFont


class RGB_Api:
    """
    High-level graphics API for RGB matrix display

    Compatible with the original CircuitPython RGB_Api interface
    """

    def __init__(self, matrix_display, width=64, height=64):
        """
        Initialize graphics API

        Args:
            matrix_display: HUB75Matrix instance
            width: Display width
            height: Display height
        """
        self.display = matrix_display
        self.width = width
        self.height = height

        # Text settings
        self.txt_lines = ["", "", ""]
        self.txt_color = 0xFFFFFF  # RGB888
        self.txt_font = DefaultFont()
        self.txt_scale = 1
        self.line_spacing = 1.0
        self.txt_x = 1
        self.txt_y = 10
        self.txt_bg_color = 0x000000
        self.txt_bg_opacity = False

        # Background image
        self.has_background = False
        self.bg_image = None
        self.bg_path = None
        self._bg_palette_orig = None

        # Brightness
        self._brightness = 1.0

    def load_background(self, path="/bild.bmp"):
        """
        Load an 8-bit BMP background image

        Args:
            path: Path to BMP file
        """
        try:
            self.bg_image = load_bmp(path)
            self._bg_palette_orig = self.bg_image.palette.copy()
            self.has_background = True
            self.bg_path = path
            print(f"Background loaded: {path}")
        except Exception as e:
            print(f"Error loading background {path}: {e}")
            self.has_background = False

    def set_brightness(self, factor):
        """
        Set display brightness

        Args:
            factor: Brightness factor (0.0 to 1.0)
        """
        self._brightness = max(0.0, min(1.0, factor))

        # Apply to matrix
        brightness_byte = int(self._brightness * 255)
        self.display.set_brightness(brightness_byte)

        # Apply to background palette if present
        if self.has_background and self.bg_image:
            self.bg_image.set_brightness(self._brightness)

        # Update text color
        if not hasattr(self, '_txt_color_orig'):
            self._txt_color_orig = self.txt_color
        self.txt_color = self._dim_color(self._txt_color_orig, self._brightness)

    def _dim_color(self, color, factor):
        """Dim an RGB888 color by a factor"""
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        return (r << 16) | (g << 8) | b

    def _rgb888_to_rgb565(self, color):
        """Convert RGB888 to RGB565"""
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        return HUB75Matrix.rgb888_to_rgb565(r, g, b)

    def update_text(self):
        """Update display with current text and background"""
        # Clear framebuffer
        self.display.fill(0x0000)

        # Draw background if present
        if self.has_background and self.bg_image:
            bg_fb = self.bg_image.get_framebuffer()
            self.display.blit(bg_fb, 0, 0)

        # Draw text lines
        text_color_rgb565 = self._rgb888_to_rgb565(self.txt_color)
        y_offset = self.txt_y

        for i, line in enumerate(self.txt_lines):
            if not line:
                continue

            # Calculate line height based on font
            font_height = getattr(self.txt_font, 'font_height', 8)
            line_height = int(font_height * self.txt_scale * self.line_spacing)

            y_pos = int(y_offset + i * line_height)

            # Draw text
            if hasattr(self.txt_font, 'draw_text'):
                # Custom BDF font
                self.txt_font.draw_text(
                    self.display.fb,
                    line,
                    self.txt_x,
                    y_pos + font_height,  # Baseline adjustment
                    text_color_rgb565
                )
            else:
                # Fallback to built-in font
                self.display.text(line, self.txt_x, y_pos, text_color_rgb565)

    def clear(self):
        """Clear the display"""
        self.display.fill(0x0000)

    def show(self):
        """Update the physical display (compatibility method)"""
        # In the ESP32 version, refresh is handled in the main loop
        pass


class DisplayManager:
    """
    Manages display refresh in the background

    This class handles the continuous refresh needed for HUB75 displays
    """

    def __init__(self, matrix_display, refresh_rate=100):
        """
        Initialize display manager

        Args:
            matrix_display: HUB75Matrix instance
            refresh_rate: Refresh rate in Hz (default 100)
        """
        self.matrix = matrix_display
        self.refresh_interval_us = int(1000000 / refresh_rate)
        self._running = False
        self._last_refresh = 0

    def start(self):
        """Start display refresh"""
        self._running = True

    def stop(self):
        """Stop display refresh"""
        self._running = False

    def update(self):
        """
        Call this in the main loop to refresh the display

        This should be called as frequently as possible for smooth display
        """
        if self._running:
            current_time = time.ticks_us()
            if time.ticks_diff(current_time, self._last_refresh) >= self.refresh_interval_us:
                self.matrix.refresh()
                self._last_refresh = current_time

    def refresh_blocking(self, duration_ms=100):
        """
        Refresh display for a specific duration (blocking)

        Args:
            duration_ms: Duration to refresh in milliseconds
        """
        end_time = time.ticks_ms() + duration_ms
        while time.ticks_ms() < end_time:
            self.matrix.refresh()
