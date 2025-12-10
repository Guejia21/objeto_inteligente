#!/bin/bash
# filepath: stop_local.sh

SESSION_NAME="oi_proyecto"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${RED}"
echo "╔════════════════════════════════════════════════════╗"
echo "║        🛑 Deteniendo Objeto Inteligente           ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ========================================
# 1. Detener sesión tmux
# ========================================
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo -e "${YELLOW}🔄 Deteniendo sesión tmux '$SESSION_NAME'...${NC}"
    tmux kill-session -t $SESSION_NAME
    echo -e "${GREEN}✅ Sesión tmux terminada${NC}"
else
    echo -e "${YELLOW}⚠️  No hay sesión tmux activa '$SESSION_NAME'${NC}"
fi

# ========================================
# 2. Limpiar procesos huérfanos de Python
# ========================================
echo -e "${YELLOW}🧹 Limpiando procesos huérfanos...${NC}"

# Buscar procesos main.py en los directorios del proyecto
pids=$(ps aux | grep -E "python3 main.py" | grep -v grep | awk '{print $2}')

if [ ! -z "$pids" ]; then
    echo -e "${YELLOW}   Encontrados procesos: $pids${NC}"
    echo "$pids" | xargs kill -9 2>/dev/null
    echo -e "${GREEN}✅ Procesos Python limpiados${NC}"
else
    echo -e "${GREEN}✅ No hay procesos huérfanos${NC}"
fi

# ========================================
# 3. Verificar puertos liberados
# ========================================
echo ""
echo -e "${BLUE}🔍 Verificando puertos...${NC}"

ports=(8000 8001 8002 8003 8004 8005)
all_free=true

for port in "${ports[@]}"; do
    if nc -z localhost $port 2>/dev/null; then
        echo -e "${RED}  ❌ Puerto $port aún ocupado${NC}"
        all_free=false
        
        # Intentar liberar el puerto
        pid=$(lsof -ti:$port 2>/dev/null)
        if [ ! -z "$pid" ]; then
            echo -e "${YELLOW}     Liberando puerto $port (PID: $pid)...${NC}"
            kill -9 $pid 2>/dev/null
        fi
    else
        echo -e "${GREEN}  ✅ Puerto $port liberado${NC}"
    fi
done

# ========================================
# 4. Opción de detener Mosquitto
# ========================================
echo ""
if pgrep -x "mosquitto" > /dev/null; then
    read -p "¿Detener también Mosquitto? (s/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo -e "${YELLOW}🔄 Deteniendo Mosquitto...${NC}"
        pkill -x mosquitto
        sleep 1
        if ! pgrep -x "mosquitto" > /dev/null; then
            echo -e "${GREEN}✅ Mosquitto detenido${NC}"
        else
            echo -e "${RED}❌ No se pudo detener Mosquitto${NC}"
        fi
    else
        echo -e "${BLUE}ℹ️  Mosquitto sigue ejecutándose${NC}"
    fi
fi

# ========================================
# 5. Resumen final
# ========================================
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✅ Detención completada               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$all_free" = true ]; then
    echo -e "${GREEN}🎉 Todos los servicios detenidos correctamente${NC}"
else
    echo -e "${YELLOW}⚠️  Algunos puertos no pudieron liberarse${NC}"
    echo -e "${YELLOW}   Puedes verificar con: lsof -i :8000-8005${NC}"
fi

echo ""
echo -e "${BLUE}📋 Para volver a iniciar:${NC}"
echo -e "   ${YELLOW}./deploy_local.sh${NC}"
echo ""