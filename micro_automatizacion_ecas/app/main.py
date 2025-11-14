
from fastapi import FastAPI
from app.api.automatizacion_router import router as ecas_router

app = FastAPI(
    title="Microservicio Automatización ECAs",
    version="1.0.0"
)
app.include_router(ecas_router)

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse("/docs")
