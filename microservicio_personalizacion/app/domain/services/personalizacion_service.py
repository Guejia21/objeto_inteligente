"""
    @file personalizacion_service.py
    @brief Servicio de aplicación para gestión de personalización de usuario.
    @details
    Implementa la lógica de negocio para:
    - Gestión de preferencias/contratos ECA del usuario
    - Carga y activación de ontologías de perfil
    - Coordinación con microservicio de automatización
    - Registro de interacciones usuario-objeto
    
    Patrón: Application Service + Domain Service
    
    Dependencias externas:
    - micro_gestion_conocimiento: para carga de ontologías
    - micro_automatizacion: para creación/gestión de ECAs
    - microservicio_data_stream: para registros de interacción
    
    @author Sistema Objeto Inteligente
    @version 1.0
    @date 2025-01-10
    
    @see PersonalizacionService Para endpoints
    @see ontology_service Para operaciones de ontología
    @see eca_service Para gestión de reglas ECA
"""

import json
import logging
import os

import requests
from infrastructure import util
from datetime import time

from fastapi import UploadFile
from fastapi.responses import JSONResponse

from config.settings import settings
from domain.services import ontology_service
import threading

from domain.services import eca_service
from application.dtos.request_dtos import MakeContractRequest, RegistroInteraccionDTO
from domain.services.ConexionPu import ConexionPu 
from infrastructure.logging.ILogPanelMQTT import ILogPanelMQTT
from infrastructure.logging.Logging import logger

