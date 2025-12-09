from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from api.objeto_controller import router
from config import settings

app = FastAPI(
    title="Microservicio de Gestión de Objetos Inteligentes",
    version="1.0.0"
    )
app.include_router(router)

@app.get('/', include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url='/docs')

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=settings.PORT)