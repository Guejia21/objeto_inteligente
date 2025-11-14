
ECAS_DB = []  # simulación de almacenamiento en memoria

class EcaService:
    def crear_eca(self, data: dict):
        ECAS_DB.append(data)
        return {"message": f"ECA '{data['name_eca']}' creada correctamente"}

    def listar_ecas(self):
        return ECAS_DB

    def obtener_eca(self, name: str):
        for eca in ECAS_DB:
            if eca["name_eca"] == name:
                return eca
        raise ValueError(f"No se encontró la ECA '{name}'")

    def cambiar_estado(self, name: str, state: str):
        for eca in ECAS_DB:
            if eca["name_eca"] == name:
                eca["state_eca"] = state
                return {"message": f"ECA '{name}' cambiada a estado '{state}'"}
        raise ValueError(f"No se encontró la ECA '{name}'")

    def eliminar_eca(self, name: str):
        global ECAS_DB
        ECAS_DB = [eca for eca in ECAS_DB if eca["name_eca"] != name]
        return {"message": f"ECA '{name}' eliminada correctamente"}