class PersonalizacionService:
    """
        @class PersonalizacionService
        @brief Servicio de aplicación para gestión de preferencias e interacciones de usuario.
        
        @details
        Responsabilidades:
        - Orquestar carga de ontologías de perfil de usuario
        - Coordinar creación de preferencias/ECAs con micro_automatizacion
        - Activar/desactivar ECAs del usuario
        - Registrar interacciones usuario-objeto para personalización
        - Mantener conexión con servidor de perfil de usuario (ConexionPu)
        
        Atributos:
        - osid: ID del objeto inteligente activo
        - ipServidorPU: dirección del servidor de perfil de usuario
        - path: ruta donde se guardan las ECAs
        - conexion_pu: cliente para comunicación con servidor perfil
        - Log: cliente MQTT para logging distribuido
        
        @note Esta clase coordina múltiples microservicios de forma distribuida.
              Considerar implementar sagas/compensación para operaciones compuestas.
        
        @author Sistema Objeto Inteligente
        @date 2025-01-10
    """
    def __init__(self, log = ILogPanelMQTT):
        """
            @brief Constructor del servicio de personalización.
            
            @param log Instancia del cliente MQTT para logging distribuido.
            
            @details
            Inicializa conexiones a servicios externos y configura rutas.
        """
        self.osid = ontology_service.get_osid()
        self.ipServidorPU = "http://localhost"  # Dirección del servidor de perfil de usuario        
        self.path =settings.PATH_ECAS
        self.conexion_pu = ConexionPu()
        self.Log = log
    async def recibir_ontologia(self,file:UploadFile, nombre: str, ipCoordinador: str) -> JSONResponse:
        """
            @brief Recibe una ontología desde el coordinador y la envía al microservicio de ontologías.

            @param file Archivo .owl con la ontología de usuario.
            @param nombre Identificador/nombre de la ontología.
            @param ipCoordinador IP del coordinador que envía la ontología (para tracking).

            @return JSONResponse con status 200 si exitoso, o error 400/500.
            
            @exception ValueError Si el archivo no es .owl.
            @exception RuntimeError Si falla el envío a micro_gestion_conocimiento.
            
            @details
            Flujo:
            1. Valida que el archivo sea .owl
            2. Delega carga en ontology_service (que se comunica con micro_gestion_conocimiento)
            3. Guarda IP del coordinador en archivo (para auditoría)
            4. Activa ECAs del usuario actual
            
            @note Esta operación es distribuida: coordina con micro_gestion_conocimiento
                  y micro_automatizacion. Considerar saga si falla en mitad.
            
            @see ontology_service.cargar_ontologia()
            @see activarEcasUsuario()
        """
        logger.info(f"Recibiendo ontología: {nombre} desde {ipCoordinador}")
        
        # Validar tipo de archivo
        if not file.filename.endswith('.owl'):
            return JSONResponse(
                status_code=400,
                content={"error": "Tipo de archivo inválido. Se espera un archivo .owl"}
            )
        # Enviar la ontología al microservicio de ontologías
        if ontology_service.cargar_ontologia(file, nombre, ipCoordinador):
            logger.info(f"Ontología {nombre} enviada exitosamente al microservicio de ontologías")
            util.guardarIpCoordinadorEnArchivo(ipCoordinador)
            self.activarEcasUsuario()
            return JSONResponse(
                status_code=200,
                content={"mensaje": "Ontología recibida y enviada al microservicio de ontologías exitosamente"}
            )
        else:
            logger.error(f"Error enviando ontología {nombre} al microservicio de ontologías")
            return JSONResponse(
                status_code=500,
                content={"error": "Error enviando ontología al microservicio de ontologías"}
            )    
    async def crear_preferencia(self, data:MakeContractRequest) -> JSONResponse:
        """
            @brief Crea una nueva preferencia/contrato ECA para el usuario.
            
            @param data DTO MakeContractRequest con definición del contrato.
            
            @return JSONResponse con status 200 si exitoso, o error 400/500.
            
            @exception ValueError Si email no coincide con usuario actual.
            @exception RuntimeError Si falla comunicación con micro_automatizacion.
            
            @details
            Flujo:
            1. Valida que el email del DTO coincida con el usuario activo
            2. Envía solicitud POST a micro_automatizacion
            3. Si es exitoso, registra preferencia en ontología de usuario
            
            @note Operación distribuida: requiere coordinación con micro_automatizacion.
                  Si micro_automatizacion responde error, la preferencia no se registra.
            
            @see MakeContractRequest DTO
            @see settings.AUTOMATIZACION_MS_URL Para endpoint remoto
        """
        if ontology_service.consultar_email_usuario() != data.email:
            logger.error("El email proporcionado no coincide con el usuario activo")
            return JSONResponse(
                status_code=400,
                content={"error": "El email proporcionado no coincide con el usuario activo"}
            )
         # Enviar solicitud al microservicio de automatización
         # Construir la URL del microservicio de automatización
         # Enviar la solicitud POST al microservicio de automatización
         # Manejar la respuesta del microservicio de automatización
         # Registrar la preferencia en la ontología del usuario si la creación fue exitosa
         # Retornar la respuesta adecuada al cliente
         # Construir la URL del microservicio de automatización
        try:
            response = requests.post(
                f"{settings.AUTOMATIZACION_MS_URL}",
                json=data.model_dump(),
                timeout=30.0
                )
            if response.status_code == 200:
                return JSONResponse(
                    status_code=200,
                    content={"mensaje": "Preferencia creada exitosamente"}
                )
            else:
                logger.error(f"Error al crear preferencia: {response.text}")
                return JSONResponse(
                    status_code=response.status_code,
                    content={"error": "Error al crear preferencia en el microservicio de automatización"}
                )
        except requests.RequestException as e:
            logger.error(f"Error al crear preferencia: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Error al comunicarse con el microservicio de automatización"}
            )
    # Métodos adaptados desde ModuloDePersonalizacion, debido a que no se tiene comunicacion con el servidor de PU
    # ni a la ontologia PU, no se pueden probar    
    def activarEcasUsuario(self):        
        ##Cada Usuario va a tener un archivo email.txt donde se almacena el nombre del ECA y su estado.        
        self.user_eca = ontology_service.consultar_email_usuario()
        if self.user_eca == "":
            logger.info("No se pudo consultar el email del usuario desde el microservicio de ontologías")
            return        
        logger.info( "BIENVENIDO " + self.user_eca)
        ##Consulta los Ecas que tiene la ontologia del Usuario
        ##OjO Cambias esto >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        try:
            logger.info( time.ctime())
            logger.info(self.ipServidorPU + ':8080/ConsultarEcasPorObjeto?email='+self.user_eca+'&osid='+self.osid)
            r = requests.get(self.ipServidorPU + ':8080/ConsultarEcasPorObjeto?email=' + self.user_eca + '&osid=' + self.osid)
            resp = r.content
            self.ecasUsuario  = json.loads(resp)
            logger.info("**************************Ecas Usuario*********************************************** ")
            for iten in self.ecasUsuario:
                logger.info(iten['name_eca']+" "+iten['state_eca'])
            
            logger.info( time.ctime())
        except:
            logger.error("Error en el modulo de personalizacion no se puede comunicar con el servidor de personalizacion de usuario ")
            self.ecasUsuario  = ontology_service.consultar_lista_preferencias_por_osid(self.osid) ## Si no se puede comunicar con el servidor que las consulte localmente
            if len(self.ecasUsuario) == 0:
                logger.info("Desde Modulo personalizacion NO existen ECAS para el usuario "+self.user_eca)
                return
      ##OjO Cambias esto >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        self.pathEcasUsuario = self.path + self.user_eca +".txt"
        if not os.path.exists(self.pathEcasUsuario):
            logger.info("Desde Modulo personalizacion NO existe el archivo "+self.pathEcasUsuario)
            archivo=open(self.pathEcasUsuario,'wb')    
            archivo.close()
        ecasArchivo = [] ## Contiene diccionarios {"eca_name", "eca_state"}
        ecasArchivo = self.ecasArchivoADiccionario()
