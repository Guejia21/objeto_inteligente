# Proyecto: Objeto Inteligente
## Contexto
Este proyecto tiene sus raíces en el trabajo de grado Modelo Ontológico para Manejo de Perfiles de Usuario en la IoT (Pabón y Rojas, 2017), el cual exploró la creación de un modelo semántico de perfil de usuario soportado en ontologías, con el fin de personalizar servicios en un entorno domótico. Dicho trabajo validó la eficacia del enfoque mediante una prueba de concepto y un estudio de caso, demostrando que el uso de perfiles semánticos mejora la interacción con objetos inteligentes. Se plantea la migración hacia una arquitectura basada en **microservicios**, que permita desacoplar los componentes principales, garantizar un mejor desempeño, facilitar la incorporación de nuevas tecnologías y brindar mayor portabilidad en diferentes escenarios.
El rediseño se centrará en separar funcionalidades clave en microservicios, con este cambio, el Objeto Inteligente se fortalecerá como una solución interoperable, escalable y flexible, capaz de gestionar perfiles personalizados de usuario e integrarse con múltiples dispositivos y plataformas, garantizando su evolución y sostenibilidad en el tiempo.

## Ejecución
Para ejecutar este proyecto, debe ejecutar Docker Compose (Posteriormente)

### Ejecución manual
- Gateway: 8000
- Micro gestión de ontología: 8001
- Micro gestión de objetos: 8002
- Micro gestión de recursos y datastreams: 8003
**Nota:** Se debe tener en cuenta que el micro de recursos y datastreams puede correse con micropython o python, para mayor información ingrese a su README.
Se debe ingresar a cada micro, activar el entorno, instalar los requerimientos y ejecutar el micro:
```sh
cd micro*
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd app
python3 main.py
```
#### Broker de mensajería
En este micro se usará una comunicación mqtt, debido a que el protocolo nativo manejado por RabbitMq no está soportado en Micropython. A pesar de eso, Rabbit ofrece un plugin mqtt, con el fin de publicar mensajes en este protocolo, para activar el plugin debe iniciarse Rabbit mq y hacer:

```sh
rabbitmq-plugins enable --offline rabbitmq_mqtt
```
Si se ejecuta por medio de Docker se debe ingresar a la consola del contenedor y ejecutar el comando anterior, posteriormente debe reinicarse el contenedor.

Para ejecutar rabbit por medio de Docker se hace:
```sh
cd objeto_inteligente/
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 -p 1883:1883 -v ~/rabbitmq/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf rabbitmq:4-management bash -c "rabbitmq-plugins enable --offline rabbitmq_management rabbitmq_mqtt && rabbitmq-server"
```

