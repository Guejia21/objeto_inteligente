from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.api.objeto_controller import router

app = FastAPI()
app.include_router(router)

@app.get('/', include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url='/docs')