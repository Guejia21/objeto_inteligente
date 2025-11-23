import grovepi
try:
    relay_pin = 3
    grovepi.pinMode(relay_pin, "OUTPUT")
    value = grovepi.digitalRead(relay_pin)
except Exception as e:
    print(f"Error: {e}")
    value = 0
