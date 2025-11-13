"""Archivo de configuración para la aplicación."""
from pathlib import Path

broker = "test.mosquitto.org" # Dirección del broker MQTT (Potencialmente será mosquitto)
urlOntologyService = "http://localhost:8001/ontology"
urlDataStreamService = "http://localhost:8003/Datastreams"
pathMetadata = str(Path(__file__).resolve().parent / "infraestructure" / "metadata" / "metadata.json")
