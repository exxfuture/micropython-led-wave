# Physical LED Abstraction Layer
# This class controls actual physical LEDs through PWM pins

from machine import Pin, PWM
import time

class LEDPhysical:
    """
    Abstraction layer for controlling physical LEDs through PWM.
    Compatible interface with LEDDisplay for easy switching.
    """
    
    def __init__(self, num_leds=6, led_pins=None):
        """
        Initialize physical LEDs with PWM control.
        
        Args:
            num_leds (int): Number of LEDs to control
            led_pins (list): List of GPIO pin numbers for LEDs
        """
        self.num_leds = num_leds
        
        # Default pin assignments if none provided
        if led_pins is None:
            # Example pins - adjust based on your hardware
            led_pins = [2, 4, 5, 18, 19, 21]  # GPIO pins for LEDs
        
        # Ensure we don't exceed available pins
        self.led_pins = led_pins[:num_leds]
        self.num_leds = len(self.led_pins)
        
        # Initialize PWM objects for each LED
        self.leds = []
        for pin_num in self.led_pins:
            pwm_led = PWM(Pin(pin_num, Pin.OUT))
            pwm_led.freq(1000)  # 1kHz PWM frequency
            pwm_led.duty(0)     # Start with LEDs off
            self.leds.append(pwm_led)
        
        # FPS tracking
        self.frame_count = 0
        self.fps_update_interval = 50
        self.start_time = time.ticks_ms()
        
        print(f"Physical LEDs initialized on pins: {self.led_pins}")
        print(f"Number of LEDs: {self.num_leds}")
    
    def set_pwm(self, led_index, pwm_value):
        """
        Set the PWM (brightness) for a specific LED.
        
        Args:
            led_index (int): Index of the LED (0 to num_leds-1)
            pwm_value (float): PWM value from 0.0 to 1.0
        """
        if 0 <= led_index < len(self.leds):
            # Convert 0.0-1.0 range to 0-1023 duty cycle
            duty_value = int(pwm_value * 1023)
            duty_value = max(0, min(1023, duty_value))  # Clamp to valid range
            
            # Set PWM duty cycle
            self.leds[led_index].duty(duty_value)
    
    def update_fps_display(self):
        """Update the FPS display (console only for physical LEDs)."""
        self.frame_count += 1
        if self.frame_count % self.fps_update_interval == 0:
            current_time = time.ticks_ms()
            elapsed_time = time.ticks_diff(current_time, self.start_time) / 1000.0
            fps = self.fps_update_interval / elapsed_time
            
            # Print FPS to console
            print(f"FPS: {fps:.1f}")
            
            # Reset for next FPS calculation
            self.start_time = current_time
    
    def get_num_leds(self):
        """Get the number of LEDs."""
        return self.num_leds
    
    def cleanup(self):
        """Clean up resources - turn off all LEDs."""
        for led in self.leds:
            led.duty(0)  # Turn off LED
            led.deinit()  # Deinitialize PWM
        print("Physical LEDs cleaned up")

# Example usage:
# To switch from display LEDs to physical LEDs, simply change the import in main.py:
# 
# Instead of:
#   from led_display import LEDDisplay as LEDController
# 
# Use:
#   from led_physical import LEDPhysical as LEDController
#
# Then in main.py:
#   leds = LEDController(num_leds=6)
#
# The rest of the code remains exactly the same!
