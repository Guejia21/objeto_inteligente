import pytest
from app.domain.eca_evaluator import ECAEvaluator


def make_base_config(**overrides):
    """Config base mínima para crear un ECAEvaluator."""
    cfg = {
        "name_eca": "ECA_TEMP",
        "state_eca": "on",
        "user_eca": "user1",

        "id_event_object": "OBJ1",
        "ip_event_object": "127.0.0.1",
        "id_event_resource": "temp",

        # Condición: temp > 30
        "comparator_condition": "mayor",
        "variable_condition": 30,
        "type_variable_condition": "int",

        # Acción: encender recurso "led1"
        "id_action_object": "OBJ1",
        "ip_action_object": "127.0.0.1",
        "id_action_resource": "led1",
        "variable_action": "on",
        "type_variable_action": "bool",
        "comparator_action": "igual",
    }
    cfg.update(overrides)
    return cfg


def test_evaluate_condition_state_off_returns_false():
    """Si la ECA está en 'off', nunca debe disparar la acción."""
    cfg = make_base_config(state_eca="off")
    evaluator = ECAEvaluator(cfg)

    assert evaluator.evaluate_condition(100) is False


def test_evaluate_condition_mayor_true():
    """Condición mayor: 40 > 30 debe cumplirse."""
    cfg = make_base_config(variable_condition=30, type_variable_condition="int")
    evaluator = ECAEvaluator(cfg)

    assert evaluator.evaluate_condition(40) is True


def test_evaluate_condition_mayor_false():
    """Condición mayor: 20 > 30 NO debe cumplirse."""
    cfg = make_base_config(variable_condition=30, type_variable_condition="int")
    evaluator = ECAEvaluator(cfg)

    assert evaluator.evaluate_condition(20) is False


def test_evaluate_condition_bool_true_with_string_one():
    """
    Condición booleana: threshold=True, valor '1' debe interpretarse como True.
    (ajusta si tu conversión booleana es distinta).
    """
    cfg = make_base_config(
        comparator_condition="igual",
        variable_condition=True,
        type_variable_condition="bool",
    )
    evaluator = ECAEvaluator(cfg)

    assert evaluator.evaluate_condition("1") is True


def test_process_telemetry_missing_resource_returns_false():
    """Si la telemetría no trae el recurso configurado, no se evalúa la condición."""
    cfg = make_base_config(id_event_resource="humedad")
    evaluator = ECAEvaluator(cfg)

    telemetry = {"temp": 50}
    assert evaluator.process_telemetry(telemetry) is False


def test_process_telemetry_with_matching_resource_true():
    """
    Si la telemetría tiene el recurso y el valor cumple la condición,
    process_telemetry debe devolver True.
    """
    cfg = make_base_config(
        id_event_resource="temp",
        comparator_condition="mayor",
        variable_condition=30,
        type_variable_condition="int",
    )
    evaluator = ECAEvaluator(cfg)

    telemetry = {"temp": 40}
    assert evaluator.process_telemetry(telemetry) is True
