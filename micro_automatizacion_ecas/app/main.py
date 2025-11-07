from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.api.ecas import router as eca_router

app = FastAPI(
    title="Microservicio de Automatización de ECAs",
    version="1.0.0",
    description="Administra la creación, ejecución y control de reglas ECA desde la ontología base."
)

# Registrar router principal
app.include_router(eca_router)

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")
