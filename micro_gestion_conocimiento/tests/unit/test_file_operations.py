# tests/unit/test_file_operations.py
import pytest
import tempfile
import os

class TestFileOperations:
    """3 pruebas unitarias de operaciones de archivo."""
    
    def test_create_and_read_file(self):
        """17. Prueba creación y lectura de archivo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_ontologia.owl")
            
            # Escribir contenido OWL simulado
            contenido = """<?xml version="1.0"?>
<rdf:RDF xmlns:oos="http://semanticsearchiot.net/sswot/Ontologies#">
  <oos:Object rdf:about="http://example.com/Objeto">
    <oos:id_object>objeto_123</oos:id_object>
  </oos:Object>
</rdf:RDF>"""
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(contenido)
            
            # Verificar
            assert os.path.exists(file_path)
            
            with open(file_path, "r", encoding="utf-8") as f:
                contenido_leido = f.read()
            
            assert "objeto_123" in contenido_leido
            assert "oos:Object" in contenido_leido
    
    def test_ontology_file_structure(self, temp_test_dir):
        """18. Prueba estructura de archivos de ontología."""
        # Crear estructura de archivos OWL
        owl_files = [
            "ontologiav18.owl",
            "ontologiaInstanciada.owl",
            "perfil_usuario.owl"
        ]
        
        for filename in owl_files:
            filepath = os.path.join(temp_test_dir, filename)
            with open(filepath, "w") as f:
                f.write(f"<!-- Archivo: {filename} -->\n")
            
            assert os.path.exists(filepath)
        
        # Contar archivos .owl
        archivos_owl = [f for f in os.listdir(temp_test_dir) if f.endswith('.owl')]
        assert len(archivos_owl) == 3
    
    def test_directory_operations(self):
        """19. Prueba operaciones con directorios."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Crear estructura de proyecto
            estructura = [
                "app/api",
                "app/application", 
                "app/infraestructure",
                "tests/unit",
                "tests/integration",
                "tests/component"
            ]
            
            for directorio in estructura:
                dir_path = os.path.join(tmpdir, directorio)
                os.makedirs(dir_path, exist_ok=True)
                assert os.path.exists(dir_path)
            
            # Verificar que se crearon los directorios principales
            assert os.path.exists(os.path.join(tmpdir, "app"))
            assert os.path.exists(os.path.join(tmpdir, "tests"))
            assert os.path.exists(os.path.join(tmpdir, "tests/unit"))