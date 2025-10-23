
import rdflib
import app.config as config
import os, threading
from rdflib import *
from rdflib.namespace import RDF
from rdflib import Literal

class Ontologia:
    """Gestor de operaciones sobre la ontología perteneciente al objeto.
    Proporciona carga, consultas (SPARQL), inserciones, actualizaciones y
    operaciones entre ontologías (resta). Cada método realiza la
    persistencia correspondiente en el fichero RDF asociado."""

    def __init__(self, ontologiaIns = None, ontologiaOriginal = None):
        self.lock = threading.Lock()
        if ontologiaOriginal == None:
            self.ontologia = config.ontologia  ##Path de la ontologia sin instanciar
        else:
            self.ontologia = ontologiaOriginal  ##Path de la ontologia sin instanciar
        if ontologiaIns == None:
            self.ontologiaInst = config.ontologiaInstanciada  ##Path de la ontologia instanciada
        else:
            self.ontologiaInst = ontologiaIns  ##Path de la ontologia instanciada


        self.g = rdflib.Graph()  ##Carga la ontologia en el grafo
        # Si ya esta instanciada, la toma, de lo contrario, carga la ontologia original para instanciarla


        if os.path.exists(self.ontologiaInst):

            self.g.parse(self.ontologiaInst)
        else:
            try:
                self.g.parse(self.ontologia)
            except Exception as e:
                self.g = rdflib.Graph()
                print( "  Error inicializando la ontologia  ")
                print( e)
                print( "")

            ###################### Grafo #####################################################

    ##Teniendo la direccion de la ontologia, la carga en el grafo g
    def cargarOntologia(self, dirOntologia):
        try:
            self.g = rdflib.Graph()
            self.g.parse(dirOntologia)
        except Exception as e:
            self.g = rdflib.Graph()
            print( "  Error cargando la ontologia  del path " + dirOntologia)
            print( e)
            print( "")

    ##Carga la ontologia instanciada
    def cargarGrafoNuevo(self):
        self.g = rdflib.Graph()
        self.g.parse(self.ontologiaInst)

    ##Si existe la ontologia instanciada la carga, de lo contrario carga la ontologia
    def cargarGrafoOntologia(self):
        self.g = rdflib.Graph()
        if os.path.exists(self.ontologiaInst):
            self.g.parse(self.ontologiaInst)
        else:
            self.g.parse(self.ontologia)

    def guardarGrafoOntologia(self):
        self.g.serialize(destination=self.ontologiaInst, format='xml')
        self.cargarGrafoNuevo()

    ###################### Consultas #####################################################
    def consultaInstancias(self, query):
        self.lock.acquire()
        ##        self.cargarGrafoNuevo()
        resultado = []
        qrest = self.g.query(query)
        for row in qrest:
            resultado.append(row[0].split("#")[1].replace("()", ("")))
        self.lock.release()
        return resultado

    ##retorna una lista con los resultados [[],[]]
    def consultaDataProperty(self, query):
        self.lock.acquire()
        ##        self.cargarGrafoNuevo()
        resultado = []
        qrest = self.g.query(query)
        for row in qrest:
            aux = []
            for subrow in row:
                if not subrow == None:
                    aux.append(subrow.encode('utf-8'))
                else:
                    aux.append("")
            resultado.append(aux)
        self.lock.release()
        return resultado

    ###################### Insertar #####################################################
    def insertarIndividuo(self, uriNuevo, uriClase):
        nodoNuevo = URIRef(uriNuevo)
        clase = URIRef(uriClase)
        self.g.add((nodoNuevo, RDF.type, clase))
        self.guardarGrafoOntologia()

    def insertarListaIndividuos(self, lista):
        for i in lista:
            nodoNuevo = URIRef(i[0])
            clase = URIRef(i[1])
            self.g.add((nodoNuevo, RDF.type, clase))
        self.guardarGrafoOntologia()

    def insertarDataProperty(self, uriIndividuo, uriData, valor):
        individuo = URIRef(uriIndividuo)
        dataProperty = URIRef(uriData)
        self.g.add((individuo, dataProperty, valor))
        self.guardarGrafoOntologia()

    def insertarListaDataProperty(self, lista):
        for i in lista:
            individuo = URIRef(i[0])
            dataProperty = URIRef(i[1])
            self.g.add((individuo, dataProperty, i[2]))
        self.guardarGrafoOntologia()

    def insertarObjectProperty(self, uriIndividuo, uriObjectProperty, uriIndividuo2):
        individuo1 = URIRef(uriIndividuo)
        individuo2 = URIRef(uriIndividuo2)
        objectProperty = URIRef(uriObjectProperty)
        self.g.add((individuo1, objectProperty, individuo2))
        self.guardarGrafoOntologia()

    def insertarListaObjectProperty(self, lista):
        for i in lista:
            individuo1 = URIRef(i[0])
            objectProperty = URIRef(i[1])
            individuo2 = URIRef(i[2])
            self.g.add((individuo1, objectProperty, individuo2))
        self.guardarGrafoOntologia()

    ###################### Modificar #####################################################
    ##Este metodo modifica un valor en la ontologia
    ##Tiene el inconveniente que agrega muchas mas laneas a la ontologia
    ##por eso se creo el metodo ActualizarDataProperty
    #    def setDataProperty(self, uriIndividuo, uriDataProperty, valorNuevo):
    #        individuo = URIRef(uriIndividuo)
    #        valor = valorNuevo
    #        dataProperty = URIRef(uriDataProperty)
    #        self.g.set ((individuo, dataProperty, Literal(valor)))
    #        self.guardarGrafoOntologia()

    def actualizarDataProperty(self, uriIndividuo, uriDataProperty, valorNuevo):
        ##Primero se elimina de la ontologia y luego se inserta
        #print( "Inicia a actualizar dataproperty " + time.ctime())
        individuo = URIRef(uriIndividuo)
        dataProperty = URIRef(uriDataProperty)
        self.g.remove((individuo, dataProperty, None))
        self.g.add((individuo, dataProperty, Literal(valorNuevo)))
        self.g.serialize(destination=self.ontologiaInst, format='xml')
        self.cargarGrafoNuevo()
       # print( "Fin actualizar dataproperty " + time.ctime())

    def actualizarListaDataProperty(self, listaIndividuos):  ##[[uriind, uridata,valornuevo]]
        ##Primero se elimina de la ontologia y luego se inserta
        for item in listaIndividuos:
            individuo = URIRef(item[0])
            dataProperty = URIRef(item[1])
            valorNuevo = item[2]
            self.g.remove((individuo, dataProperty, None))
            self.g.add((individuo, dataProperty, Literal(valorNuevo)))
        self.g.serialize(destination=self.ontologiaInst, format='xml')
        self.cargarGrafoNuevo()

    ###################### Eliminar #####################################################
    def eliminarTodoIndividuo(self, uriIndividuo):
        try:
            ontologiaInst = self.ontologiaInst
            g = rdflib.Graph()
            g.parse(ontologiaInst)
            individuo = URIRef(uriIndividuo)
            g.remove((individuo, None, None))
            g.serialize(destination=ontologiaInst, format='xml')
            self.cargarGrafoNuevo()
        except Exception as e:
            ontologiaInst = self.ontologiaInst
            g = rdflib.Graph()
            g.parse(ontologiaInst)
            g.serialize(destination=ontologiaInst, format='xml')
            self.cargarGrafoNuevo()
            print( " Problemas eliminando todo del individuo")
            print( e)
            print( "")

    def eliminarListaTodoIndividuo(self, ListauriIndividuo):
        try:
            ontologiaInst = self.ontologiaInst
            g = rdflib.Graph()
            g.parse(ontologiaInst)
            for uriIndividuo in ListauriIndividuo:
                individuo = URIRef(uriIndividuo)
                g.remove((individuo, None, None))
            g.serialize(destination=ontologiaInst, format='xml')
            self.cargarGrafoNuevo()
        except Exception as e:
            ontologiaInst = self.ontologiaInst
            g = rdflib.Graph()
            g.parse(ontologiaInst)
            g.serialize(destination=ontologiaInst, format='xml')
            self.cargarGrafoNuevo()
            print( " Problemas eliminando todo del individuo")
            print( e)
            print( "")

    def eliminarDataProperty(self, uriIndividuo, uriDatapropertyP):
        try:
            ontologiaInst = self.ontologiaInst
            g = rdflib.Graph()
            g.parse(ontologiaInst)
            individuo = URIRef(uriIndividuo)
            dataProperty = URIRef(uriDatapropertyP)
            g.remove((individuo, dataProperty, None))
            g.serialize(destination=ontologiaInst, format='xml')
            self.cargarGrafoNuevo()
        except Exception as e:
            ontologiaInst = self.ontologiaInst
            g = rdflib.Graph()
            g.parse(ontologiaInst)
            g.serialize(destination=ontologiaInst, format='xml')
            self.cargarGrafoNuevo()
            print( " Problemas eliminando DataProperty")
            print( e)
            print( "")

    ##    def eliminarObjectProperty(self, uriIndividuo):

    ###################### Operaciones entre ontologias #####################################################
    def restarOntologias(self, pathOntologiaMinuendo, pathOntologiaSustraendo, pathOntologiaResultado):
        minuendo = rdflib.Graph()
        sustraendo = rdflib.Graph()
        r = rdflib.Graph()
        sustraendo.parse(pathOntologiaSustraendo)
        minuendo.parse(pathOntologiaMinuendo)
        r = minuendo - sustraendo
        r.serialize(destination=pathOntologiaResultado, format='xml')
        return pathOntologiaResultado
