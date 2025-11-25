#!/usr/bin/env python3
"""
Script para limpiar archivos de persistencia del proyecto Objeto Inteligente.
Elimina archivos generados durante la ejecución.
"""

import os
import shutil
import json
from pathlib import Path
from typing import List, Tuple

# Colores ANSI para terminal
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_header(message: str):
    """Imprime un encabezado con formato"""
    print(f"\n{Colors.BLUE}{message}{Colors.NC}")

def print_success(message: str):
    """Imprime un mensaje de éxito"""
    print(f"{Colors.GREEN}✓{Colors.NC} {message}")

def print_warning(message: str):
    """Imprime una advertencia"""
    print(f"{Colors.YELLOW}⚠{Colors.NC} {message}")

def print_error(message: str):
    """Imprime un error"""
    print(f"{Colors.RED}✗{Colors.NC} {message}")

def safe_delete_file(filepath: Path, description: str) -> bool:
    """Elimina un archivo de forma segura"""
    try:
        if filepath.exists():
            filepath.unlink()
            print_success(f"{description} eliminado: {filepath}")
            return True
        else:
            print_warning(f"No encontrado: {filepath}")
            return False
    except Exception as e:
        print_error(f"Error eliminando {filepath}: {e}")
        return False

def safe_delete_directory_contents(dirpath: Path, description: str) -> bool:
    """Elimina el contenido de un directorio pero mantiene el directorio"""
    try:
        if dirpath.exists() and dirpath.is_dir():
            for item in dirpath.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            print_success(f"{description} limpiado: {dirpath}")
            return True
        else:
            print_warning(f"Directorio no encontrado: {dirpath}")
            ensure_directory(dirpath)
            return False
    except Exception as e:
        print_error(f"Error limpiando {dirpath}: {e}")
        return False

def ensure_directory(dirpath: Path) -> bool:
    """Crea un directorio si no existe"""
    try:
        dirpath.mkdir(parents=True, exist_ok=True)
        print_success(f"Directorio creado/verificado: {dirpath}")
        return True
    except Exception as e:
        print_error(f"Error creando directorio {dirpath}: {e}")
        return False

def reset_metadata(filepath: Path, description: str) -> bool:
    """Resetea un archivo de metadata a un objeto JSON vacío"""
    try:
        # Asegurar que el directorio padre existe
        ensure_directory(filepath.parent)
        
        # Escribir metadata vacío
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)
        
        print_success(f"{description} reseteado: {filepath}")
        return True
    except Exception as e:
        print_error(f"Error reseteando {filepath}: {e}")
        return False

def clean_pattern_files(base_path: Path, pattern: str, description: str) -> int:
    """Elimina archivos que coinciden con un patrón"""
    count = 0
    try:
        for filepath in base_path.rglob(pattern):
            if filepath.is_file():
                filepath.unlink()
                count += 1
        if count > 0:
            print_success(f"{description} eliminados: {count} archivo(s)")
        return count
    except Exception as e:
        print_error(f"Error eliminando {pattern}: {e}")
        return count

def clean_pattern_directories(base_path: Path, pattern: str, description: str) -> int:
    """Elimina directorios que coinciden con un patrón"""
    count = 0
    try:
        for dirpath in base_path.rglob(pattern):
            if dirpath.is_dir():
                shutil.rmtree(dirpath)
                count += 1
        if count > 0:
            print_success(f"{description} eliminados: {count} directorio(s)")
        return count
    except Exception as e:
        print_error(f"Error eliminando directorios {pattern}: {e}")
        return count

def main():
    """Función principal de limpieza"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}🧹 Limpieza del Proyecto Objeto Inteligente{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    
    # Obtener directorio raíz del proyecto
    project_root = Path(__file__).parent
    
    # Estadísticas de limpieza
    stats = {
        'executables': 0,
        'metadata': 0,
        'ontologies': 0,
        'databases': 0,
        'cache': 0
    }
    
    # 1. Limpiar ejecutables del microservicio de data stream
    print_header("📂 Limpiando ejecutables de microservicio_data_stream...")
    executables_dir = project_root / "microservicio_data_stream" / "storage" / "executables"
    if safe_delete_directory_contents(executables_dir, "Ejecutables"):
        stats['executables'] += 1
    
    # 2. Limpiar metadata del microservicio de data stream
    print_header("📄 Limpiando metadata de microservicio_data_stream...")
    metadata_file = project_root / "microservicio_data_stream" / "storage" / "metadata" / "metadata.json"
    if reset_metadata(metadata_file, "Metadata de data stream"):
        stats['metadata'] += 1
    
    # 3. Limpiar metadata del microservicio de gestión de objetos
    print_header("📄 Limpiando metadata de micro_gestion_objetos...")
    objetos_metadata = project_root / "micro_gestion_objetos" / "app" / "infraestructure" / "metadata" / "metadata.json"
    if reset_metadata(objetos_metadata, "Metadata de gestión de objetos"):
        stats['metadata'] += 1
    
    # 4. Limpiar ontología instanciada
    print_header("🧠 Limpiando ontología instanciada de micro_gestion_conocimiento...")
    ontologia_file = project_root / "micro_gestion_conocimiento" / "app" / "infraestructure" / "OWL" / "ontologiaInstanciada.owl"
    if safe_delete_file(ontologia_file, "Ontología instanciada"):
        stats['ontologies'] += 1
        
    # 5. Limpiar archivos temporales y cache
    print_header("🗑️  Limpiando archivos temporales y cache...")
    
    # Cache de Python
    cache_count = clean_pattern_directories(project_root, "__pycache__", "Directorios __pycache__")
    cache_count += clean_pattern_files(project_root, "*.pyc", "Archivos .pyc")
    cache_count += clean_pattern_files(project_root, "*.pyo", "Archivos .pyo")
    
    # Archivos de log
    log_count = clean_pattern_files(project_root, "*.log", "Archivos de log")
    cache_count += log_count
    
    stats['cache'] = cache_count
    
    # 6. Resumen final
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.GREEN}✅ Limpieza completada exitosamente{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
    
    print("📋 Resumen de limpieza:")
    print(f"  • Directorios de ejecutables limpiados: {stats['executables']}")
    print(f"  • Archivos de metadata reseteados: {stats['metadata']}")
    print(f"  • Ontologías eliminadas: {stats['ontologies']}")    
    print(f"  • Archivos de cache/temporales eliminados: {stats['cache']}")
    
    print(f"\n💡 El proyecto está listo para una nueva ejecución limpia\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠ Limpieza interrumpida por el usuario{Colors.NC}\n")
    except Exception as e:
        print(f"\n{Colors.RED}✗ Error inesperado: {e}{Colors.NC}\n")