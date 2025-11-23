import grovepi
try:
    led_pin = 4
    grovepi.pinMode(led_pin, "OUTPUT")
    grovepi.digitalWrite(led_pin, 0)
except Exception as e:
    print(f"Error: {e}")
