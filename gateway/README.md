# Nota
Este proyecto de API Gateway se basa en: https://github.com/pichasi/gateway-fastapi
# Uso
Para iniciar la gateway se debe crear un entorno virtual e instalar las dependencias (todo debe hacerse desde la raiz del proyecto: ../gateway/)
- python3 -m venv .venv
- source .venv/bin/activate
- pip install -r requirements.txt
Posteriormente se inicia el proyecto
- uvicorn app.main:app --port 8000
