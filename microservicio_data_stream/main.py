from microdot import Microdot
from routes.datastreams import register_routes
from config import Config

# Crear aplicación
app = Microdot()

# Registrar rutas
register_routes(app)

# Ejecutar servidor
if __name__ == '__main__':
    print(f"   Datastream Service iniciando en {Config.HOST}:{Config.PORT}")
    print(f"   OSID: {Config.OSID}")
    print(f"   Title: {Config.TITLE}")
    app.run(host=Config.HOST, port=Config.PORT, debug=True)