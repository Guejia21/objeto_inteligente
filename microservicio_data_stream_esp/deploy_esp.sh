#!/bin/bash
# deploy_full.sh - Despliega todo el microservicio al ESP32

PUERTO="/dev/ttyUSB0"

echo "=========================================="
echo "     Despliegue Completo ESP32"
echo "=========================================="

# 1. Permisos
echo "1. Configurando permisos y activando entorno..."
sudo chmod 666 $PUERTO
source .venv/bin/activate

# 2. Limpiando archivos anteriores...
echo "2. Limpiando archivos anteriores..."
ampy --port $PUERTO rm boot.py 2>/dev/null || true
ampy --port $PUERTO rm main.py 2>/dev/null || true
ampy --port $PUERTO rm config.py 2>/dev/null || true

# 3. Subiendo archivos principales...
echo "3. Subiendo archivos principales..."
ampy --port $PUERTO put boot.py
ampy --port $PUERTO put main.py
ampy --port $PUERTO put config.py

# 4. Subiendo módulos...
echo "4. Subiendo módulos..."
for dir in broker hardware lib routes services storage utils; do
    echo "   📁 $dir/"
    ampy --port $PUERTO put $dir
done

# 5. Verificar
echo "5. Verificando archivos..."
ampy --port $PUERTO ls

echo ""
echo "=========================================="
echo " Despliegue completado!"
echo "=========================================="
echo ""
echo "Para ver logs:"
echo "  picocom $PUERTO -b 115200"
echo ""
echo "Para resetear:"
echo "  ampy --port $PUERTO reset"
echo ""