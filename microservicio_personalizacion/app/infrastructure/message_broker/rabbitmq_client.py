import pika
import json
import logging
from app.config.settings import settings

logger = logging.getLogger(__name__)

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        
    def connect(self):
        try:
            credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS)
            parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                credentials=credentials,
                heartbeat=600
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info("Conectado a RabbitMQ exitosamente")
        except Exception as e:
            logger.error(f"Error conectando a RabbitMQ: {e}")
            raise
        
    def publish_message(self, queue_name: str, message: dict):
        try:
            if not self.connection or self.connection.is_closed:
                self.connect()
                
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type='application/json'
                )
            )
            logger.info(f"Mensaje publicado en cola {queue_name}: {message}")
        except Exception as e:
            logger.error(f"Error publicando mensaje en RabbitMQ: {e}")
            raise
    
    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Conexión RabbitMQ cerrada")
