# Proyecto: Objeto Inteligente
## Contexto
Este proyecto tiene sus raíces en el trabajo de grado Modelo Ontológico para Manejo de Perfiles de Usuario en la IoT (Pabón y Rojas, 2017), el cual exploró la creación de un modelo semántico de perfil de usuario soportado en ontologías, con el fin de personalizar servicios en un entorno domótico. Dicho trabajo validó la eficacia del enfoque mediante una prueba de concepto y un estudio de caso, demostrando que el uso de perfiles semánticos mejora la interacción con objetos inteligentes. Se plantea la migración hacia una arquitectura basada en **microservicios**, que permita desacoplar los componentes principales, garantizar un mejor desempeño, facilitar la incorporación de nuevas tecnologías y brindar mayor portabilidad en diferentes escenarios.
El rediseño se centrará en separar funcionalidades clave en microservicios, con este cambio, el Objeto Inteligente se fortalecerá como una solución interoperable, escalable y flexible, capaz de gestionar perfiles personalizados de usuario e integrarse con múltiples dispositivos y plataformas, garantizando su evolución y sostenibilidad en el tiempo.

# Ejecución (Pensada para Rasbperry, también se puede correr en un pc con Linux)

## Requisitos
- python3
- mosquitto
- Docker Desktop (Opcional)

Para ejecutar este proyecto primero debe clonarse en el dispositivo donde se desea ejecutar, haciendo:

```sh
# Clonar al repo
git clone https://github.com/Guejia21/objeto_inteligente

# Ingresar a la carpeta raiz
cd objeto_inteligente

#Si se desea instalar mosquitto
sudo apt install mosquitto
```

### Ejecución manual
- Gateway: 8000
- Micro gestión de ontología: 8001
- Micro gestión de objetos: 8002
- Micro gestión de recursos y datastreams: 8003


Para preparar los micros para su ejecución, ejecute los siguientes comandos
```sh
# Dar permisos de ejecución
chmod +x setup.sh

# Ejecutar
./setup.sh
```

Si se desea limpiar los archivos generados en la ejecución del proyecto, se hace:
```sh
python3 clean.py
```

Si se desea correr la plataforma IoT localmente, se debe hacer:
```sh
cd things_board/
docker compose up
```
**Importante:** Apesar de que el proyecto se conecta a ThingsBoard para exponer telemetría, el hecho de no tenerlo no es un impedimento para que el proyecto funcione

Para iniciar cada micro (estando en la carpeta raiz):
```sh
#Gateway
cd gateway/app/ && source ../.venv/bin/activate && python3 main.py
#Ecas
cd micro_automatizacion_ecas/app/ && source ../.venv/bin/activate && python3 main.py
#Base del conocimiento
cd micro_gestion_conocimiento/app/ && source ../.venv/bin/activate && python3 main.py
#Objetos
cd micro_gestion_objetos/app/ && source ../.venv/bin/activate && python3 main.py
#Datastreams
cd microservicio_data_stream/ && source .venv/bin/activate && python3 main.py
#Personalizacion
cd microservicio_personalizacion/app && source ../.venv/bin/activate && python3 main.py
```

## Notas adicionales
Todo este proyecto está pensado para ejecutarse en una raspberry, pero el micro de `microservicio_data_stream_esp` está pensado para ejecutarse en una ESP32, para más información ingrese a su `README.md`

Finalmente, en la carpeta de `Ejemplo` se encuentran los ejecutables y el JSON usados de prueba para un objeto inteligente que tiene un led, un relay, un sensor de temperatura y otro de luz, adicionalmente, existe una ontologia llamada `usuarioActual.owl` la cual es una simulación para probar el endpoint de `RecibirOntologia` en el micro de personalización de usuarios