##listaEcasCrear [{'name_event_resource': 'temperatura', 'unit_action': 'None', 'type_variable_action': 'bool', 'comparator_action': 'igual', 'id_action_object': '708637323', 'ip_action_object': '192.168.123.104', 'name_eca': 'subirTemperatura', 'end_date_activity': '', 'variable_condition': '20', 'comparator_condition': 'igual', 'meaning_condition': 'hace calor', 'state_eca': 'on', 'name_action_object': 'Regulador Temperatura', 'id_action_resource': 'ventilador', 'start_date_activity': '', 'name_activity': '', 'meaning_action': 'encender ventilador', 'name_event_object': 'Regulador Temperatura', 'id_event_resource': 'temperatura', 'variable_action': '1', 'ip_event_object': '192.168.123.104', 'unit_condition': '%', 'id_event_object': '708637323', 'name_action_resource': 'ventilador', 'type_variable_condition': 'float'}]
        listaEcasEliminar = []
        listaEcasIgualEstado = []
        listaEcasModificarEstado = []
        listaEcasCrear = []
        posicionesEcasEncontrados = []
        for item in self.ecasUsuario:
            posicion = self.posicionValor(ecasArchivo, "name_eca", item["name_eca"])
            if  posicion != -1: ##Si el eca del archivo esta en los del usuario, hay que activarlo osea ecaArchivo en listaEcasUsuario
                itemEcaArchivo = ecasArchivo[posicion]                
                logger.info(item)                
                logger.info(itemEcaArchivo)
                if itemEcaArchivo["state_eca"] == item['state_eca']:
                    listaEcasIgualEstado.append(item)
                else:
                    listaEcasModificarEstado.append(item)
                posicionesEcasEncontrados.append(posicion)
            else: ##Esta en los ecas del usuario, pero no el el archivo
                listaEcasCrear.append(item)
        i = 0
        for item in ecasArchivo:
            if not i in posicionesEcasEncontrados:
                listaEcasEliminar.append(ecasArchivo[i])
            i = i + 1
            
        logger.info("Desde modulo de personalizacion ECAS A CREAR")
        for iten in listaEcasCrear:
            logger.info(iten['name_eca'])        
        logger.info("Desde modulo de personalizacion lista ECAS A MODIFICAR ")
        for iten in listaEcasModificarEstado:
            logger.info(iten['name_eca'])        
        logger.info("Desde modulo de personalizacion lista ECAS A ELIMINAR ")
        for iten in listaEcasEliminar:
            logger.info(iten['name_eca'])        
        logger.info("Desde modulo de personalizacion lista ECAS A LANZAR")
        for iten in listaEcasIgualEstado:
            logger.info(iten['name_eca'])                    
        hiloCrearEcas = threading.Thread(target = self.crearEcas, name="HiloCrearEcas", args =(listaEcasCrear,))
        hiloinicializarEcasUsuario = threading.Thread(target = self.inicializarEcasUsuario, name="HiloInicializarEcasUsuario", args =(listaEcasIgualEstado,))
        hiloEliminarEcasUsurio = threading.Thread(target = self.eliminarEcas, name="HiloEliminarEcasUsurio", args =(listaEcasEliminar,))
