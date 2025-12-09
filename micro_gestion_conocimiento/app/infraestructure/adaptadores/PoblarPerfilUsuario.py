from rdflib import Literal
import os
from os import listdir
import time
from config import settings
from infraestructure.acceso_ontologia.OntologiaPU import OntologiaPU
from infraestructure.interfaces.IPoblacionPerfilUsuario import IPoblarPerfilUsuario
from infraestructure.util import UrisPu
from infraestructure.logging.Logging import logger

pathUsuActual = settings.ONTOLOGIA_PU
    
class PoblarPerfilUsuario(IPoblarPerfilUsuario):
    def __init__(self, mac, idUsuario, accion):
        try:           
            os.stat(settings.PATH_OWL)
        except:
            os.mkdir(settings.PATH_OWL, 0o777)
        if accion == "CARGAR":
            try:    
                self.path = settings.PATH_PU_OWL + mac + "&" + idUsuario + ".owl"
                #self.path = AppUtil.pathOWL + mac +  ".owl"
                self.ontologia = OntologiaPU(self.path)
                logger.info(f"Ruta de ontología cargada: {self.path}")
            except:
                logger.error("Desde PobladorPU. El path es incorrecto, cargando ontologia de prueba")
                self.ontologia = OntologiaPU(settings.ONTOLOGIA_PU)

        elif accion == "CREAR":
            self.path = settings.PATH_OWL + mac + "&" + idUsuario + ".owl"
            self.ontologia = OntologiaPU(self.path)
            self.ontologia.crearNuevaOntologia(self.path)
        elif accion == "usuarioActual":
            try:
                self.path = pathUsuActual
                #self.path = AppUtil.pathOWL + mac +  ".owl"
                self.ontologia = OntologiaPU(self.path)
                logger.info(f"Ruta de ontología cargada: {self.path}")
            except:
                logger.error("Desde PobladorPU. El path es incorrecto")
            
  
    
    def registroInteraccionUsuarioObjeto(self, email, idDataStream, comando, osid, dateInteraction):
        try:  
            if dateInteraction == "00/00/00 00:00:00":
                horayfecha=str(time.strftime("%c"))
                horayfecha = horayfecha.replace(" ", "-" )
            else:
                horayfecha=dateInteraction
            uriIndividuoObject = UrisPu.individuoObject + osid
            uriShedule=UrisPu.individuoShedule_Interaction+email +horayfecha
            self.ontologia.insertarIndividuo(uriShedule,UrisPu.individuoShedule_Interaction)
            listaShedule=[]
            listaShedule.append([uriShedule, UrisPu.dp_id_resource_interaction, Literal(idDataStream)])
            listaShedule.append([uriShedule, UrisPu.dp_type_command_interaction, Literal(comando)])
            listaShedule.append([uriShedule, UrisPu.dp_date_interaction, Literal(horayfecha)])
            
            self.ontologia.insertarListaDataProperty(listaShedule)
            self.ontologia.insertarObjectProperty(uriIndividuoObject, UrisPu.op_date_interaction, uriShedule)      
            return True
        except Exception as e:
            logger.error("Error:")
            logger.error(e)
            return False

    def editarSmartUsuario(self, diccObjetivo):
