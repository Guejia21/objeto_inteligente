# Microservicio Recursos & Datastreams

## Endpoints
- **GET /SendData**: osid, variableEstado, tipove (sen|act)
- **POST /SetDatastream**: { osid, idDataStream, comando, [email, mac, dateInteraction] }
- **GET /ListDatastreams**: osid

## Run local
```bash
uvicorn app.main:app --reload --port 8080
