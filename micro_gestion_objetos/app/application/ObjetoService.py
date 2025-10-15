from app.infraestructure.logging import ILogPanel
class ObjetoService:
    def __init__(self, log_panel: ILogPanel):
        self.log_panel = log_panel

    async def getIdentificator(self, osid: int):        
        #TO DO: osid debe existir en ObjetoService como atributo
        #Para eso debe también crearse un atributo objetoInteligente y en este
        #debe definirse su atributo osid
        await self.log_panel.PubRawLog(osid, osid, "Enviando Metadata.xml")
        await self.log_panel.PubLog("metadata_query", osid, self.tittle, osid, self.tittle,
                                     "metadata_query", "Solicitud Recibida")
        