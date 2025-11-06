from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.api.consultas import ontologia_router as consultas_router
from app.api.poblacion import ontologia_router as poblacion_router
from app.api.poblacion import ontologia_usuario_router as poblacion_usuario_router

app = FastAPI()
app.include_router(consultas_router)
app.include_router(poblacion_router)
app.include_router(poblacion_usuario_router)

@app.get('/', include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url='/docs')
