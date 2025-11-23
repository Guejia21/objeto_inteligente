"""Adaptador de Población de la Ontología OOS
Se extiende de la interfaz IPoblacion permitiendo poblar los metadatos del objeto inteligente en la ontología instanciada ubicada en /OWL/ontologiainstanciada.owl."""
import app.config as config
import os, shutil
from app.infraestructure.interfaces.IPoblacion import IPoblacion
from app.infraestructure.acceso_ontologia.Ontologia import Ontologia
from owlready2 import *
from app.infraestructure.util.ClasesOOS import *
from app.infraestructure.logging.Logging import logger
from rdflib import Literal

onto_path = [config.pathOWL] #("app/infraestucture/OWL/")
logger.info("Ruta Ontologias: " + config.pathOWL)


class PobladorOOS(IPoblacion):

    def __init__(self):
        self.individuoObjecto = None
        self.individuoEstado = None
        self.location = None
        self.onto = get_ontology("file://" + config.ontologia).load(reload_if_newer=True)
        self.uris = UrisOOS()
        self.ontologia = Ontologia()

        logger.info("Inicio Poblar Objeto Semantico con OWLReady2")        
        if not os.path.exists(config.pathOWL):
            os.makedirs(config.pathOWL, mode=0o777)    
        try:
            # Copio la ontologia base a la ontologia instanciada
            shutil.copyfile(config.ontologia, config.ontologiaInstanciada)
        except Exception as e:
            logger.error("Fallo al copiar ontologia base a ontologia instanciada")
            logger.error(e)

        logger.info("Ontologia Cargada: " + str(self.onto.loaded))

    def poblarMetadatosObjeto(self, diccionarioObjeto:dict, listaRecursos:dict):
        try:            
            self.individuoEstado = State("Estado")
            self.individuoObjecto = Object()
            self.individuoObjecto.set_name("Objeto")
            self.location = location()
            self.location.set_name("Localizacion")                    

            self.__poblarObjecto(diccionarioObjeto)

            self.__poblarEstado(diccionarioObjeto)

            self.__poblarLocation(diccionarioObjeto)

            self.__poblarDataStreams(listaRecursos)
            # Las clases se utilizan anteriormente están asociadas a la ontología, por lo que al guardar la ontología se guardan los individuos creados
            self.onto.save(file=config.ontologiaInstanciada,format="rdfxml")
            logger.info("Población de metadatos exitosa")
            return True
        except Exception as e:
            destroy_entity(self.individuoEstado)
            destroy_entity(self.individuoObjecto)
            destroy_entity(self.location)
            self.onto = get_ontology("file://" + config.ontologia).load(reload_if_newer=True)
            logger.info("Se destruyeron las entidades")
            logger.error(e)
            return False

    def __poblarObjecto(self, diccionarioObjeto):
        self.individuoObjecto.id_object = [diccionarioObjeto["id"]]
        if ("ip_object" in diccionarioObjeto):
            self.individuoObjecto.ip_object = [diccionarioObjeto["ip_object"]]        

    def __poblarEstado(self, diccionarioObjeto):
        self.individuoEstado.version = [diccionarioObjeto["version"]]
        self.individuoEstado.creator = [diccionarioObjeto["creator"]]
        self.individuoEstado.status = [diccionarioObjeto["status"]]
        items = diccionarioObjeto["tags"]
        for item in items:
            self.individuoEstado.tags.append(item)
        self.individuoEstado.title = [diccionarioObjeto["title"]]
        self.individuoEstado.private = [diccionarioObjeto["private"]]
        self.individuoEstado.description = [diccionarioObjeto["description"]]
        self.individuoEstado.updated = [diccionarioObjeto["updated"]]
        self.individuoEstado.website = [diccionarioObjeto["website"]]
        self.individuoEstado.feed = [diccionarioObjeto["feed"]]
        self.individuoEstado.created = [diccionarioObjeto["created"]]        

    def __poblarLocation(self, ds):
        self.location.lon = [ds["lon"]]
        self.location.lat = [ds["lat"]]
        self.location.name_location = [ds["name"]]
        self.location.domain = [ds["domain"]]
        self.location.ele = [ds["ele"]]

    def __poblarDataStreams(self, listaRecursos):                
        ds = listaRecursos        
        logger.info("Poblando DataStreams...")
        for item in ds:            
            dataStreamsIRI = item["datastream_id"]
            unidadIRI = dataStreamsIRI + "_unidad"
            entityIRI = dataStreamsIRI + "_entity_of_interest"
            featureIRI = dataStreamsIRI + "_feature_of_interest"
            
            datastreamObj = datastreams(dataStreamsIRI)
            unidadObj = Unit(unidadIRI)
            entityObj = EntitiesOfInterest(entityIRI)
            featureObj = FeatureOfInterest(featureIRI)

            datastreamObj.min_value = [item["min_value"]]
            datastreamObj.max_value = [item["max_value"]]
            datastreamObj.datastream_id = [item["datastream_id"]]
            datastreamObj.datastream_type = [item["datastream_type"]]
            datastreamObj.datastream_format = [item["datastream_format"]]

            for item2 in item['tags']:
                datastreamObj.tags.append(item2)

            unidadObj.label = [item["label"]]
            unidadObj.symbol = [item["symbol"]]

            featureObj.name_feature = [item["featureofinterest"]]
            entityObj.name_entity = [item["entityofinterest"]]

            datastreamObj.isMeasured.append(unidadObj)
            entityObj.isDefinedBy.append(featureObj)            
        logger.info("DataStreams poblados correctamente.")

    def poblarECA(self, diccionarioECA:dict):        
        logger.info("Poblando regla ECA...")
        user_eca = "default"        
        ##Si está usando el perfil de usuario
        if "user_eca" in diccionarioECA:
            user_eca = diccionarioECA["user_eca"]

        ##Reemplaza los espacios para no tener problemas en la ontología
        nombreEca = diccionarioECA['name_eca'].replace(" ", "_") + user_eca

        ##Creacion de los individuos
        individuoECA = self.uris.prefijo + nombreEca
        individuoEvento = self.uris.prefijo + nombreEca + "evento"
        individuoAccion = self.uris.prefijo + nombreEca + "accion"
        individuoCondicion = self.uris.prefijo + nombreEca + "condicion"
        listaIndividuos = []
        listaIndividuos.append([individuoECA, self.uris.clase_dinamic])
        listaIndividuos.append([individuoEvento, self.uris.clase_event])
        listaIndividuos.append([individuoAccion, self.uris.clase_Action])
        listaIndividuos.append([individuoCondicion, self.uris.clase_condition])
        self.ontologia.insertarListaIndividuos(listaIndividuos)

        dinamic = self.__poblarDinamic(diccionarioECA, individuoECA)
        event = self.__poblarEvent(diccionarioECA, individuoEvento)
        accion = self.__poblarAction(diccionarioECA, individuoAccion)
        condicion = self.__poblarCondition(diccionarioECA, individuoCondicion)
        self.ontologia.insertarListaDataProperty(dinamic + event + accion + condicion)

        listaObjectProperty = []
        listaObjectProperty.append([individuoECA, self.uris.op_starts_with, individuoEvento])
        listaObjectProperty.append([individuoEvento, self.uris.op_check, individuoCondicion])
        listaObjectProperty.append([individuoCondicion, self.uris.op_is_related_with, individuoAccion])
        self.ontologia.insertarListaObjectProperty(listaObjectProperty)
        logger.info("Regla ECA poblada correctamente.")
        return True

    def __poblarDinamic(self, diccionarioECA, individuoECA):
        dinamic = []
        # dinamic.append([individuoECA, self.uris.dp_, Literal(diccionarioECA[""])])
        nombreEca = diccionarioECA['name_eca'].replace(" ", "_")
        if "interest_entity_eca" in diccionarioECA:
            dinamic.append(
                [individuoECA, self.uris.dp_interest_entity_eca, Literal(diccionarioECA["interest_entity_eca"])])
        dinamic.append([individuoECA, self.uris.dp_name_eca, Literal(nombreEca)])
        dinamic.append([individuoECA, self.uris.dp_state_eca, Literal(diccionarioECA["state_eca"])])
        user_eca = "default"
        if "user_eca" in diccionarioECA:
            user_eca = diccionarioECA["user_eca"]
        dinamic.append([individuoECA, self.uris.dp_user_eca, Literal(user_eca)])
        return dinamic

    ##        self.ontologia.insertarListaDataProperty(dinamic)

    def __poblarEvent(self, diccionarioECA, individuoEvento):
        event = []
        # dinamic.append([individuoEvento, self.uris.dp_, Literal(diccionarioECA[""])])
        event.append([individuoEvento, self.uris.dp_id_event_object, Literal(diccionarioECA["id_event_object"])])
        event.append([individuoEvento, self.uris.dp_ip_event_object, Literal(diccionarioECA["ip_event_object"])])
        event.append([individuoEvento, self.uris.dp_id_event_resource, Literal(diccionarioECA["id_event_resource"])])
        event.append(
            [individuoEvento, self.uris.dp_name_event_resource, Literal(diccionarioECA["name_event_resource"])])
        event.append([individuoEvento, self.uris.dp_name_event_object, Literal(diccionarioECA["name_event_object"])])
        return event

    def __poblarAction(self, diccionarioECA, individuoAccion):
        action = []
        action.append([individuoAccion, self.uris.dp_comparator_action, Literal(diccionarioECA["comparator_action"])])
        action.append([individuoAccion, self.uris.dp_id_action_resource, Literal(diccionarioECA["id_action_resource"])])
        action.append([individuoAccion, self.uris.dp_id_action_object, Literal(diccionarioECA["id_action_object"])])
        action.append([individuoAccion, self.uris.dp_ip_action_object, Literal(diccionarioECA["ip_action_object"])])
        action.append([individuoAccion, self.uris.dp_meaning_action, Literal(diccionarioECA["meaning_action"])])
        action.append([individuoAccion, self.uris.dp_name_action_object, Literal(diccionarioECA["name_action_object"])])
        action.append(
            [individuoAccion, self.uris.dp_name_action_resource, Literal(diccionarioECA["name_action_resource"])])
        action.append(
            [individuoAccion, self.uris.dp_type_variable_action, Literal(diccionarioECA["type_variable_action"])])
        action.append([individuoAccion, self.uris.dp_unit_action, Literal(diccionarioECA["unit_action"])])
        action.append([individuoAccion, self.uris.dp_variable_action, Literal(diccionarioECA["variable_action"])])
        return action

    def __poblarCondition(self, diccionarioECA, individuoCondicion):
        condition = []
        condition.append(
            [individuoCondicion, self.uris.dp_comparator_condition, Literal(diccionarioECA["comparator_condition"])])
        condition.append(
            [individuoCondicion, self.uris.dp_meaning_condition, Literal(diccionarioECA["meaning_condition"])])
        condition.append([individuoCondicion, self.uris.dp_type_variable_condition,
                          Literal(diccionarioECA["type_variable_condition"])])
        condition.append([individuoCondicion, self.uris.dp_unit_condition, Literal(diccionarioECA["unit_condition"])])
        condition.append(
            [individuoCondicion, self.uris.dp_variable_condition, Literal(diccionarioECA["variable_condition"])])
        return condition

