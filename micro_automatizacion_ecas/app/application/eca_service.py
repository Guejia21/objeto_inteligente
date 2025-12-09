from ast import Dict
import os
from random import random
import time

from fastapi.responses import JSONResponse
from application.dtos import ECAResponse, ECAStateRequest, MakeContractRequest, SendCommandRequest
from infra.logging.Logging import logger
from config import settings
from application import ontology_service
from infra.logging.ILogPanelMQTT import ILogPanelMQTT
from domain.eca import ECA
from domain.eca_task_manager import eca_task_manager
from infra import util
from application import datastream_service

class EcaService:
    def __init__(self, log_panel: ILogPanelMQTT):
        self.pathEca = settings.PATH_ECA        
        self.osid = ontology_service.get_id()
        self.title = ontology_service.get_title()
        self.Log = log_panel
        self.eca = ECA()        
        
    async def crear_eca(self, eca_data: MakeContractRequest) -> JSONResponse:
        """
        Crea un nuevo contrato ECA para el objeto inteligente.
        
        :param self: Instancia de la clase
        :param eca_data: Datos para crear el contrato ECA
        :type eca_data: MakeContractRequest
        :return: Respuesta de la creación del contrato ECA
        :rtype: ECAResponse
        """       
        logger.info("Iniciando creación de ECA")
        
        if self.osid == eca_data.osid:
            try:
                # Guardar archivo del contrato
                if not os.path.exists(self.pathEca):
                    os.makedirs(self.pathEca, mode=0o777, exist_ok=True)
                    
                filename = f"ECA_{eca_data.contrato.name_eca}_{eca_data.contrato.user_eca}.json"
                filepath = os.path.join(self.pathEca, filename)
                
                with open(filepath, 'w', encoding='utf-8') as fout:
                    fout.write(eca_data.contrato.model_dump_json())
                    
            except Exception as e:
                logger.error(f"Error al guardar el archivo del contrato ECA: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",                        
                        "message": "Error al guardar el archivo del contrato ECA.",
                        "data": {}
                    }
                )
            
            try:
                # Obtener diccionario aplanado del ECA
                logger.info("Agregando ECA a la Ontología")
                diccEca = self.eca.getDiccionarioECA(filename)
                diccEca['user_eca'] = eca_data.email
                
                # Poblar ontología
                if not ontology_service.poblate_eca(diccEca):
                    logger.error("Error al poblar el ECA en la ontología.")
                    return JSONResponse(
                        status_code=500,
                        content={
                            "status": "error",                            
                            "message": "Error al poblar el ECA en la ontología.",
                            "data": {}
                        }
                    )
                
                logger.info(f"ECA {diccEca['name_eca']} guardado en ontología")
                
                # Registrar ECA en el gestor de tareas para monitoreo
                if await eca_task_manager.register_eca(diccEca):
                    logger.info(f"ECA {diccEca['name_eca']} registrado para monitoreo")
                    return JSONResponse(
                        status_code=200,
                        content={
                            "status": "success",                            
                            "message": "El contrato ECA ha sido creado exitosamente.",
                            "data": {
                                "eca_name": diccEca["name_eca"],
                                "state": diccEca["state_eca"],
                                "filename": filename
                            }
                        }
                    )
                else:
                    logger.error("Error al registrar el ECA en el gestor de tareas.")
                    return JSONResponse(
                        status_code=500,
                        content={
                            "status": "error",                            
                            "message": "Error al registrar el ECA en el gestor de tareas.",
                            "data": {}
                        }
                    )            
            except Exception as e:
                logger.error(f"Error creando ECA: {e}")
                import traceback
                traceback.print_exc()
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",                            
                        "message": f"Error al crear el ECA: {str(e)}",
                        "data": {}
                    }
                )
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "code": "INVALID_OSID",
                    "message": "El identificador del objeto no corresponde.",
                    "data": {}
                }
            )
    
    async def listar_ecas(self,osid:str) -> JSONResponse:
        """Lista todas las ECAs del objeto inteligente.

        Args:
            osid (str): ID del objeto inteligente.

        Returns:
            JSONResponse: Respuesta con la lista de ECAs.
        """
        await self.Log.PubRawLog(self.osid, self.osid, "Listar todos ecas")
        if self.osid == osid:
            try:
                logger.info("Listando Todos los ECAS")
                listaEcas = ontology_service.get_ecas()
                logger.info(f"{len(listaEcas)} ECAs obtenidos de la ontología")                
                await self.Log.PubRawLog(self.osid, self.osid, "Fin Listar todos ecas")
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "success",                        
                        "message": "Listado de ECAs obtenido exitosamente.",
                        "data": {"ecas": listaEcas}
                    }
                )
            except Exception as e:
                await self.Log.PubRawLog(self.osid, self.osid, "Error Listar todos ecas")
                logger.error("Error Listando ECAS: %s", e)                
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",
                        "code": "ECAS_LISTING_ERROR",
                        "message": f"Error al listar los ECAs: {str(e)}",
                        "data": {}
                    }
                )
        else:
            await self.Log.PubRawLog(self.osid, self.osid, "Listar todos ecas Id incorrecto")
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "code": "INVALID_OSID",
                    "message": "El identificador del objeto no corresponde.",
                    "data": {}
                }
            )
    
    async def apagar_ecas(self, osid: str) -> JSONResponse:
        """Apaga todas las ECAs del objeto inteligente, pone su estado en off en la ontologia y desactiva su monitorizacion.

        Args:
            osid (str): ID del objeto inteligente.

        Returns:
            JSONResponse: Respuesta de la operación de apagado.
        """
        await self.Log.PubRawLog(self.osid, self.osid, "Apagar todos ecas")
        if self.osid == osid:
            try:               
                if os.listdir(self.pathEca) == []:
                    logger.info("No hay ECAS para apagar")
                    await self.Log.PubRawLog(self.osid, self.osid, "Fin Apagar todos ecas - No hay ECAS")
                    return JSONResponse(
                        status_code=200,
                        content={
                            "status": "success",                            
                            "message": "No hay ECAs para apagar.",
                            "data": {}
                        }
                    ) 
                logger.info("Apagando Todos los ECAS")
                ti = time.time()
                await self.__apagar_ecas()
                logger.info("Todas las ECAS apagadas en ontología")
                await self.Log.PubRawLog(self.osid, self.osid, "Fin Apagar todos ecas")
                tf = time.time()
                tt = tf - ti
                logger.info("Termina de apagar Ecas en " + str(tt) + " Segundos")
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "success",                        
                        "message": "Todas las ECAs han sido apagadas exitosamente.",
                        "data": {}
                    }
                )                               
            except Exception as e:
                await self.Log.PubRawLog(self.osid, self.osid, "Error Apagar todos ecas")
                logger.error("Error apagando todos los ECA: %s", e)                
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",                        
                        "message": f"Error al apagar las ECAs: {str(e)}",
                        "data": {}
                    }
                )
        else:
            await self.Log.PubRawLog(self.osid, self.osid, "Apagar todos ecas id incorrecto")
            logger.error("Identificador Incorrecto")            
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",                    
                    "message": "El identificador del objeto no corresponde.",
                    "data": {}
                }
            )  
    
    async def eliminar_eca(self, osid:str,eca_name: str, user_eca: str = "default") -> JSONResponse:
        """
        Elimina un ECA específico del objeto inteligente.
        
        :param self: Intancia de la clase
        :param osid: Identificador del objeto inteligente
        :type osid: str
        :param eca_name: Nombre del ECA a eliminar
        :type eca_name: str
        :param user_eca: Usuario asociado al ECA
        :type user_eca: str
        :return: Respuesta de la operación de eliminación
        :rtype: ECAResponse
        """
        if self.osid == osid:
            try:
                filename = f"ECA_{eca_name}_{user_eca}.json"
                filepath = os.path.join(settings.PATH_ECA, filename)
                if not os.path.exists(filepath):
                    logger.error(f"Archivo del ECA no encontrado: {filepath}")
                    return JSONResponse(
                        status_code=404,
                        content={
                            "status": "error",                            
                            "message": f"No se encontró el archivo del ECA {eca_name}.",
                            "data": {}
                        }
                    )
                await self.Log.PubLog("eca_delete", self.osid, self.title, self.osid, self.title, eca_name, "Solicitud Recibida")
                # Eliminar del gestor de tareas
                eca_task_manager.unregister_eca(eca_name, user_eca)
                # Eliminar su json
                filename = f"ECA_{eca_name}_{user_eca}.json"
                filepath = os.path.join(self.pathEca, filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
                    logger.info(f"Archivo del ECA eliminado: {filepath}")
                else:
                    logger.warning(f"Archivo del ECA no encontrado para eliminar: {filepath}")
                # Eliminar de ontología
                nombre_completo = eca_name+user_eca
                if ontology_service.delete_eca(nombre_completo):
                    logger.info(f"ECA {eca_name} eliminado correctamente")
                    await self.Log.PubLog("eca_delete", self.osid, self.title, self.osid, self.title, eca_name, "Eca eliminado en objeto")
                    return JSONResponse(
                        status_code=200,
                        content={
                            "status": "success",                            
                            "message": f"El ECA {eca_name} ha sido eliminado exitosamente.",
                            "data": {}
                        }
                    )
                else:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "status": "error",
                            "message": f"No se encontró el ECA {eca_name}",
                            "data": {}
                        }
                    )
            except Exception as e:
                await self.Log.PubRawLog(self.osid, self.osid, "Error Eliminar ecas")
                logger.error(f"Error eliminando ECA: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",
                        "message": f"Error al eliminar el ECA: {str(e)}",
                        "data": {}
                    }
                )   
        else:
            await self.Log.PubRawLog(self.osid, self.osid, "Error eliminarEca, Id incorrecto")
            logger.error("Error - Identificador Incorrecto")            
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "El identificador del objeto no corresponde.",
                    "data": {}
                }
            )
    
    async def cambiar_estado_eca(self, parametros: ECAStateRequest) -> JSONResponse:
        """Cambia el estado de un ECA específico. Actualiza su monitorizacion y estado en la ontologia

        Args:
            parametros (ECAStateRequest): Datos relacionados al cambio de estado

        Returns:
            JSONResponse: Resultado de la operación
        """
        if self.osid == parametros.osid:
            try:
                filename = f"ECA_{parametros.nombreECA}_{parametros.userECA}.json"
                filepath = os.path.join(settings.PATH_ECA, filename)
                if not os.path.exists(filepath):
                    logger.error(f"Archivo del ECA no encontrado: {filepath}")
                    return JSONResponse(
                        status_code=404,
                        content={
                            "status": "error",                            
                            "message": f"No se encontró el archivo del ECA {parametros.nombreECA}.",
                            "data": {}
                        }
                    )
                logger.info("Cambiando Estado a " + parametros.comando + " del ECA: " + parametros.nombreECA)
                await self.__change_eca_state(parametros.nombreECA, parametros.userECA, parametros.comando)
                logger.info("Estado " + parametros.comando + " del ECA: " + parametros.nombreECA)
                await self.Log.PubRawLog(self.osid, self.osid,"Estado de " + parametros.nombreECA + " cambiado a : " + parametros.comando)
                await self.Log.PubLog("set_eca_state", self.osid, self.title, self.osid, self.title,parametros.nombreECA, "ECA modificado en Objeto")
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "success",                        
                        "message": f"El estado del ECA {parametros.nombreECA} ha sido cambiado a {parametros.comando} exitosamente.",
                        "data": {}
                    }
                )                
            except Exception as e:
                logger.error("Error cambiando estado ECA")
                logger.error( e)
                print( "")
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",
                        "message": f"Error al cambiar el estado del ECA: {str(e)}",
                        "data": {}
                    }
                )                        
        else:
            await self.Log.PubRawLog(self.osid, self.osid, "Error setEcaState Id incorrecto")
            logger.error("Error - Identificador Incorrecto")            
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",                    
                    "message": "El identificador del objeto no corresponde.",
                    "data": {}
                }
            )
    async def editar_eca(self, data : MakeContractRequest) -> JSONResponse:                        
        if self.osid == data.osid:
            try:
                if not os.path.exists(self.pathEca):
                    os.mkdir(self.pathEca, 0o777)
                filename = f"ECA_{data.contrato.name_eca}_{data.contrato.user_eca}.json"
                if not os.path.exists(self.pathEca + '/' + filename):
                    logger.info("Error  El ECA no existe")
                    return JSONResponse(
                        status_code=404,
                        content={
                            "status": "error",                            
                            "message": "El ECA no existe",
                            "data": {}
                        }
                    )                                
                fout = open(self.pathEca + '/' + filename, 'w')
                fout.write(data.contrato.model_dump_json())
                fout.close()
            except Exception as e:
                self.Log.PubRawLog(self.osid, self.osid, "makeContract Error guardando archivo")
                logger.error("Error  Guardando el contrato")
                logger.error(e)
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",                        
                        "message": "Error guardando el contrato",
                        "data": {}
                    }
                )
            try:
                diccEca = self.eca.getDiccionarioECA(filename)
                diccEca['user_eca'] = data.email
                # Actualizar el gestor de tareas
                # Se elimina del monitoreo y se vuelve a agregar en caso de que hayan cambiado umbrales
                eca_task_manager.unregister_eca(data.contrato.name_eca, data.contrato.user_eca)
                await eca_task_manager.register_eca(diccEca)                
                logger.info( "       Editando ECA en la Ontologia")
                logger.info( "Tiempor en el que inicia  ----------------------> " + time.ctime())
                diccEca = self.eca.getDiccionarioECA(filename)
                await self.Log.PubLog("eca_gen", self.osid, self.title, self.osid, self.title, diccEca["name_eca"], "Solicitud Recibida")
                if ontology_service.edit_eca(diccEca):
                    await self.Log.PubLog("eca_gen", self.osid, self.title, self.osid, self.title, diccEca["name_eca"], "ECA creado en Objeto")
                    await self.Log.PubRawLog(self.osid, self.osid, "ECA Creado")
                    logger.info( "       ECA guardado")
                    logger.info( "Tiempo en el que termina----------------> " + time.ctime())
                    return JSONResponse(
                        status_code=200,
                        content={
                            "status": "success",
                            "code": "ECA_EDITED",
                            "message": "El ECA ha sido editado exitosamente.",
                            "data": {
                                "eca_name": diccEca["name_eca"],
                                "state": diccEca["state_eca"],
                                "filename": filename
                            }
                        }                
                    )
                else:                    
                    logger.error("Error  Guardando ECA en ontologia")
                    return JSONResponse(
                        status_code=500,
                        content={
                            "status": "error",                            
                            "message": "Error guardando el ECA en la ontología",
                            "data": {}}
                    )
            except Exception as e:
                # self.Log.PubRawLog("eca_gen", self.osid, self.tittle, self.osid, self.tittle, diccEca["name_eca"], "Error ECA creado en Objeto")
                logger.error("Error  Guardando ECA")
                logger.error(e)
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",
                        "message": "Error guardando el ECA en la ontología",
                        "data": {}
                    }
                )
        else:
            logger.error("Error - Identificador Incorrecto")            
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",                    
                    "message": "El identificador del objeto no corresponde.",
                    "data": {}
                }
            )
    async def send_command(self, data: SendCommandRequest)->JSONResponse:
        """Envía un comando a un datastream actuador si existe un contrato.

        Args:
            data (SendCommandRequest): Datos del comando a enviar.

        Returns:
            ECAResponse: Respuesta de la operación de envío del comando.
        """
        await self.Log.PubRawLog(self.osid, self.osid, "SendCommand")        
        logger.info("SendCommand -- Recibiendo comando")
        osidDestino = data.osidDestino
        if self.osid == osidDestino:
            respuesta = self.__estaCommand(data)  # {osid osidDestino id_action_resource comparator_action variable_action type_variable_action eca_state}
            logger.debug(respuesta)
            if (respuesta[0] == 1):
                state_eca = respuesta[1]["eca_state"]
                if state_eca == 'on':
                    try:
                        logger.info("Va a ejecutar " + respuesta[1]["id_action_resource"] + " " + str(respuesta[1]["comparator_action"]) + " " + str(respuesta[1]["variable_action"]))
                        if datastream_service.send_command(self.osid, respuesta[1]["id_action_resource"], data.comando):
                            await self.Log.PubRawLog(self.osid, self.osid, "Fin SendCommand")
                            return JSONResponse(
                                status_code=200,
                                content={
                                    "status": "success",                                    
                                    "message": "El comando ha sido enviado exitosamente al datastream actuador.",
                                    "data": {}
                                }
                            )
                        else:
                            await self.Log.PubRawLog(self.osid, self.osid, "Error SendCommand")
                            logger.error("Error enviando SendCommand")                            
                            return JSONResponse(
                                status_code=500,
                                content={
                                    "status": "error",                                    
                                    "message": "Error al ejecutar el comando en el datastream.",
                                    "data": {}
                                }
                            )
                    except Exception as e:
                        await self.Log.PubRawLog(self.osid, self.osid, "Error SendCommand")
                        logger.error("Error enviando SendCommand")
                        logger.error( e)                        
                        return JSONResponse(
                            status_code=500,
                            content={
                                "status": "error",                                    
                                "message": "Error al ejecutar el comando en el datastream.",
                                "data": {}
                            }
                        )
                else:
                    await self.Log.PubRawLog(self.osid, self.osid, "Error SendCommand")
                    logger.error("Error enviando SendCommand")
                    logger.error("ECA apagado")                    
                    return JSONResponse(
                        status_code=500,
                        content={
                            "status": "error",                            
                            "message": "El ECA asociado al comando está apagado.",
                            "data": {}
                        }
                    )
            ##Si el contrato no existe retorna la respuesta de error
            else:
                await self.Log.PubRawLog(self.osid, self.osid, "Error SendCommand")
                logger.error("Error enviando SendCommand")
                logger.error("Contrato no existe")                
                return respuesta[1]  ##ECAResponse sobre el error
        else:
            await self.Log.PubRawLog(self.osid, self.osid, "Error SendCommand")
            logger.error("Error enviando SendCommand - Identificador Incorrecto")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "code": "INVALID_OSID",
                    "message": "El identificador del objeto no corresponde.",
                    "data": {}
                }
            )
    def __estaCommand(self, parametros:SendCommandRequest):
        """Verifica si el comando recibido coincide con algún contrato ECA.
        Args:
            parametros (SendCommandRequest): Datos del comando a verificar.
        Returns:
            List: Lista con el resultado de la verificación.
        """
        osid = parametros.osid
        osidDestino = parametros.osidDestino
        comando = parametros.comando
        respuesta = []
        listaECAS = ontology_service.verificar_contrato(osid, osidDestino)
        # devuelve [{osid osidDestino id_action_resource comparator_action variable_action type_variable_action eca_state}]
        # leer el comando y compararlo con la lista si coincide entonces ejecutar el comando y si no mandar xml de error
        logger.info("Se recibieron " + str(len(listaECAS)) + " ecas")
        if len(listaECAS) > 0:
            try:
                os.stat(settings.PATH_COMANDOS)
            except:
                os.mkdir(settings.PATH_COMANDOS, 0o777)
            nombreArchivo = 'comando' + str(random) + ".json"
            archivoComando = open(settings.PATH_COMANDOS + nombreArchivo, 'w')
            archivoComando.write(comando.model_dump_json())
            archivoComando.close()
            listaComando = util.procesar_comando_json_archivo(settings.PATH_COMANDOS + nombreArchivo)  # Dicc {"id_action_resource" "comparator_action" "variable_action" "type_variable_action"}
            os.remove(settings.PATH_COMANDOS + nombreArchivo)
            #            sublistas = listaECAS[0]
            if len(listaComando) > 0:
                dicComando = listaComando[0]
                for sublistas in listaECAS:
                    ##Verifica que los comando sean iguales
                    # if listaComando[0]==sublistas[2] and listaComando[1]==sublistas[3] and listaComando[2]==sublistas[4] and listaComando[3]==sublistas[5]:
                    if dicComando["id_action_resource"] == sublistas["id_action_resource"] and dicComando[
                        "comparator_action"] == sublistas["comparator_action"] and dicComando["variable_action"] == \
                            sublistas["variable_action"] and dicComando["type_variable_action"] == sublistas[
                        "type_variable_action"]:
                        respuesta.append(1)
                        respuesta.append(sublistas)
                        return respuesta
                respuesta.append(0)
                respuesta.append(JSONResponse(
                    status_code=500,
                    content={                        
                        "code": "COMMAND_NOT_FOUND",
                        "message": "El comando no coincide con ningún contrato ECA.",
                        "data": {}
                    }
                ))
                return respuesta
            else:
                respuesta.append(0)
                respuesta.append(JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",                        
                        "message": "Error de conexión al procesar el comando.",
                        "data": {}
                    }
                ))
                return respuesta
        else:
            respuesta.append(0)
            respuesta.append(JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "Error de conexión al procesar el comando.",
                    "data": {}
                }
            ))
            return respuesta
        
    def obtener_ecas_activos(self) -> Dict:
        """Retorna todos los ECAs activos en monitoreo"""
        return eca_task_manager.get_active_ecas()
    async def __apagar_ecas(self)->bool:                
        listaEcas = self.obtener_ecas_activos()
        logger.info("Apagando un total de " + str(len(listaEcas)) + " ECAS")        
        if len(listaEcas) > 0:
            lista = []
            for eca in listaEcas.values():
                #logger.debug(eca)
                #Cancela el monitoreo de la ECA
                await eca_task_manager.update_eca_state(eca["eca_name"], "off", eca["user_eca"])
                #Actualizar su json
                util.update_eca_state_json(eca["eca_name"], eca["user_eca"], "off")
                nombre_completo_eca = eca["eca_name"] + eca["user_eca"] #Se envia de esta manera para que funcione correctamente en la base del conocimiento
                lista.append([nombre_completo_eca, "off"])
            if ontology_service.setEcaListState(lista):        
                return True
            else:
                return False
        else:
            logger.info("No hay ECAS encendidas")
            return True
    
    async def __change_eca_state(self, eca_name: str, user_eca: str, new_state: str):
        """
        Cambia el estado de un ECA tanto en la ontología, gestor de tareas y su archivo JSON.
        
        :param self: Instancia de la clase
        :param eca_name: Nombre del ECA a modificar
        :type eca_name: str
        :param user_eca: Usuario asociado al ECA
        :type user_eca: str
        :param new_state: Nuevo estado del ECA
        :type new_state: str
        :return: Indica si el cambio de estado fue exitoso
        :rtype: bool
        """
        eca_dict = self.eca.getDiccionarioECA(f"ECA_{eca_name}_{user_eca}.json")
        estado_actual = eca_dict.get("state_eca", "off")
        if estado_actual == new_state:
            logger.info(f"El ECA {eca_name} ya está en el estado {new_state}")
            return  # No es necesario cambiar el estado
        nombre_completo_eca = eca_name + user_eca  # Se envia de esta manera para que funcione correctamente en la base del conocimiento
        if ontology_service.set_eca_state(nombre_completo_eca, new_state):
            await eca_task_manager.update_eca_state(eca_name, new_state, user_eca)
            util.update_eca_state_json(eca_name, user_eca, new_state)
            logger.info(f"ECA {eca_name} cambiado a estado {new_state}")            
        else:
            logger.error(f"Error cambiando el estado del ECA {eca_name} en ontología")