import grovepi
def main(comparador, variable):
     try:
         relay_pin = 3
         grovepi.pinMode(relay_pin, "OUTPUT")
         if(comparador == "igual"):
             if(int(variable) == 1):
                 grovepi.digitalWrite(relay_pin, 1)
 
             if(int(variable) == 0):
                 grovepi.digitalWrite(relay_pin, 0)
     except Exception as e:
         print(f"Error: {e}")
