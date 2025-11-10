"""Interface para el broker de mensajería (por ejemplo, MQTT)"""
class BrokerInterface:
    async def publicar(self, topico, mensaje):
        raise NotImplementedError("Debe implementar 'publicar'")

    async def suscribirse(self, topico, callback):
        raise NotImplementedError("Debe implementar 'suscribirse'")
