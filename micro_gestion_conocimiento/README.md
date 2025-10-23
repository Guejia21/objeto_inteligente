## Ejecución del microservicio
Para ejecutar este micro, primero debe instalarse un entorno de python, haciendo (*Todo debe hacerse dentro de la carpeta de micro_gestion_conocimiento*)
- python3 -m .venv
Posteriormente se deben descargar las librerias usadas:
- source .venv/bin/activate
- pip install -r requeriments.txt
Finalmente se inicializa el proyecto:
- uvicorn app.main:app --reload
