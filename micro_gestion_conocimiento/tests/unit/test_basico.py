# tests/unit/test_basico.py
import pytest

class TestBasico:
    """5 pruebas unitarias básicas."""
    
    def test_suma(self):
        """1. Prueba básica de aritmética."""
        assert 1 + 1 == 2
    
    def test_string(self):
        """2. Prueba básica de strings."""
        texto = "gestión conocimiento"
        assert texto.upper() == "GESTIÓN CONOCIMIENTO"
    
    def test_lista(self):
        """3. Prueba básica de listas."""
        lista = ["unitarias", "integración", "componentes"]
        assert len(lista) == 3
        assert "unitarias" in lista
    
    def test_diccionario(self):
        """4. Prueba básica de diccionarios."""
        dic = {"tipo": "prueba", "cantidad": 12}
        assert dic["tipo"] == "prueba"
        assert dic["cantidad"] == 12
    
    def test_mock_basico(self):
        """5. Prueba básica con mocks."""
        from unittest.mock import Mock
        mock_obj = Mock()
        mock_obj.metodo.return_value = "resultado_mock"
        
        resultado = mock_obj.metodo()
        assert resultado == "resultado_mock"
        mock_obj.metodo.assert_called_once()