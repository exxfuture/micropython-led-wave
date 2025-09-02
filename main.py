# LED Wave Animation
# Controls X LEDs with wave brightness animation using abstraction layer

from time import sleep
from led_display import LEDDisplay as LEDController
# from led_physical import LEDPhysical as LEDController

# Animation parameters
MIN_PWM = 0.05      # % minimum brightness
MAX_PWM = 1.0      # 100% maximum brightness
WAVE_SPEED = 0.05   # Speed of wave movement

def main():
    """Main LED wave animation control."""
    print("LED Wave Animation Starting...")

    # Initialize LED display
    leds = LEDController(num_leds=6)

    # Wave animation variables
    wave_offset = 0.0

    try:
        while True:
            # Calculate and set PWM for each LED with linear wave effect
            for i in range(leds.get_num_leds()):
                # Calculate linear wave brightness for this LED
                # Each LED has a phase offset to create wave effect
                phase_offset = i / leds.get_num_leds()  # Phase offset (0.0 to 1.0)

                # Create linear wave using sawtooth pattern
                wave_position = (wave_offset + phase_offset) % 2.0  # 0 to 2.0 cycle

                if wave_position <= 1.0:
                    # Rising edge: 0 to 1
                    wave_value = wave_position
                else:
                    # Falling edge: 1 to 0
                    wave_value = 2.0 - wave_position

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
