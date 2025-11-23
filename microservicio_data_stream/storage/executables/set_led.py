import grovepi
try:
    led_pin = 4
    grovepi.pinMode(led_pin, "OUTPUT")
    if "value" in locals() or "value" in globals():
        grovepi.digitalWrite(led_pin, int(value))
except Exception as e:
    print(f"Error: {e}")
