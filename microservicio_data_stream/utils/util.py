from config import Config
import os as uos

def convert_metadata_format(input_metadata):
    """
    Convierte metadata del formato de micro_gestion_objetos al formato de microservicio_data_stream
    
    Args:
        input_metadata: Dict con formato largo (dicObj, dicRec)
    
    Returns:
        Dict con formato corto (object, datastreams)
    """
    dic_obj = input_metadata.get("dicObj", {})
    dic_rec = input_metadata.get("dicRec", [])    
    tb_token = input_metadata.get("thingsboard_token", "")
    
    # Construir objeto simplificado
    output = {
        "object": {
            "id": dic_obj.get("id", ""),
            "title": dic_obj.get("title", ""),
            "description": dic_obj.get("description", ""),
            "ip_object": dic_obj.get("ip_object", ""),
            "thingsboard_token": tb_token
        },
        "datastreams": []
    }
    
    # Convertir datastreams
    for rec in dic_rec:
        datastream = {
            "datastream_id": rec.get("datastream_id", ""),
            "datastream_format": rec.get("datastream_format", ""),
            "datastream_type": rec.get("datastream_type", ""),
            "unit_symbol": rec.get("symbol", "")
        }
        
        # Agregar campos opcionales solo si existen
        if rec.get("featureofinterest"):
            datastream["featureofinterest"] = rec["featureofinterest"]
        
        if rec.get("entityofinterest"):
            datastream["entityofinterest"] = rec["entityofinterest"]
        
        output["datastreams"].append(datastream)
    
    return output
def save_metadata(metadata):
    """Guarda la metadata en un archivo JSON"""
    import json as json
    try:
        with open(Config.PATH_METADATA + "metadata.json", 'w') as f:
            json.dump(metadata, f)
        print("Metadata guardada correctamente.")
    except Exception as e:
        print(f"Error guardando metadata: {e}")
def create_executables(listaRecursos, idObjeto):
    """Genera archivos ejecutables (plantillas) para cada datastream si no existen"""
    print("GENERANDO EJECUTABLES")
    if archivo_existe(Config.PATH_EJECUTABLES) == False:
        uos.mkdir(Config.PATH_EJECUTABLES, 0o777)
    if archivo_existe(Config.PATH_EJECUTABLES + "set_clean.py") == False:
        f_set_clean = open(Config.PATH_EJECUTABLES + "set_clean.py", 'w')
        f_set_clean.write("def main():")
        f_set_clean.close()
        # TODO Configurar publicador MQTT para logs
        # self.Log.PubRawLog(idObjeto, idObjeto, "Archivo: set_clean.py Sin Modificar")
        print("Archivo: set_clean.py Sin Modificar")
    #Generar los archivos para cambiar el estado de los datastreams    
    for var in listaRecursos:
        com_line = Config.PATH_EJECUTABLES + "set_" + var["datastream_id"] + ".py"
        try:
            uos.stat(com_line)
        except:
            f_set = open(com_line, 'w')
            f_set.write("def main(comparador, variable):")
            f_set.close()
            print("Archivo: set_" + var["datastream_id"] + ".py Sin Modificar")
    for var in listaRecursos:
        com_line = Config.PATH_EJECUTABLES + "get_" + var["datastream_id"] + ".py"
        try:
            uos.stat(com_line)
        except:
            f_get = open(com_line, 'w')
            f_get.write("value = 0")
            f_get.close()
            #self.Log.PubRawLog(idObjeto, idObjeto, "Archivo: get_" + var["datastream_id"] + ".py Sin Modificar")
            print("Archivo: get_" + var["datastream_id"] + ".py Sin Modificar")
    for var in listaRecursos:
        com_lineOn = Config.PATH_EJECUTABLES + "on_" + var["datastream_id"] + ".py"
        com_lineOff = Config.PATH_EJECUTABLES + "off_" + var["datastream_id"] + ".py"
        try:
            uos.stat(com_lineOn)
            uos.stat(com_lineOff)
        except:
            f_on = open(com_lineOn, 'w')
            f_on.write("def main()")
            f_on.close()
            #self.Log.PubRawLog(idObjeto, idObjeto, "Archivo: on_" + var["datastream_id"] + ".py Sin Modificar")
            print("Archivo: on_" + var["datastream_id"] + ".py Sin Modificar")
            f_off = open(com_lineOff, 'w')
            f_off.write("def main():")
            f_off.close()
            print("Archivo: off_" + var["datastream_id"] + ".py Sin Modificar")
    print("Ejecutables Cargados")
def archivo_existe(rutaArchivo):
    try:
        uos.stat(rutaArchivo)
        return True
    except:
        print("El archivo no existe:", rutaArchivo)
        return False