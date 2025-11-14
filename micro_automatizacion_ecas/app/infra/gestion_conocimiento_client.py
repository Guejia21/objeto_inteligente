import httpx

class GestionConocimientoClient:

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def listar_ecas(self, osid: str):
        """
        Llama al microservicio de Gestión del Conocimiento para obtener las ECAs de un objeto.
        """
        url = f"{self.base_url}/ontology/ecas/listar?osid={osid}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
