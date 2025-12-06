# Proyecto: Objeto Inteligente
## Contexto
Este proyecto tiene sus raíces en el trabajo de grado Modelo Ontológico para Manejo de Perfiles de Usuario en la IoT (Pabón y Rojas, 2017), el cual exploró la creación de un modelo semántico de perfil de usuario soportado en ontologías, con el fin de personalizar servicios en un entorno domótico. Dicho trabajo validó la eficacia del enfoque mediante una prueba de concepto y un estudio de caso, demostrando que el uso de perfiles semánticos mejora la interacción con objetos inteligentes. Se plantea la migración hacia una arquitectura basada en **microservicios**, que permita desacoplar los componentes principales, garantizar un mejor desempeño, facilitar la incorporación de nuevas tecnologías y brindar mayor portabilidad en diferentes escenarios.
El rediseño se centrará en separar funcionalidades clave en microservicios, con este cambio, el Objeto Inteligente se fortalecerá como una solución interoperable, escalable y flexible, capaz de gestionar perfiles personalizados de usuario e integrarse con múltiples dispositivos y plataformas, garantizando su evolución y sostenibilidad en el tiempo.

## Ejecución
Para ejecutar este proyecto, debe ejecutar Docker Compose (Posteriormente)

## Requisitos
- python
- mosquitto

### Ejecución manual
- Gateway: 8000
- Micro gestión de ontología: 8001
- Micro gestión de objetos: 8002
- Micro gestión de recursos y datastreams: 8003
**Nota:** Se debe tener en cuenta que el micro de recursos y datastreams puede correse con micropython o python, para mayor información ingrese a su README.
Se debe ingresar a cada micro, activar el entorno, instalar los requerimientos y ejecutar el micro:
```sh
cd micro*
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd app
python3 main.py
```

Si se desea limpiar los archivos generados en la ejecución del proyecto, se hace:
```sh
python clean.py
```


