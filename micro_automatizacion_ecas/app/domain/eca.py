import time
import threading
import json
from config import settings

class ECA:
    def __init__(self):        
        pass  
    def getDiccionarioECA(self, nombreArchivo) -> dict:
        """
        Lee un archivo JSON con el contrato ECA y retorna un diccionario aplanado con los datos.
        
        Args:
            nombreArchivo: Nombre del archivo JSON del contrato ECA
            
        Returns:
            Diccionario aplanado con los datos del contrato ECA
        """

        
        try:
            # Leer el archivo JSON del contrato
            filepath = settings.PATH_ECA + '/' + nombreArchivo
            with open(filepath, 'r', encoding='utf-8') as f:
                contrato = json.load(f)
            
            # Si el contrato viene envuelto en la estructura MakeContractRequest
            if 'contrato' in contrato:
                contrato = contrato['contrato']
            
            # Aplanar el contrato al formato EcaPayloadDTO
            diccionario_eca = {
                # General ECA attributes
                "name_eca": contrato.get("name_eca", ""),
                "state_eca": contrato.get("state_eca", "off"),
                "interest_entity_eca": contrato.get("interest_entity_eca", ""),
                "user_eca": contrato.get("user_eca"),
                
                # Event attributes (desde objeto anidado "event")
                "id_event_object": contrato.get("event", {}).get("id_event_object", ""),
                "ip_event_object": contrato.get("event", {}).get("ip_event_object", ""),
                "name_event_object": contrato.get("event", {}).get("name_event_object", ""),
                "id_event_resource": contrato.get("event", {}).get("id_event_resource", ""),
                "name_event_resource": contrato.get("event", {}).get("name_event_resource", ""),
                
                # Condition attributes (desde objeto anidado "condition")
                "comparator_condition": contrato.get("condition", {}).get("comparator_condition", ""),
                "meaning_condition": contrato.get("condition", {}).get("meaning_condition", ""),
                "unit_condition": contrato.get("condition", {}).get("unit_condition", ""),
                "variable_condition": contrato.get("condition", {}).get("variable_condition", {}).get("value", ""),
                "type_variable_condition": contrato.get("condition", {}).get("variable_condition", {}).get("type", "string"),
                
                # Action attributes (desde objeto anidado "action")
                "id_action_object": contrato.get("action", {}).get("id_action_object", ""),
                "ip_action_object": contrato.get("action", {}).get("ip_action_object", ""),
                "name_action_object": contrato.get("action", {}).get("name_action_object", ""),
                "id_action_resource": contrato.get("action", {}).get("id_action_resource", ""),
                "name_action_resource": contrato.get("action", {}).get("name_action_resource", ""),
                "comparator_action": contrato.get("action", {}).get("comparator_action", ""),
                "unit_action": contrato.get("action", {}).get("unit_action", ""),
                "meaning_action": contrato.get("action", {}).get("meaning_action", ""),
                "variable_action": contrato.get("action", {}).get("variable_action", {}).get("value", ""),
                "type_variable_action": contrato.get("action", {}).get("variable_action", {}).get("type", "string"),
            }
            
            return diccionario_eca
            
        except FileNotFoundError:
            print(f"Error: Archivo no encontrado: {nombreArchivo}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error: JSON inválido en {nombreArchivo}: {e}")
            return {}
        except Exception as e:
            print(f"Error leyendo contrato ECA: {e}")
            return {}
    
