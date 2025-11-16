"""
BMP Image Loader for MicroPython ESP32
=======================================
Loads 8-bit indexed BMP images with palette support.

This loader is compatible with the 8-bit BMP format used in the original
Wiener Uhr project.
"""

import framebuf


class BMPImage:
    """Represents a loaded BMP image with palette"""

    def __init__(self, width, height, data, palette):
        """
        Initialize BMP image

        Args:
            width: Image width in pixels
            height: Image height in pixels
            data: Pixel data (8-bit indexed)
            palette: Color palette (list of RGB565 colors)
        """
        self.width = width
        self.height = height
        self.data = data
        self.palette = palette
        self._original_palette = palette.copy()

    def get_framebuffer(self):
        """Create a framebuffer from the image data"""
        # Convert indexed data to RGB565
        fb_data = bytearray(self.width * self.height * 2)
        for i, index in enumerate(self.data):
            if index < len(self.palette):
                color = self.palette[index]
                fb_data[i * 2] = color & 0xFF
                fb_data[i * 2 + 1] = (color >> 8) & 0xFF

        return framebuf.FrameBuffer(fb_data, self.width, self.height, framebuf.RGB565)

    def reset_palette(self):
        """Reset palette to original colors"""
        self.palette = self._original_palette.copy()

    def set_brightness(self, factor):
        """
        Adjust palette brightness

        Args:
            factor: Brightness factor (0.0 to 1.0)
        """
        factor = max(0.0, min(1.0, factor))
        for i, color in enumerate(self._original_palette):
            # Extract RGB565 components
            r = (color >> 11) & 0x1F
            g = (color >> 5) & 0x3F
            b = color & 0x1F

            # Scale to 8-bit, apply brightness, scale back
            r8 = (r << 3) | (r >> 2)
            g8 = (g << 2) | (g >> 4)
            b8 = (b << 3) | (b >> 2)

            r8 = int(r8 * factor)
            g8 = int(g8 * factor)
            b8 = int(b8 * factor)

            # Convert back to RGB565
            r = (r8 >> 3) & 0x1F
            g = (g8 >> 2) & 0x3F
            b = (b8 >> 3) & 0x1F

            self.palette[i] = (r << 11) | (g << 5) | b


def load_bmp(filename):
    """
    Load an 8-bit indexed BMP file

    Args:
        filename: Path to BMP file

    Returns:
        BMPImage: Loaded image with palette

    Raises:
        ValueError: If BMP format is not supported
    """
    with open(filename, 'rb') as f:
        # Read BMP header
        header = f.read(54)

        # Check BMP signature
        if header[0:2] != b'BM':
            raise ValueError("Not a valid BMP file")

        # Parse header
        file_size = int.from_bytes(header[2:6], 'little')
        pixel_offset = int.from_bytes(header[10:14], 'little')
        dib_header_size = int.from_bytes(header[14:18], 'little')
        width = int.from_bytes(header[18:22], 'little')
        height = int.from_bytes(header[22:26], 'little')
        bits_per_pixel = int.from_bytes(header[28:30], 'little')
        compression = int.from_bytes(header[30:34], 'little')

        # Validate format
        if bits_per_pixel != 8:
            raise ValueError(f"Only 8-bit BMP supported (got {bits_per_pixel}-bit)")

        if compression != 0:
            raise ValueError("Compressed BMP not supported")

        # Read color palette (256 colors, 4 bytes each: B, G, R, Reserved)
        palette_size = 256
        palette_data = f.read(palette_size * 4)
        palette = []

        for i in range(palette_size):
            offset = i * 4
            b = palette_data[offset]
            g = palette_data[offset + 1]
            r = palette_data[offset + 2]

            # Convert RGB888 to RGB565
            r565 = (r >> 3) & 0x1F
            g565 = (g >> 2) & 0x3F
            b565 = (b >> 3) & 0x1F
            rgb565 = (r565 << 11) | (g565 << 5) | b565
            palette.append(rgb565)

        # Seek to pixel data
        f.seek(pixel_offset)

        # Read pixel data (BMP is stored bottom-up)
        row_size = ((width * bits_per_pixel + 31) // 32) * 4  # Row size with padding
        pixel_data = bytearray(width * height)

        for y in range(height):
            row = f.read(row_size)
            # Copy row (BMP is bottom-up, so reverse Y)
            dest_y = height - 1 - y
            for x in range(width):
                pixel_data[dest_y * width + x] = row[x]

        return BMPImage(width, height, pixel_data, palette)


def load_image(filename):
    """
    Load image file (wrapper for compatibility)

    Args:
        filename: Path to image file

    Returns:
        tuple: (BMPImage, palette) for compatibility with original API
    """
    img = load_bmp(filename)
    return img, img.palette
