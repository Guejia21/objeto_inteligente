import grovepi
try:
    relay_pin = 3
    grovepi.pinMode(relay_pin, "OUTPUT")
    if "value" in locals() or "value" in globals():
        grovepi.digitalWrite(relay_pin, int(value))
except Exception as e:
    print(f"Error: {e}")