# {'objetivo1': {'name_objective': 'objetivo1', 'specific': 'especificacion', 'start_date': '01/01/2000',
#                'Measurable': 'criterios', 'suitable_for': 'Salud', 'actcs': [
#         {'Número': '1', 'Nombre': 'accion1', 'Fecha_Inicio': '01/01/2000', 'Fecha Fin': '01/01/2000',
#          'Estado': 'En espera', 'Descripcion': 'descriAccion'}],
#                'resource': [{'Numero': '1', 'Nombre': 'recurdo'}]}}
        #try:
            query = """ PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                                PREFIX pu: <http://localhost/default#>
            	                PREFIX onto:<http://localhost/OntoProfile#>
                                SELECT DISTINCT ?email_user
                                WHERE {
                                    ?persona pu:email ?email_user.
                                    ?persona rdf:type onto:Person.
                                }"""
            correo = ""
            listaIps = self.ontologia.consultaDataProperty(query)
            for lista in listaIps:
                for cadena in lista:
                    pos = lista.index(cadena)
                    lista[pos] = cadena.decode('utf-8')
            if len(listaIps) > 0:
                correo = listaIps[0][0]
            else:
                correo = ""

            objetivo_nombre = diccObjetivo['name_objective'].replace(" ", "_")
            individuo_persona = UrisPu.individuoPersona + correo
            individuo_objetivo = UrisPu.individuoObjective + objetivo_nombre


            listaIndividuos = []
            listaIndividuos.append([individuo_persona, UrisPu.individuoPersona])
            listaIndividuos.append([individuo_objetivo, UrisPu.individuoObjective])

            for item in diccObjetivo['actcs']:
                individuo_acto = UrisPu.individuoActs + objetivo_nombre + "acto" + item['Número']
                listaIndividuos.append([individuo_acto, UrisPu.individuoActs])

            for item in diccObjetivo['resource']:
                individuo_resource = UrisPu.individuoresource + objetivo_nombre + "rec" + item['Numero']
                listaIndividuos.append([individuo_resource, UrisPu.individuoresource])


            ##self.ontologia.insertarListaIndividuos(listaIndividuos)
            # {'': {'name_objective': '', 'specific': '', 'start_date': '01/01/2000', 'Measurable': '',
            #       'suitable_for': 'Personal', 'actcs': [], 'resource': []}}
            lista = []
            # dinamic.append([individuoEvento, self.uris.dp_, Literal(diccionarioECA[""])])
            lista.append([individuo_objetivo, UrisPu.dp_name_objective, Literal(diccObjetivo['name_objective'])])
            lista.append([individuo_objetivo, UrisPu.dp_specific, Literal(diccObjetivo['specific'])])
            lista.append([individuo_objetivo, UrisPu.dp_start_date, Literal(diccObjetivo['start_date'])])
            lista.append([individuo_objetivo, UrisPu.dp_Measurable, Literal(diccObjetivo["Measurable"])])
            lista.append([individuo_objetivo, UrisPu.dp_suitable_for, Literal(diccObjetivo["suitable_for"])])

            for item in diccObjetivo['actcs']:
                #{'Número': '1', 'Nombre': 'accion1', 'Fecha_Inicio': '01/01/2000', 'Fecha Fin': '01/01/2000', 'Estado': 'En espera', 'Descripcion': 'descriAccion'}

                individuo_acto = UrisPu.individuoActs + objetivo_nombre + "acto" + item['Número']
                lista.append([individuo_acto, UrisPu.dp_number, Literal(item["Número"])])
                lista.append([individuo_acto, UrisPu.dp_name_acts, Literal(item["Nombre"])])
                lista.append([individuo_acto, UrisPu.dp_start_date_acts, Literal(item["Fecha Inicio"])])
                lista.append([individuo_acto, UrisPu.dp_final_date, Literal(item["Fecha Fin"])])
                lista.append([individuo_acto, UrisPu.dp_state_act, Literal(item["Estado"])])
                lista.append([individuo_acto, UrisPu.dp_description_act, Literal(item["Descripcion"])])

            for item in diccObjetivo['resource']:
                individuo_resource = UrisPu.individuoresource + objetivo_nombre + "rec" + item['Numero']
                lista.append([individuo_resource, UrisPu.dp_number_resource, Literal(item["Numero"])])
                lista.append([individuo_resource, UrisPu.dp_name_resource, Literal(item["Nombre"])])
            self.ontologia.actualizarListaDataProperty(lista)

            listaObjectProperty = []
            listaObjectProperty.append([individuo_persona, UrisPu.op_proposes, individuo_objetivo])

            for item in diccObjetivo['actcs']:
                individuo_acto = UrisPu.individuoActs + objetivo_nombre + "acto" + item['Número']
                listaObjectProperty.append([individuo_objetivo, UrisPu.op_makes, individuo_acto])

            for item in diccObjetivo['resource']:
                individuo_resource = UrisPu.individuoresource + objetivo_nombre + "rec" + item['Numero']
                listaObjectProperty.append([individuo_objetivo, UrisPu.op_requires, individuo_resource])

            ########listaObjectProperty.append([individuo_, UrisPu.op_, individuo_])
            self.ontologia.insertarListaObjectProperty(listaObjectProperty)

        # except Exception as e:
        #     print("Error al poblar smart")
        #     print((e))
        #     print()
    def registroSmartUsuario(self, diccObjetivo):
