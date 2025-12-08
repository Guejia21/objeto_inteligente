
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import RedirectResponse
from api.ecas import router as ecas_router
from config import settings
from deps import load_ecas_on_startup, get_broker
from domain.eca_task_manager import ECATaskManager


@asynccontextmanager
async def lifespan(app: FastAPI):    
    eca_task_manager = ECATaskManager()
    eca_task_manager.set_broker(get_broker())
    await load_ecas_on_startup()
    yield

app = FastAPI(
    title="Microservicio Automatización ECAs",
    version="1.0.0",
    lifespan=lifespan
)
app.include_router(ecas_router)

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse("/docs")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=settings.PORT)
