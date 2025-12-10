#!/bin/bash
# filepath: run.sh

set -e  # Salir si hay error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SESSION_NAME="oi_proyecto"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════╗"
echo "║   🚀 Despliegue Objeto Inteligente - Proyecto I   ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ========================================
# 1. Verificar tmux instalado
# ========================================
if ! command -v tmux &> /dev/null; then
    echo -e "${RED}❌ Error: tmux no está instalado${NC}"
    echo -e "${YELLOW}Instalar con: sudo apt install tmux${NC}"
    exit 1
fi

echo -e "${GREEN}✅ tmux instalado (versión $(tmux -V))${NC}"

# ========================================
# 2. Verificar Mosquitto
# ========================================
echo -e "${YELLOW}🔍 Verificando Mosquitto...${NC}"
if ! pgrep -x "mosquitto" > /dev/null; then
    echo -e "${YELLOW}⚠️  Mosquitto no está corriendo. Iniciando...${NC}"
    mosquitto -d  # -d para daemon mode
    sleep 2
    if pgrep -x "mosquitto" > /dev/null; then
        echo -e "${GREEN}✅ Mosquitto iniciado${NC}"
    else
        echo -e "${RED}❌ Error: No se pudo iniciar Mosquitto${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Mosquitto activo${NC}"
fi

# ========================================
# 3. Limpiar sesión anterior si existe
# ========================================
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Sesión '$SESSION_NAME' ya existe. Eliminando...${NC}"
    tmux kill-session -t $SESSION_NAME
    sleep 1
fi

# ========================================
# 4. Opción: Limpiar estado previo
# ========================================
echo ""
read -p "¿Limpiar estado previo del proyecto? (s/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${YELLOW}🧹 Ejecutando clean.py...${NC}"
    if [ -f "clean.py" ]; then
        python3 clean.py
        echo -e "${GREEN}✅ Limpieza completada${NC}"
    else
        echo -e "${RED}❌ Error: clean.py no encontrado${NC}"
    fi
fi

# ========================================
# 5. Información sobre ejecutables
# ========================================
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║            📝 NOTA SOBRE EJECUTABLES               ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
echo -e "${YELLOW}Los ejecutables son específicos para cada objeto y deben${NC}"
echo -e "${YELLOW}cargarse DESPUÉS de crear el objeto con StartObject.${NC}"
echo ""
echo -e "${YELLOW}Proceso recomendado:${NC}"
echo -e "  ${CYAN}1.${NC} Iniciar microservicios (este script)"
echo -e "  ${CYAN}2.${NC} Enviar petición StartObject"
echo -e "  ${CYAN}3.${NC} Copiar ejecutables específicos del objeto:"
echo -e "     ${YELLOW}cp -r Ejemplo/executables/* microservicio_data_stream/storage/executables/${NC}"
echo -e "  ${CYAN}4.${NC} Reiniciar microservicio de datastreams:"
echo -e "     ${YELLOW}Ctrl+B → 3 → Ctrl+C → python3 main.py${NC}"
echo ""
read -p "Presiona Enter para continuar con el inicio de servicios..."
echo ""

# ========================================
# 6. Crear sesión tmux e iniciar servicios
# ========================================
echo -e "${BLUE}🖥️  Iniciando microservicios en tmux...${NC}"

# Crear sesión con primera ventana (Gateway)
tmux new-session -d -s $SESSION_NAME -n gateway
tmux send-keys -t $SESSION_NAME:0 "cd $PROJECT_ROOT/gateway/app" C-m
tmux send-keys -t $SESSION_NAME:0 "source ../.venv/bin/activate" C-m
tmux send-keys -t $SESSION_NAME:0 "clear" C-m
tmux send-keys -t $SESSION_NAME:0 "cat << 'EOF'" C-m
tmux send-keys -t $SESSION_NAME:0 "╔════════════════════════════════════╗" C-m
tmux send-keys -t $SESSION_NAME:0 "║   🌐 Gateway - Puerto 8000         ║" C-m
tmux send-keys -t $SESSION_NAME:0 "╚════════════════════════════════════╝" C-m
tmux send-keys -t $SESSION_NAME:0 "EOF" C-m
tmux send-keys -t $SESSION_NAME:0 "python3 main.py" C-m