# if __name__ == "__main__":
#     pob = PobladorOOS()
#     dicObj = {'id': '777', 'title': 'Coach',
#      'tags': ['Entidad Estudio', 'Entity studying room', 'funcionalidad ejecucion tecnicas PNL',
#               'NLP technical execution functionality', 'Coach', 'Coach'],
#      'description': 'Es un servicio que permite ejecutar tecnicas de PNL adecuadas para prevenir el sindrome de Burnout',
#      'feed': 'https://api.xively.com/v2/feeds/777.json', 'auto_feed_url': '', 'status': 0,
#      'updated': '11/18/2020 01:49:59', 'created': '11/18/2020 01:49:59',
#      'creator': 'https://personal.xively.com/users/manzamb', 'version': '', 'website': '',
#      'TitleHTML': '<a style="color: #336600; font-size:110%;"  href="https://xively.com/feeds/777" >Coach</a>',
#      'URLMostrar': 'https://xively.com/feeds/777', 'name': '', 'domain': 0, 'lat': '4', 'lon': '4', 'ele': '0',
#      'exposure': 0, 'disposition': 0, 'private': False, 'ip_object': ''}
#     dicRec = [{'datastream_format': 'string', 'feedid': None, 'current_value': None, 'at': '11/18/2020 01:49:59',
#       'max_value': 'Bravo', 'min_value': 'Neutral',
#       'tags': ['Actuador', 'Actuator', 'Emotion', 'Emotion', 'Caracteristica Emocion ', 'Entidad Emotion',
#                'Entidad cuarto de estudio', 'Entity studying room'], 'datapoints': None, 'datastream_id': 'Emotion',
#       'symbol': '', 'label': 'String', 'unitType': 0, 'datastream_type': 'actuador', 'featureofinterest': 'Emocion ',
#       'entityofinterest': 'Emotion'},
#      {'datastream_format': 'string', 'feedid': None, 'current_value': None, 'at': '11/18/2020 01:49:59',
#       'max_value': '0', 'min_value': '0',
#       'tags': ['Funcionalidad para mostrar mensajes', 'Functionality todisplay messages', 'Actuador', 'Actuator',
#                'Pantalla', 'screen', 'Entidad oficina', 'Caracteristica Pantalla'], 'datapoints': None,
#       'datastream_id': 'Pantalla', 'symbol': '', 'label': 'String', 'unitType': 0, 'datastream_type': 'actuador',
#       'featureofinterest': 'Pantalla', 'entityofinterest': 'oficina'}]
#     pob.poblarMetadatosObjeto("777", dicObj, dicRec)
