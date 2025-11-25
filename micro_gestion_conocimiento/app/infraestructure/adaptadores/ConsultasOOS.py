"""
Adaptador de Consultas a la Base de Conocimiento OOS
Se extiende de la interfaz IConsultasOOS permitiendo generar todo tipo de consultas a la ontología instanciada ubicada en /OWL/ontologiainstanciada.owl.
"""
#TODO configurar los metodos para que no se ejecuten cuando la onto no está activa

import os

from app.infraestructure.logging.Logging import logger
from app.infraestructure.acceso_ontologia.Ontologia import Ontologia
from app.infraestructure.util.UrisOOS import UrisOOS
from app import config

from app.infraestructure.interfaces.IConsultas import IConsultasOOS


class ConsultasOOS(IConsultasOOS):    

    def __init__(self):
        if os.path.exists(config.ontologiaInstanciada):
            self.ontologia = Ontologia(config.ontologiaInstanciada)
            self.ontoExists = True
        else:
            logger.error(f"La ontologia instanciada no existe en la ruta especificada: {config.ontologiaInstanciada}")
            self.ontoExists = False

    ## ---->  El metodo ontologia.consultaDataProperty retorna una lista con los resultados [[],[]]

# Propiedades válidas del State
    STATE_PROPERTIES = {
        'title', 'description', 'feed', 'private', 
        'status', 'updated', 'created', 'creator', 'version', 
        'website', 'service_state'
    }
    def consultar_state_property(self, property_name: str):
        """
        Consulta genérica de propiedades del State.
        
        Args:
            property_name: Nombre de la propiedad (sin prefijo oos:)
            
        Returns:
            El valor de la propiedad o None si no existe
            
        Raises:
            ValueError: Si la propiedad no está en STATE_PROPERTIES
        """
        if not self.consultarOntoActiva():
            logger.error("La ontología no está activa.")
            raise Exception("La ontología no está activa.")
        if property_name not in self.STATE_PROPERTIES:
            raise ValueError(
                f"Propiedad '{property_name}' no válida. "                
            )
        
        query = f"""
        PREFIX oos: <{UrisOOS.ns_oos}>
        SELECT ?{property_name}
        WHERE {{
            ?entity oos:{property_name} ?{property_name}.
            ?entity rdf:type  oos:State .
        }}
        """
        resultado = self.ontologia.consultaDataProperty(query)
        return resultado[0][0] if resultado and resultado[0] else None
    
