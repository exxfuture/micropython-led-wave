# ESP32 CYD Test - Single Circle Brightness Animation
# Test immediate circle drawing with brightness changes

from machine import Pin, SPI
import time
import math
from ili9341 import Display, color565
from xglcd_font import XglcdFont

# Display configuration for ESP32 CYD
display_spi = SPI(1, baudrate=60000000, sck=Pin(14), mosi=Pin(13))
display = Display(display_spi, dc=Pin(2), cs=Pin(15), rst=Pin(0), width=240, height=320)

# Turn on display backlight
backlight = Pin(21, Pin.OUT)
backlight.on()

def get_pwm_value(brightness):
    color = color565(255, 255, 255)
    """
    Adjust the brightness of an RGB565 color while maintaining hue.

    Args:
        color (int): RGB565 color value
        brightness (float): Brightness factor (0.0 to 1.0)

    Returns:
        int: RGB565 color with adjusted brightness
    """
    # Extract RGB components from RGB565
    r = (color >> 11) & 0x1F  # 5 bits
    g = (color >> 5) & 0x3F   # 6 bits
    b = color & 0x1F          # 5 bits

    # Convert to 8-bit values
    r8 = (r * 255) // 31
    g8 = (g * 255) // 63
    b8 = (b * 255) // 31

    # Apply brightness
    r8 = int(r8 * brightness)
    g8 = int(g8 * brightness)
    b8 = int(b8 * brightness)

    # Clamp values
    r8 = min(255, max(0, r8))
    g8 = min(255, max(0, g8))
    b8 = min(255, max(0, b8))

    # Convert back to RGB565
    return color565(r8, g8, b8)

def draw_circle_fast(x0, y0, radius, color):
    """
    Draw a filled circle immediately using optimized block drawing.
    Optimizations: smaller buffer, pre-calculated values, efficient loops.
    """
    # Calculate bounding box
    x_min = max(0, x0 - radius)
    x_max = min(display.width - 1, x0 + radius)
    y_min = max(0, y0 - radius)
    y_max = min(display.height - 1, y0 + radius)

    width = x_max - x_min + 1
    height = y_max - y_min + 1

    # Pre-calculate values to avoid repeated calculations
    radius_squared = radius * radius
    black_color = color565(0, 0, 0)

    # Create buffer - this is the bottleneck, but necessary for immediate drawing
    buffer_size = width * height * 2
    pixel_data = bytearray(buffer_size)

    # Optimized buffer filling with minimal calculations
    pixel_index = 0
    for y in range(height):
        actual_y = y_min + y
        dy = actual_y - y0
        dy_squared = dy * dy

        for x in range(width):
            actual_x = x_min + x
            dx = actual_x - x0

            # Fast distance check
            if dx * dx + dy_squared <= radius_squared:
                pixel_color = color
            else:
                pixel_color = black_color

            # Store in buffer (optimized)
            pixel_data[pixel_index] = pixel_color >> 8
            pixel_data[pixel_index + 1] = pixel_color & 0xFF
            pixel_index += 2

    # Draw entire block at once - immediate appearance
    display.block(x_min, y_min, x_max, y_max, pixel_data)

def main():
    """Test immediate circle drawing with brightness animation."""
    print("ESP32 CYD Circle Brightness Test Starting...")

    # Clear display
    display.clear(color565(0, 0, 0))
    print("Display cleared")

    # 6 Circles parameters
    num_circles = 6
    circle_radius = 8  # Smaller circles for better performance
    padding = 5
    base_color = color565(255, 255, 255)  # White base color

    # Calculate circle positions in a horizontal line
    total_width = num_circles * (circle_radius * 2) + (num_circles - 1) * padding
    start_x = (display.width - total_width) // 2 + circle_radius
    center_y = display.height // 2

    circle_positions = []
    for i in range(num_circles):
        x = start_x + i * (circle_radius * 2 + padding)
        if x + circle_radius <= display.width:  # Ensure circle fits
            circle_positions.append(x)

    print(f"Drawing {len(circle_positions)} circles with radius {circle_radius}")
    print(f"Circle positions: {circle_positions}")

    # Animation parameters
    min_brightness = 0.1  # 10%
    max_brightness = 1.0  # 100%
    brightness_step = 0.02  # How much to change brightness per frame

    print("Running wave brightness animation at maximum speed")

    # Wave animation variables
    wave_offset = 0.0  # Wave animation offset
    wave_speed = 0.1   # Speed of wave movement

    try:
        while True:
            # Draw all 6 circles with wave brightness effect
            for i, circle_x in enumerate(circle_positions):
                # Calculate wave brightness for this circle
                # Each circle has a phase offset to create wave effect
                phase = (i * 2.0 * math.pi) / len(circle_positions)  # Phase offset
                wave_value = (1.0 + math.sin(wave_offset + phase)) / 2.0  # 0 to 1

                # Map wave value to brightness range
                brightness = min_brightness + wave_value * (max_brightness - min_brightness)

                # Calculate current color with brightness
                current_color = adjust_brightness_rgb565(base_color, brightness)

                # Draw circle with new brightness immediately
                draw_circle_fast(circle_x, center_y, circle_radius, current_color)

            # Update wave offset for animation
            wave_offset += wave_speed

    except KeyboardInterrupt:
        print("Animation stopped by user")

    print("Test complete")

# Run the test
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Test interrupted")
        display.clear(color565(0, 0, 0))
