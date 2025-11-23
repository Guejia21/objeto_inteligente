import grovepi
try:
    grovepi.digitalWrite(3, 0)
    grovepi.digitalWrite(4, 0)
except Exception as e:
    print(f"Error: {e}")
