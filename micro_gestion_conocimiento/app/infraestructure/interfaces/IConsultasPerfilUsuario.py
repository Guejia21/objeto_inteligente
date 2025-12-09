"""Interfaz para consultas en la ontología del perfil de usuario."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IConsultasPerfilUsuario(ABC):
    """Interfaz abstracta para consultas sobre el perfil de usuario."""
    @abstractmethod
    def consultarActive(self)->bool:
        """
        Consulta si la ontologia de usuario está activa
        
        Returns:
            bool: True si lo está, False en caso contrario
        """
        pass
    @abstractmethod
    def consultarEmailUsuario(self) -> str:
        """
        Consulta el email del usuario desde la ontología.
        
        Returns:
            str: Email del usuario o cadena vacía si no se encuentra.
        """
        pass

    @abstractmethod
    def consultarListaIpObjectos(self) -> List[List[Any]]:
        """
        Consulta la lista de IPs de objetos relacionados al usuario.
        
        Returns:
            List[List[Any]]: Lista de IPs de objetos.
        """
        pass

    @abstractmethod
    def consultarListaIpIdObjectosUsuario(self) -> List[Dict[str, str]]:
        """
        Consulta la lista de IPs e IDs de objetos del usuario.
        
        Returns:
            List[Dict[str, str]]: Lista de diccionarios con claves 'ipobjeto' e 'idobjeto'.
        """
        pass

    @abstractmethod
    def consultarListaObjetosRelacionadosEdificio(self, nombreEdificio: str) -> List[Dict[str, str]]:
        """
        Consulta los objetos relacionados a un edificio específico.
        
        Args:
            nombreEdificio: Nombre del edificio a consultar.
            
        Returns:
            List[Dict[str, str]]: Lista de diccionarios con claves 
                'name_object', 'ipobjeto', 'idobjeto'.
        """
        pass

    @abstractmethod
    def consultarPartesEdificioConObjetosRelacionados(self, nombreEdificio: str) -> List[Dict[str, str]]:
        """
        Consulta las partes de un edificio con sus objetos relacionados.
        
        Args:
            nombreEdificio: Nombre del edificio a consultar.
            
        Returns:
            List[Dict[str, str]]: Lista de diccionarios con claves 
                'nombreparte', 'name_object', 'ipobjeto', 'idobjeto'.
        """
        pass

    @abstractmethod
    def consultarObjetosRelacionadosACosasDeEdificio(self, nombreEdificio: str) -> List[Dict[str, str]]:
        """
        Consulta los objetos relacionados a cosas de un edificio.
        
        Args:
            nombreEdificio: Nombre del edificio a consultar.
            
        Returns:
            List[Dict[str, str]]: Lista de diccionarios con claves 
                'name_thing', 'name_object', 'ipobjeto', 'idobjeto'.
        """
        pass

    @abstractmethod
    def consultarListaIpIdObjectosEdificio(self, nombreEdificio: str) -> List[Dict[str, str]]:
        """
        Consulta la lista completa de IPs e IDs de objetos de un edificio.
        Incluye objetos relacionados directamente, en partes del edificio y en cosas.
        
        Args:
            nombreEdificio: Nombre del edificio a consultar.
            
        Returns:
            List[Dict[str, str]]: Lista combinada de objetos del edificio.
        """
        pass

    @abstractmethod
    def consultarEdificioRelacionadoObjeto(self, idObjeto: str) -> List[List[Any]]:
        """
        Consulta el edificio relacionado a un objeto específico.
        
        Args:
            idObjeto: ID del objeto a consultar.
            
        Returns:
            List[List[Any]]: Lista con el nombre del edificio relacionado.
        """
        pass

    @abstractmethod
    def consultarListaPreferenciasObjetoEventoporOSID(self, idObjeto: str) -> List[Dict[str, str]]:
        """
        Consulta las preferencias donde el objeto es el evento (origen).
        
        Args:
            idObjeto: OSID del objeto evento.
            
        Returns:
            List[Dict[str, str]]: Lista de diccionarios con información completa del ECA.
                Claves: 'name_eca', 'state_eca', 'id_event_object', 'ip_event_object',
                'name_event_object', 'id_event_resource', 'name_event_resource',
                'comparator_condition', 'variable_condition', 'type_variable_condition',
                'unit_condition', 'meaning_condition', 'id_action_object', 'ip_action_object',
                'name_action_object', 'id_action_resource', 'name_action_resource',
                'comparator_action', 'variable_action', 'type_variable_action',
                'unit_action', 'meaning_action', 'name_activity', 'start_date_activity',
                'end_date_activity'.
        """
        pass

    @abstractmethod
    def consultarListaPreferenciasObjetoAccionporOSID(self, idObjeto: str) -> List[Dict[str, str]]:
        """
        Consulta las preferencias donde el objeto es la acción (destino).
        
        Args:
            idObjeto: OSID del objeto acción.
            
        Returns:
            List[Dict[str, str]]: Lista de diccionarios con información completa del ECA.
                Claves: igual que consultarListaPreferenciasObjetoEventoporOSID.
        """
        pass

    @abstractmethod
    def consultarListaPreferenciasporOSID(self, idObjeto: str) -> List[Dict[str, str]]:
        """
        Consulta todas las preferencias relacionadas a un objeto (evento o acción).
        
        Args:
            idObjeto: OSID del objeto.
            
        Returns:
            List[Dict[str, str]]: Lista combinada de preferencias donde el objeto
                es evento o acción.
        """
        pass

    @abstractmethod
    def consultarObjetivoUsuario(self) -> List[Dict[str, str]]:
        """
        Consulta los objetivos del usuario.
        
        Returns:
            List[Dict[str, str]]: Lista de diccionarios con claves 
                'name_objective', 'specific', 'start_date', 'Measurable', 'suitable_for'.
        """
        pass

    @abstractmethod
    def consultarActosObjetivosUsuario(self) -> List[Dict[str, str]]:
        """
        Consulta los actos asociados a los objetivos del usuario.
        
        Returns:
            List[Dict[str, str]]: Lista de diccionarios con claves 
                'name_objective', 'name_acts', 'number', 'start_date_acts', 
                'final_date', 'description_act', 'state_acts', 'specific', 
                'start_date', 'Measurable', 'suitable_for'.
        """
        pass

    @abstractmethod
    def consultarRecursosObjetivosUsuario(self) -> List[Dict[str, str]]:
        """
        Consulta los recursos asociados a los objetivos del usuario.
        
        Returns:
            List[Dict[str, str]]: Lista de diccionarios con claves 
                'name_objective', 'name_resource', 'number_resource',
                'specific', 'start_date', 'Measurable', 'suitable_for'.
        """
        pass

    @abstractmethod
    def consultarActosGroupObjetivos(self) -> List[List[Dict[str, str]]]:
        """
        Consulta los actos agrupados por objetivo.
        
        Returns:
            List[List[Dict[str, str]]]: Lista de listas, donde cada sublista
                contiene los actos de un objetivo específico.
        """
        pass

    @abstractmethod
    def consultarRecGroupObjetivos(self) -> List[List[Dict[str, str]]]:
        """
        Consulta los recursos agrupados por objetivo.
        
        Returns:
            List[List[Dict[str, str]]]: Lista de listas, donde cada sublista
                contiene los recursos de un objetivo específico.
        """
        pass

    @abstractmethod
    def consultarActosUsuario(self) -> List[Dict[str, str]]:
        """
        Consulta todos los actos del usuario sin información completa del objetivo.
        
        Returns:
            List[Dict[str, str]]: Lista de diccionarios con claves 
                'name_objective', 'name_acts', 'number', 'start_date_acts',
                'final_date', 'description_act', 'state_acts'.
        """
        pass

    @abstractmethod
    def consultarRecursosUsuario(self) -> List[Dict[str, str]]:
        """
        Consulta todos los recursos del usuario sin información completa del objetivo.
        
        Returns:
            List[Dict[str, str]]: Lista de diccionarios con claves 
                'name_objective', 'name_resource', 'number_resource'.
        """
        pass

    def pasarListaDiccionario(self, lista: List[Any], keys: List[str]) -> Dict[str, str]:
        """
        Convierte una lista de valores a un diccionario usando las claves proporcionadas.
        
        Args:
            lista: Lista de valores a convertir.
            keys: Lista de claves para el diccionario.
            
        Returns:
            Dict[str, str]: Diccionario con los valores mapeados a las claves.
        """
        pass

    def decodificar(self, diccionario: Dict[str, Any]) -> Dict[str, str]:
        """
        Decodifica los valores de un diccionario de bytes a string UTF-8.
        
        Args:
            diccionario: Diccionario con valores posiblemente en bytes.
            
        Returns:
            Dict[str, str]: Diccionario con valores decodificados.
        """
        pass