# Ventana 1: Ontología
tmux new-window -t $SESSION_NAME:1 -n ontologia
tmux send-keys -t $SESSION_NAME:1 "cd $PROJECT_ROOT/micro_gestion_conocimiento/app" C-m
tmux send-keys -t $SESSION_NAME:1 "source ../.venv/bin/activate" C-m
tmux send-keys -t $SESSION_NAME:1 "clear" C-m
tmux send-keys -t $SESSION_NAME:1 "cat << 'EOF'" C-m
tmux send-keys -t $SESSION_NAME:1 "╔════════════════════════════════════╗" C-m
tmux send-keys -t $SESSION_NAME:1 "║ 🧠 Gestión Conocimiento - 8001     ║" C-m
tmux send-keys -t $SESSION_NAME:1 "╚════════════════════════════════════╝" C-m
tmux send-keys -t $SESSION_NAME:1 "EOF" C-m
tmux send-keys -t $SESSION_NAME:1 "python3 main.py" C-m

# Ventana 2: Objetos
tmux new-window -t $SESSION_NAME:2 -n objetos
tmux send-keys -t $SESSION_NAME:2 "cd $PROJECT_ROOT/micro_gestion_objetos/app" C-m
tmux send-keys -t $SESSION_NAME:2 "source ../.venv/bin/activate" C-m
tmux send-keys -t $SESSION_NAME:2 "clear" C-m
tmux send-keys -t $SESSION_NAME:2 "cat << 'EOF'" C-m
tmux send-keys -t $SESSION_NAME:2 "╔════════════════════════════════════╗" C-m
tmux send-keys -t $SESSION_NAME:2 "║   📦 Gestión Objetos - 8002        ║" C-m
tmux send-keys -t $SESSION_NAME:2 "╚════════════════════════════════════╝" C-m
tmux send-keys -t $SESSION_NAME:2 "EOF" C-m
tmux send-keys -t $SESSION_NAME:2 "python3 main.py" C-m

# Ventana 3: DataStreams
tmux new-window -t $SESSION_NAME:3 -n datastreams
tmux send-keys -t $SESSION_NAME:3 "cd $PROJECT_ROOT/microservicio_data_stream" C-m
tmux send-keys -t $SESSION_NAME:3 "source .venv/bin/activate" C-m
tmux send-keys -t $SESSION_NAME:3 "clear" C-m
tmux send-keys -t $SESSION_NAME:3 "cat << 'EOF'" C-m
tmux send-keys -t $SESSION_NAME:3 "╔════════════════════════════════════╗" C-m
tmux send-keys -t $SESSION_NAME:3 "║   📊 DataStreams - Puerto 8003     ║" C-m
tmux send-keys -t $SESSION_NAME:3 "║                                    ║" C-m
tmux send-keys -t $SESSION_NAME:3 "║ ⚠️  Cargar ejecutables después de  ║" C-m
tmux send-keys -t $SESSION_NAME:3 "║    crear objeto con StartObject    ║" C-m
tmux send-keys -t $SESSION_NAME:3 "╚════════════════════════════════════╝" C-m
tmux send-keys -t $SESSION_NAME:3 "EOF" C-m
tmux send-keys -t $SESSION_NAME:3 "python3 main.py" C-m

# Ventana 4: ECAs
tmux new-window -t $SESSION_NAME:4 -n ecas
tmux send-keys -t $SESSION_NAME:4 "cd $PROJECT_ROOT/micro_automatizacion_ecas/app" C-m
tmux send-keys -t $SESSION_NAME:4 "source ../.venv/bin/activate" C-m
tmux send-keys -t $SESSION_NAME:4 "clear" C-m
tmux send-keys -t $SESSION_NAME:4 "cat << 'EOF'" C-m
tmux send-keys -t $SESSION_NAME:4 "╔════════════════════════════════════╗" C-m
tmux send-keys -t $SESSION_NAME:4 "║  ⚡ Automatización ECAs - 8004     ║" C-m
tmux send-keys -t $SESSION_NAME:4 "╚════════════════════════════════════╝" C-m
tmux send-keys -t $SESSION_NAME:4 "EOF" C-m
tmux send-keys -t $SESSION_NAME:4 "python3 main.py" C-m

# Ventana 5: Personalización
tmux new-window -t $SESSION_NAME:5 -n personalizacion
tmux send-keys -t $SESSION_NAME:5 "cd $PROJECT_ROOT/microservicio_personalizacion/app" C-m
tmux send-keys -t $SESSION_NAME:5 "source ../.venv/bin/activate" C-m
tmux send-keys -t $SESSION_NAME:5 "clear" C-m
tmux send-keys -t $SESSION_NAME:5 "cat << 'EOF'" C-m
tmux send-keys -t $SESSION_NAME:5 "╔════════════════════════════════════╗" C-m
tmux send-keys -t $SESSION_NAME:5 "║   🎨 Personalización - 8005        ║" C-m
tmux send-keys -t $SESSION_NAME:5 "╚════════════════════════════════════╝" C-m
tmux send-keys -t $SESSION_NAME:5 "EOF" C-m
tmux send-keys -t $SESSION_NAME:5 "python3 main.py" C-m