############################################## CONSUTAS BaSICAS ###############################################################
    def consultarOntoActiva(self) -> bool:
        return self.ontoExists

    def consultarId(self):
        self.consultarOntoActiva()
        query = """ PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
                    SELECT ?id
                    WHERE {
                        ?entity oos:id_object ?id. 
                        ?entity rdf:type  oos:Object
                    }"""
        resultado = self.ontologia.consultaDataProperty(query)
        # print "desde consultar ID "
        # print resultado
        # print ""
        if resultado ==[]:
            resultado = ""
        else:
            resultado = resultado[0][0].decode('utf-8')
        return resultado

    ##Retornar la descripcion
    def consultarDescription(self):        
        return self.consultar_state_property('description')

    ###Retorna si el Feed es private(true) o si es public(false)
    def consultarPrivate(self):        
        return self.consultar_state_property('private')

    ###Retorna el tittle (Un nombre descriptivo para el Feed
    def consultarTitle(self):        
        return self.consultar_state_property('title')

    ###Retorna la url del feed (.json)
    def consultarFeed(self):        
        return self.consultar_state_property('feed')

    ###Retorna live si el Feed ha sido actualizado
    ###en los ultimos 15min, de lo contrario frozen
    def consultarStatus(self):       
        return self.consultar_state_property('status')

    ###Retorna la hora en la cual Feed tuvo su ultim actualizacion
    def consultarUpdated(self):
        return self.consultar_state_property('updated')

    ###Retorna la fecha en que el Feed fue creado
    def consultarCreated(self):
        return self.consultar_state_property('created')

    ###Retorna una URL referenciando al creador del Feed
    def consultarCreator(self):
        return self.consultar_state_property('creator')

    ###Retorna Version of the data format Feed returned.
    def consultarVersion(self):
        return self.consultar_state_property('version')
    ###Retorna la URL de un sitio web que es relevante para este feed
    def consultarWebsite(self):
        return self.consultar_state_property('website')

    ###Retorna el estado del servicio basico del objeto
    def consultarServiceState(self):
        return self.consultar_state_property('service_state')

    def consultarTagsDatastream(self, idDatastream):
        if not self.consultarOntoActiva():
            logger.error("La ontología no está activa.")
            raise Exception("La ontología no está activa.")
        queryTags = """PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
                    SELECT ?tags
                    WHERE {
                        ?entity oos:tags ?tags .
                        ?entity oos:datastream_id ?datastream_id.
                        FILTER regex(?datastream_id,""" + "'" + idDatastream + """')
                        ?entity rdf:type  oos:datastreams.}"""
        resultadoTags = self.ontologia.consultaDataProperty(queryTags)
        return resultadoTags

    ##Retorna un diccionario {label, symbol}
    def consultarUnitDatastream(self, idDatastream):
        if not self.consultarOntoActiva():
            logger.error("La ontología no está activa.")
            raise Exception("La ontología no está activa.")
        queryUnit = """PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
                    PREFIX kos:<http://localhost/kos#>
                    SELECT ?label ?symbol 
                    WHERE {
                        ?unidad oos:label ?label .
                        ?unidad oos:Symbol ?symbol.     
                        ?datastream  oos:isMeasured ?unidad.	             
                        ?unidad rdf:type  kos:Unit.
                        ?datastream oos:datastream_id ?datastream_id. 
                        FILTER regex(?datastream_id,""" + "'" + idDatastream + """').}"""
        keysUnit = ['label', 'symbol']
        resultadoUnit = self.ontologia.consultaDataProperty(queryUnit)
        dicUnit = self.pasarListaDiccionario(resultadoUnit, keysUnit)
        return dicUnit


    ########################################################################################################################
    ################################     #############################################

    ###Retorna una coleccion de los Datastreams en ese Feed en un
    ###diccionario { 'min_value', 'max_value', 'datastream_id', "datastream_format",  "datastream_type" ,'tags','unit':{'label','symbol'} }
    def consultarDatastreams(self, idDatastream):
        if not self.consultarOntoActiva():
            logger.error("La ontología no está activa.")
            raise Exception("La ontología no está activa.")
        keys = ['min_value', 'max_value', 'datastream_id', "datastream_format", "datastream_type", 'tags', 'unit']
        query = """ PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
                    PREFIX kos:<http://localhost/kos#>
                    SELECT ?min_value ?max_value  ?datastream_id ?datastream_format ?datastream_type ?label ?symbol
                    WHERE {  
                            ?entity oos:min_value ?min_value.
                            ?entity oos:max_value ?max_value.
                            ?entity oos:datastream_id ?datastream_id.
                            ?entity oos:datastream_format ?datastream_format.
                            ?unidad oos:label ?label .
                            ?unidad oos:Symbol ?symbol.     
                            ?entity  oos:isMeasured ?unidad.	             
                            ?unidad rdf:type  kos:Unit.
                            ?entity oos:datastream_type ?datastream_type.
                            FILTER regex(?datastream_id,""" + "'" + idDatastream + """')
                            ?entity rdf:type  oos:datastreams.}"""
        resultado = self.ontologia.consultaDataProperty(query)
        ##Consulta para los tags
        resultadoTags = self.consultarTagsDatastream(idDatastream)
        resultado.append(resultadoTags)
        dictUnit = {}
        dictUnit['label'] = resultado[5]
        dictUnit['symbol'] = resultado[6]
        resultado.append(dictUnit)
        diccionario = self.pasarListaDiccionario(resultado, keys)
        return diccionario

    ##Retorna [[],[],[]]
    def consultarTagsTodosDatastreams(self):
        if not self.consultarOntoActiva():
            logger.error("La ontología no está activa.")
            raise Exception("La ontología no está activa.")
        queryTags = """PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
                    SELECT ?datastream_id ?tags
                    WHERE {
                        ?entity oos:tags ?tags .
                        ?entity oos:datastream_id ?datastream_id.
                        ?entity rdf:type  oos:datastreams.}"""
        resultadoTags = self.ontologia.consultaDataProperty(queryTags)
        return resultadoTags

    def consultarUnitTodosDatastreams(self):
        if not self.consultarOntoActiva():
            logger.error("La ontología no está activa.")
            raise Exception("La ontología no está activa.")
        keys = ["datastream_id", "label", "symbol"]
        queryUnit = """PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
                    PREFIX kos:<http://localhost/kos#>
                    SELECT ?datastream_id ?label ?symbol 
                    WHERE {
                        ?unidad oos:label ?label .
                        ?unidad oos:Symbol ?symbol.     
                        ?datastream  oos:isMeasured ?unidad.	             
                        ?unidad rdf:type  kos:Unit.
                        ?datastream oos:datastream_id ?datastream_id.}"""
        resultadoUnit = self.ontologia.consultaDataProperty(queryUnit)
        listaDicc = []
        for item in resultadoUnit:
            listaDicc.append(self.pasarListaDiccionario(item, keys))
        return listaDicc

    def consultarTodosDatastreams(self):
        if not self.consultarOntoActiva():
            logger.error("La ontología no está activa.")
            raise Exception("La ontología no está activa.")
        keys = ['datastream_id', 'min_value', 'max_value', "datastream_format", "datastream_type", 'tags', 'unit']
        keysMetaDatos = ['datastream_id', 'min_value', 'max_value', "datastream_format", "datastream_type"]
        query = """PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
                    PREFIX kos:<http://localhost/kos#>
                    SELECT ?datastream_id ?min_value ?max_value   ?datastream_format ?datastream_type ?label ?symbol
                    WHERE {  
                        ?entity oos:min_value ?min_value.
                        ?entity oos:max_value ?max_value.
                        ?entity oos:datastream_id ?datastream_id.
                        ?entity oos:datastream_format ?datastream_format.
                        ?unidad oos:label ?label .
                                     
                       OPTIONAL{
                        ?unidad oos:Symbol ?symbol}.     
                        ?entity  oos:isMeasured ?unidad.	             
                        ?unidad rdf:type  kos:Unit.
                        ?entity oos:datastream_type ?datastream_type.
                        ?entity rdf:type  oos:datastreams.}"""
        resultado = self.ontologia.consultaDataProperty(query)
        listaDataStreams = []
        for item in resultado:
            diccDS = self.pasarListaDiccionario(item, keysMetaDatos)
            dicUnit = {}
            dicUnit['label'] = item[5]
            dicUnit['symbol'] = item[6]
            diccDS['unit'] = dicUnit
            listaDataStreams.append(diccDS)
            diccDS["tags"] = []

        ##consulta los tags
        resultadoTags = self.consultarTagsTodosDatastreams()
        for dic in listaDataStreams:
            Did = dic['datastream_id']
            for tag in resultadoTags:
                if tag[0] == Did:
                    dic['tags'].append(tag[1].decode("utf8"))
        return listaDataStreams

    ###Retorna una lista con los id de los Datastreams
    def consultarListaIdDatastreams(self):
        if not self.consultarOntoActiva():
            logger.error("La ontología no está activa.")
            raise Exception("La ontología no está activa.")
        query = """PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
                    SELECT ?datastreams
                    WHERE {
                        ?entity oos:datastream_id ?datastreams. 
                        ?entity rdf:type  oos:datastreams
                    }"""
        resultado = self.ontologia.consultaDataProperty(query)
        lista = []
        for item in resultado:
            try:
                lista.append(item[0].decode('utf-8'))
            except:
                lista.append(item[0])
        return lista

    ###Retornar la localizacion del objeto en una
    ###diccionario{lon,lat,name,domail,ele}
    def consultarLocation(self):
        if not self.consultarOntoActiva():
            logger.error("La ontología no está activa.")
            raise Exception("La ontología no está activa.")
        keys = ['lon', 'lat', 'name', 'domain', 'ele']
        query = """PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
                SELECT ?lon ?lat ?name ?domain ?ele
                WHERE {
                    ?entity oos:lon ?lon.
                    ?entity oos:lat ?lat.
                    ?entity oos:name ?name.
                    ?entity oos:domain ?domain.
                    ?entity oos:ele ?ele.
                    ?entity rdf:type  oos:location}"""
        resultado = self.ontologia.consultaDataProperty(query)[0]
        diccionario = self.pasarListaDiccionario(resultado, keys)
        return diccionario

    ################################################################################################################

    def consultarState(self):
        if not self.consultarOntoActiva():
            logger.error("La ontología no está activa.")
            raise Exception("La ontología no está activa.")
        keys = ['id', 'title', 'description', 'created', 'creator', 'feed', 'private', 'status', 'updated'
            , 'version', 'website', 'service_state', "ip_object", "tags"]
        query = """PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#> 
                SELECT ?id ?title ?description ?created ?creator ?feed ?private ?status ?updated ?version ?website ?service_state
                ?ip_object 
                WHERE {
                    ?entityObject oos:id_object ?id. 
                    ?entity oos:title ?title.
                    ?entity oos:description ?description.	
                    ?entity oos:created ?created. 	
                    ?entity oos:creator ?creator. 	
                    ?entity oos:feed ?feed. 	
                    ?entity oos:private ?private. 
                    ?entity oos:status ?status. 
                    ?entity oos:updated ?updated.
                    ?entity oos:version ?version.
                    ?entity oos:website ?website.
                    ?entity oos:service_state ?service_state.
                    ?entity oos:ip_object ?ip_object.
                    ?entity rdf:type  oos:State.
                    ?entityObject rdf:type oos:Object.
                }"""
        resultado = self.ontologia.consultaDataProperty(query)[0]
        resultadoTags = self.consultarTagsObjeto()
        resultado.append(resultadoTags)

        diccionario = self.pasarListaDiccionario(resultado, keys)
        diccionario = self.decodificar(diccionario)
        return diccionario

    ##Retorna una lista con los tags
    def consultarTagsObjeto(self):
        if not self.consultarOntoActiva():
            logger.error("La ontología no está activa.")
            raise Exception("La ontología no está activa.")
        queryTags = """ PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
                    SELECT ?tags
                    WHERE {
                        ?entity oos:tags ?tags. 
                        ?entity rdf:type  oos:State
                    }"""
        ##Llega una lista de listas
        rTags = self.ontologia.consultaDataProperty(queryTags)
        resultadoTags = []
        for item in rTags:
            resultadoTags.append(item[0])
        return resultadoTags

    def consultarDataStreamFormat(self):
        if not self.consultarOntoActiva():
            logger.error("La ontología no está activa.")
            raise Exception("La ontología no está activa.")
        keys = ["datastream_id", "datastream_format", 'datastream_type']
        query = """PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
                    SELECT ?datastream_id ?datastream_format ?datastream_type
                    WHERE {
                        ?entity oos:datastream_id  ?datastream_id ;
                        oos:datastream_format ?datastream_format.
                        ?entity oos:datastream_type ?datastream_type.
                        ?entity rdf:type  oos:datastreams.
                    }"""
        resultado = self.ontologia.consultaDataProperty(query)
        listaDic = []
        for item in resultado:
            dcAux = self.pasarListaDiccionario(item, keys)
            try:
                dcAux = self.decodificar(dcAux)
            except:
                dcAux = dcAux
            listaDic.append(dcAux)
        return listaDic

    def consultarDataStreamFormatPorId(self, datastream_id):
        if not self.consultarOntoActiva():
            logger.error("La ontología no está activa.")
            raise Exception("La ontología no está activa.")
        query = """PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
                    SELECT ?datastream_id ?datastream_format
                    WHERE {
                        ?entity oos:datastream_id  ?datastream_id ;
                        oos:datastream_format ?datastream_format.
                        FILTER regex(?datastream_id, """ + "'" + datastream_id + """').
                        ?entity rdf:type  oos:datastreams.
                    }"""
        resultado = self.ontologia.consultaDataProperty(query)
        return resultado

    def consultarServiceIntelligent(self):
        if not self.consultarOntoActiva():
            logger.error("La ontología no está activa.")
            raise Exception("La ontología no está activa.")
        keys = ["id", "service_state", "datastream"]
        query = """PREFIX oos: <http://semanticsearchiot.net/sswot/Ontologies#>
                    SELECT DISTINCT ?id ?service_state ?datastream
                    WHERE {
                        ?entity oos:id_object ?id. 
                        ?entityData oos:datastream_id ?datastream. 
                        ?entityState oos:service_state ?service_state. 
                        ?entity rdf:type oos:Object.
                        ?entityData rdf:type oos:datastreams.	
                        ?entityState rdf:type oos:State.}"""
        resultadoConsulta = self.ontologia.consultaDataProperty(query)
        resultado = []
        datastream = []

        for i in resultadoConsulta:
            datastream.append(i[2])
        dicc = {}
        dicc["datastreams"] = datastream
        dicc["id"] = resultadoConsulta[0][0]
        dicc["service_state"] = resultadoConsulta[0][1]
        return dicc

    def consultarMetodosSend(self):
        if not self.consultarOntoActiva():
            logger.error("La ontología no está activa.")
            raise Exception("La ontología no está activa.")
        query = """PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
                SELECT ?entity
                WHERE {
                ?entity rdf:type ?type.
                ?type rdfs:subClassOf* oos:Send.
                }"""
        resultadoConsulta = self.ontologia.consultarInstancias(query)
        return resultadoConsulta

    def consultarMetodosReceive(self):
        if not self.consultarOntoActiva():
            logger.error("La ontología no está activa.")
            raise Exception("La ontología no está activa.")
        query = """PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
                SELECT ?entity
                WHERE {
                ?entity rdf:type ?type.
                ?type rdfs:subClassOf* oos:Receive.
                }"""
        resultadoConsulta = self.ontologia.consultarInstancias(query)
        return resultadoConsulta

    def consultarMetodosExternal(self):
        self.consultarOntoActiva()
        query = """PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
                SELECT ?entity
                WHERE {
                ?entity rdf:type ?type.
                ?type rdfs:subClassOf* oos:External.
                }"""
        resultadoConsulta = self.ontologia.consultaInstancias(query)
        return resultadoConsulta

    ########################################################################################################################
    def diccionarioMetaDatosObjeto(self):
        if not self.consultarOntoActiva():
            logger.error("La ontología no está activa.")
            raise Exception("La ontología no está activa.")
        # keys = ['id','title','description','created','creator','feed','private','status','updated' ,'version','website','service_state',"ip_object", 'lon','lat','name','domain','ele',"tags"]
        keys = ['id', 'title', 'description', 'created', 'creator', 'feed', 'private', 'status', 'updated'
            , 'version', 'website', "ip_object", 'lon', 'lat', 'name', 'domain', 'ele', "tags"]
        query = """PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#> 
                SELECT ?id ?title ?description ?created ?creator ?feed ?private ?status ?updated ?version ?website 
                ?ip_object ?lon ?lat ?name ?domain ?ele
                WHERE {
                    ?entityObject oos:id_object ?id. 
                    ?entityObject oos:ip_object ?ip_object.
                    ?entityObject rdf:type oos:Object.
                    ?entity oos:title ?title.
                    ?entity oos:description ?description.	
                    ?entity oos:created ?created. 	
                    ?entity oos:creator ?creator. 	
                    ?entity oos:feed ?feed. 	
                    ?entity oos:private ?private. 
                    ?entity oos:status ?status. 
                    ?entity oos:updated ?updated.
                    ?entity oos:version ?version.
                    ?entity oos:website ?website.
                    ?entity rdf:type oos:State.
                    ?location oos:lon ?lon.
                    ?location oos:lat ?lat.
                    ?location oos:name_location ?name.
                    ?location oos:domain ?domain.
                    ?location oos:ele ?ele.
                    ?location rdf:type  oos:location
                }"""

        ##print(query)
        ##print (self.ontologia.consultaDataProperty(query))
        r = self.ontologia.consultaDataProperty(query)
        #print(r)
        resultado = self.ontologia.consultaDataProperty(query)[0]
        resultadoTags = self.consultarTagsObjeto()
        resultado.append(resultadoTags)

        diccionario = self.pasarListaDiccionario(resultado, keys)
        diccionario = self.decodificar(diccionario)
        return diccionario

    ##Retorna una lista de diccionarios
    ##cada diccionario tiene las claves:
    # [("datastream_id", ("label", ("symbol", ("datastream_type",("min_value"("max_value"]
    def listaMetaDatosDataStreams(self):
        lista = []
        datastreams = self.consultarTodosDatastreams()
        return datastreams

    ########## Consultas ecas###########################################################################################

    def tieneContrato(self, osidDestino):
        self.consultarOntoActiva()
        keys = ["id", "id_action_resource", "comparator_action", "variable_action", "type_variable_action"]
        # [['708637323', 'calefactor', 'igual', '1']]
        query = """ PREFIX : <http://semanticsearchiot.net/sswot/Ontologies#>
                    SELECT DISTINCT ?id ?id_action_resource ?comparator_action ?variable_action ?type_variable_action
                    where{
                            {
                                ?evento :id_event_object ?id.
                                FILTER regex(?id, """ + "'" + osidDestino + """').
                                ?entity rdf:type :Event}
                        UNION {
                                ?accion :id_action_object ?id.
                                ?action :id_action_resource ?id_action_resource.
                                ?action :comparator_action ?comparator_action.
                                ?action :variable_action ?variable_action.
                                ?action :type_variable_action ?type_variable_action.
                                FILTER regex(?id, """ + "'" + osidDestino + """').
                                ?entity rdf:type :Action
                                }
                              }"""

        resultadoConsulta = self.ontologia.consultaDataProperty(query)
        listaDic = []
        for item in resultadoConsulta:
            listaDic.append(self.pasarListaDiccionario(item, keys))
        return listaDic

    def verificarContrato(self, osid, osidDestino):
        self.consultarOntoActiva()
        keys = ["osid", "osidDestino", "id_action_resource", "comparator_action", "variable_action",
                "type_variable_action", "eca_state"]
        # [['708637323', 'calefactor', 'igual', '1']]
        query = """ PREFIX : <http://semanticsearchiot.net/sswot/Ontologies#>
                    SELECT DISTINCT ?osid ?osidDestino ?id_action_resource ?comparator_action ?variable_action ?type_variable_action ?eca_state
                    where{                            
                                ?evento :id_event_object ?osid.
                                FILTER regex(?osid, """ + "'" + osid + """').
                                ?evento rdf:type :Event.
                                ?accion :id_action_object ?osidDestino.
                                ?action :id_action_resource ?id_action_resource.
                                ?action :comparator_action ?comparator_action.
                                ?action :variable_action ?variable_action.
                                ?action :type_variable_action ?type_variable_action.
                                FILTER regex(?osidDestino, """ + "'" + osidDestino + """').
                                ?action rdf:type :Action.
                                ?eca :state_eca ?eca_state.
                                ?eca rdf:type :Dinamic.
                                ?eca :StartsWith ?evento.
                              }"""

        resultadoConsulta = self.ontologia.consultaDataProperty(query)
        listaDic = []
        for item in resultadoConsulta:
            listaDic.append(self.pasarListaDiccionario(item, keys))
        return listaDic

    ##    [[]]
    def listarDinamicEstado(self, eca_state):
        if not self.consultarOntoActiva():
            logger.error("La ontología no está activa.")
            raise Exception("La ontología no está activa.")
        keys = ["eca_state", "name_eca"]
        query = """PREFIX : <http://semanticsearchiot.net/sswot/Ontologies#>
                SELECT DISTINCT ?eca_state ?name_eca 
                where{
                ?eca :name_eca ?name_eca.
                ?eca :state_eca ?eca_state.
                FILTER regex(?eca_state, """ + "'" + eca_state + """').
                ?eca rdf:type :Dinamic.
                }"""
        resultadoConsulta = self.ontologia.consultaDataProperty(query)
        listaDic = []
        for item in resultadoConsulta:
            listaDic.append(self.pasarListaDiccionario(item, keys))
        return listaDic

    def estadoEca(self, eca_name):
        self.consultarOntoActiva()
        keys = ["eca_state", "name_eca"]
        query = """PREFIX : <http://semanticsearchiot.net/sswot/Ontologies#>
                SELECT DISTINCT ?eca_state ?name_eca 
                where{
                ?eca :name_eca ?name_eca.
                ?eca :state_eca ?eca_state.
                FILTER regex(?name_eca, """ + "'" + eca_name + """').
                ?eca rdf:type :Dinamic.
                }"""
        resultadoConsulta = self.ontologia.consultaDataProperty(query)
        listaDic = []
        for item in resultadoConsulta:
            listaDic.append(self.pasarListaDiccionario(item, keys))
        return listaDic

    def usuarioEca(self, eca_name):
        self.consultarOntoActiva()
        keys = ["user_eca", "name_eca"]
        query = """PREFIX : <http://semanticsearchiot.net/sswot/Ontologies#>
                SELECT DISTINCT ?user_eca ?name_eca 
                where{
                ?eca :name_eca ?name_eca.
                ?eca :user_eca ?user_eca.
                FILTER regex(?name_eca, """ + "'" + eca_name + """').
                ?eca rdf:type :Dinamic.
                }"""
        resultadoConsulta = self.ontologia.consultaDataProperty(query)
        listaDic = []
        for item in resultadoConsulta:
            listaDic.append(self.pasarListaDiccionario(item, keys))
        return listaDic

    def listarEcasEvento(self, osid, eca_state):
        self.consultarOntoActiva()
        keys = ["eca_state", "id_event_resource", "comparator_condition", "variable_condition",
                "type_variable_condition", "unit_condition", "meaning_condition", "ip_action_object",
                "osid_object_action", "name_action_object", "comparator_action", "type_variable_action",
                "variable_action", "meaning_action", "id_action_resource", "name_action_resource", "name_eca",
                "name_event_object", "name_event_resource", "user_eca"]
        # [['708637323', 'calefactor', 'igual', '1']]
        query = """PREFIX : <http://semanticsearchiot.net/sswot/Ontologies#>
                    SELECT DISTINCT ?eca_state ?id_event_resource ?comparator_condition ?variable_condition ?type_variable_condition 
                    ?unit_condition ?meaning_condition ?ip_action_object ?osid_object_action ?name_action_object ?comparator_action
                    ?type_variable_action ?variable_action ?meaning_action ?id_action_resource ?name_action_resource ?name_eca
                    ?name_event_object ?name_event_resource
                    ?user_eca
                where{               	
                    ?evento :id_event_resource ?id_event_resource. 
                    ?evento :id_event_object ?osid.
                    ?evento :name_event_resource ?name_event_resource.
                    ?evento :name_event_object ?name_event_object.
                    FILTER regex(?osid, """ + "'" + osid + """').
                    ?evento rdf:type :Event.
                    ?eca :name_eca ?name_eca.
                    ?eca :state_eca ?eca_state.
                    OPTIONAL{?eca :user_eca ?user_eca}.
                    FILTER regex(?eca_state, """ + "'" + eca_state + """').
                    ?eca rdf:type :Dinamic. 
                    ?condicion :comparator_condition ?comparator_condition. 
                    ?condicion :variable_condition ?variable_condition. 
                    ?condicion :type_variable_condition ?type_variable_condition. 
                    ?condicion :unit_condition ?unit_condition. 
                    ?condicion :meaning_condition ?meaning_condition. 
                    ?condicion rdf:type :Condition. 
                    ?accion :id_action_object ?osid_object_action.
                    ?accion :name_action_object ?name_action_object.
                    ?accion :ip_action_object ?ip_action_object.
                    ?accion :comparator_action ?comparator_action.
                    ?accion :type_variable_action ?type_variable_action.
                    ?accion :variable_action ?variable_action. 
                    ?accion :meaning_action ?meaning_action.
                    ?accion :id_action_resource ?id_action_resource.
                    ?accion :name_action_resource ?name_action_resource.
                    ?accion rdf:type :Action.
                    ?eca :StartsWith ?evento.
                    ?evento :Check ?condicion.
                    ?condicion ?isRelatedWith ?accion.
               }"""
        resultadoConsulta = self.ontologia.consultaDataProperty(query)
        listaDic = []
        for item in resultadoConsulta:
            listaDic.append(self.pasarListaDiccionario(item, keys))
        return listaDic

    def listarEcasEventoSegunUsuario(self, osid, state_eca, usuario_eca):
        self.consultarOntoActiva()
        keys = ["eca_state", "id_event_resource", "comparator_condition", "variable_condition",
                "type_variable_condition", "unit_condition", "meaning_condition", "ip_action_object",
                "osid_object_action", "name_action_object", "comparator_action", "type_variable_action",
                "variable_action", "meaning_action", "id_action_resource", "name_action_resource", "name_eca",
                "name_event_object", "name_event_resource", "user_eca"]
        # [['708637323', 'calefactor', 'igual', '1']]
        query = """PREFIX : <http://semanticsearchiot.net/sswot/Ontologies#>
                    SELECT DISTINCT ?eca_state ?id_event_resource ?comparator_condition ?variable_condition ?type_variable_condition 
                    ?unit_condition ?meaning_condition ?ip_action_object ?osid_object_action ?name_action_object ?comparator_action
                    ?type_variable_action ?variable_action ?meaning_action ?id_action_resource ?name_action_resource ?name_eca
                    ?name_event_object ?name_event_resource
                    ?user_eca
                where{       
                ?eca :name_eca ?name_eca.
                    ?eca :state_eca ?eca_state.
                    ?eca :user_eca ?user_eca.
                        FILTER regex(?user_eca, """ + "'" + usuario_eca + """').
                    FILTER regex(?eca_state, """ + "'" + state_eca + """').
                    ?eca rdf:type :Dinamic.         	
                    ?evento :id_event_resource ?id_event_resource. 
                    ?evento :id_event_object ?osid.
                    ?evento :name_event_resource ?name_event_resource.
                    ?evento :name_event_object ?name_event_object.
                    FILTER regex(?osid, '""" + osid + """').
                    ?evento rdf:type :Event.
                    
                    ?condicion :comparator_condition ?comparator_condition. 
                    ?condicion :variable_condition ?variable_condition. 
                    ?condicion :type_variable_condition ?type_variable_condition. 
                    ?condicion :unit_condition ?unit_condition. 
                    ?condicion :meaning_condition ?meaning_condition. 
                    ?condicion rdf:type :Condition. 
                    ?accion :id_action_object ?osid_object_action.
                    ?accion :name_action_object ?name_action_object.
                    ?accion :ip_action_object ?ip_action_object.
                    ?accion :comparator_action ?comparator_action.
                    ?accion :type_variable_action ?type_variable_action.
                    ?accion :variable_action ?variable_action. 
                    ?accion :meaning_action ?meaning_action.
                    ?accion :id_action_resource ?id_action_resource.
                    ?accion :name_action_resource ?name_action_resource.
                    ?accion rdf:type :Action.
                    ?eca :StartsWith ?evento.
                    
                    ?evento :Check ?condicion.
                    ?condicion ?isRelatedWith ?accion.
               }"""
        resultadoConsulta = self.ontologia.consultaDataProperty(query)
        listaDic = []
        for item in resultadoConsulta:
            listaDic.append(self.pasarListaDiccionario(item, keys))
        return listaDic

    def listarEcas(self):
        self.consultarOntoActiva()
        # keys=['name_eca','eca_state','id_event_resource', 'ip_event_object','comparator_condition','variable_condition','type_variable_condition','unit_condition','meaning_condition','ip_action_object','osid_object_action','name_action_object' ,'comparator_action','type_variable_action','variable_action','meaning_action','id_action_resource','name_action_resource']
        keys = ['name_eca', 'eca_state', 'user_eca', 'osid_object_event', 'ip_event_object', 'name_event_object',
                'id_event_resource', 'name_event_resource', 'comparator_condition', 'variable_condition',
                'type_variable_condition', 'unit_condition', 'meaning_condition', 'osid_object_action',
                'ip_action_object', 'name_action_object', 'id_action_resource', 'name_action_resource',
                'comparator_action', 'variable_action', 'type_variable_action', 'unit_action', 'meaning_action']
        query = """PREFIX : <http://semanticsearchiot.net/sswot/Ontologies#>
                    SELECT DISTINCT ?name_eca ?eca_state ?user_eca
                    ?osid_object_event ?ip_event_object ?name_event_object
                    ?id_event_resource ?name_event_resource
                    ?comparator_condition ?variable_condition ?type_variable_condition ?unit_condition ?meaning_condition
                    ?osid_object_action ?ip_action_object  ?name_action_object
                    ?id_action_resource ?name_action_resource 
                    ?comparator_action ?variable_action ?type_variable_action  ?unit_action ?meaning_action 
                where{
                    ?eca :name_eca ?name_eca.
                    ?eca :state_eca ?eca_state.
                    OPTIONAL{?eca :user_eca ?user_eca}.
                    ?eca rdf:type :Dinamic.
                    ?evento :id_event_object ?osid_object_event.
                    ?evento :ip_event_object ?ip_event_object.
                    ?evento :id_event_resource ?id_event_resource.
                    ?evento :name_event_object ?name_event_object.
                    ?evento rdf:type :Event.
                    ?condicion :comparator_condition ?comparator_condition. 
                    ?condicion :variable_condition ?variable_condition. 
                    ?condicion :type_variable_condition ?type_variable_condition. 
                    ?condicion :unit_condition ?unit_condition. 
                    ?condicion :meaning_condition ?meaning_condition. 
                    ?condicion rdf:type :Condition.
                    ?accion :id_action_object ?osid_object_action.
                    ?accion :name_action_object ?name_action_object.
                    ?accion :ip_action_object ?ip_action_object.
                    ?accion :comparator_action ?comparator_action.
                    ?accion :type_variable_action ?type_variable_action.
                    ?accion :variable_action ?variable_action. 
                    ?accion :meaning_action ?meaning_action.
                    ?accion :id_action_resource ?id_action_resource.
                    ?accion :unit_action ?unit_action.
                    ?accion :name_action_resource ?name_action_resource.
                    ?accion rdf:type :Action.
                    ?eca :StartsWith ?evento.
                    ?evento :Check ?condicion.
                    ?condicion ?isRelatedWith ?accion.
               }"""
        try:
            resultadoConsulta = self.ontologia.consultaDataProperty(query)
            diccionarioEcas = []
            for eca in resultadoConsulta:
                diccionarioEcas.append(self.pasarListaDiccionario(eca, keys))
            return diccionarioEcas
        except Exception as e:
            print( "Error en listarontologios ontologias pck")
            print( e)

    def listarEcasUsuario(self, user_eca):
        self.consultarOntoActiva()
        # keys=['name_eca','eca_state','id_event_resource', 'ip_event_object','comparator_condition','variable_condition','type_variable_condition','unit_condition','meaning_condition','ip_action_object','osid_object_action','name_action_object' ,'comparator_action','type_variable_action','variable_action','meaning_action','id_action_resource','name_action_resource']
        keys = ['name_eca', 'eca_state', 'user_eca', 'osid_object_event', 'ip_event_object', 'name_event_object',
                'id_event_resource', 'name_event_resource', 'comparator_condition', 'variable_condition',
                'type_variable_condition', 'unit_condition', 'meaning_condition', 'osid_object_action',
                'ip_action_object', 'name_action_object', 'id_action_resource', 'name_action_resource',
                'comparator_action', 'variable_action', 'type_variable_action', 'unit_action', 'meaning_action']
        query = """PREFIX : <http://semanticsearchiot.net/sswot/Ontologies#>
                    SELECT DISTINCT ?name_eca ?eca_state ?user_eca
                    ?osid_object_event ?ip_event_object ?name_event_object
                    ?id_event_resource ?name_event_resource
                    ?comparator_condition ?variable_condition ?type_variable_condition ?unit_condition ?meaning_condition
                    ?osid_object_action ?ip_action_object  ?name_action_object
                    ?id_action_resource ?name_action_resource 
                    ?comparator_action ?variable_action ?type_variable_action  ?unit_action ?meaning_action 
                where{
                    ?eca :name_eca ?name_eca.
                    ?eca :state_eca ?eca_state.
                    ?eca :user_eca ?user_eca.
                    FILTER regex(?user_eca, """ + "'" + user_eca + """').
                    ?eca rdf:type :Dinamic.
                    
                    ?evento :id_event_object ?osid_object_event.
                    ?evento :ip_event_object ?ip_event_object.
                    ?evento :id_event_resource ?id_event_resource.
                    ?evento :name_event_object ?name_event_object.
                    ?evento rdf:type :Event.
                    
                    ?condicion :comparator_condition ?comparator_condition. 
                    ?condicion :variable_condition ?variable_condition. 
                    ?condicion :type_variable_condition ?type_variable_condition. 
                    ?condicion :unit_condition ?unit_condition. 
                    ?condicion :meaning_condition ?meaning_condition. 
                    ?condicion rdf:type :Condition.
                    
                    ?accion :id_action_object ?osid_object_action.
                    ?accion :name_action_object ?name_action_object.
                    ?accion :ip_action_object ?ip_action_object.
                    ?accion :comparator_action ?comparator_action.
                    ?accion :type_variable_action ?type_variable_action.
                    ?accion :variable_action ?variable_action. 
                    ?accion :meaning_action ?meaning_action.
                    ?accion :id_action_resource ?id_action_resource.
                    ?accion :unit_action ?unit_action.
                    ?accion :name_action_resource ?name_action_resource.
                    ?accion rdf:type :Action.
                    
                    ?eca :StartsWith ?evento.
                    ?evento :Check ?condicion.
                    ?condicion ?isRelatedWith ?accion.
               }"""
        try:
            resultadoConsulta = self.ontologia.consultaDataProperty(query)
            diccionarioEcas = []
            for eca in resultadoConsulta:
                diccionarioEcas.append(self.pasarListaDiccionario(eca, keys))
            return diccionarioEcas
        except Exception as e:
            print( "Error en listarontologios ontologias pck")
            print( e)

    def listarNombresEcasUsuario(self, user_eca):
        self.consultarOntoActiva()
        query = """PREFIX : <http://semanticsearchiot.net/sswot/Ontologies#>
                    SELECT DISTINCT ?name_eca ?eca_state 
                where{
                    ?eca :name_eca ?name_eca.
                    ?eca :state_eca ?eca_state.
                    OPTIONAL{?eca :user_eca ?user_eca}.
                    FILTER regex(?user_eca, """ + "'" + user_eca + """').
                    ?eca rdf:type :Dinamic.
               }"""
        try:
            resultadoConsulta = self.ontologia.consultaDataProperty(query)
            return resultadoConsulta
        except Exception as e:
            print( "Error en listarontologios ontologias pck")
            print( e)

    def getEca(self, nombreEca):
        self.consultarOntoActiva()
        self.ontologia = Ontologia()
        # keys=['name_eca','eca_state', 'user_eca','id_event_resource', 'ip_event_object','comparator_condition','variable_condition','type_variable_condition','unit_condition','meaning_condition','ip_action_object','osid_object_action','name_action_object' ,'comparator_action','type_variable_action','variable_action','meaning_action','id_action_resource','name_action_resource']
        keys = ['name_eca', 'eca_state', 'user_eca', 'osid_object_event', 'ip_event_object', 'name_event_object',
                'id_event_resource', 'name_event_resource', 'comparator_condition', 'variable_condition',
                'type_variable_condition', 'unit_condition', 'meaning_condition', 'osid_object_action',
                'ip_action_object', 'name_action_object', 'id_action_resource', 'name_action_resource',
                'comparator_action', 'variable_action', 'type_variable_action', 'unit_action', 'meaning_action']
        query = """PREFIX : <http://semanticsearchiot.net/sswot/Ontologies#>
                    SELECT DISTINCT ?name_eca ?eca_state ?user_eca
                    ?osid_object_event ?ip_event_object ?name_event_object
                    ?id_event_resource ?name_event_resource
                    ?comparator_condition ?variable_condition ?type_variable_condition ?unit_condition ?meaning_condition
                    ?osid_object_action ?ip_action_object  ?name_action_object
                    ?id_action_resource ?name_action_resource 
                    ?comparator_action ?variable_action ?type_variable_action  ?unit_action ?meaning_action 
                where{
                    ?eca :name_eca ?name_eca.
                    FILTER regex(?name_eca, """ + "'" + nombreEca + """').
                    ?eca :state_eca ?eca_state.
                    OPTIONAL{?eca :user_eca ?user_eca}.
                    ?eca rdf:type :Dinamic.
                    ?evento :id_event_object ?osid_object_event.
                    ?evento :ip_event_object ?ip_event_object.
                    ?evento :id_event_resource ?id_event_resource.
                    ?evento :name_event_object ?name_event_object.
                    ?evento :name_event_resource ?name_event_resource.
                    ?evento rdf:type :Event.
                    
                    ?condicion :comparator_condition ?comparator_condition. 
                    ?condicion :variable_condition ?variable_condition. 
                    ?condicion :type_variable_condition ?type_variable_condition. 
                    ?condicion :unit_condition ?unit_condition. 
                    ?condicion :meaning_condition ?meaning_condition. 
                    ?condicion rdf:type :Condition.
                    
                    ?accion :id_action_object ?osid_object_action.
                    ?accion :name_action_object ?name_action_object.
                    ?accion :ip_action_object ?ip_action_object.
                    ?accion :comparator_action ?comparator_action.
                    ?accion :type_variable_action ?type_variable_action.
                    ?accion :variable_action ?variable_action. 
                    ?accion :meaning_action ?meaning_action.
                    ?accion :id_action_resource ?id_action_resource.
                    ?accion :unit_action ?unit_action.
                    ?accion :name_action_resource ?name_action_resource.
                    ?accion rdf:type :Action.
                    
                    ?eca :StartsWith ?evento.
                    ?evento :Check ?condicion.
                    ?condicion :isRelatedWith ?accion.
               }"""
        ###try:
        req = self.ontologia.consultaDataProperty(query)
        #print()
        #print(query)
        resultadoConsulta = req[0]
        diccionarioEcas = self.pasarListaDiccionario(resultadoConsulta, keys)
        return diccionarioEcas
        # except Exception as e:
        #     print( "Error en getECA ontologias pck")
        #     print( e)
        #     return {}

    def setServiceIntelligent(self, valorNuevo):
        # self.ontologia = Ontologia()
        uri = UrisOOS()
        uriIndividuo = uri.individuoEstaddo
        uriDataProperty = uri.dp_service_state
        self.ontologia.actualizarDataProperty(uriIndividuo, uriDataProperty, valorNuevo)

    def setEcaState(self, valorNuevo:str, nombreECA:str):
        # self.ontologia = Ontologia()
        if not self.consultarOntoActiva():
            logger.error("La ontología no está activa.")
            raise Exception("La ontología no está activa.")
        uri = UrisOOS()
        uriIndividuo = uri.prefijo + nombreECA
        uriDataProperty = uri.dp_state_eca
        self.ontologia.actualizarDataProperty(uriIndividuo, uriDataProperty, valorNuevo)

    def setEcaListState(self, listaEcas):
        # self.ontologia = Ontologia()
        uri = UrisOOS()
        lista = []
        for item in listaEcas:  ##[[nombreEca, valornuevo]]
            uriIndividuo = uri.prefijo + item[0]  ##nombreECA
            uriDataProperty = uri.dp_state_eca
            valorNuevo = item[1]
            lista.append([uriIndividuo, uriDataProperty, valorNuevo])
        self.ontologia.actualizarListaDataProperty(lista)

    def eliminarEca(self, nombreECA):
        # self.ontologia = Ontologia()
        uri = UrisOOS()
        uriIndividuoEca = uri.prefijo + nombreECA.replace(" ", "_")
        uriIndividuoEventoEca = uri.prefijo + nombreECA + "evento"
        uriIndividuoCondicionEca = uri.prefijo + nombreECA + "condicion"
        uriIndividuoAccionEca = uri.prefijo + nombreECA + "accion"
        listaIndividuos = []
        listaIndividuos.append(uriIndividuoEca)
        listaIndividuos.append(uriIndividuoEventoEca)
        listaIndividuos.append(uriIndividuoCondicionEca)
        listaIndividuos.append(uriIndividuoAccionEca)
        self.ontologia.eliminarListaTodoIndividuo(listaIndividuos)

    ########################################################################################################################
    def pasarListaDiccionario(self, lista, keys):
        dicAux = {}
        i = 0  #
        for key in keys:
            dicAux[key] = lista[i]
            i = i + 1
        self.decodificar(dicAux)
        return dicAux

##Debido a que algunos datos tienen tildes, ennes, etc. se hace necesario este matodo
    def decodificar(self, diccionario):
        for key in diccionario:
            try:
                diccionario[key] = diccionario[key].decode("utf-8")
            except:
                diccionario[key] = diccionario[key]

        return diccionario
        ########################################################################################################################
        ################################ PLANTILLA DE LAS CONSULTAS A OOS  #############################################
        #        query = """PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
        #               SELECT ?
        #              WHERE {
        #                 ?entity oos: ?.
        #            }"""
        #        resultado = self.ontologia.consultaDataProperty(query)
        #        pprint.pprint(resultado)