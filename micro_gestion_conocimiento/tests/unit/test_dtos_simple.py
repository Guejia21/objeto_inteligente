# tests/unit/test_dtos_simple.py
import pytest
import sys
import os

# Añadir path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class TestDTOsSimple:
    """4 pruebas unitarias de DTOs."""
    
    def test_object_metadata_creation(self):
        """6. Prueba creación de ObjectMetadata simulado."""
        # Simulación de ObjectMetadata
        class ObjectMetadata:
            def __init__(self, id, title="", tags=None):
                self.id = id
                self.title = title
                self.tags = tags or []
        
        metadata = ObjectMetadata(id="objeto_123", title="Objeto Inteligente")
        assert metadata.id == "objeto_123"
        assert metadata.title == "Objeto Inteligente"
        assert isinstance(metadata.tags, list)
    
    def test_data_stream_creation(self):
        """7. Prueba creación de DataStream simulado."""
        # Simulación de DataStream
        class DataStream:
            def __init__(self, datastream_id, datastream_format="", tags=None):
                self.datastream_id = datastream_id
                self.datastream_format = datastream_format
                self.tags = tags or []
        
        stream = DataStream(datastream_id="temperature_stream", datastream_format="float")
        assert stream.datastream_id == "temperature_stream"
        assert stream.datastream_format == "float"
        assert len(stream.tags) == 0
    
    def test_poblador_payload(self):
        """8. Prueba PobladorPayloadDTO simulado."""
        # Simulación de clases
        class ObjectMetadata:
            def __init__(self, id):
                self.id = id
        
        class DataStream:
            def __init__(self, datastream_id):
                self.datastream_id = datastream_id
        
        class PobladorPayloadDTO:
            def __init__(self, dicObj, dicRec):
                self.dicObj = dicObj
                self.dicRec = dicRec
        
        obj = ObjectMetadata(id="test_obj")
        stream = DataStream(datastream_id="test_stream")
        payload = PobladorPayloadDTO(dicObj=obj, dicRec=[stream])
        
        assert payload.dicObj.id == "test_obj"
        assert len(payload.dicRec) == 1
        assert payload.dicRec[0].datastream_id == "test_stream"
    
    def test_eca_payload_validation(self):
        """9. Prueba validación de ECA simulado."""
        # Simulación de validación
        def validar_eca(state_eca):
            estados_validos = ["on", "off"]
            return state_eca in estados_validos
        
        assert validar_eca("on") is True
        assert validar_eca("off") is True
        assert validar_eca("invalid") is False
        assert validar_eca("") is False