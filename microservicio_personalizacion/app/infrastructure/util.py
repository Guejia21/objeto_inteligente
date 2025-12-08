from config.settings import settings
def guardarIpCoordinadorEnArchivo(ipCoordinador):    
    archivo=open(settings.PATH_IP_COORDINADOR,'w')
    archivo.write(ipCoordinador)            
    archivo.close()