##
        hiloCrearEcas.start()
        hiloinicializarEcasUsuario.start()
        hiloEliminarEcasUsurio.start()
        ##Sobreescribo el archivo para que solo tenga los ecas de la ontologia del usuario
        archivo=open(self.pathEcasUsuario,'w+')
        listaEcasArchivo = listaEcasCrear + listaEcasModificarEstado + listaEcasIgualEstado
        for item in listaEcasArchivo :
            linea = item["name_eca"] + "," + item["state_eca"] + "\n"
            archivo.write(linea)
        archivo.close()
        
    def desactivarEcasUsuarioActual(self)->JSONResponse:
        ##Cada Usuario va a tener un archivo email.txt donde se almacena el nombre del ECA y su estado.                
        self.user_eca = ontology_service.consultar_email_usuario()
        if self.user_eca == "":
            logger.error("El usuario no existe en la ontologia PU")
            return JSONResponse(content={"error": "No se pudo consultar el email del usuario"}, status_code=500)
        self.pathEcasUsuario = self.path + self.user_eca +".txt"
        if  os.path.exists(self.pathEcasUsuario):
            #ecasArchivo = self.ecasArchivoADiccionario()
            #Apaga las ecas haciendo un llamado al micro de ecas
            #Suponemos que las ecas contenidas en el archivo .txt equivalen a todas las ecas del usuario
            if eca_service.apagar_ecas(self.osid):
                logger.info("ECAS del usuario "+ self.user_eca +" apagadas correctamente")
            else:
                logger.error("Error apagando las ECAS del usuario "+ self.user_eca)
                return JSONResponse(content={"error": "Error apagando ECAs del usuario"}, status_code=500)
        # No sabemos como se manejan las ecas cuando se traen del micro de personalizacion, pero suponemos que deben apagarse al notificar la salida del usuario
        if eca_service.apagar_ecas(self.osid):
                logger.info("ECAS del usuario "+ self.user_eca +" apagadas correctamente")
        #Elimina la ontologia del usuario en el micro de ontologias        
        if ontology_service.eliminar_ontologia_usuario():
            logger.info("Ontologia del usuario "+ self.user_eca +" eliminada correctamente")
        else:
            logger.error("Error eliminando la ontologia del usuario "+ self.user_eca)
            return JSONResponse(content={"error": "Error eliminando ontología del usuario"}, status_code=500)        
        #modulo.setClean()
        return JSONResponse(content={"message": "Salida de usuario procesada exitosamente"}, status_code=200)
    def crearEcas(self, listaEcasCrear):
        #Retorna todos los datos del eca
        #?name_activity ?start_date_activity ?end_date_activity
        ##Se deben consultar los ecas del objeto para encender los que son del usuario y apagar lo0s demas
        ##Si un eca no existe, debe crearlo
        print( "   Creando ECAs Desde el Modulo de Personalizacion.")
        print( "Creando un total de " + str(len(listaEcasCrear)) + " ECAs")
        ##Lanza todos los ecas que esten en ON
        for item in listaEcasCrear:
                print( "Creando Eca " + item["name_activity"])
                print( "")
                item['user_eca'] = self.user_eca
                if item["name_activity"] != "":
                    if item["variable_condition"] == "1":
                        item["variable_condition"] = item["start_date_activity"]
                    elif item["variable_condition"] == "0":
                        item["variable_condition"] = item["end_date_activity"]
                    else:
                        print ("Desde Personalizar, el eca tiene actividad, pero la variable condicion no es 0 ni 1: "+ item['name_eca'])
        self.Log.PubUserLog( self.user_eca ,self.osid , "ModuloDePersonalizacion", "inicia poblar ecas cantidad "+str(len(listaEcasCrear)))
        self.eca.poblarListaEca(listaEcasCrear)
        self.Log.PubUserLog( self.user_eca ,self.osid , "ModuloDePersonalizacion", "fin poblar ecas cantidad "+str(len(listaEcasCrear)))
        print( "ECAS Creados Desde el Modulo de Personalizacion")

    def inicializarEcasUsuario(self, listaEcasActivar):
        print( "Inicializando un total de " + str(len(listaEcasActivar)) + " ECAs")
        self.Log.PubUserLog( self.user_eca ,self.osid , "ModuloDePersonalizacion", "inicia inicializando ecas cantidad "+str(len(listaEcasActivar)))

        self.eca.lanzarHiloListaEca(listaEcasActivar)
        print( "ECAS iniciados Desde el Modulo de Personalizacion")

    """def modificarEstadoEcasUsuario(self, listaEcasModificar):
        print( "Modificando estado de  un total de " + str(len(listaEcasModificar)) + " ECAs")
        self.Log.PubUserLog( self.user_eca ,self.osid , "ModuloDePersonalizacion", "inicia modificar estado ecas cantidad "+str(len(listaEcasModificar)))
        self.eca.cambiarEstadoListaEcas(listaEcasModificar)
        print( "ECAS con estado modificado Desde el Modulo de Personalizacion")"""
    #Modificar para que elimine ecas en el micro de ecas
    def eliminarEcas(self, listaEcasEliminar):
        print( "Eliminando estado de  un total de " + str(len(listaEcasEliminar)) + " ECAs")
        self.eca.eliminarListaEcas(listaEcasEliminar)
        print( "ECAS ELIMINADOS Desde el Modulo de Personalizacion")
    
    def verificarUsuario(self, email):
        #Convertir a consulta de ontologia de perfil de usuario        
        if  ontology_service.consultar_email_usuario() == email:
            return True
        else:
            return False

    """def eliminarEcaUsuario(self, listaEcasUsuario, clave, valor):
        for item in listaEcasUsuario:
            if item[clave] == valor:
                listaEcasUsuario.remove(item)
                return listaEcasUsuario
        return listaEcasUsuario"""

    """def estaValor(self, listaDic, clave, valor):
        for item in listaDic:
            if item[clave] == valor:
                return True
        return False"""

    def posicionValor(self, listaDic, clave, valor):
        i = 0
        for item in listaDic:
            if item[clave] == valor:
                return i
            i = i + 1
        return -1

    """
    def guardarEcasArchivo(self, rutaArchivo, listaEcas):
        archivo = open(rutaArchivo,  'r+')
        for item in listaEcas:
            linea = item["name_eca"] + "," + item["state_eca"]
    """

    def ecasArchivoADiccionario(self):
        rutaArchivo = self.pathEcasUsuario
        archivo = open(rutaArchivo,  'r+')
        lineas = archivo.readlines()
        archivo.close()
        ecasArchivo = []
        #TODO Cambiar el archivo
        for linea in lineas:
            linea = linea.rstrip('\n')
            split = linea.split(",")
            nombreEca = split[0]
            estadoEca = split[1]
            dicEca = {"name_eca": nombreEca, "state_eca" : estadoEca}
            ecasArchivo.append(dicEca)
        return ecasArchivo
    
    def registroInteraccionUsuarioObjeto(self,data:RegistroInteraccionDTO)->JSONResponse:
        """if os.path.exists(AppUtil.pathOWL + mac +  ".owl"):
            poblador = PoblarPerfilUsuario(mac, email, "CARGAR")
            poblador.registroInteraccionUsuarioObjeto( email, idDataStream, comando, osid, dateInteraction)"""
        #Si la ontologia existe, se registra la interaccion en el micro de ontologias
        if ontology_service.verificar_perfil_activo():
            if ontology_service.registrar_interaccion(data):
                return JSONResponse(content={"message": "Interacción registrada exitosamente en el microservicio de ontologías"}, status_code=200)
            else:
                return JSONResponse(content={"error": "Error registrando la interacción en el microservicio de ontologías"}, status_code=500)
        else:
            logger.info("El usuario no esta en la casa, notificando al servidor de perfil usuario")
            #EL usuario no esta en la casa actualmente, por eso se envia la peticion al servidor perfil de usuario            
            self.conexion_pu.enviarRegistroInteraccionUsuarioObjetoAlServidorPerfilUsuario(data.email,data.idDataStream, data.comando,data.osid, data.mac,  data.dateInteraction)
        return JSONResponse(content={"message": "La interacción fue registrada en el servidor de perfil de usuario"}, status_code=200)    
        """
        def enviarRegistroInteraccionUsuarioObjetoAlCoordinador(self, email,idDataStream,comando, osid, mac, dateInteraction):
        conexion = ConexionPu()
        conexion.enviarRegistroInteraccionUsuarioObjetoAlCoordinador(email, idDataStream,comando, osid, mac, dateInteraction)
        """