import grovepi
def main(comparador, variable):
     try:
         led_pin = 4
         grovepi.pinMode(led_pin, "OUTPUT")
         if(comparador == "igual"):
             if(int(variable) == 1):
                 grovepi.digitalWrite(led_pin, 1)

             if(int(variable) == 0):
                 grovepi.digitalWrite(led_pin, 0)
     except Exception as e:
         print(f"Error: {e}")