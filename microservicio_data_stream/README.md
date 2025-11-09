Para instalar micropython en linux debe seguirse la guia:
https://docs.micropython.org/en/latest/develop/gettingstarted.html
Se puede crear un enlace simbolico para usar micropython como un comando nativo, de esta forma:

sudo ln -s <"rutamicropython">/micropython /usr/local/bin/micropython

# Nota importante
Para la ejecución con la rasberry se recomienda hacerlo con python3, por lo tanto se deberán hacer cambios respecto a las librerias, por ejemplo, en vez de ujson (para micropython) usar json

# Broker de mensajería
En este micro se usará una comunicación mqtt, debido a que el protocolo nativo manejado por RabbitMq no está soportado en Micropython. A pesar de eso, Rabbit ofrece un plugin mqtt, con el fin de publicar mensajes en este protocolo, para activar el plugin debe iniciarse Rabbit mq y hacer:

rabbitmq-plugins enable --offline rabbitmq_mqtt

Si se ejecuta por medio de Docker se debe ingresar a la consola del contenedor y ejecutar el comando anterior, posteriormente debe reinicarse el contenedor.

Para ejecutar rabbit por medio de Docker se hace (debe ejecutarse dese obojeto_inteligente/):
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 -p 1883:1883 -v ~/rabbitmq/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf -e RABBITMQ_DEFAULT_USER=admin -e RABBITMQ_DEFAULT_PASS=admin rabbitmq:3.13-management bash -c "rabbitmq-plugins enable --offline rabbitmq_management rabbitmq_mqtt && rabbitmq-server"