# {'objetivo1': {'name_objective': 'objetivo1', 'specific': 'especificacion', 'start_date': '01/01/2000',
#                'Measurable': 'criterios', 'suitable_for': 'Salud', 'actcs': [
#         {'Número': '1', 'Nombre': 'accion1', 'Fecha_Inicio': '01/01/2000', 'Fecha Fin': '01/01/2000',
#          'Estado': 'En espera', 'Descripcion': 'descriAccion'}],
#                'resource': [{'Numero': '1', 'Nombre': 'recurdo'}]}}
            print("*************  Desde registro Smart Usuario ****************************")
            print(diccObjetivo)
            print()
            print()

        #try:
            query = """ PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                                PREFIX pu: <http://localhost/default#>
            	                PREFIX onto:<http://localhost/OntoProfile#>
                                SELECT DISTINCT ?email_user
                                WHERE {
                                    ?persona pu:email ?email_user.
                                    ?persona rdf:type onto:Person.
                                }"""
            correo = ""
            listaIps = self.ontologia.consultaDataProperty(query)
            for lista in listaIps:
                for cadena in lista:
                    pos = lista.index(cadena)
                    lista[pos] = cadena.decode('utf-8')
            if len(listaIps) > 0:
                correo = listaIps[0][0]
            else:
                correo = ""

            objetivo_nombre = diccObjetivo['name_objective'].replace(" ", "_")
            individuo_persona = UrisPu.individuoPersona + correo
            individuo_objetivo = UrisPu.individuoObjective + objetivo_nombre


            listaIndividuos = []
            listaIndividuos.append([individuo_persona, UrisPu.individuoPersona])
            listaIndividuos.append([individuo_objetivo, UrisPu.individuoObjective])

            for item in diccObjetivo['actcs']:
                individuo_acto = UrisPu.individuoActs + objetivo_nombre + "acto" + item['Número']
                listaIndividuos.append([individuo_acto, UrisPu.individuoActs])

            for item in diccObjetivo['resource']:
                individuo_resource = UrisPu.individuoresource + objetivo_nombre + "rec" + item['Numero']
                listaIndividuos.append([individuo_resource, UrisPu.individuoresource])


            self.ontologia.insertarListaIndividuos(listaIndividuos)
            # {'': {'name_objective': '', 'specific': '', 'start_date': '01/01/2000', 'Measurable': '',
            #       'suitable_for': 'Personal', 'actcs': [], 'resource': []}}
            lista = []
            # dinamic.append([individuoEvento, self.uris.dp_, Literal(diccionarioECA[""])])
            lista.append([individuo_objetivo, UrisPu.dp_name_objective, Literal(diccObjetivo['name_objective'])])
            lista.append([individuo_objetivo, UrisPu.dp_specific, Literal(diccObjetivo['specific'])])
            lista.append([individuo_objetivo, UrisPu.dp_start_date, Literal(diccObjetivo['start_date'])])
            lista.append([individuo_objetivo, UrisPu.dp_Measurable, Literal(diccObjetivo["Measurable"])])
            lista.append([individuo_objetivo, UrisPu.dp_suitable_for, Literal(diccObjetivo["suitable_for"])])

            for item in diccObjetivo['actcs']:
                #{'Número': '1', 'Nombre': 'accion1', 'Fecha_Inicio': '01/01/2000', 'Fecha Fin': '01/01/2000', 'Estado': 'En espera', 'Descripcion': 'descriAccion'}

                individuo_acto = UrisPu.individuoActs + objetivo_nombre + "acto" + item['Número']
                lista.append([individuo_acto, UrisPu.dp_number, Literal(item["Número"])])
                lista.append([individuo_acto, UrisPu.dp_name_acts, Literal(item["Nombre"])])
                lista.append([individuo_acto, UrisPu.dp_start_date_acts, Literal(item["Fecha Inicio"])])
                lista.append([individuo_acto, UrisPu.dp_final_date, Literal(item["Fecha Fin"])])
                lista.append([individuo_acto, UrisPu.dp_state_act, Literal(item["Estado"])])
                lista.append([individuo_acto, UrisPu.dp_description_act, Literal(item["Descripcion"])])

            for item in diccObjetivo['resource']:
                individuo_resource = UrisPu.individuoresource + objetivo_nombre + "rec" + item['Numero']
                lista.append([individuo_resource, UrisPu.dp_number_resource, Literal(item["Numero"])])
                lista.append([individuo_resource, UrisPu.dp_name_resource, Literal(item["Nombre"])])
            self.ontologia.insertarListaDataProperty(lista)

            listaObjectProperty = []
            listaObjectProperty.append([individuo_persona, UrisPu.op_proposes, individuo_objetivo])

            for item in diccObjetivo['actcs']:
                individuo_acto = UrisPu.individuoActs + objetivo_nombre + "acto" + item['Número']
                listaObjectProperty.append([individuo_objetivo, UrisPu.op_makes, individuo_acto])

            for item in diccObjetivo['resource']:
                individuo_resource = UrisPu.individuoresource + objetivo_nombre + "rec" + item['Numero']
                listaObjectProperty.append([individuo_objetivo, UrisPu.op_requires, individuo_resource])

            ########listaObjectProperty.append([individuo_, UrisPu.op_, individuo_])
            self.ontologia.insertarListaObjectProperty(listaObjectProperty)

