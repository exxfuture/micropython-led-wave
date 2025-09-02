# LED Display Abstraction Layer
# This class abstracts LED control to work with either display circles or physical LEDs

from machine import Pin, SPI
import time
from ili9341 import Display, color565
from xglcd_font import XglcdFont

class LEDDisplay:
    """
    Abstraction layer for controlling LEDs through display circles.
    Can be easily swapped with physical LED implementation.
    """
    
    def __init__(self, num_leds=6, led_radius=8, padding=5):
        """
        Initialize the LED display with circles on screen.
        
        Args:
            num_leds (int): Number of LEDs to simulate
            led_radius (int): Radius of each circle LED
            padding (int): Padding between LEDs
        """
        self.num_leds = num_leds
        self.led_radius = led_radius
        self.padding = padding
        self.base_color = color565(255, 255, 255)  # White base color
        
        # Initialize display
        self._init_display()
        
        # Calculate LED positions
        self.led_positions = self._calculate_led_positions()
        
        # FPS tracking
        self.frame_count = 0
        self.fps_update_interval = 50
        self.start_time = time.ticks_ms()
        self.font = self._load_font()
        
        print(f"LED Display initialized with {len(self.led_positions)} LEDs")
        print(f"LED positions: {self.led_positions}")
    
    def _init_display(self):
        """Initialize the display hardware."""
        display_spi = SPI(1, baudrate=60000000, sck=Pin(14), mosi=Pin(13))
        self.display = Display(display_spi, dc=Pin(2), cs=Pin(15), rst=Pin(0), width=320, height=240)
        
        # Turn on display backlight
        backlight = Pin(21, Pin.OUT)
        backlight.on()
        
        # Clear display
        self.display.clear(color565(0, 0, 0))
        print("Display initialized and cleared")
    
    def _calculate_led_positions(self):
        """Calculate the X positions for LEDs in a horizontal line."""
        total_width = self.num_leds * (self.led_radius * 2) + (self.num_leds - 1) * self.padding
        start_x = (self.display.width - total_width) // 2 + self.led_radius
        center_y = self.display.height // 2
        
        positions = []
        for i in range(self.num_leds):
            x = start_x + i * (self.led_radius * 2 + self.padding)
            if x + self.led_radius <= self.display.width:  # Ensure LED fits
                positions.append(x)
        
        return positions
    
    def _load_font(self):
        """Load font for FPS display."""
        try:
            font = XglcdFont('fonts/FixedFont5x8.c', 5, 8)
            print("Font loaded successfully")
            return font
        except:
            print("Font not found, using built-in text")
            return None
    
    def _adjust_brightness_rgb565(self, color, brightness):
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
    
    def _draw_circle_fast(self, x0, y0, radius, color):
        """
        Draw a filled circle immediately using optimized block drawing.
        """
        # Calculate bounding box
        x_min = max(0, x0 - radius)
        x_max = min(self.display.width - 1, x0 + radius)
        y_min = max(0, y0 - radius)
        y_max = min(self.display.height - 1, y0 + radius)
        
        width = x_max - x_min + 1
        height = y_max - y_min + 1
        
        # Pre-calculate values to avoid repeated calculations
        radius_squared = radius * radius
        black_color = color565(0, 0, 0)
        
        # Create buffer
        buffer_size = width * height * 2
        pixel_data = bytearray(buffer_size)
        
        # Optimized buffer filling
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
                
                # Store in buffer
                pixel_data[pixel_index] = pixel_color >> 8
                pixel_data[pixel_index + 1] = pixel_color & 0xFF
                pixel_index += 2
        
        # Draw entire block at once
        self.display.block(x_min, y_min, x_max, y_max, pixel_data)
    
    def set_pwm(self, led_index, pwm_value):
        """
        Set the PWM (brightness) for a specific LED.
        
        Args:
            led_index (int): Index of the LED (0 to num_leds-1)
            pwm_value (float): PWM value from 0.0 to 1.0
        """
        if 0 <= led_index < len(self.led_positions):
            # Convert PWM to color with brightness
            current_color = self._adjust_brightness_rgb565(self.base_color, pwm_value)
            
            # Draw the LED circle
            center_y = self.display.height // 2
            self._draw_circle_fast(self.led_positions[led_index], center_y, self.led_radius, current_color)
    
    def update_fps_display(self):
        """Update the FPS display on screen."""
        self.frame_count += 1
        if self.frame_count % self.fps_update_interval == 0:
            current_time = time.ticks_ms()
            elapsed_time = time.ticks_diff(current_time, self.start_time) / 1000.0
            fps = self.fps_update_interval / elapsed_time
            
            # Print FPS to console
            print(f"FPS: {fps:.1f}")
            
            # Display FPS at bottom of screen
            fps_text = f"FPS: {fps:.1f}"
            fps_color = color565(255, 255, 0)  # Yellow text
            black_bg = color565(0, 0, 0)      # Black background
            
            # Clear previous FPS text area
            self.display.fill_rectangle(0, self.display.height - 25, 120, 25, black_bg)
            
            # Draw FPS text using font library if available
            if self.font:
                self.display.draw_text(5, self.display.height - 20, fps_text, self.font, fps_color, black_bg)
            else:
                self.display.draw_text8x8(5, self.display.height - 15, fps_text, fps_color, black_bg, 0)
            
            # Reset for next FPS calculation
            self.start_time = current_time
    
    def get_num_leds(self):
        """Get the number of LEDs."""
        return len(self.led_positions)
    
    def cleanup(self):
        """Clean up resources."""
        self.display.clear(color565(0, 0, 0))
        print("LED Display cleaned up")
