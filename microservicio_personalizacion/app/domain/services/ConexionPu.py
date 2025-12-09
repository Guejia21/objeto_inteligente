from infrastructure.logging.Logging import logger
import os
from os import listdir
import requests
import time

from config.settings import settings


class ConexionPu:
     
    def __init__(self):
        #self.path =Paths.pathOWL
        pass
    
    def recuperarOntologia(self,listaMac,ip):
        rutaArchivo=""
        for mac in listaMac:
            try:
                print( "Probando con la Mac "+ mac)
                #print 'http://'+ip+':8080/RecuperarOntologia?mac='+identificador+'&tipo=owl'
                r = requests.get('http://'+ip+':8080/RecuperarOntologia?identificador='+mac+'&tipo=owl')
                resp = r.content
##                print resp
                if not resp == 'False':
                    if not os.path.exists(self.path):
                        os.mkdir(self.path, 0o777)
                    rutaArchivo = self.path +mac+".owl"
                    archivo=open(rutaArchivo,'wb')    
                    archivo.write(resp)            
                    archivo.close()
                    break
                    #return rutaArchivo
            except Exception as e:
                print( "No es posible conectar con el servidor de perfil usuario Clase Conexion Recuperar ontologia")
                return ""
        return rutaArchivo
    """ 
    def enviarOntologiaAobjeto(self,listaIp):
        for ip in listaIp:
            datos={
                "nombre": "UsuarioActual.owl"
                }
            usuarioActual=""
            for archivo in listdir(Paths.pathOWL):
                usuarioActual = archivo

            myfile = {'file': open(Paths.pathOWL+usuarioActual ,'rb').read()}
            headers={'Content-Type':"text/xml; charset=utf-8"}
            requests.post('http://'+ip+':80/RecibirOntologia', files=myfile, data=datos)
              
    def notificarSalidaDeUsuario(self, ip,osid):
        try:
            r = requests.get('http://'+ip+':8080/NotificarSalidaDeUsuario?osid='+osid)
            resp = r.content
            resp=str(resp)                    
                
        except Exception as e:
            print( e)
            print( "No es posible conectar con el servidor de perfil usuario Clase Conexion notificarSalidaDeUsuario")
    
    def enviarRegistroInteraccionUsuarioObjetoAlCoordinador(self, email,idDataStream, comando,osid, mac, dateInteraction):
        ipCoordinador = AppUtil.leerIpCoordinadorDesdeArchivo()
        try:
            r = requests.get('http://'+ipCoordinador+':80/RegistroInteraccionUsuarioObjeto?osid='+osid+'&idDataStream='+idDataStream+'&comando='+comando+'&email='+email+'&mac='+mac+'&dateInteraction='+dateInteraction)    
            print( colored("IpDelCoordinador "+'http://'+ipCoordinador+':80/RegistroInteraccionUsuarioObjeto?osid='+osid+'&idDataStream='+idDataStream+'&comando='+comando+'&email='+email+'&mac='+mac, 'red'))
            resp = r.content                
        except Exception as e:
            print( e)
            print( "No es posible conectar con el servidor de perfil usuario Clase Conexion notificarSalidaDeUsuario")
    """
    def enviarRegistroInteraccionUsuarioObjetoAlServidorPerfilUsuario(self, email,idDataStream, comando,osid, mac,  dateInteraction):
        try:
            if dateInteraction == "00/00/00 00:00:00":
                dateInteraction=str(time.strftime("%c"))
                dateInteraction = dateInteraction.replace(" ", "-" )
            #Se simula la peticion al servidor de perfil de usuario
            #r = requests.get('http://'+ AppUtil.ipServidorPerfilUsuario +':8080/RegistrarInteraction?osid='+osid+'&idDatastream='+idDataStream+'&comando='+comando+'&email='+email+'&mac='+mac +'&dateInteraction='+dateInteraction)
            logger.info("IpDelServidorPerfilU "+'http://'+ settings.IP_SERVIDOR_PERFIL_USUARIO +':8080/RegistrarInteraction?osid='+osid+'&idDatastream='+idDataStream+'&comando='+comando+'&email='+email+'&mac='+mac +'&dateInteraction='+dateInteraction)
            #resp = r.content                
            logger.info("Registro de interaccion enviado al servidor de perfil de usuario")
        except Exception as e:
            print( e)
            print( "No es posible conectar con el servidor de perfil usuario Clase Conexion notificarSalidaDeUsuario")
        
                    

    
