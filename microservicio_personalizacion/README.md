# Microservicio de Personalización

Microservicio para gestión de preferencias, ECAs y ontologías de usuario, manteniendo compatibilidad total con el sistema legacy.

## Características

- Gestión de preferencias de usuario (ECAs)
- Compatibilidad total con endpoints legacy
- Arquitectura DDD (Domain-Driven Design)
- Integración con ontologías OWL
- Comunicación via RabbitMQ

## Endpoints Compatibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/CrearPreferencia` | GET | Crear preferencia/ECA |
| `/SetEcaState` | GET | Activar/desactivar ECA |
| `/ApagarTodosEcas` | GET | Desactivar todos los ECAs |
| `/EcaList` | GET | Listar ECAs |
| `/DeleteEca` | GET | Eliminar ECA |
| `/RecibirOntologia` | POST | Cargar ontología de usuario |
| `/NotificarSalidaDeUsuario` | GET | Desactivar ECAs al salir |
| `/RegistroInteraccionUsuarioObjeto` | GET | Registrar interacción |

## Instalación

1. Clonar el repositorio
2. Crear entorno virtual: `python -m venv venv`
3. Activar entorno: `source venv/bin/activate`
4. Instalar dependencias: `pip install -r requirements.txt`
5. Configurar variables de entorno: `cp .env.example .env`
6. Ejecutar: `python -m app.main`

## Docker

```bash
docker build -t microservicio-personalizacion .
docker run -p 8001:8001 microservicio-personalizacion
