class ObjetoInteligente:
    _instance = None  # Variable de clase para almacenar la única instancia
    # Implementación del patrón Singleton
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ObjetoInteligente, cls).__new__(cls)
            cls._instance.__initialized = False  # Bandera para inicialización
        return cls._instance

    def __init__(self):
        if not self.__initialized:  # Solo inicializa una vez            
            self.__initialized = True
            #Aqui se deben poner los atributos del objeto inteligente 
            #que deben ser sacados de la ontología en caso de que aplique
            self.osid = None  # ID del objeto inteligente
            self.title = None  # Título del objeto inteligente