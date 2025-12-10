# tests/test_ecas_api_integration.py
from fastapi.testclient import TestClient
from fastapi.routing import APIRoute

from app.main import app  # usamos la app REAL del micro


def test_listar_ecas_route_integration():
    """
    Prueba de INTEGRACIÓN de la API de ECAs.

    - Utiliza la aplicación FastAPI real definida en app.main.
    - Localiza dinámicamente una ruta GET relacionada con "eca"
      que no tenga parámetros de ruta (sin '{' en el path).
    - Llama a esa ruta con un OSID inválido y verifica que:

      * La ruta exista (si no, el test falla).
      * La respuesta tenga un código de estado razonable
        (200, 400 o 422 según la validación que haga tu API).
      * El cuerpo de la respuesta sea JSON (dict).
    """

    client = TestClient(app)

    # Buscar una ruta GET que contenga "eca" y NO tenga parámetros en el path
    eca_paths = [
        route.path
        for route in app.routes
        if isinstance(route, APIRoute)
        and "GET" in route.methods
        and "eca" in route.path.lower()
        and "{" not in route.path
    ]

    # Debe existir al menos una ruta de este tipo
    assert (
        len(eca_paths) > 0
    ), f"No se encontró ninguna ruta GET sin parámetros que contenga 'eca'. Rutas actuales: {[r.path for r in app.routes if isinstance(r, APIRoute)]}"

    # Usamos la primera que coincida
    path = eca_paths[0]

    # Llamamos la ruta con un OSID de prueba (inválido)
    response = client.get(f"{path}?osid=OBJ_TEST")

    # La API podría responder 200 (si ignora OSID), 400 (OSID inválido) o 422 (validación)
    assert response.status_code in (
        200,
        400,
        422,
    ), f"Status inesperado: {response.status_code} en {path}"

    # Debe ser un JSON
    data = response.json()
    assert isinstance(
        data, dict
    ), f"La respuesta no es un JSON dict. Tipo obtenido: {type(data)}"
