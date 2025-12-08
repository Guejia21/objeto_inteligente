# tests/component/test_ontology_component_simple.py
import pytest

class TestOntologyComponentSimple:
    """2 pruebas de componentes de ontología."""
    
    def test_triple_store_component(self):
        """22. Prueba componente de almacenamiento de triples."""
        class TripleStoreComponent:
            def __init__(self):
                self.store = []
            
            def add_triple(self, s, p, o):
                """Añade una tripleta (sujeto, predicado, objeto)."""
                self.store.append((s, p, o))
                return True
            
            def query(self, s=None, p=None, o=None):
                """Consulta tripletas."""
                resultados = []
                for triple in self.store:
                    if (s is None or triple[0] == s) and \
                       (p is None or triple[1] == p) and \
                       (o is None or triple[2] == o):
                        resultados.append(triple)
                return resultados
            
            def count_triples(self):
                return len(self.store)
        
        # Crear componente
        store = TripleStoreComponent()
        
        # Añadir triples de ontología OOS
        triples_ontologia = [
            ("http://oos/Objeto", "http://oos/tipo", "http://oos/Object"),
            ("http://oos/Objeto", "http://oos/id", "micro_001"),
            ("http://oos/Estado", "http://oos/tipo", "http://oos/State"),
            ("http://oos/Estado", "http://oos/titulo", "Micro Gestion Conocimiento")
        ]
        
        for triple in triples_ontologia:
            store.add_triple(*triple)
        
        # Verificar componente
        assert store.count_triples() == 4
        
        # Consultar
        resultados = store.query(s="http://oos/Objeto")
        assert len(resultados) == 2
        
        resultados_id = store.query(p="http://oos/id")
        assert len(resultados_id) == 1
        assert resultados_id[0][2] == "micro_001"
    
    def test_eca_rule_component(self):
        """23. Prueba componente de reglas ECA."""
        class ECAComponent:
            def __init__(self):
                self.rules = {}
                self.next_id = 1
            
            def create_eca(self, name, event, condition, action, state="on"):
                """Crea una regla ECA."""
                eca_id = f"eca_{self.next_id}"
                self.rules[eca_id] = {
                    "name": name,
                    "event": event,
                    "condition": condition,
                    "action": action,
                    "state": state
                }
                self.next_id += 1
                return eca_id
            
            def get_eca(self, eca_id):
                return self.rules.get(eca_id)
            
            def update_state(self, eca_id, new_state):
                if eca_id in self.rules and new_state in ["on", "off"]:
                    self.rules[eca_id]["state"] = new_state
                    return True
                return False
            
            def list_by_state(self, state):
                return [eca for eca in self.rules.values() if eca["state"] == state]
        
        # Crear componente
        eca_component = ECAComponent()
        
        # Crear reglas ECA de ejemplo
        eca1 = eca_component.create_eca(
            name="Temperatura_Alta",
            event="temperatura_sensor",
            condition=">30",
            action="encender_ventilador",
            state="on"
        )
        
        eca2 = eca_component.create_eca(
            name="Humedad_Baja", 
            event="humedad_sensor",
            condition="<30",
            action="activar_humidificador",
            state="off"
        )
        
        # Verificar componente
        assert len(eca_component.rules) == 2
        
        # Obtener regla
        regla = eca_component.get_eca(eca1)
        assert regla["name"] == "Temperatura_Alta"
        assert regla["state"] == "on"
        
        # Cambiar estado
        eca_component.update_state(eca1, "off")
        assert eca_component.get_eca(eca1)["state"] == "off"
        
        # Listar por estado
        ecas_off = eca_component.list_by_state("off")
        assert len(ecas_off) == 2  # eca1 cambió a off, eca2 ya estaba off
        
        ecas_on = eca_component.list_by_state("on")
        assert len(ecas_on) == 0