#!/bin/bash

# Script para configurar entornos virtuales en todos los microservicios
# Crea .venv si no existe, activa el entorno e instala dependencias

echo "🚀 Configurando entornos virtuales para todos los microservicios"
echo "================================================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directorio raíz del proyecto
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lista de microservicios (carpetas que contienen requirements.txt)
MICROSERVICIOS=(
    "gateway"
    "micro_automatizacion_ecas"
    "micro_gestion_conocimiento"
    "micro_gestion_objetos"
    "microservicio_data_stream"
    "microservicio_personalizacion"
)

# Contador de éxitos y fallos
SUCCESS_COUNT=0
FAIL_COUNT=0

# Función para configurar un microservicio
setup_microservice() {
    local micro_path=$1
    local micro_name=$(basename "$micro_path")
    
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📦 Procesando: ${micro_name}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Verificar que la carpeta existe
    if [ ! -d "$micro_path" ]; then
        echo -e "${YELLOW}⚠️  Directorio no encontrado: ${micro_path}${NC}"
        return 1
    fi
    
    # Entrar al directorio del microservicio
    cd "$micro_path" || return 1
    
    # Verificar que existe requirements.txt
    if [ ! -f "requirements.txt" ]; then
        echo -e "${YELLOW}⚠️  No se encontró requirements.txt en ${micro_name}${NC}"
        cd "$PROJECT_ROOT"
        return 1
    fi
    
    # 1. Verificar/Crear entorno virtual
    if [ -d ".venv" ]; then
        echo -e "${GREEN}✓${NC} Entorno virtual ya existe"
    else
        echo -e "${YELLOW}📁 Creando entorno virtual...${NC}"
        python3 -m venv .venv
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC} Entorno virtual creado"
        else
            echo -e "${RED}✗${NC} Error creando entorno virtual"
            cd "$PROJECT_ROOT"
            return 1
        fi
    fi
    
    # 2. Activar entorno virtual
    echo -e "${YELLOW}🔄 Activando entorno virtual...${NC}"
    source .venv/bin/activate
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗${NC} Error activando entorno virtual"
        cd "$PROJECT_ROOT"
        return 1
    fi
    echo -e "${GREEN}✓${NC} Entorno virtual activado"
    
    # 3. Actualizar pip
    echo -e "${YELLOW}📦 Actualizando pip...${NC}"
    pip install --upgrade pip --quiet
    
    # 4. Instalar dependencias
    echo -e "${YELLOW}📥 Instalando dependencias desde requirements.txt...${NC}"
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Dependencias instaladas correctamente"
    else
        echo -e "${RED}✗${NC} Error instalando dependencias"
        deactivate
        cd "$PROJECT_ROOT"
        return 1
    fi
    
    # 5. Mostrar paquetes instalados (resumen)
    PACKAGE_COUNT=$(pip list --format=freeze | wc -l)
    echo -e "${GREEN}✓${NC} ${PACKAGE_COUNT} paquetes instalados en ${micro_name}"
    
    # 6. Desactivar entorno virtual
    deactivate
    echo -e "${GREEN}✓${NC} Entorno virtual desactivado"
    
    # Volver al directorio raíz
    cd "$PROJECT_ROOT"
    
    return 0
}

# Función para mostrar resumen
show_summary() {
    echo ""
    echo "================================================================"
    echo -e "${BLUE}📊 RESUMEN DE CONFIGURACIÓN${NC}"
    echo "================================================================"
    echo -e "${GREEN}✅ Exitosos: ${SUCCESS_COUNT}${NC}"
    echo -e "${RED}❌ Fallidos: ${FAIL_COUNT}${NC}"
    echo ""
    
    if [ $FAIL_COUNT -eq 0 ]; then
        echo -e "${GREEN}🎉 ¡Todos los microservicios configurados correctamente!${NC}"
    else
        echo -e "${YELLOW}⚠️  Algunos microservicios no se configuraron correctamente${NC}"
    fi
    
    echo ""
    echo "Para activar un entorno específico:"
    echo "  cd <microservicio> && source .venv/bin/activate"
    echo ""
}

# Verificar que Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no está instalado${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 3 encontrado: $(python3 --version)"

# Verificar que venv está disponible
python3 -c "import venv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ El módulo venv no está disponible${NC}"
    echo "Instálalo con: sudo apt install python3-venv"
    exit 1
fi

# Procesar cada microservicio
for micro in "${MICROSERVICIOS[@]}"; do
    micro_path="${PROJECT_ROOT}/${micro}"
    
    if setup_microservice "$micro_path"; then
        ((SUCCESS_COUNT++))
    else
        ((FAIL_COUNT++))
    fi
done

# Mostrar resumen
show_summary

exit $FAIL_COUNT