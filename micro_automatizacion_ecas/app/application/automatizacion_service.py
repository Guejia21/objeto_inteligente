from typing import List, Dict, Any, Optional, Union

from app.domain.eca_models import (
    EcaDTO,
    EventoMedicionDTO,
    AccionResultDTO,
)
from app.infra.gestion_conocimiento_client import GestionConocimientoClient


Number = Union[int, float]


class AutomatizacionECAService:
    """
    Servicio que:
      - Crea ECAs delegando al micro de gestión de conocimiento.
      - Dado un evento (osid, datastream_id, valor) consulta ECAs relevantes,
        evalúa sus condiciones y devuelve las acciones que aplican.
    """

    def __init__(self, client: GestionConocimientoClient):
        self.client = client

    # ------------------ Creación de ECAs ------------------

    async def crear_eca(self, eca: EcaDTO) -> Dict[str, Any]:
        # Convertimos el DTO a diccionario con los mismos nombres
        eca_dict = eca.model_dump()
        # Delegamos la persistencia al micro de gestión de conocimiento
        result = await self.client.crear_eca(eca_dict)
        return {"status": "ECA creada (delegado en gestión de conocimiento)", "detalle": result}

    # ------------------ Evaluación de ECAs ------------------

    async def procesar_evento(self, evento: EventoMedicionDTO) -> List[AccionResultDTO]:
        """
        Flujo:
          1. Verificar ontología activa.
          2. Listar ECAs que empiezan con ese evento (osid) y están 'activos'.
          3. (Opcional) Verificar contratos si hay osid_destino.
          4. Evaluar condición comparando valor recibido vs. variable_condition.
          5. Devolver lista de acciones que se deben ejecutar.
        """
        # 1. Verificar ontología
        if not await self.client.consultar_onto_activa():
            raise RuntimeError("La ontología no está activa en micro_gestion_conocimiento.")

        # 2. Listar ECAs relevantes según osid y usuario
        ecas_raw = await self.client.listar_ecas_evento(
            osid=evento.osid,
            state_eca="activo",
            user_eca=evento.user_eca,
        )

        acciones: List[AccionResultDTO] = []

        for eca_raw in ecas_raw:
            try:
                if self._cumple_condicion_eca(eca_raw, evento.valor):
                    # 3. Verificar contrato entre osid y osid_destino
                    osid_destino = eca_raw.get("osid_object_action")
                    if osid_destino:
                        contratos = await self.client.verificar_contrato(evento.osid, osid_destino)
                        if not contratos:
                            continue

                    # 4. Construimos la acción de resultado
                    accion = AccionResultDTO(
                        name_eca=eca_raw.get("name_eca", ""),
                        osid_object_action=str(eca_raw.get("osid_object_action", "")),
                        ip_action_object=str(eca_raw.get("ip_action_object", "")),
                        id_action_resource=str(eca_raw.get("id_action_resource", "")),
                        name_action_resource=str(eca_raw.get("name_action_resource", "")),
                        variable_action=str(eca_raw.get("variable_action", "")),
                        type_variable_action=str(eca_raw.get("type_variable_action", "")),
                        meaning_action=str(eca_raw.get("meaning_action", "")),
                        unit_action=eca_raw.get("unit_action"),
                    )
                    acciones.append(accion)

            except Exception:
                continue

        return acciones

    # ---------- Helpers ----------

    def _parse_valor(self, valor_str: str, tipo: str) -> Union[Number, str, bool]:
        if tipo == "int":
            return int(valor_str)
        if tipo == "float":
            return float(valor_str)
        if tipo == "bool":
            return valor_str.lower() in ["true", "1", "sí", "si"]
        return valor_str

    def _cumple_condicion_eca(self, eca_raw: Dict[str, Any], valor_evento_str: str) -> bool:
        comparator = str(eca_raw.get("comparator_condition", "igual"))
        tipo = str(eca_raw.get("type_variable_condition", "string"))
        valor_condition_str = str(eca_raw.get("variable_condition", ""))

        v_evento = self._parse_valor(valor_evento_str, tipo)
        v_cond = self._parse_valor(valor_condition_str, tipo)

        m = comparator.lower()

        if m in ["==", "igual"]:
            return v_evento == v_cond
        if m in ["!=", "distinto"]:
            return v_evento != v_cond
        if m in [">", "mayor"]:
            return v_evento > v_cond
        if m in ["<", "menor"]:
            return v_evento < v_cond
        if m in [">=", "mayor_igual"]:
            return v_evento >= v_cond
        if m in ["<=", "menor_igual"]:
            return v_evento <= v_cond

        return False
