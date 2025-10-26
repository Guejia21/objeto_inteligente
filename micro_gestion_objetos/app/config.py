"""Archivo de configuración para la aplicación."""
from pathlib import Path

broker = "test.mosquitto.org" # Dirección del broker MQTT (Potencialmente será mosquitto)
urlOntologyService = "http://localhost:8000"
pathMetadata = str(Path(__file__).resolve().parent / "infraestructure" / "metadata" / "metadata.json")
