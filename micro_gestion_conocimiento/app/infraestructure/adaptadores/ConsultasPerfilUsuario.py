"""Adaptador para consultas en la ontología del perfil de usuario."""

from app.infraestructure.interfaces.IConsultasPerfilUsuario import IConsultasPerfilUsuario
from app.infraestructure.acceso_ontologia.OntologiaPU import OntologiaPU
from itertools import groupby
from operator import itemgetter
from app import config
import os

class ConsultasPerfilUsuario(IConsultasPerfilUsuario):

    def __init__(self, nombreOntologia):
            self.usuarioActual= nombreOntologia
            try:           
                os.stat(config.pathOWL)
            except:
                os.mkdir(config.pathOWL, 0o777)
            try:              
                self.path = config.pathOWL +self.usuarioActual #se espera que el pathOWL haya solo un archivo, la ontologia del usuario actual
                self.ontologia = OntologiaPU(self.path)
            except:
                print("DESDE INIT CONSULTAS PERFIL USUARIO ERROR AL CARGAR LA ONTOLOGIA")
            
    def consultarEmailUsuario(self):
        #print("consultarEmailUsuario")
        listaIps = []
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
        listaIps = self.ontologia.consultaDataProperty(query)
        for lista in listaIps:
            for cadena in lista:
                pos = lista.index(cadena)
                lista[pos] = cadena.decode('utf-8')
        if len(listaIps) > 0:
            return listaIps[0][0]
        else:
            return ""
        
    def consultarListaIpObjectos(self):
        listaIps = []
        query = """ PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
                    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                    PREFIX pu: <http://localhost/default#> 
                    PREFIX dogont: <http://elite.polito.it/ontologies/dogont.owl#>  
                    PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
                    PREFIX ontoprofile: <http://localhost/OntoProfile#> 

                    SELECT DISTINCT ?ipobjeto
                    WHERE {
                    OPTIONAL{
                        ?entity pu:name_thing ?nombreCosa.                  
                        ?entity rdf:type ?type.                  
                        ?type rdfs:subClassOf*  ontoprofile:Thing.
                        ?objeto oos:ip_object ?ipobjeto. 
                        ?objeto oos:id_object ?idobjeto.
                        ?objeto rdf:type oos:Object.
                        ?entity pu:related ?objeto.	
                        ?parteCasa pu:name_building_environment ?nombreparte. 	
                        ?parteCasa rdf:type ?type2.		
                        ?type2 rdfs:subClassOf* dogont:BuildingEnvironment.
                        ?edificio pu:name_building_environment ?nombedificio.   	
                        ?edificio rdf:type dogont:Building.		
                        ?edificio dogont:contains ?parteCasa.
                        ?entity oos:isUbicated ?parteCasa.
                      }.  
                    }"""
        
        listaIps = self.ontologia.consultaDataProperty(query)
        
        return listaIps

