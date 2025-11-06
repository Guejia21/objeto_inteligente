import requests

from app import config


class ObjetoInteligente:
    _instance = None  # Variable de clase para almacenar la única instancia
    # Implementación del patrón Singleton
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ObjetoInteligente, cls).__new__(cls)
            cls._instance._initialized = False  # Bandera para inicialización
        return cls._instance

    def __init__(self, osid: str = None, title: str = None):
        if not getattr(self, "_initialized", False):
            self._initialized = True
            self.osid = osid
            self.title = title
            self.json = {}
            self.datastreams = []
    
    def update_attributes(self, osid: str, title: str):
        """Actualiza los atributos del objeto inteligente"""
        self.osid = osid
        self.title = title

    def estructurarJSON(self, jsonOriginal):
        """Prepara el JSON del objeto y lo adapta al formato {dicObj, dicRec} requerido.

        Acepta dos formas de entrada:
        - El dict completo que contiene keys como Conceptos, lugares, feed, etc.
        - Directamente el dict del `feed`.

        Devuelve:
            {"dicObj": {...}, "dicRec": [...]} con tipos y campos normalizados.
        """
        from app.infraestructure.logging.Logging import logger

        # Aceptar que nos pasen el objeto entero o solo el feed
        payload = jsonOriginal or {}
        if "feed" in payload and isinstance(payload.get("feed"), dict):
            feed = payload.get("feed")
        else:
            # Si nos pasó directamente el feed
            feed = payload

        # Normalizar nulos
        def norm(v, default=""):
            if v is None or v == "None":
                return default
            return v

        # Extraer datastreams (si vienen en feed)
        datastreams = []
        if isinstance(feed.get("datastreams"), list):
            datastreams = feed.get("datastreams")

        # Construir dicRec
        dicRec = []
        for recurso in datastreams:
            if not isinstance(recurso, dict):
                continue

            # Desanidar unidad
            unit = recurso.get("unit") or {}
            symbol = norm(unit.get("symbol", ""))
            label = norm(unit.get("label", ""))
            try:
                unitType = int(unit.get("unitType", 0) or 0)
            except Exception:
                unitType = 0

            # Tags: limpiar etiquetas de control y extraer caracteristica/entidad
            raw_tags = recurso.get("tags") or []
            tags = []
            featureofinterest = ""
            entityofinterest = ""
            for t in raw_tags:
                if not isinstance(t, str):
                    continue
                if t.lower() in ("sensor", "actuador", "actuator"):
                    # etiqueta de tipo, no la añadimos a tags
                    continue
                if "Caracteristica" in t:
                    # extraer lo que viene después
                    try:
                        featureofinterest = t.split("Caracteristica ", 1)[1]
                        tags.append(featureofinterest)
                    except Exception:
                        pass
                elif "Entidad" in t:
                    try:
                        entityofinterest = t.split("Entidad ", 1)[1]
                        tags.append(entityofinterest)
                    except Exception:
                        pass
                else:
                    tags.append(t)

            # Clasificar datastream_type por tags originales
            ds_type = ""
            if any(x in ("Actuador", "Actuator") for x in raw_tags):
                ds_type = "actuador"
            elif any(x == "Sensor" for x in raw_tags):
                ds_type = "sensor"

            dicRec.append({
                "datastream_id": str(recurso.get("id") or recurso.get("datastream_id", "")),
                "datastream_format": str(recurso.get("datastream_format", "float")),
                "feedid": str(recurso.get("feedid") or feed.get("id", "")),
                "current_value": str(norm(recurso.get("current_value", ""))),
                "at": str(norm(recurso.get("at", ""))),
                "max_value": str(norm(recurso.get("max_value", ""))),
                "min_value": str(norm(recurso.get("min_value", ""))),
                "tags": list(tags),
                "datapoints": str(norm(recurso.get("datapoints", ""))),
                "symbol": str(symbol),
                "label": str(label),
                "unitType": int(unitType),
                "datastream_type": str(ds_type),
                "featureofinterest": str(featureofinterest),
                "entityofinterest": str(entityofinterest)
            })

        # Construir dicObj a partir de feed + location
        location = feed.get("location") or {}
        try:
            lat = float(location.get("lat") or feed.get("lat") or 0)
        except Exception:
            lat = 0.0
        try:
            lon = float(location.get("lon") or feed.get("lon") or 0)
        except Exception:
            lon = 0.0
        try:
            ele = float(location.get("ele") or feed.get("ele") or 0)
        except Exception:
            ele = 0.0

        # id: prefer feed.id, sino primer feedid de datastreams, sino osid
        id_val = norm(feed.get("id") or (datastreams[0].get("feedid") if datastreams and isinstance(datastreams[0], dict) else None) or self.osid or "")

        dicObj = {
            "id": id_val,
            "ip_object": str(norm(payload.get("ip_object", ""))),
            "version": str(norm(feed.get("version", ""))),
            "creator": str(norm(feed.get("creator", ""))),
            "status": int(feed.get("status") or 0),
            "tags": list(feed.get("tags") or []),
            "title": str(norm(feed.get("title", ""))),
            "private": bool(feed.get("Private") or feed.get("private") or False),
            "description": str(norm(feed.get("description", ""))),
            "updated": str(norm(feed.get("updated", ""))),
            "website": str(norm(feed.get("website", ""))),
            "feed": str(norm(feed.get("feed", ""))),
            "created": str(norm(feed.get("created", ""))),
            "name": str(norm(location.get("name") or feed.get("name", ""))),
            "domain": int(location.get("domain") or feed.get("domain") or 0),
            "lat": lat,
            "lon": lon,
            "ele": ele
        }

        return {"dicObj": dicObj, "dicRec": dicRec}