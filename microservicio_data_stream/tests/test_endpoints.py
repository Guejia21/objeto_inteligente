import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/health")
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_send_data():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/SendData", params={"osid":"2","variableEstado":"temp_cocina","tipove":"sen"})
    assert r.status_code == 200
    assert "value" in r.json()

@pytest.mark.asyncio
async def test_set_datastream():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post("/SetDatastream", json={"osid":"2","idDataStream":"ventilador","comando":"on"})
    assert r.status_code == 200
