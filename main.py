# ESP32 CYD LED Wave Animation
# Controls 6 LEDs with wave brightness animation using abstraction layer

import math
import time
from led_display import LEDDisplay

# Animation parameters
MIN_PWM = 0.1      # 10% minimum brightness
MAX_PWM = 1.0      # 100% maximum brightness
WAVE_SPEED = 0.1   # Speed of wave movement

def main():
    """Main LED wave animation control."""
    print("ESP32 CYD LED Wave Animation Starting...")

    # Initialize LED display (6 LEDs)
    leds = LEDDisplay(num_leds=6, led_radius=8, padding=5)

    # Wave animation variables
    wave_offset = 0.0

    try:
        while True:
            # Calculate and set PWM for each LED with wave effect
            for i in range(leds.get_num_leds()):
                # Calculate wave brightness for this LED
                # Each LED has a phase offset to create wave effect
                phase = (i * 2.0 * math.pi) / leds.get_num_leds()  # Phase offset
                wave_value = (1.0 + math.sin(wave_offset + phase)) / 2.0  # 0 to 1

                # Map wave value to PWM range
                pwm_value = MIN_PWM + wave_value * (MAX_PWM - MIN_PWM)

                # Set PWM for this LED
                leds.set_pwm(i, pwm_value)

            # Update wave offset for animation
            wave_offset += WAVE_SPEED

            # Update FPS display
            leds.update_fps_display()

    except KeyboardInterrupt:
        print("Animation stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        leds.cleanup()
        print("Program ended")

# Run the main program
if __name__ == "__main__":
    main()
