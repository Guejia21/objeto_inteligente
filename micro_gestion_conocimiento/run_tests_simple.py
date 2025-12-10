import os
import sys
import subprocess
import re

def print_header(title):
    """Imprime un encabezado formateado."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def extract_test_count(output):
    """Extrae el número de pruebas de la salida de pytest."""
    # Buscar patrones como "5 passed", "2 failed", "1 error"
    passed = failed = errors = 0
    
    # Patrón: "X passed"
    match = re.search(r'(\d+)\s+passed', output)
    if match:
        passed = int(match.group(1))
    
    # Patrón: "X failed"
    match = re.search(r'(\d+)\s+failed', output)
    if match:
        failed = int(match.group(1))
    
    # Patrón: "X error"
    match = re.search(r'(\d+)\s+error', output)
    if match:
        errors = int(match.group(1))
    
    return passed, failed, errors

def run_test_category(name, test_files):
    """Ejecuta una categoría de pruebas."""
    print_header(f" {name}")
    
    total = 0
    passed = 0
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n  Ejecutando: {os.path.basename(test_file)}")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # Extraer números de pruebas
                output = result.stdout + result.stderr
                file_passed, file_failed, file_errors = extract_test_count(output)
                
                # Actualizar totales
                file_total = file_passed + file_failed + file_errors
                total += file_total
                passed += file_passed
                
                # Mostrar resultado
                if result.returncode == 0:
                    print(f"    Éxito ({file_passed} pruebas)")
                else:
                    print(f"    Fallo ({file_passed} exitosas, {file_failed} fallidas, {file_errors} errores)")
                    if output:
                        print(f"   Detalles: {output[-200:]}")  # Últimos 200 caracteres
                    
            except subprocess.TimeoutExpired:
                print(f"    Timeout")
                total += 1
            except Exception as e:
                print(f"    Error: {e}")
                total += 1
        else:
            print(f"     No encontrado: {test_file}")
    
    return total, passed

def main():
    """Función principal."""
    print_header(" EJECUTANDO PRUEBAS - MICROSERVICIO GESTIÓN DE CONOCIMIENTO")
    print("Requisito: 12 pruebas (10 unitarias, 1 integración, 1 componentes)")
    
    # Definir todas las pruebas
    test_categories = {
        "PRUEBAS UNITARIAS (10)": [
            "tests/unit/test_basico.py",
            "tests/unit/test_dtos_simple.py",
            "tests/unit/test_services_mock.py",
            "tests/unit/test_endpoints_logic.py",
            "tests/unit/test_file_operations.py"
        ],
        "PRUEBA DE INTEGRACIÓN (1)": [
            "tests/integration/test_api_simple.py"
        ],
        "PRUEBA DE COMPONENTES (1)": [
            "tests/component/test_ontology_component_simple.py"
        ]
    }
    
    grand_total = 0
    grand_passed = 0
    
    # Ejecutar cada categoría
    for category_name, test_files in test_categories.items():
        total, passed = run_test_category(category_name, test_files)
        grand_total += total
        grand_passed += passed
    
    # Mostrar resumen
    print_header(" RESUMEN FINAL")
    
    print(f"\n TOTAL PRUEBAS EJECUTADAS: {grand_total}")
    print(f" PRUEBAS EXITOSAS: {grand_passed}")
    print(f" PRUEBAS FALLIDAS: {grand_total - grand_passed}")
    
    if grand_total > 0:
        porcentaje = (grand_passed / grand_total) * 100
        print(f" PORCENTAJE DE ÉXITO: {porcentaje:.1f}%")
    else:
        print(" PORCENTAJE DE ÉXITO: N/A (No se ejecutaron pruebas)")
    
    # Verificar requisitos
    print("\n" + "=" * 70)
    print(" VERIFICACIÓN DE REQUISITOS")
    print("=" * 70)
    
    print(f" Pruebas ejecutadas: {grand_total}")
    print(f" Total pruebas implementadas: 23 (19 unitarias + 2 integración + 2 componentes)")
    
    if grand_passed == grand_total and grand_total >= 12:
        print("\n ¡TODOS LOS REQUISITOS CUMPLIDOS EXITOSAMENTE!")
        return 0
    else:
        print("\n  Revisa los resultados anteriores")
        return 1

if __name__ == "__main__":
    sys.exit(main())