import pytest
from app.domain.eca_task_manager import ECATaskManager


def make_simple_eca_config(name="ECA1", user="user1", state="on"):
    return {
        "name_eca": name,
        "state_eca": state,
        "user_eca": user,
        "id_event_object": "OBJ1",
        "id_action_object": "OBJ1",
        "id_event_resource": "temp",
        "id_action_resource": "led1",
        "comparator_condition": "mayor",
        "variable_condition": 30,
        "type_variable_condition": "int",
        "variable_action": "on",
        "type_variable_action": "bool",
        "comparator_action": "igual",
    }


@pytest.mark.asyncio
async def test_register_eca_adds_evaluator():
    """register_eca debe agregar una ECA al diccionario active_ecas."""
    manager = ECATaskManager()

    cfg = make_simple_eca_config()
    ok = await manager.register_eca(cfg)

    assert ok is True
    assert len(manager.active_ecas) == 1
    assert "ECA1_user1" in manager.active_ecas


def test_unregister_eca_removes_evaluator():
    """unregister_eca debe eliminar una ECA existente."""
    manager = ECATaskManager()

    # simulamos el registro previo
    manager.active_ecas["ECA1_user1"] = object()

    removed = manager.unregister_eca("ECA1", "user1")
    assert removed is True
    assert "ECA1_user1" not in manager.active_ecas


@pytest.mark.asyncio
async def test_update_eca_state_changes_state():
    """update_eca_state debe cambiar el estado de una ECA ya registrada."""
    manager = ECATaskManager()
    cfg = make_simple_eca_config(state="off")
    await manager.register_eca(cfg)

    await manager.update_eca_state("ECA1", "on", "user1")

    info = manager.get_active_ecas()
    key = list(info.keys())[0]
    assert info[key]["eca_state"] == "on"


def test_get_active_ecas_structure():
    """get_active_ecas debe devolver un dict con información básica de cada ECA."""
    manager = ECATaskManager()

    class FakeEvaluator:
        def __init__(self):
            self.name = "ECA_FAKE"
            self.state = "on"
            self.user_eca = "user1"
            self.event_resource_id = "temp"
            self.action_resource_id = "led1"
            self.threshold_value = 30
            self.comparator = "mayor"

    manager.active_ecas["ECA_FAKE_user1"] = FakeEvaluator()

    active = manager.get_active_ecas()
    assert "ECA_FAKE_user1" in active
    data = active["ECA_FAKE_user1"]
    for key in (
        "eca_name",
        "eca_state",
        "user_eca",
        "event_resource",
        "action_resource",
        "threshold",
        "comparator",
    ):
        assert key in data
