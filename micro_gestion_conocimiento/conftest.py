# conftest.py
import sys
import os
from pathlib import Path

# Añadir el directorio del proyecto al path para imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configuración mínima de pytest
import pytest

@pytest.fixture
def temp_test_dir():
    """Fixture para directorio temporal de pruebas."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir