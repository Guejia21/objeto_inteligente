from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from api.consultas import router as consultas_router
from api.poblacion import router as poblacion_router
from config import settings

app = FastAPI(prefix="/ontology")
app.include_router(consultas_router)
app.include_router(poblacion_router)
@app.get('/', include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url='/docs')
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=settings.PORT)