"""
    def poblarListaEca(self, listaDiccEca):
        for item in listaDiccEca:
            try:
                objPoblarEca = PoblarECA()
                objPoblarEca.poblarECA(item)
                nomHilo = "hilo" + item["name_eca"]
                hiloEca = threading.Thread(target=self.__ecas, name=nomHilo, args=(item["name_eca"],))
                hiloEca.start()
            except Exception as e:
                print( "Excepcion desde poblarLista0ca con el eca " + item["name_eca"])
                print( e)

    def cambiarEstadoListaEcas(self, listaEcas):  ##[{"name_eca", state_eca'}]
        for item in listaEcas:
            ################################self.consultas = ConsultasOOS()
            if item['state_eca'] == "off":
                try:
                    AppUtil.killProcess(item['name_eca'])
                    # os.system(
                    #     "sudo kill -s 9 $(ps ax | grep " + item['name_eca'] + " | grep -v grep | awk '{print$1}')")
                    self.consultas.setEcaState(item['state_eca'], item['name_eca'])
                except Exception as e:
                    print( e)
                    pass


    def eliminarListaEcas(self, listaEcas):  ##lista de strings [{'name_eca': 'luzcalefactorOn', 'state_eca': 'on'}, {'name_eca': 'luzcalefactorOff', 'state_eca': 'on'}, {'name_eca': 'calefactorBombilloOff', 'state_eca': 'on'}, {'name_eca': 'calefactorBombilloOn', 'state_eca': 'on'}]
        for item in listaEcas:
            ################################self.consultas = ConsultasOOS()
            self.consultas.eliminarEca(item['name_eca'])

            ####################################################################################################################################################

    def verificarContrato(self, osid, osidDestino):
        ################################self.consultas = ConsultasOOS()
        ##{osid osidDestino id_action_resource comparator_action variable_action type_variable_action eca_state}
        resultado = self.consultas.verificarContrato(osid, osidDestino)
        return resultado

    def listarDinamicEstado(self, eca_state):
        ################################self.consultas = ConsultasOOS()
        # [{"eca_state" ,"name_eca"}]
        resultado = self.consultas.listarDinamicEstado(eca_state)
        return resultado

    def listarEcasEvento(self, osid, state_eca):
        ################################self.consultas = ConsultasOOS()
        ##{}eca_state id_event_resource comparator_condition variable_condition
        ##type_variable_condition unit_condition meaning_condition
        ##ip_action_object osid_object_action name_action_object comparator_action
        ##type_variable_action variable_action meaning_action id_action_resource name_action_resource
        resultado = self.consultas.listarEcasEvento(osid, state_eca)
        return resultado

    def listarEcasEventoSegunUsuario(self, osid, state_eca, usuario_eca):
        ################################self.consultas = ConsultasOOS()
        ##{}eca_state id_event_resource comparator_condition variable_condition
        ##type_variable_condition unit_condition meaning_condition
        ##ip_action_object osid_object_action name_action_object comparator_action
        ##type_variable_action variable_action meaning_action id_action_resource name_action_resource
        resultado = self.consultas.listarEcasEventoSegunUsuario(osid, state_eca, usuario_eca)
        return resultado

    
    def getDiccionarioECAOntologia(self, nombreEca):
        ################################self.consultas = ConsultasOOS()
        return self.consultas.getEca(nombreEca)

    def poblarEca(self, diccEca):
        try:
            objPoblarEca = PoblarECA()
            objPoblarEca.poblarECA(diccEca)
            return True
        except Exception as e:
            print( "Excepcion desde poblarEca")
            print( e)
            return False

    def SetEcaState(self, parametros):
        print( "llego a objeto setecastate cpmn el comando " + parametros['comando'])
        ################################self.consultas = ConsultasOOS()
        if parametros['comando'] == "off":
            try:
                AppUtil.killProcess(parametros['nombreECA'])
                self.consultas.setEcaState(parametros['comando'], parametros['nombreECA'])
                #os.system(
                 #   "sudo kill -s 9 $(ps ax | grep " + parametros['nombreECA'] + " | grep -v grep | awk '{print$1}')")
            except Exception as e:
                print( e)
                pass


    def estadoEca(self, eca_name):
        ################################self.consultas = ConsultasOOS()
        estado = self.consultas.estadoEca(eca_name)  ##[{"eca_state" ,"name_eca"}]
        estadoEca = ""
        for eca in estado:
            estadoEca = eca["eca_state"]
        return estadoEca

    def listarEcas(self):
        ##{'name_eca','eca_state','osid_object_event','ip_event_object','name_event_object','id_event_resource','name_event_resource','comparator_condition',
        # 'variable_condition','type_variable_condition','unit_condition', 'meaning_condition','osid_object_action','ip_action_object','name_action_object',
        # 'id_action_resource','name_action_resource','comparator_action','variable_action','type_variable_action','unit_action','meaning_action'}
        ################################self.consultas = ConsultasOOS()
        listaEcas = self.consultas.listarEcas()
        return listaEcas

    def listarEcasUsuario(self, user_eca):
        ################################self.consultas = ConsultasOOS()
        listaEcas = self.consultas.listarEcasUsuario(user_eca)
        return listaEcas

    def listarNombresEcasUsuario(self, user_eca):
        ################################self.consultas = ConsultasOOS()
        listaEcas = self.consultas.listarNombresEcasUsuario(user_eca)
        return listaEcas

    def apagarTodosEcas(self, parametros):
        # [['708637323', 'calefactor', 'igual', '1', 'name_eca']]
        ################################self.consultas = ConsultasOOS()
        ti = time.time()
        listaEcas = self.listarDinamicEstado("on")  ##[{"eca_state" ,"name_eca"}]
        print(  "    Apagando un total de " + str(len(listaEcas)) + " ECAS")
        if len(listaEcas) > 0:
            lista = []
            for eca in listaEcas:
                AppUtil.killProcess(eca["name_eca"])
                #os.system("sudo kill -s 9 $(ps ax | grep " + eca["name_eca"] + " | grep -v grep | awk '{print$1}')")
                # os.system("sudo ps ax | grep " + eca["name_eca"] + " | grep -v grep | awk '{print$1}'|xargs  kill")
                lista.append([eca["name_eca"], "off"])
            self.consultas.setEcaListState(lista)
        tf = time.time()
        tt = tf - ti
        print ("Termina de apagar Ecas en " + str(tt) + " Segundos")

    def apagarListaEcas(self, listaEcas):
        # [['708637323', 'calefactor', 'igual', '1', 'name_eca']]
        ################################self.consultas = ConsultasOOS()
        ti = time.time()
        print(  "    Apagando un total de " + str(len(listaEcas)) + " ECAS")
        print( ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Lista de ecas desde objeto ")
        print( listaEcas)
        if len(listaEcas) > 0:
            lista = []
            for eca in listaEcas:
                AppUtil.killProcess(eca["name_eca"])
                #os.system("sudo kill -s 9 $(ps ax | grep " + eca["name_eca"] + " | grep -v grep | awk '{print$1}')")
                # os.system("sudo ps ax | grep " + eca["name_eca"] + " | grep -v grep | awk '{print$1}'|xargs  kill")
                lista.append([eca["name_eca"], "off"])
            self.consultas.setEcaListState(lista)
        tf = time.time()
        tt = tf - ti
        print( "Termina de apagar Ecas en " + str(tt) + " Segundos")

    def eliminarEca(self, nombreECA):
        try:
            ################################self.consultas = ConsultasOOS()
            self.consultas.eliminarEca(nombreECA)
            return True
        except Exception as e:
            print( "desde objeto eliminareca ")
            print( e)
            return False

    def editarEca(self, diccEca):
        try:
            objEditarEca = EditarECA()
            objEditarEca.editarECA(diccEca)
            return True
        except Exception as e:
            print( "Excepcion desde poblarEca")
            print( e)
            return False

    def __ecas(self, nombreEca):
       # os.system("python " + Paths.pathIndependientePck + "EjecutarEcaIndependiente.py " + nombreEca)
       modulo = Modulo()
       modulo.ejecutarClaseIndependiente("EjecutarEcaIndependiente.py", nombreEca)


    def lanzarHiloListaEca(self, ecasUsuario):
        for eca in ecasUsuario:
            if ( 'eca_state' in eca and eca['eca_state'] == 'on') or ('state_eca' in eca and eca['state_eca'] == 'on'):  ##Algunas veces llega eca_state y otras state_eca
                print( "    Lanzando el hilo del ECA " + eca["name_eca"])
                nomHilo = "hilo" + eca["name_eca"]
                hiloEca = threading.Thread(target=self.__ecas, name=nomHilo, args=(eca["name_eca"], ))
                hiloEca.start()
"""