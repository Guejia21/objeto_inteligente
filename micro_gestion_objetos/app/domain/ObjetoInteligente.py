from fastapi import requests

from app import config


class ObjetoInteligente:
    _instance = None  # Variable de clase para almacenar la única instancia
    # Implementación del patrón Singleton
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ObjetoInteligente, cls).__new__(cls)
            cls._instance.__initialized = False  # Bandera para inicialización
        return cls._instance

    def __init__(self, osid: str = None, title: str = None):
        if not self.__initialized:
            self.__initialized = True
            self.osid = osid
            self.title = title
            self.json = {}
            self.datastreams = []
    
    def update_attributes(self, osid: str, title: str):
        """Actualiza los atributos del objeto inteligente"""
        self.osid = osid
        self.title = title
    def estructurarJSON(self, jsonOriginal):
        self.json = jsonOriginal
        if self.json != {}:
            ##En el json la location esta como diccionario, aqui la agrego a la lista.
            for i in self.json:
                if (self.json[i] == None or self.json[i] == "None" or self.json[i] is None):
                    self.json[i] = ""
            if 'location' in self.json:
                location = self.json["location"]
                del self.json["location"]
                for item in location:  ##Name es la entidad superior
                    aux = location[item]
                    if (aux == None):
                        aux = ""
                    try:
                        self.json[item] = aux.decode("utf8")  ##location[item]
                    except:
                        self.json[item] = aux
            if "Private" in self.json:
                private = self.json["Private"]
                del self.json["Private"]
                if (private == None):
                    private = ""
                try:
                    self.json["private"] = private.decode("utf8")
                except:
                    self.json["private"] = private
            if "datastreams" in self.json:
                self.datastreams = self.json["datastreams"]
                del self.json["datastreams"]
                ##Comodin es solo para hacer algo con la hora de xively, por eso lo elimino
                for item2 in self.datastreams:
                    if item2['id'] == 'comodin':
                        self.datastreams.remove(item2)
                ##Se cambia la clave id por datastream_id
                for recurso in self.datastreams:
                    id = recurso['id']
                    del recurso["id"]
                    if (id == None):
                        id = ""
                    try:
                        recurso["datastream_id"] = id.decode("utf8")
                    except:
                        recurso["datastream_id"] = id
                    if "unit" in recurso:
                        unidad = recurso["unit"]
                        for u in unidad:
                            unidadAux = unidad[u]
                            if (unidadAux == None):
                                unidadAux = ""
                            try:
                                recurso[u] = unidadAux.decode("utf8")  # unidad[u]
                            except:
                                recurso[u] = unidadAux
                        del recurso["unit"]
                    if "tags" in recurso:
                        listaTags = recurso['tags']
                        if 'Actuador' in listaTags or 'Actuator' in listaTags:
                            recurso['datastream_type'] = "actuador"
                        elif 'Sensor' in listaTags:
                            recurso['datastream_type'] = "sensor"
                        caracteristica = [s for s in listaTags if "Caracteristica" in s]
                        if len(caracteristica) > 0:
                            recurso['featureofinterest'] = caracteristica[0].split("Caracteristica ")[1]
                        entidad = [s for s in listaTags if "Entidad" in s]
                        if len(entidad) > 0:
                            recurso['entityofinterest'] = entidad[0].split("Entidad ")[1]
        else:
            print("json vacio")
        return self.json