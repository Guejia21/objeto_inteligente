
class Config:
    # Servidor
    HOST = '0.0.0.0'
    PORT = 8003

    # BASE_DIR: obtener carpeta del fichero actual
    try:
        _f = __file__
    except NameError:
        _f = ''
    _sep_idx = _f.rfind('/')
    if _sep_idx != -1:
        BASE_DIR = _f[:_sep_idx]
    else:
        BASE_DIR = '.'

    # Rutas (compatibles con MicroPython)
    PATH_EJECUTABLES = BASE_DIR + '/storage/executables/'
    PATH_METADATA = BASE_DIR + '/storage/metadata/'

    # Objeto (se carga dinámicamente desde metadata)
    OSID = None
    TITLE = None

    # Códigos de respuesta
    CODES = {
        'exitoso': '1000',
        'datastreamEncendido': '1001',
        'idIncorrecto': '1025',
        'dataStremNoExiste': '1026',
        'errorDatastream': '1027',
        'noImplementado': '1099'
    }
# ...existing code...