# Ventana 6: Monitor y Comandos Útiles
tmux new-window -t $SESSION_NAME:6 -n monitor
tmux send-keys -t $SESSION_NAME:6 "cd $PROJECT_ROOT" C-m
tmux send-keys -t $SESSION_NAME:6 "clear" C-m
tmux send-keys -t $SESSION_NAME:6 "cat << 'EOF'" C-m
tmux send-keys -t $SESSION_NAME:6 "╔════════════════════════════════════════════════════╗" C-m
tmux send-keys -t $SESSION_NAME:6 "║            📡 Monitor del Sistema                  ║" C-m
tmux send-keys -t $SESSION_NAME:6 "╚════════════════════════════════════════════════════╝" C-m
tmux send-keys -t $SESSION_NAME:6 "" C-m
tmux send-keys -t $SESSION_NAME:6 "📋 Comandos útiles:" C-m
tmux send-keys -t $SESSION_NAME:6 "" C-m
tmux send-keys -t $SESSION_NAME:6 "  🔍 Monitoreo:" C-m
tmux send-keys -t $SESSION_NAME:6 "    htop                           # Monitor de recursos" C-m
tmux send-keys -t $SESSION_NAME:6 "    mosquitto_sub -t \"#\" -v        # Ver todos los mensajes MQTT" C-m
tmux send-keys -t $SESSION_NAME:6 "" C-m
tmux send-keys -t $SESSION_NAME:6 "  📦 Gestión de Objetos:" C-m
tmux send-keys -t $SESSION_NAME:6 "    curl -X POST http://localhost:8002/startObject \\" C-m
tmux send-keys -t $SESSION_NAME:6 "      -H \"Content-Type: application/json\" \\" C-m
tmux send-keys -t $SESSION_NAME:6 "      -d @Ejemplo/EjemploReguladorTemp.json" C-m
tmux send-keys -t $SESSION_NAME:6 "" C-m
tmux send-keys -t $SESSION_NAME:6 "    curl http://localhost:8002/getObjectInfo" C-m
tmux send-keys -t $SESSION_NAME:6 "" C-m
tmux send-keys -t $SESSION_NAME:6 "  📂 Cargar Ejecutables (DESPUÉS de StartObject):" C-m
tmux send-keys -t $SESSION_NAME:6 "    cp -r Ejemplo/executables/* \\" C-m
tmux send-keys -t $SESSION_NAME:6 "      microservicio_data_stream/storage/executables/" C-m
tmux send-keys -t $SESSION_NAME:6 "    # Luego: Ctrl+B → 3 → Ctrl+C → python3 main.py" C-m
tmux send-keys -t $SESSION_NAME:6 "" C-m
tmux send-keys -t $SESSION_NAME:6 "  ⚡ ECAs:" C-m
tmux send-keys -t $SESSION_NAME:6 "    curl http://localhost:8004/ListarECAs" C-m
tmux send-keys -t $SESSION_NAME:6 "    curl -X POST http://localhost:8004/CrearECA \\" C-m
tmux send-keys -t $SESSION_NAME:6 "      -H \"Content-Type: application/json\" \\" C-m
tmux send-keys -t $SESSION_NAME:6 "      -d @test_eca.json" C-m
tmux send-keys -t $SESSION_NAME:6 "" C-m
tmux send-keys -t $SESSION_NAME:6 "  🛑 Detener todo:" C-m
tmux send-keys -t $SESSION_NAME:6 "    ./stop.sh" C-m
tmux send-keys -t $SESSION_NAME:6 "    tmux kill-session -t oi_proyecto" C-m
tmux send-keys -t $SESSION_NAME:6 "EOF" C-m

# Volver a la ventana 0 (gateway)
tmux select-window -t $SESSION_NAME:0

# ========================================
# 7. Esperar a que servicios inicien
# ========================================
echo -e "${YELLOW}⏳ Esperando 5 segundos para que los servicios inicien...${NC}"
sleep 5

# ========================================
# 8. Verificar que los servicios estén escuchando
# ========================================
echo ""
echo -e "${BLUE}🔍 Verificando servicios...${NC}"

services=(
    "8000:Gateway"
    "8001:Ontología"
    "8002:Objetos"
    "8003:DataStreams"
    "8004:ECAs"
    "8005:Personalización"
)

all_ok=true

