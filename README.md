# Proyecto: Objeto Inteligente
## Contexto
Este proyecto tiene sus raíces en el trabajo de grado Modelo Ontológico para Manejo de Perfiles de Usuario en la IoT (Pabón y Rojas, 2017), el cual exploró la creación de un modelo semántico de perfil de usuario soportado en ontologías, con el fin de personalizar servicios en un entorno domótico. Dicho trabajo validó la eficacia del enfoque mediante una prueba de concepto y un estudio de caso, demostrando que el uso de perfiles semánticos mejora la interacción con objetos inteligentes. Se plantea la migración hacia una arquitectura basada en **microservicios**, que permita desacoplar los componentes principales, garantizar un mejor desempeño, facilitar la incorporación de nuevas tecnologías y brindar mayor portabilidad en diferentes escenarios.
El rediseño se centrará en separar funcionalidades clave en microservicios, con este cambio, el Objeto Inteligente se fortalecerá como una solución interoperable, escalable y flexible, capaz de gestionar perfiles personalizados de usuario e integrarse con múltiples dispositivos y plataformas, garantizando su evolución y sostenibilidad en el tiempo.

# Ejecución (Pensada para Rasbperry, también se puede correr en un pc con Linux)

## Requisitos
- python3
- mosquitto
- Docker Desktop (Opcional)
- tmux (Opcional)

Para ejecutar este proyecto primero debe clonarse en el dispositivo donde se desea ejecutar, haciendo:

```sh
# Clonar al repo
git clone https://github.com/Guejia21/objeto_inteligente

# Ingresar a la carpeta raiz
cd objeto_inteligente

#Si se desea instalar mosquitto
sudo apt install mosquitto

#Si se desea instalar tmux
sudo apt install tmux
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

Para iniciar cada micro de manera manual(estando en la carpeta raiz):
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
### Ejecución automatizada
Si se desea correr el proyecto con un solo comando (**DEBE INSTALARSE TMUX**) se hace:
```sh
./run.sh
```
## Documentación

### Acceso a Documentación de APIs

Para acceder a la documentación interactiva de los microservicios (Swagger/OpenAPI):

| Microservicio | URL |
|---------------|-----|
| Gateway | http://localhost:8000/docs |
| Ontología | http://localhost:8001/docs |
| Objetos | http://localhost:8002/docs |
| Datastreams | http://localhost:8003/docs |
| ECAs | http://localhost:8004/docs |
| Personalización | http://localhost:8005/docs |

### Generar Documentación Completa (Doxygen)

Para generar la documentación técnica completa del código:

#### Requisitos

```bash
# Ubuntu/Debian/Raspberry Pi
sudo apt install doxygen graphviz

# macOS
brew install doxygen graphviz

# Windows (con Chocolatey)
choco install doxygen.install graphviz
```

#### Generación

```bash
# Desde la raíz del proyecto
cd docs/
doxygen Doxyfile

# La documentación se generará en:
# - docs/html/index.html (navegable en web)
# - docs/latex/ (para compilar a PDF)
```

#### Ver Documentación

```bash
# Linux/macOS
xdg-open docs/html/index.html

# Raspberry Pi
chromium-browser docs/html/index.html

# Windows
start docs/html/index.html
```

#### Generar PDF (Opcional)

```bash
cd docs/latex/
make
# Se generará docs/latex/refman.pdf
```
> **Nota:** La documentación HTML/LaTeX **NO** está incluida en el repositorio por su gran tamaño (800MB). Se genera bajo demanda ejecutando `doxygen` como se indica arriba.

## Notas adicionales
Todo este proyecto está pensado para ejecutarse en una raspberry, pero el micro de `microservicio_data_stream_esp` está pensado para ejecutarse en una ESP32, para más información ingrese a su `README.md`

Finalmente, en la carpeta de `Ejemplo` se encuentran los ejecutables y el JSON usados de prueba para un objeto inteligente que tiene un led, un relay, un sensor de temperatura y otro de luz, adicionalmente, existe una ontologia llamada `usuarioActual.owl` la cual es una simulación para probar el endpoint de `RecibirOntologia` en el micro de personalización de usuarios

