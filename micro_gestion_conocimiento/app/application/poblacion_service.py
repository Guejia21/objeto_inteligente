from ..infraestructure.interfaces.IPoblacion import IPoblacion


class PoblacionService:
    """Clase base para servicios de población."""
    
    def __init__(self, gestion_poblacion: IPoblacion):
        self.gestion_poblacion = gestion_poblacion

    def poblar_metadatos_objeto(self, diccionarioObjeto:dict, listaRecursos:dict ) -> None:
        """Pobla los metadatos del objeto inteligente en la base de conocimiento."""
        self.gestion_poblacion.poblarMetadatosObjeto(diccionarioObjeto, listaRecursos)