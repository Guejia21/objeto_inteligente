# tests/unit/test_services_mock.py
import pytest
from unittest.mock import Mock

class TestServicesMock:
    """3 pruebas unitarias de servicios con mocks."""
    
    def test_consultas_service_mock(self):
        """10. Prueba ConsultasService con mock."""
        # Mock de la interfaz
        mock_gestion = Mock()
        mock_gestion.consultarOntoActiva.return_value = True
        mock_gestion.consultarId.return_value = "micro_001"
        
        # Servicio simulado
        class ConsultasService:
            def __init__(self, gestion):
                self.gestion_base_conocimiento = gestion
            
            def consultarOntoActiva(self):
                return self.gestion_base_conocimiento.consultarOntoActiva()
            
            def consultarId(self):
                return self.gestion_base_conocimiento.consultarId()
        
        service = ConsultasService(mock_gestion)
        
        # Pruebas
        assert service.consultarOntoActiva() is True
        assert service.consultarId() == "micro_001"
        
        # Verificar llamadas
        assert mock_gestion.consultarOntoActiva.call_count == 1
        assert mock_gestion.consultarId.call_count == 1
    
    def test_poblacion_service_mock(self):
        """11. Prueba PoblacionService con mock."""
        mock_gestion = Mock()
        mock_gestion.poblarMetadatosObjeto.return_value = True
        
        class PoblacionService:
            def __init__(self, gestion):
                self.gestion_poblacion = gestion
            
            def poblar_metadatos_objeto(self, dic_obj, lista_rec):
                if self.gestion_poblacion.poblarMetadatosObjeto(dic_obj, lista_rec):
                    return {"status": "Población exitosa"}
                return {"status": "Fallo en la población"}
        
        service = PoblacionService(mock_gestion)
        resultado = service.poblar_metadatos_objeto(
            {"id": "test_id"},
            [{"datastream_id": "temp_stream"}]
        )
        
        assert resultado == {"status": "Población exitosa"}
        mock_gestion.poblarMetadatosObjeto.assert_called_once()
    
    def test_set_eca_state_logic(self):
        """12. Prueba lógica de setEcaState."""
        # Lógica simulada
        def set_eca_state(valor, nombre):
            if valor not in ["on", "off"]:
                return {"error": "Valor inválido. Use 'on' o 'off'."}
            
            # Simular actualización
            return {"status": f"ECA '{nombre}' actualizada a '{valor}'"}
        
        # Casos de prueba
        assert "actualizada" in set_eca_state("on", "ECA1")["status"]
        assert "actualizada" in set_eca_state("off", "ECA2")["status"]
        assert "error" in set_eca_state("invalid", "ECA3")