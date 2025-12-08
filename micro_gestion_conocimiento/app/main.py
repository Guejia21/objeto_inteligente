from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from api.consultas import ontologia_router as consultas_router
from api.consultas import ontologia_usuario_router as consultas_usuario_router
from api.poblacion import ontologia_router as poblacion_router
from config import settings
from api.poblacion import ontologia_usuario_router as poblacion_usuario_router

app = FastAPI(
    prefix="/ontology",
    title="Microservicio de Gestión de Base del Conocimiento",
    version="1.0.0"
    )
app.include_router(consultas_router)
app.include_router(poblacion_router)
app.include_router(poblacion_usuario_router)
app.include_router(consultas_usuario_router)
@app.get('/', include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url='/docs')
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=settings.PORT)