# Verificar si nc (netcat) está disponible
if command -v nc &> /dev/null; then
    for service in "${services[@]}"; do
        port="${service%%:*}"
        name="${service##*:}"
        
        if nc -z localhost $port 2>/dev/null; then
            echo -e "${GREEN}  ✅ $name (puerto $port)${NC}"
        else
            echo -e "${YELLOW}  ⏳ $name (puerto $port) - Iniciando...${NC}"
            all_ok=false
        fi
    done
else
    # Si nc no está disponible, usar método alternativo con timeout
    echo -e "${YELLOW}⚠️  netcat no instalado, usando método alternativo...${NC}"
    for service in "${services[@]}"; do
        port="${service%%:*}"
        name="${service##*:}"
        
        if timeout 1 bash -c "echo >/dev/tcp/localhost/$port" 2>/dev/null; then
            echo -e "${GREEN}  ✅ $name (puerto $port)${NC}"
        else
            echo -e "${YELLOW}  ⏳ $name (puerto $port) - Iniciando...${NC}"
            all_ok=false
        fi
    done
fi

# ========================================
# 9. Mostrar información de uso
# ========================================
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        ✅ Microservicios iniciados en tmux         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📋 Para acceder a la sesión tmux:${NC}"
echo -e "   ${YELLOW}tmux attach -t $SESSION_NAME${NC}"
echo ""
echo -e "${BLUE}📋 Navegación en tmux:${NC}"
echo -e "   ${YELLOW}Ctrl+B → 0${NC}    Gateway"
echo -e "   ${YELLOW}Ctrl+B → 1${NC}    Ontología"
echo -e "   ${YELLOW}Ctrl+B → 2${NC}    Objetos"
echo -e "   ${YELLOW}Ctrl+B → 3${NC}    DataStreams"
echo -e "   ${YELLOW}Ctrl+B → 4${NC}    ECAs"
echo -e "   ${YELLOW}Ctrl+B → 5${NC}    Personalización"
echo -e "   ${YELLOW}Ctrl+B → 6${NC}    Monitor (comandos útiles)"
echo ""
echo -e "   ${YELLOW}Ctrl+B → n${NC}    Siguiente ventana"
echo -e "   ${YELLOW}Ctrl+B → p${NC}    Ventana anterior"
echo -e "   ${YELLOW}Ctrl+B → w${NC}    Listar todas las ventanas"
echo -e "   ${YELLOW}Ctrl+B → d${NC}    Salir de tmux (servicios siguen corriendo)"
echo -e "   ${YELLOW}Ctrl+B → [${NC}    Modo scroll (ver logs antiguos)"
echo ""
echo -e "${BLUE}📋 Para detener todo:${NC}"
echo -e "   ${YELLOW}./stop.sh${NC}"
echo ""
echo -e "${BLUE}🔗 URLs disponibles:${NC}"
echo -e "   Gateway:         ${YELLOW}http://localhost:8000${NC}"
echo -e "   Ontología:       ${YELLOW}http://localhost:8001${NC}"
echo -e "   Objetos:         ${YELLOW}http://localhost:8002${NC}"
echo -e "   DataStreams:     ${YELLOW}http://localhost:8003${NC}"
echo -e "   ECAs:            ${YELLOW}http://localhost:8004${NC}"
echo -e "   Personalización: ${YELLOW}http://localhost:8005${NC}"
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║          📝 PRÓXIMOS PASOS RECOMENDADOS            ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
echo -e "${YELLOW}1.${NC} Enviar petición StartObject para crear un objeto"
echo -e "${YELLOW}2.${NC} Copiar ejecutables específicos del objeto:"
echo -e "   ${CYAN}cp -r Ejemplo/executables/* microservicio_data_stream/storage/executables/${NC}"
echo -e "${YELLOW}3.${NC} Reiniciar microservicio de datastreams:"
echo -e "   ${CYAN}tmux attach -t $SESSION_NAME${NC}"
echo -e "   ${CYAN}Ctrl+B → 3 (ir a ventana datastreams)${NC}"
echo -e "   ${CYAN}Ctrl+C (detener servicio)${NC}"
echo -e "   ${CYAN}python3 main.py (reiniciar)${NC}"
echo ""

if [ "$all_ok" = false ]; then
    echo -e "${YELLOW}⚠️  Algunos servicios aún están iniciando.${NC}"
    echo -e "${YELLOW}   Accede con: ${CYAN}tmux attach -t $SESSION_NAME${YELLOW} para ver el progreso.${NC}"
fi

echo -e "${GREEN}🎉 Despliegue completado! Los servicios están iniciando en tmux.${NC}"
echo ""