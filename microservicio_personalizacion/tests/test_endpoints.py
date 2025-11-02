#!/usr/bin/env python3
"""
Script para probar todos los endpoints del microservicio
"""
import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_health():
    """Probar endpoint de health check"""
    print("🧪 Probando /health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_root():
    """Probar endpoint raíz"""
    print("\n🧪 Probando /...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_crear_preferencia():
    """Probar creación de preferencia"""
    print("\n Probando /CrearPreferencia...")
    
    # Contrato ECA de ejemplo (similar al formato legacy)
    contrato_ejemplo = {
        "evento": {
            "recurso": "temperatura",
            "operador": "mayor",
            "valor": 25,
            "nombre_recurso": "Sensor de Temperatura",
            "nombre_objeto": "Termostato Sala",
            "descripcion": "Temperatura mayor a 25 grados",
            "unidad": "grados"
        },
        "accion": {
            "recurso": "ventilador", 
            "valor": 1,
            "nombre_recurso": "Ventilador",
            "nombre_objeto": "Ventilador Sala",
            "descripcion": "Encender ventilador",
            "unidad": "bool",
            "operador": "igual"
        }
    }
    
    try:
        params = {
            "email": "usuario@ejemplo.com",
            "osid": "obj_sala_001",
            "osidDestino": "obj_sala_002", 
            "contrato": json.dumps(contrato_ejemplo)
        }
        
        response = requests.get(f"{BASE_URL}/CrearPreferencia", params=params)
        print(f" Status: {response.status_code}")
        print(f" Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f" Error: {e}")
        return False

def test_listar_ecas():
    """Probar listado de ECAs"""
    print("\n Probando /EcaList...")
    try:
        params = {
            "osid": "obj_sala_001"
        }
        
        response = requests.get(f"{BASE_URL}/EcaList", params=params)
        print(f" Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f" ECAs encontrados: {len(data)}")
            for eca in data:
                print(f"   - {eca.get('name_eca', 'N/A')}")
        else:
            print(f" Response: {response.text}")
            
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_set_eca_state():
    """Probar cambio de estado de ECA"""
    print("\n Probando /SetEcaState...")
    try:
        params = {
            "osid": "obj_sala_001",
            "nombreECA": "eca_usuario@ejemplo.com_obj_sala_001_1", 
            "comando": "off"
        }
        
        response = requests.get(f"{BASE_URL}/SetEcaState", params=params)
        print(f" Status: {response.status_code}")
        print(f" Response: {response.text}")
        return response.status_code in [200, 404]  # 404 si el ECA no existe
    except Exception as e:
        print(f" Error: {e}")
        return False

def test_apagar_todos_ecas():
    """Probar apagar todos los ECAs"""
    print("\nProbando /ApagarTodosEcas...")
    try:
        params = {
            "osid": "obj_sala_001"
        }
        
        response = requests.get(f"{BASE_URL}/ApagarTodosEcas", params=params)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f" Error: {e}")
        return False

def test_notificar_salida():
    """Probar notificación de salida de usuario"""
    print("\n Probando /NotificarSalidaDeUsuario...")
    try:
        params = {
            "osid": "usuario@ejemplo.com"
        }
        
        response = requests.get(f"{BASE_URL}/NotificarSalidaDeUsuario", params=params)
        print(f" Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_registro_interaccion():
    """Probar registro de interacción"""
    print("\n Probando /RegistroInteraccionUsuarioObjeto...")
    try:
        params = {
            "email": "usuario@ejemplo.com",
            "idDataStream": "luz_sala",
            "comando": "encender",
            "osid": "obj_sala_001",
            "mac": "AA:BB:CC:DD:EE:FF",
            "dateInteraction": "2024-01-15 10:30:00"
        }
        
        response = requests.get(f"{BASE_URL}/RegistroInteraccionUsuarioObjeto", params=params)
        print(f" Status: {response.status_code}")
        print(f" Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print(" INICIANDO PRUEBAS DEL MICROSERVICIO DE PERSONALIZACIÓN")
    print("=" * 60)
    
    # Esperar un poco para que el servidor esté listo
    print("⏳ Esperando que el servidor esté listo...")
    time.sleep(2)
    
    tests = [
        test_health,
        test_root,
        test_crear_preferencia,
        test_listar_ecas,
        test_set_eca_state,
        test_apagar_todos_ecas,
        test_notificar_salida,
        test_registro_interaccion
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"Error ejecutando test: {e}")
            results.append(False)
        
        time.sleep(1)  # Pequeña pausa entre tests
    
    print("\n" + "=" * 60)
    print(" RESUMEN DE PRUEBAS:")
    passed = sum(results)
    total = len(results)
    print(f" Pruebas pasadas: {passed}/{total}")
    print(f" Pruebas falladas: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron!")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los logs.")
    
    print(f"\n Documentación disponible en: {BASE_URL}/docs")

if __name__ == "__main__":
    main()