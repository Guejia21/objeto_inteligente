from config import Config


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
    
    # Construir objeto simplificado
    output = {
        "object": {
            "id": dic_obj.get("id", ""),
            "title": dic_obj.get("title", ""),
            "description": dic_obj.get("description", ""),
            "ip_object": dic_obj.get("ip_object", "")
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
    import ujson as json
    try:
        with open(Config.PATH_METADATA + "metadata.json", 'w') as f:
            json.dump(metadata, f)
        print("Metadata guardada correctamente.")
    except Exception as e:
        print(f"Error guardando metadata: {e}")