##    def consultarListaIpIdObjectos(self):
##        listaIps = []
##        query = """ PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
##                    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
##                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
##                    PREFIX pu: <http://localhost/default#> 
##                    PREFIX dogont: <http://elite.polito.it/ontologies/dogont.owl#>  
##                    PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
##                    SELECT DISTINCT ?ipobjeto ?idobjeto
##                    WHERE {
##                        ?entity pu:name_thing ?nombreCosa.                  
##                        ?entity rdf:type ?type.                  
##                        ?type rdfs:subClassOf*  ontoprofile:Thing.
##                        ?objeto oos:ip_object ?ipobjeto.
##                        ?objeto oos:id_object ?idobjeto.
##                        ?objeto rdf:type oos:Object.
##                        ?entity pu:related ?objeto.	
##                        ?parteCasa pu:name_building_environment ?nombreparte. 	
##                        ?parteCasa rdf:type ?type2.		
##                        ?type2 rdfs:subClassOf* dogont:BuildingEnvironment.
##                        ?edificio pu:name_building_environment ?nombedificio.   	
##                        ?edificio rdf:type dogont:Building.		
##                        ?edificio dogont:contains ?parteCasa.
##                        ?entity oos:isUbicated ?parteCasa.
##                    }"""
##        
##        listaIps = self.ontologia.consultaDataProperty(query)
##        
##        return listaIps
    def consultarListaIpIdObjectosUsuario(self):
        listaIps = []
        keys = ["ipobjeto", "idobjeto"]
        query = """ PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX owl: <http://www.w3.org/2002/07/owl#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX pu: <http://localhost/default#>
                    PREFIX dogont: <http://elite.polito.it/ontologies/dogont.owl#>
                    PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
                    PREFIX ontoprofile: <http://localhost/OntoProfile#> 
                    SELECT DISTINCT ?ipobjeto ?idobjeto
                    WHERE {
                        ?entity pu:name_thing ?nombreCosa.
                        ?entity rdf:type ?type.
                        ?type rdfs:subClassOf*  ontoprofile:Thing.
                        ?objeto oos:ip_object ?ipobjeto.
                        ?objeto oos:id_object ?idobjeto.
                        ?objeto rdf:type oos:Object.
                        OPTIONAL {
                            ?entity pu:related ?objeto
                        }.	
                        ?parteCasa pu:name_building_environment ?nombreparte.
                        ?parteCasa rdf:type ?type2.
                        ?type2 rdfs:subClassOf* dogont:BuildingEnvironment.
                        OPTIONAL {
                            ?parteCasa pu:related ?objeto
                        }.
                        ?edificio pu:name_building_environment ?nombedificio.
                        ?edificio rdf:type dogont:Building.
                        ?edificio dogont:contains ?parteCasa.
                        ?entity oos:isUbicated ?parteCasa.
                    }"""
        listaIps = self.ontologia.consultaDataProperty(query)
        listaIpID = []
        for item in listaIps:
            listaIpID.append(self.pasarListaDiccionario(item, keys))
        return listaIpID
        
    def consultarListaObjetosRelacionadosEdificio(self, nombreEdificio):
        try:
            nombreEdificio = nombreEdificio.decode('utf-8')
        except:
            pass
        keys = [ "name_object", "ipobjeto", "idobjeto"]
        query="""
                PREFIX pu: <http://localhost/default#> 
                PREFIX dogont: <http://elite.polito.it/ontologies/dogont.owl#> 
                PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
                SELECT  
                        ?nameobjeto ?ipobjeto ?idobjeto  
                WHERE{   
                    OPTIONAL{
                        ?objeto oos:ip_object ?ipobjeto.                         
                        ?objeto pu:name_object ?nameobjeto.                        
                        ?objeto oos:id_object ?idobjeto .                        
                        ?objeto rdf:type oos:Object.
                        ?edificio pu:related ?objeto. 
                        ?edificio pu:name_building_environment ?nombedificio. 
                        FILTER regex(?nombedificio ,'""" + nombreEdificio + """'). 
                        ?edificio rdf:type dogont:Building.
                    }.       
                }"""
        resultado = self.ontologia.consultaDataProperty(query)
        listaDiccionarios = []
        for item in resultado:
                diccionarioEcas = {}
                diccionarioEcas = self.pasarListaDiccionario(item, keys)
                listaDiccionarios.append(diccionarioEcas)
        return listaDiccionarios
        
    def consultarPartesEdificioConObjetosRelacionados(self, nombreEdificio):
        keys = [ "nombreparte",  "name_object", "ipobjeto", "idobjeto"]
        query = """
                     PREFIX pu: <http://localhost/default#> 
                     PREFIX dogont: <http://elite.polito.it/ontologies/dogont.owl#> 
                     PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#> 
                     SELECT DISTINCT ?nombreparte       
                     ?nameobjeto ?ipobjeto ?idobjeto  
                     WHERE  {   
                       OPTIONAL {                                    
                                   ?edificio pu:name_building_environment ?nombedificio.   
                                   
                        FILTER regex(?nombedificio ,'""" + nombreEdificio + """').       
                                   ?edificio rdf:type dogont:Building. 
                                   ?piso pu:name_building_environment ?nombrepiso.   ?piso rdf:type dogont:Flat.   
                                    ?parteCasa pu:name_building_environment ?nombreparte.
                                    ?parteCasa rdf:type ?typeParte.    
                                    ?typeParte rdfs:subClassOf* dogont:BuildingEnvironment.
                                    ?piso dogont:contains ?parteCasa. 
                                    ?edificio dogont:contains ?piso.
                                    ?objeto oos:ip_object ?ipobjeto.                         
                                    ?objeto pu:name_object ?nameobjeto.                        
                                    ?objeto oos:id_object ?idobjeto .                        
                                    ?objeto rdf:type oos:Object.
                                    ?parteCasa pu:related ?objeto. 
                                    ?edificio dogont:contains ?parteCasa
                        }. 
                    }
                """
        resultado = self.ontologia.consultaDataProperty(query)
        listaDiccionarios = []
        for item in resultado:
                diccionarioEcas = {}
                diccionarioEcas = self.pasarListaDiccionario(item, keys)
                listaDiccionarios.append(diccionarioEcas)
        return listaDiccionarios
        
    def consultarObjetosRelacionadosACosasDeEdificio(self, nombreEdificio): # 
        keys = [  "name_thing", "name_object", "ipobjeto", "idobjeto"]
        query = """
                PREFIX pu: <http://localhost/default#> 
                PREFIX dogont: <http://elite.polito.it/ontologies/dogont.owl#> 
                PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
                SELECT  
                        ?nombreCosa   
                        ?nameobjeto ?ipobjeto ?idobjeto  
                WHERE{OPTIONAL {
                    ?edificio pu:name_building_environment ?nombedificio.  
                    ?edificio rdf:type dogont:Building.  
                    
                        FILTER regex(?nombedificio ,'""" + nombreEdificio + """').                   
                    
                        ?piso pu:name_building_environment ?nombrepiso.                          
                        ?piso rdf:type dogont:Flat.                           
                        ?parteCasa pu:name_building_environment ?nombreparte.
                        ?parteCasa rdf:type ?typeParte.                            
                        ?typeParte rdfs:subClassOf* dogont:BuildingEnvironment.                        
                        ?piso dogont:contains ?parteCasa.                         
                       
                    }.       
                }"""
        resultado = self.ontologia.consultaDataProperty(query)
        listaDiccionarios = []
        for item in resultado:
                diccionarioEcas = {}
                diccionarioEcas = self.pasarListaDiccionario(item, keys)
                listaDiccionarios.append(diccionarioEcas)
        return listaDiccionarios

    def consultarListaIpIdObjectosEdificio(self, nombreEdificio): # sale tmbn el coordinador
        listaIps = []
        try:
            nombreEdificio = nombreEdificio.decode('utf-8')
        except:
            pass
        ListaObjetosRelacionadosEdificio = self.consultarListaObjetosRelacionadosEdificio(nombreEdificio)
        PartesEdificioConObjetosRelacionados = self.consultarPartesEdificioConObjetosRelacionados(nombreEdificio)
        ObjetosRelacionadosACosasDeEdificio = self.consultarObjetosRelacionadosACosasDeEdificio(nombreEdificio)

        listaIps = ListaObjetosRelacionadosEdificio + PartesEdificioConObjetosRelacionados + ObjetosRelacionadosACosasDeEdificio
        return listaIps

    def consultarEdificioRelacionadoObjeto(self, idObjeto):
        listaIps = []
        query = """ PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX owl: <http://www.w3.org/2002/07/owl#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX pu: <http://localhost/default#>
                    PREFIX dogont: <http://elite.polito.it/ontologies/dogont.owl#>
                    PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#>
                    SELECT DISTINCT ?nombedificio
                    WHERE {
                        OPTIONAL {?objeto oos:ip_object ?ipobjeto}.
                        OPTIONAL {?objeto oos:id_object ?idobjeto}.
                        FILTER regex(?idobjeto ,'""" + idObjeto + """').
                        ?objeto rdf:type oos:Object.
                        ?edificio pu:name_building_environment ?nombedificio.
                        ?edificio rdf:type dogont:Building.
                        ?edificio pu:related ?objeto
                    }"""
        listaIps = self.ontologia.consultaDataProperty(query)
        #print (colored("la lista de ips edificio relacionado ", 'green'))
        #print (listaIps)
        return listaIps
    
    
    def consultarListaPreferenciasObjetoEventoporOSID(self, idObjeto):
        keys = ['name_eca','state_eca','id_event_object','ip_event_object','name_event_object','id_event_resource','name_event_resource', 'comparator_condition','variable_condition','type_variable_condition','unit_condition','meaning_condition','id_action_object','ip_action_object','name_action_object','id_action_resource','name_action_resource','comparator_action','variable_action','type_variable_action','unit_action','meaning_action', 'name_activity', 'start_date_activity','end_date_activity' ]
        query = """ PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#> 
                    PREFIX : <http://localhost/default#>                    
                    PREFIX upo:<http://localhost/UPO#>
                    SELECT DISTINCT ?name_eca ?eca_state 
                    ?osid_object_event ?ip_event_object ?name_event_object ?id_event_resource ?name_event_resource 
                    ?comparator_condition ?variable_condition ?type_variable_condition ?unit_condition ?meaning_condition 
                    ?osid_object_action ?ip_action_object  ?name_action_object ?id_action_resource ?name_action_resource ?comparator_action ?variable_action ?type_variable_action  ?unit_action ?meaning_action 
                    ?name_activity ?start_date_activity ?end_date_activity
                    WHERE{
                        ?eca :name_preference ?name_eca. 
                        ?eca :state_preference ?eca_state. 
                        ?eca rdf:type upo:Preference.
                        ?evento oos:id_event_object ?osid_object_event.  
                        FILTER regex(?osid_object_event, '""" + idObjeto + """').
                        ?evento oos:ip_event_object ?ip_event_object. 
                        ?evento oos:id_event_resource ?id_event_resource. 
                        ?evento oos:name_event_object ?name_event_object.
                        ?evento oos:name_event_resource ?name_event_resource. 
                        ?evento rdf:type oos:Event.
                        ?condicion oos:comparator_condition ?comparator_condition. 
                        ?condicion oos:variable_condition ?variable_condition.  
                        ?condicion oos:type_variable_condition ?type_variable_condition. 
                        OPTIONAL{
                            ?condicion oos:unit_condition ?unit_condition
                        }.  
                        ?condicion oos:meaning_condition ?meaning_condition.   
                        ?condicion rdf:type oos:Condition.
                        ?accion oos:id_action_object ?osid_object_action. 
                        ?accion oos:name_action_object ?name_action_object.
                        ?accion oos:ip_action_object 
                        ?ip_action_object. ?accion oos:comparator_action ?comparator_action. 
                        ?accion oos:variable_action ?variable_action.  
                        ?accion oos:meaning_action ?meaning_action. 
                        ?accion oos:type_variable_action ?type_variable_action. 
                        ?accion oos:id_action_resource ?id_action_resource. 
                        OPTIONAL{
                            ?accion oos:unit_action ?unit_action
                        }. 
                        ?accion oos:name_action_resource ?name_action_resource.
                        ?accion rdf:type oos:Action.
                        ?eca oos:StartsWith ?evento. 
                        ?evento oos:Check ?condicion. 
                        ?condicion oos:isRelatedWith ?accion.
                        OPTIONAL{ 
                            ?activity :name_activity  ?name_activity. 
                            ?activity rdf:type :Activity.
                            ?shedule :start_date_activity ?start_date_activity. 
                            ?shedule :end_date_activity ?end_date_activity.
                            ?shedule rdf:type :Shedule_Activity. 
                            ?activity :realize ?shedule.
                            ?eca  oos:StartsWith ?activity.
                        }   
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
            
    def consultarListaPreferenciasObjetoAccionporOSID(self, idObjeto):
        keys = ['name_eca','state_eca','id_event_object','ip_event_object','name_event_object','id_event_resource','name_event_resource', 'comparator_condition','variable_condition','type_variable_condition','unit_condition','meaning_condition','id_action_object','ip_action_object','name_action_object','id_action_resource','name_action_resource','comparator_action','variable_action','type_variable_action','unit_action','meaning_action', 'name_activity', 'start_date_activity','end_date_activity' ]
        query = """ PREFIX  oos: <http://semanticsearchiot.net/sswot/Ontologies#> 
                    PREFIX : <http://localhost/default#>
                    SELECT DISTINCT ?name_eca ?eca_state 
                    PREFIX upo:<http://localhost/UPO#>
                    ?osid_object_event ?ip_event_object ?name_event_object ?id_event_resource ?name_event_resource 
                    ?comparator_condition ?variable_condition ?type_variable_condition ?unit_condition ?meaning_condition 
                    ?osid_object_action ?ip_action_object  ?name_action_object ?id_action_resource ?name_action_resource ?comparator_action ?variable_action ?type_variable_action  ?unit_action ?meaning_action 
                    ?name_activity ?start_date_activity ?end_date_activity
                    WHERE{
                        ?eca :name_preference ?name_eca. 
                        ?eca :state_preference ?eca_state. 
                        ?eca rdf:type upo:Preference.
                        ?evento oos:id_event_object ?osid_object_event.  
                        ?evento oos:ip_event_object ?ip_event_object. 
                        ?evento oos:id_event_resource ?id_event_resource. 
                        ?evento oos:name_event_object ?name_event_object.
                        ?evento oos:name_event_resource ?name_event_resource. 
                        ?evento rdf:type oos:Event.
                        ?condicion oos:comparator_condition ?comparator_condition. 
                        ?condicion oos:variable_condition ?variable_condition.  
                        ?condicion oos:type_variable_condition ?type_variable_condition. 
                        OPTIONAL{
                            ?condicion oos:unit_condition ?unit_condition
                        }.  
                        ?condicion oos:meaning_condition ?meaning_condition.   
                        ?condicion rdf:type oos:Condition.
                        ?accion oos:id_action_object ?osid_object_action. 
                        FILTER regex(?osid_object_action, '""" + idObjeto + """').
                        ?accion oos:name_action_object ?name_action_object.
                        ?accion oos:ip_action_object 
                        ?ip_action_object. ?accion oos:comparator_action ?comparator_action. 
                        ?accion oos:variable_action ?variable_action.  
                        ?accion oos:meaning_action ?meaning_action. 
                        ?accion oos:type_variable_action ?type_variable_action. 
                        ?accion oos:id_action_resource ?id_action_resource. 
                        OPTIONAL{
                            ?accion oos:unit_action ?unit_action
                        }. 
                        ?accion oos:name_action_resource ?name_action_resource.
                        ?accion rdf:type oos:Action.
                        ?eca oos:StartsWith ?evento. 
                        ?evento oos:Check ?condicion. 
                        ?condicion oos:isRelatedWith ?accion.
                        OPTIONAL{ 
                            ?activity :name_activity  ?name_activity. 
                            ?activity rdf:type :Activity.
                            ?shedule :start_date_activity ?start_date_activity. 
                            ?shedule :end_date_activity ?end_date_activity.
                            ?shedule rdf:type :Shedule_Activity. 
                            ?activity :realize ?shedule.
                            ?eca  oos:StartsWith ?activity.
                        }   
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
            
    def consultarListaPreferenciasporOSID(self, idObjeto):
        return self.consultarListaPreferenciasObjetoAccionporOSID(idObjeto)+self.consultarListaPreferenciasObjetoEventoporOSID(idObjeto)
########################################################################################################################
    def pasarListaDiccionario(self, lista, keys):
        dicAux = {}
        i = 0#      
        for key in keys:
            try:
                dicAux[key] = lista[i].decode('utf-8')
            except:
                dicAux[key] = lista[i]
            i = i+1
        return dicAux
    
    def decodificar(self, diccionario):
        for key in diccionario:
            try:
                diccionario[key]=diccionario[key].decode("utf8")
            
            except:
                diccionario[key]=diccionario[key]
                
        return diccionario
 ########################################################################################################################


    def consultarObjetivoUsuario(self):
        listaObjetivos = []
        keys = ["name_objective", "specific", 'start_date', 'Measurable', 'suitable_for']
        query = """ PREFIX pnl: <http://localhost/PNL#>
                    PREFIX :<http://localhost/default#>
                    SELECT ?name_objective ?specific ?start_date ?Measurable ?suitable_for
                    WHERE{
                    ?objetivo :name_objective ?name_objective.
                    ?objetivo :specific ?specific.
                    ?objetivo :start_date ?start_date.
                    ?objetivo pnl:Measurable ?Measurable.
                    ?objetivo pnl:suitable_for ?suitable_for.
                    ?objetivo rdf:type pnl:Objective.
                    }
                    """
        listaObjetivos = self.ontologia.consultaDataProperty(query)
        resultado = []
        for item in listaObjetivos:
            resultado.append(self.pasarListaDiccionario(item, keys))
        return resultado

    def consultarActosObjetivosUsuario(self):
        listaActos = []
        keys = ['name_objective', 'name_acts', 'number', 'start_date_acts', 'final_date', 'description_act', 'state_acts',
                "specific", 'start_date', 'Measurable', 'suitable_for']
        query = """ PREFIX pnl: <http://localhost/PNL#>
                    PREFIX :<http://localhost/default#>
                    SELECT ?name_objective  ?name_acts ?number ?start_date_acts ?final_date ?description_act 
                        ?state_acts ?specific ?start_date ?Measurable ?suitable_for
                    WHERE{
                        ?acto pnl:name_acts ?name_acts.
                        ?acto :number ?number.
                        ?acto :start_date_acts ?start_date_acts.
                        ?acto pnl:final_date ?final_date.
                        ?acto pnl:description_act ?description_act.
                        ?acto :state_acts ?state_acts.
                        ?acto rdf:type pnl:Acts.
                        ?objetivo :name_objective ?name_objective.
                        ?objetivo :specific ?specific.
                        ?objetivo :start_date ?start_date.
                        ?objetivo pnl:Measurable ?Measurable.
                        ?objetivo pnl:suitable_for ?suitable_for.
                        ?objetivo rdf:type pnl:Objective.
                        ?objetivo pnl:makes ?acto.
                    }"""
        listaActos = self.ontologia.consultaDataProperty(query)
        resultado = []
        for item in listaActos:
            resultado.append(self.pasarListaDiccionario(item, keys))
        return resultado

    def consultarRecursosObjetivosUsuario(self):
        listaRecursos = []
        keys = ['name_objective','name_resource', 'number_resource',
                "specific", 'start_date', 'Measurable', 'suitable_for']
        query = """ PREFIX pnl: <http://localhost/PNL#>
                    PREFIX :<http://localhost/default#>
                    SELECT ?name_objective ?name_resource ?number_resource
                           ?specific ?start_date ?Measurable ?suitable_for
                    WHERE{
                    ?rec :number_resource ?number_resource.
                    ?rec :name_resource ?name_resource.
                    ?rec rdf:type pnl:resource.
                    ?objetivo :name_objective ?name_objective.
                    ?objetivo :specific ?specific.
                    ?objetivo :start_date ?start_date.
                    ?objetivo pnl:Measurable ?Measurable.
                    ?objetivo pnl:suitable_for ?suitable_for.
                    ?objetivo rdf:type pnl:Objective.
                    ?objetivo rdf:type pnl:Objective.
                    ?objetivo pnl:requires ?rec.
                    }"""
        listaRecursos = self.ontologia.consultaDataProperty(query)
        resultado = []
        for item in listaRecursos:
            resultado.append(self.pasarListaDiccionario(item, keys))
        return resultado


    def consultarActosGroupObjetivos(self):
        actos = self.consultarActosObjetivosUsuario()
        acts = sorted(actos, key=itemgetter('name_objective'))
        listaDicActs = []
        for key, value in groupby(acts, key=itemgetter('name_objective')):
            l = []
            for k in value:
                l.append(k)
            listaDicActs.append(l)
        return listaDicActs

    def consultarRecGroupObjetivos(self):
        recursos = self.consultarRecursosObjetivosUsuario()
        listaDicRec = []
        recs = sorted(recursos, key=itemgetter('name_objective'))
        for key, value in groupby(recs, key=itemgetter('name_objective')):
            l = []
            for k in value:
                l.append(k)
            listaDicRec.append(l)
        return (listaDicRec)

        # [[{'name_objective': 'graduarce', 'name_resource': 'r2grado', 'number_resource': '2'},
        #   {'name_objective': 'graduarce', 'name_resource': 'r3grado', 'number_resource': '3'},
        #   {'name_objective': 'graduarce', 'name_resource': 'r1grado','number_resource': '1'}],
        #  [{'name_objective': 'teminar mono', 'name_resource': 'djfdd', 'number_resource': '1'},
        #   {'name_objective': 'teminar mono', 'name_resource': 'recurso2', 'number_resource': '2'}]]

        # [[{'name_objective': 'graduarce', 'name_acts': 'pagar derechos de grado', 'number': '3','start_date_acts': '01/01/2000', 'final_date': '01/01/2000', 'description_act': 'un derecho de grado','state_acts': 'En espera'},
        #   {'name_objective': 'graduarce', 'name_acts': 'comprar toga', 'number': '1', 'start_date_acts': '01 / 01 / 2000', 'final_date': '01 / 01 / 2000', 'description_act': 'una toga', 'state_acts': 'En espera'},
        #   {'name_objective': 'graduarce', 'name_acts': 'comprar diploma', 'number': '2', 'start_date_acts': '01 / 01 / 2000', 'final_date': '01 / 01 / 2000', 'description_act': 'una diploma', 'state_acts': 'En espera'}],
        #  [{'name_objective': 'teminar mono', 'name_acts': 'nobre accion 2', 'number':'2','start_date_acts': '01/01/2000', 'final_date': '01/01/2000', 'description_act': 'una accion', 'state_acts': 'En espera'},
        #   {'name_objective': 'teminar mono', 'name_acts': 'nobre accion 1', 'number': '1', 'start_date_acts': '01/01 / 2000', 'final_date': '01 / 01 / 2000', 'description_act': 'una accion', 'state_acts': 'En espera'}]
        # ]

    def consultarActosUsuario(self):
        listaActos = []
        keys = ['name_objective', 'name_acts', 'number', 'start_date_acts', 'final_date', 'description_act', 'state_acts']
        query = """ PREFIX pnl: <http://localhost/PNL#>
                    PREFIX :<http://localhost/default#>
                    SELECT ?name_objective  ?name_acts ?number ?start_date_acts ?final_date ?description_act ?state_acts
                    WHERE{
                        ?acto pnl:name_acts ?name_acts.
                        ?acto :number ?number.
                        ?acto :start_date_acts ?start_date_acts.
                        ?acto pnl:final_date ?final_date.
                        ?acto pnl:description_act ?description_act.
                        ?acto :state_acts ?state_acts.
                        ?acto rdf:type pnl:Acts.
                        ?objetivo :name_objective ?name_objective.
                        ?objetivo rdf:type pnl:Objective.
                        ?objetivo pnl:makes ?acto.
                    }"""
        listaActos = self.ontologia.consultaDataProperty(query)
        resultado = []
        for item in listaActos:
            resultado.append(self.pasarListaDiccionario(item, keys))
        return resultado

    def consultarRecursosUsuario(self):
        listaRecursos = []
        keys = ['name_objective','name_resource', 'number_resource']
        query = """ PREFIX pnl: <http://localhost/PNL#>
                    PREFIX :<http://localhost/default#>
                    SELECT ?name_objective ?name_resource ?number_resource
                    WHERE{
                    ?rec :number_resource ?number_resource.
                    ?rec :name_resource ?name_resource.
                    ?rec rdf:type pnl:resource.

                        ?objetivo :name_objective ?name_objective.
                        ?objetivo rdf:type pnl:Objective.
                        ?objetivo pnl:requires ?rec.
                    }"""
        listaRecursos = self.ontologia.consultaDataProperty(query)
        resultado = []
        for item in listaRecursos:
            resultado.append(self.pasarListaDiccionario(item, keys))
        return resultado

# con = ConsultasPerfilUsuario('UsuarioActual.owl')
# print(con.consultarActosGroupObjetivos())
# print(con.consultarRecGroupObjetivos())

