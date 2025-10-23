"""Este modulo define las clases de la ontología OOS representandolas como instancias de objetos en Python."""
from app.infraestructure.util.UrisOOS import *
from owlready2 import *
from app import config

onto_path.append(config.pathOWL) # Añade la ruta de la ontología al path de OWLReady2
#Se carga la ontología para que las clases sepan cual es el esquema OWL que deben seguir
onto = get_ontology("file://" + config.ontologia).load()


class Unit(Thing):
    space_unity = get_namespace(UrisOOS.ns_kos)
    namespace = space_unity

class SOAP(Thing):
    space_soap = get_namespace(UrisOOS.ns_wei)
    namespace = space_soap

class REST(Thing):
    space_rest = get_namespace(UrisOOS.ns_wei)
    namespace = space_rest

class ServiceType(Thing):
    space_service_type = get_namespace(UrisOOS.ns_wei)
    namespace = space_service_type

class Sensor(Thing):
    space_sensor = get_namespace(UrisOOS.ns_ssn)
    namespace = space_sensor

class SemanticObject(Thing):
    space_semantic_object = get_namespace(UrisOOS.ns_oos)
    namespace = space_semantic_object

class OSDestino(Thing):
    space_os_destino = get_namespace(UrisOOS.ns_oos)
    namespace = space_os_destino

class OSOrigen(Thing):
    space_os_origen = get_namespace(UrisOOS.ns_oos)
    namespace = space_os_origen

class Properties(Thing):
    space_properties = get_namespace(UrisOOS.ns_oos)
    namespace = space_properties

class Object(Thing):
    space_object = get_namespace(UrisOOS.ns_oos)
    namespace = space_object

class State(Thing):
    space_state = get_namespace(UrisOOS.ns_oos)
    namespace = space_state

class Methods(Thing):
    space_methods = get_namespace(UrisOOS.ns_oos)
    namespace = space_methods

class External(Thing):
    space_external = get_namespace(UrisOOS.ns_oos)
    namespace = space_external

class IoTService(Thing):
    space_IoTService = get_namespace(UrisOOS.ns_wei)
    namespace = space_IoTService

class Receive(Thing):
    space_receive = get_namespace(UrisOOS.ns_oos)
    namespace = space_receive

class Send(Thing):
    space_Send = get_namespace(UrisOOS.ns_oos)
    namespace = space_Send

class Internal(Thing):
    space_Internal = get_namespace(UrisOOS.ns_oos)
    namespace = space_Internal

class location(Thing):
    space_location = get_namespace(UrisOOS.ns_oos)
    namespace = space_location

class User(Thing):
    space_User = get_namespace(UrisOOS.ns_oos)
    namespace = space_User

class Contact(Thing):
    space_Contact = get_namespace(UrisOOS.ns_ontoprofile)
    namespace = space_Contact

class Person(Thing):
    space_Person = get_namespace(UrisOOS.ns_ontoprofile)
    namespace = space_Person

class Service(Thing):
    space_Service = get_namespace(UrisOOS.ns_oos)
    namespace = space_Service

class Context(Thing):
    space_Context = get_namespace(UrisOOS.ns_oos)
    namespace = space_Context

class Knowledges(Thing):
    space_Knowledges = get_namespace(UrisOOS.ns_oos)
    namespace = space_Knowledges

class Interactions(Thing):
    space_Interactions = get_namespace(UrisOOS.ns_oos)
    namespace = space_Interactions

class Dinamic(Thing):
    space_Dinamic = get_namespace(UrisOOS.ns_oos)
    namespace = space_Dinamic

class Structural(Thing):
    space_Structural = get_namespace(UrisOOS.ns_oos)
    namespace = space_Structural

class FeatureOfInterest(Thing):
    space_FeatureOfInterest = get_namespace(UrisOOS.ns_ssn)
    namespace = space_FeatureOfInterest

class Event(Thing):
    space_Event = get_namespace(UrisOOS.ns_oos)
    namespace = space_Event

class EntitiesOfInterest(Thing):
    space_EntitiesOfInterest = get_namespace(UrisOOS.ns_oos)
    namespace = space_EntitiesOfInterest

class datastreams(Thing):
    space_datastreams = get_namespace(UrisOOS.ns_oos)
    namespace = space_datastreams

class Condition(Thing):
    space_Condition = get_namespace(UrisOOS.ns_oos)
    namespace = space_Condition

class Action(Thing):
    space_Action = get_namespace(UrisOOS.ns_oos)
    namespace = space_Action

class Activity(Thing):
    space_Activity = get_namespace(UrisOOS.ns_ontoprofile)
    namespace = space_Activity

class Mood(Thing):
    space_Mood = get_namespace(UrisOOS.ns_pnl)
    namespace = space_Mood


