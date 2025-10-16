from app.infraestructure.logging import ILogPanelMQTT
from app.domain.ObjetoInteligente import ObjetoInteligente
import infraestructure.logging.Logging as logging

# Configurar el logger
logger = logging.getLogger(__name__)

class ObjetoService:
    def __init__(self, log_panel: ILogPanelMQTT):
        self.log_panel = log_panel
        self.objetoInteligente = ObjetoInteligente()
    async def getIdentificator(self, osid: int):        
        #TO DO: osid debe existir en ObjetoService como atributo
        #Para eso debe también crearse un atributo objetoInteligente y en este
        #debe definirse su atributo osid
        await self.log_panel.PubRawLog(self.osid, self.osid, "Enviando Metadata.json")
        await self.log_panel.PubLog("metadata_query", self.osid, self.tittle, self.osid, self.tittle,
                                     "metadata_query", "Solicitud Recibida")
        #Si el osid coincide con el del objeto inteligente guardado, se retorna su info
        if osid == self.objetoInteligente.osid:
            logger.info("Enviando identificador del objeto con oid %s", osid)
            try:
                #Definir ruta donde va a estar el metadata
                path = ""
                file = open(path, "rb")
                await self.log_panel.PubRawLog(self.osid, self.osid, "Solicitud entregada")
                logger.info("Identificador enviado correctamente")
                await self.log_panel.PubLog("metadata_query", self.osid, self.tittle, self.osid, self.tittle,
                                "metadata_query", "Publicando Respuesta")
                resultado = file.read()
                file.close()
                return resultado
            except Exception as e:
                logger.error("Error al leer el archivo de metadata: %s", e)                
                #TODO: Retornar un JSON estructurado (como ellos hacian con XML) con el error relacionado
                return None
            
        