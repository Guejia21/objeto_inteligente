import grovepi
try:
    relay_pin = 3
    grovepi.pinMode(relay_pin, "OUTPUT")
    grovepi.digitalWrite(relay_pin, 0)
except Exception as e:
    print(f"Error: {e}")
