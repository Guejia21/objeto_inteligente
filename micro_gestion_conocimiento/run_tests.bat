@echo off
chcp 65001 >nul
echo ==============================================================================
echo  EJECUTACIÓN DE PRUEBAS - MICROSERVICIO GESTIÓN DE CONOCIMIENTO
echo ==============================================================================
echo.
echo  Requisito: 12 pruebas (10 unitarias, 1 integración, 1 componentes)
echo.

cd /d "C:\Users\karen\OneDrive\Documentos\Proyecto I\objeto_inteligente\micro_gestion_conocimiento"

echo 1. Activando virtual environment...
call venv\Scripts\activate.bat

echo.
echo 2. Instalando dependencias de testing...
pip install -r requirements-test.txt

echo.
echo 3. Verificando instalación de pytest...
python -m pytest --version

echo.
echo 4. Ejecutando todas las pruebas...
echo.

python run_tests_simple.py

echo.
echo ==============================================================================
echo  PROCESO COMPLETADO
echo ==============================================================================
echo.
pause