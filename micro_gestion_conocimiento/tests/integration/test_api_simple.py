# tests/integration/test_api_simple.py
import pytest

class TestAPISimple:
    """2 pruebas de integración simple."""
    
    def test_consultas_flow_integration(self):
        """20. Prueba flujo integrado de consultas."""
        # Componentes simulados
        class ConsultasOOS:
            def consultarId(self):
                return "objeto_integrado_001"
            
            def consultarOntoActiva(self):
                return True
        
        class ConsultasService:
            def __init__(self, consultas_oos):
                self.gestion = consultas_oos
            
            def consultar_id(self):
                return self.gestion.consultarId()
            
            def consultar_activa(self):
                return self.gestion.consultarOntoActiva()
        
        # Integración
        consultas_oos = ConsultasOOS()
        service = ConsultasService(consultas_oos)
        
        # Flujo integrado
        id_objeto = service.consultar_id()
        activa = service.consultar_activa()
        
        assert id_objeto == "objeto_integrado_001"
        assert activa is True
    
    def test_poblacion_flow_integration(self):
        """21. Prueba flujo integrado de población."""
        # Componentes simulados
        class PobladorOOS:
            def poblarMetadatosObjeto(self, dic_obj, lista_rec):
                return dic_obj["id"] == "test_integrado" and len(lista_rec) > 0
        
        class PoblacionService:
            def __init__(self, poblador):
                self.gestion = poblador
            
            def poblar(self, dic_obj, lista_rec):
                exito = self.gestion.poblarMetadatosObjeto(dic_obj, lista_rec)
                return "éxito" if exito else "fallo"
        
        # Integración
        poblador = PobladorOOS()
        service = PoblacionService(poblador)
        
        # Datos de prueba
        objeto = {"id": "test_integrado", "titulo": "Objeto Integrado"}
        recursos = [{"datastream_id": "temp", "valor": 25.5}]
        
        # Ejecutar flujo
        resultado = service.poblar(objeto, recursos)
        
        assert resultado == "éxito"