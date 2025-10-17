from app.infraestructure.IGestionBaseConocimiento import IGestionBaseConocimiento

class BaseConocimientoService:
    def __init__(self, gestion_base_conocimiento: IGestionBaseConocimiento):
        self.gestion_base_conocimiento = gestion_base_conocimiento