from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.api.consultas import router as consultas_router
from app.api.poblacion import router as poblacion_router

app = FastAPI(prefix="/ontology")
app.include_router(consultas_router)
app.include_router(poblacion_router)
@app.get('/', include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url='/docs')
