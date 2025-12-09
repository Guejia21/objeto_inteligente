"""Adaptador de Población de la Ontología OOS"""
from config import settings
import os, shutil
from infraestructure.interfaces.IPoblacion import IPoblacion
from infraestructure.acceso_ontologia.Ontologia import Ontologia
from owlready2 import *
from infraestructure.logging.Logging import logger
from rdflib import Literal
from infraestructure.util.UrisOOS import UrisOOS

onto_path = [settings.PATH_OWL]
logger.info("Ruta Ontologias: " + settings.PATH_OWL)


class PobladorOOS(IPoblacion):
    def __init__(self):
        self.individuoObjecto = None
        self.individuoEstado = None
        self.location = None
        self.uris = UrisOOS()
        self.ontologia = Ontologia()
        self._inicializar_ontologia_instanciada()

    def _inicializar_ontologia_instanciada(self):        
        if not os.path.exists(settings.PATH_OWL):
            os.makedirs(settings.PATH_OWL, mode=0o777)    
        if not os.path.exists(settings.ONTOLOGIA_INSTANCIADA):
            try:
                logger.debug("La ontologia instanciada no existe, se crea una nueva a partir de la base")
                shutil.copyfile(settings.ONTOLOGIA, settings.ONTOLOGIA_INSTANCIADA)
            except Exception as e:
                logger.error("Fallo al copiar ontologia base a ontologia instanciada")
                logger.error(e)
        self._cargar_ontologia()

    def _cargar_ontologia(self):
        """Carga la ontología instanciada."""
        self.onto = get_ontology("file://" + settings.ONTOLOGIA_INSTANCIADA).load(reload_if_newer=True)
        logger.info("Ontologia Cargada (owlready2): " + str(self.onto.loaded))

    def _recargar_ontologia(self):
        """Recarga la ontología instanciada después de cambios."""
        self.onto = get_ontology("file://" + settings.ONTOLOGIA_INSTANCIADA).load(reload=True)
        logger.debug("Ontologia recargada desde archivo")

    def _get_class(self, class_name: str):
        """Obtiene una clase de la ontología instanciada por nombre."""
        return self.onto.search_one(iri=f"*{class_name}")

    def poblarMetadatosObjeto(self, diccionarioObjeto:dict, listaRecursos:dict):
        """Pobla los metadatos del objeto inteligente usando owlready2."""        
        try:            
            # Limpiar objetos existentes
            try:
                existing_objects = self.onto.search(id_object=str(diccionarioObjeto["id"]))
                for obj in existing_objects:
                    destroy_entity(obj)
                logger.info(f"Limpiados objetos existentes con ID {diccionarioObjeto['id']}")
            except Exception as cleanup_error:
                logger.warning(f"Error durante limpieza: {cleanup_error}")
            
            # Obtener las clases de la ontología instanciada
            StateClass = self.onto.search_one(iri=self.uris.ns_oos + "State")
            ObjectClass = self.onto.search_one(iri=self.uris.ns_oos + "Object")
            LocationClass = self.onto.search_one(iri=self.uris.ns_oos + "location")
            
            if not all([StateClass, ObjectClass, LocationClass]):
                logger.error("No se encontraron las clases necesarias en la ontología")
                return False
            
            # Crear individuos en la ontología instanciada
            with self.onto:
                self.individuoEstado = StateClass("Estado")
                self.individuoObjecto = ObjectClass("Objeto")
                self.location = LocationClass("Localizacion")

            self.__poblarObjecto(diccionarioObjeto)
            self.__poblarEstado(diccionarioObjeto)
            self.__poblarLocation(diccionarioObjeto)
            self.__poblarDataStreams(listaRecursos)
            
            # Guardar la ontología instanciada
            self.onto.save(file=settings.ONTOLOGIA_INSTANCIADA, format="rdfxml")
            logger.info("Ontología guardada correctamente")
            
            logger.info("Población de metadatos exitosa")
            return True
            
        except Exception as e:
            logger.error(f"Error en poblarMetadatosObjeto: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Limpieza en caso de error
            try:
                if hasattr(self, 'individuoEstado') and self.individuoEstado is not None:
                    destroy_entity(self.individuoEstado)
                if hasattr(self, 'individuoObjecto') and self.individuoObjecto is not None:
                    destroy_entity(self.individuoObjecto)
                if hasattr(self, 'location') and self.location is not None:
                    destroy_entity(self.location)
            except:
                pass
            
            return False

    def __poblarObjecto(self, diccionarioObjeto):
        """Pobla propiedades del objeto."""
        self.individuoObjecto.id_object = [diccionarioObjeto["id"]]
        if "ip_object" in diccionarioObjeto:
            self.individuoObjecto.ip_object = [diccionarioObjeto["ip_object"]]
        logger.debug(f"Objeto poblado: id={diccionarioObjeto['id']}")

    def __poblarEstado(self, diccionarioObjeto):
        """Pobla propiedades del estado."""
        self.individuoEstado.version = [diccionarioObjeto["version"]]
        self.individuoEstado.creator = [diccionarioObjeto["creator"]]
        self.individuoEstado.status = [diccionarioObjeto["status"]]
        
        if "tags" in diccionarioObjeto:
            for item in diccionarioObjeto["tags"]:
                self.individuoEstado.tags.append(item)
        
        self.individuoEstado.title = [diccionarioObjeto["title"]]
        self.individuoEstado.private = [diccionarioObjeto["private"]]
        self.individuoEstado.description = [diccionarioObjeto["description"]]
        self.individuoEstado.updated = [diccionarioObjeto["updated"]]
        self.individuoEstado.website = [diccionarioObjeto["website"]]
        self.individuoEstado.feed = [diccionarioObjeto["feed"]]
        self.individuoEstado.created = [diccionarioObjeto["created"]]
        logger.debug(f"Estado poblado: title={diccionarioObjeto['title']}")

    def __poblarLocation(self, ds):
        """Pobla propiedades de la localización."""
        self.location.lon = [ds["lon"]]
        self.location.lat = [ds["lat"]]
        self.location.name_location = [ds["name"]]
        self.location.domain = [ds["domain"]]
        self.location.ele = [ds["ele"]]
        logger.debug(f"Localización poblada: {ds['name']}")

    def __poblarDataStreams(self, listaRecursos):
        """Pobla los datastreams del objeto."""
        logger.info("Poblando DataStreams...")
        
        # Obtener clases de la ontología instanciada
        DatastreamsClass = self.onto.search_one(iri=self.uris.ns_oos + "datastreams")
        UnitClass = self.onto.search_one(iri=self.uris.ns_kos + "Unit")
        EntitiesOfInterestClass = self.onto.search_one(iri=self.uris.ns_oos + "EntitiesOfInterest")
        FeatureOfInterestClass = self.onto.search_one(iri=self.uris.ns_ssn + "FeatureOfInterest")
        
        if not all([DatastreamsClass, UnitClass, EntitiesOfInterestClass, FeatureOfInterestClass]):
            logger.error("No se encontraron las clases necesarias para DataStreams")
            return
        
        for item in listaRecursos:            
            dataStreamsIRI = item["datastream_id"]
            unidadIRI = dataStreamsIRI + "_unidad"
            entityIRI = dataStreamsIRI + "_entity_of_interest"
            featureIRI = dataStreamsIRI + "_feature_of_interest"
            
            # Limpiar recursos existentes
            try:
                for iri in [dataStreamsIRI, unidadIRI, entityIRI, featureIRI]:
                    existing = self.onto.search(iri="*" + iri)
                    for entity in existing:
                        destroy_entity(entity)
                        logger.debug(f"Limpiado recurso existente: {iri}")
            except Exception as cleanup_error:
                logger.warning(f"Error durante limpieza de recursos: {cleanup_error}")
            
            # Crear individuos con las clases de la ontología instanciada
            with self.onto:
                datastreamObj = DatastreamsClass(dataStreamsIRI)
                unidadObj = UnitClass(unidadIRI)
                entityObj = EntitiesOfInterestClass(entityIRI)
                featureObj = FeatureOfInterestClass(featureIRI)

            # Propiedades del datastream
            datastreamObj.min_value = [str(item["min_value"])]
            datastreamObj.max_value = [str(item["max_value"])]
            datastreamObj.datastream_id = [item["datastream_id"]]
            datastreamObj.datastream_type = [item["datastream_type"]]
            datastreamObj.datastream_format = [item["datastream_format"]]

            if "tags" in item:
                for tag in item['tags']:
                    datastreamObj.tags.append(tag)

            unidadObj.label = [item["label"]]
            unidadObj.symbol = [item["symbol"]]

            featureObj.name_feature = [item["featureofinterest"]]
            entityObj.name_entity = [item["entityofinterest"]]

            # Relaciones
            datastreamObj.isMeasured.append(unidadObj)
            entityObj.isDefinedBy.append(featureObj)
            
            logger.debug(f"DataStream poblado: {item['datastream_id']}")
            
        logger.info(f"DataStreams poblados correctamente ({len(listaRecursos)} recursos)")

    def poblarECA(self, diccionarioECA:dict):  
        """Pobla una regla ECA usando RDFLib (clase Ontologia)."""      
        if not os.path.exists(settings.ONTOLOGIA_INSTANCIADA):
            logger.error("La ontología instanciada no existe en la ruta especificada.")
            return False        
        logger.info("Poblando regla ECA...")
        
        user_eca = diccionarioECA.get("user_eca", "default")
        nombreEca = diccionarioECA['name_eca'].replace(" ", "_") + user_eca

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
        
        # CRÍTICO: Recargar owlready2 después de que RDFLib guardó
        self._recargar_ontologia()
        
        logger.info("Regla ECA poblada correctamente.")
        return True

    def __poblarDinamic(self, diccionarioECA, individuoECA):
        dinamic = []
        nombreEca = diccionarioECA['name_eca'].replace(" ", "_")
        if "interest_entity_eca" in diccionarioECA:
            dinamic.append(
                [individuoECA, self.uris.dp_interest_entity_eca, Literal(diccionarioECA["interest_entity_eca"])])
        dinamic.append([individuoECA, self.uris.dp_name_eca, Literal(nombreEca)])
        dinamic.append([individuoECA, self.uris.dp_state_eca, Literal(diccionarioECA["state_eca"])])
        user_eca = diccionarioECA.get("user_eca", "default")
        dinamic.append([individuoECA, self.uris.dp_user_eca, Literal(user_eca)])
        return dinamic

    def __poblarEvent(self, diccionarioECA, individuoEvento):
        event = []
        event.append([individuoEvento, self.uris.dp_id_event_object, Literal(diccionarioECA["id_event_object"])])
        event.append([individuoEvento, self.uris.dp_ip_event_object, Literal(diccionarioECA["ip_event_object"])])
        event.append([individuoEvento, self.uris.dp_id_event_resource, Literal(diccionarioECA["id_event_resource"])])
        event.append([individuoEvento, self.uris.dp_name_event_resource, Literal(diccionarioECA["name_event_resource"])])
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
        action.append([individuoAccion, self.uris.dp_name_action_resource, Literal(diccionarioECA["name_action_resource"])])
        action.append([individuoAccion, self.uris.dp_type_variable_action, Literal(diccionarioECA["type_variable_action"])])
        action.append([individuoAccion, self.uris.dp_unit_action, Literal(diccionarioECA["unit_action"])])
        action.append([individuoAccion, self.uris.dp_variable_action, Literal(diccionarioECA["variable_action"])])
        return action

    def __poblarCondition(self, diccionarioECA, individuoCondicion):
        condition = []
        condition.append([individuoCondicion, self.uris.dp_comparator_condition, Literal(diccionarioECA["comparator_condition"])])
        condition.append([individuoCondicion, self.uris.dp_meaning_condition, Literal(diccionarioECA["meaning_condition"])])
        condition.append([individuoCondicion, self.uris.dp_type_variable_condition, Literal(diccionarioECA["type_variable_condition"])])
        condition.append([individuoCondicion, self.uris.dp_unit_condition, Literal(diccionarioECA["unit_condition"])])
        condition.append([individuoCondicion, self.uris.dp_variable_condition, Literal(diccionarioECA["variable_condition"])])
        return condition
        
    def editarECA(self, diccionarioECA)->bool:
        """Edita una regla ECA usando owlready2."""               
        try:
            user_eca = diccionarioECA.get("user_eca", "default")
            nombreEca = diccionarioECA['name_eca'].replace(" ", "_") + user_eca
            logger.info(f"Nombre ECA a editar: {nombreEca}")
            
            iri_eca = self.uris.prefijo + nombreEca
            iri_evento = self.uris.prefijo + nombreEca + "evento"
            iri_accion = self.uris.prefijo + nombreEca + "accion"
            iri_condicion = self.uris.prefijo + nombreEca + "condicion"
            
            # Buscar con owlready2
            individuoECA_list = self.onto.search(iri=iri_eca)
            individuoEvento_list = self.onto.search(iri=iri_evento)
            individuoAccion_list = self.onto.search(iri=iri_accion)
            individuoCondicion_list = self.onto.search(iri=iri_condicion)
            
            if not individuoECA_list:
                logger.error(f"No se encontró la regla ECA con IRI: {iri_eca}")
                logger.info("Reglas ECA disponibles en la ontología:")
                dinamics = self.onto.search(type=self.onto.search_one(iri=self.uris.clase_dinamic))
                for d in dinamics:
                    logger.info(f"  - {d.iri} (name: {d.name_eca if hasattr(d, 'name_eca') else 'N/A'})")
                return False
            
            if not individuoEvento_list or not individuoAccion_list or not individuoCondicion_list:
                logger.error(f"No se encontraron todos los componentes del ECA")
                return False
            
            individuoECA = individuoECA_list[0]
            individuoEvento = individuoEvento_list[0]
            individuoAccion = individuoAccion_list[0]
            individuoCondicion = individuoCondicion_list[0]
            
            logger.info("Todos los individuos encontrados. Procediendo a editar...")
            
            self.__editarDinamic(diccionarioECA, individuoECA)
            self.__editarEvent(diccionarioECA, individuoEvento)
            self.__editarAction(diccionarioECA, individuoAccion)
            self.__editarCondition(diccionarioECA, individuoCondicion)
            
            # Guardar con owlready2 y recargar
            self.onto.save(file=settings.ONTOLOGIA_INSTANCIADA, format="rdfxml")
            self._recargar_ontologia()
            
            logger.info(f"Regla ECA '{diccionarioECA['name_eca']}' editada correctamente.")
            return True
            
        except Exception as e:
            logger.error(f"Error inesperado al editar el ECA: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def __editarDinamic(self, diccionarioECA, individuoECA):
        if "interest_entity_eca" in diccionarioECA:
            individuoECA.interest_entity_eca = [diccionarioECA["interest_entity_eca"]]
        if "name_eca" in diccionarioECA:
            individuoECA.name_eca = [diccionarioECA["name_eca"]]
        if "state_eca" in diccionarioECA:
            individuoECA.state_eca = [diccionarioECA["state_eca"]]
        user_eca = diccionarioECA.get("user_eca", "default")
        individuoECA.user_eca = [user_eca]

    def __editarEvent(self, diccionarioECA, individuoEvento):
        if "id_event_object" in diccionarioECA:
            individuoEvento.id_event_object = [diccionarioECA["id_event_object"]]
        if "ip_event_object" in diccionarioECA:
            individuoEvento.ip_event_object = [diccionarioECA["ip_event_object"]]
        if "id_event_resource" in diccionarioECA:
            individuoEvento.id_event_resource = [diccionarioECA["id_event_resource"]]
        if "name_event_resource" in diccionarioECA:
            individuoEvento.name_event_resource = [diccionarioECA["name_event_resource"]]
        if "name_event_object" in diccionarioECA:
            individuoEvento.name_event_object = [diccionarioECA["name_event_object"]]

    def __editarAction(self, diccionarioECA, individuoAccion):
        if "comparator_action" in diccionarioECA:
            individuoAccion.comparator_action = [diccionarioECA["comparator_action"]]
        if "id_action_resource" in diccionarioECA:
            individuoAccion.id_action_resource = [diccionarioECA["id_action_resource"]]
        if "id_action_object" in diccionarioECA:
            individuoAccion.id_action_object = [diccionarioECA["id_action_object"]]
        if "ip_action_object" in diccionarioECA:
            individuoAccion.ip_action_object = [diccionarioECA["ip_action_object"]]
        if "meaning_action" in diccionarioECA:
            individuoAccion.meaning_action = [diccionarioECA["meaning_action"]]
        if "name_action_object" in diccionarioECA:
            individuoAccion.name_action_object = [diccionarioECA["name_action_object"]]
        if "name_action_resource" in diccionarioECA:
            individuoAccion.name_action_resource = [diccionarioECA["name_action_resource"]]
        if "type_variable_action" in diccionarioECA:
            individuoAccion.type_variable_action = [diccionarioECA["type_variable_action"]]
        if "unit_action" in diccionarioECA:
            individuoAccion.unit_action = [diccionarioECA["unit_action"]]
        if "variable_action" in diccionarioECA:
            individuoAccion.variable_action = [diccionarioECA["variable_action"]]

    def __editarCondition(self, diccionarioECA, individuoCondicion):
        if "comparator_condition" in diccionarioECA:
            individuoCondicion.comparator_condition = [diccionarioECA["comparator_condition"]]
        if "meaning_condition" in diccionarioECA:
            individuoCondicion.meaning_condition = [diccionarioECA["meaning_condition"]]
        if "type_variable_condition" in diccionarioECA:
            individuoCondicion.type_variable_condition = [diccionarioECA["type_variable_condition"]]
        if "unit_condition" in diccionarioECA:
            individuoCondicion.unit_condition = [diccionarioECA["unit_condition"]]
        if "variable_condition" in diccionarioECA:
            individuoCondicion.variable_condition = [diccionarioECA["variable_condition"]]