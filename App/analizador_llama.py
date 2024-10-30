### ---------------- Clase Analizador_Llama encargada del manejo de Llama 3 y las transcripciones para la generación del análisis de ODS ----------------

### IMPORTANTE: Las transcripciones se reciben en el siguiente formato: {ID del vídeo 1: ["Nombre del video", "Texto de la transcripción"], ID del vídeo 2: ["Nombre del video", "Texto de la transcripción"], ...}

# Librería de OpenAI para la conexión con el modelo
from openai import OpenAI

# Librerías de uso general
import os, json, shutil, ast

class Analizador_Llama:
    """Clase para el análisis de ODS a partir de un texto"""
    # Diccionario con la información de cada ODS
    dict_ods = {
         "ODS 1": "Fin de la Pobreza",
         "ODS 2": "Hambre Cero",
         "ODS 3": "Salud y Bienestar",
         "ODS 4": "Educación de Calidad",
         "ODS 5": "Igualdad de Género",
         "ODS 6": "Agua Limpia y Saneamiento",
         "ODS 7": "Energía Asequible y No Contaminante",
         "ODS 8": "Trabajo Decente y Crecimiento Económico",
         "ODS 9": "Industria, Innovación e Infraestructura",
         "ODS 10": "Reducción de las Desigualdades",
         "ODS 11": "Ciudades y Comunidades Sostenibles",
         "ODS 12": "Producción y Consumo Responsables",
         "ODS 13": "Acción por el Clima",
         "ODS 14": "Vida Submarina",
         "ODS 15": "Vida de Ecosistemas Terrestres",
         "ODS 16": "Paz, Justicia e Instituciones Sólidas",
         "ODS 17": "Alianza Para Lograr los Objetivos"
    }

    # Diccionario para almacenar los resultados de ODS detectados
    dict_ods_resultado = {
         "ODS 1": [False, None],
         "ODS 2": [False, None],
         "ODS 3": [False, None],
         "ODS 4": [False, None],
         "ODS 5": [False, None],
         "ODS 6": [False, None],
         "ODS 7": [False, None],
         "ODS 8": [False, None],
         "ODS 9": [False, None],
         "ODS 10": [False, None],
         "ODS 11": [False, None],
         "ODS 12": [False, None],
         "ODS 13": [False, None],
         "ODS 14": [False, None],
         "ODS 15": [False, None],
         "ODS 16": [False, None],
         "ODS 17": [False, None]
    }

    def __init__(self, ruta_carpeta):
        # Nos conectamos al modelo
        self.client = OpenAI(base_url="http://localhost:1234/v1", api_key="")

        # Ruta a la carpeta de resultados
        self.ruta_carpeta = os.path.join(os.getcwd(), ruta_carpeta)

    def generar_analisis_ods(self, partido, transcripciones, restablecer, id_video):
        """Función para obtener todos los ODS que están presentes en un discurso"""
        # Se completa la ruta de los resultados
        ruta_partido = os.path.join(self.ruta_carpeta, partido)
        ruta_resultado = os.path.join(ruta_partido, id_video)

        # Nombre del archivo donde está/estará el resultado
        nombre_archivo = os.path.join(ruta_resultado, "Resultados-{partido}-{id}.txt".format(partido=partido, id=id_video))

        # Se restablece la carpeta de resutlados al completo solo si se pide. También se comprueba si el análisis ya existe antes de generarlo de nuevo
        if not restablecer:
            if os.path.isfile(nombre_archivo):
                return self.leer_resultados(nombre_archivo)
        else:
            # Se limpia el directorio de resultados
            self.restablecer_directorio(partido)

        # Se restablece el diccionario de resultados
        self.restablecer_diccionario
        
        # Se obtiene el resumen de las transcripciones
        texto = self.devolver_discurso(transcripciones, id_video)

        # Se utiliza un bucle para detectar de forma individual cada ODS
        for ods, nombre in self.dict_ods.items():
            # Uso del modelo para la detección
            resultado = self.client.chat.completions.create(
                model="QuantFactory/Meta-Llama-3-8B-Instruct-GGUF",
                messages = [
                    {"role": "system", "content": """Eres un sistema de reconocimiento de temáticas en textos experto en los objetivos de desarrollo sostenibles de las naciones unidas que devuelve un resultado en formato JSON.
                    Recibirás un objetivo de desarrollo sostenible y un discurso político y detectarás si el objetivo recibido está en el discurso. Se asociará el valor "true" a la primera clave del JSON cuando el tema recibido esté presente en alguna parte del discurso y "false" cuando no. Si el primer valor ha sido “false”, el valor de la segunda clave será la string “No presente” y no se dará una explicación y si ha sido “true” el valor de la segunda clave será una string con el siguiente formato:
                    “El ODS [NumODS] de las Naciones Unidas, [NombreODS], consiste en [ExplicaciónODS]. Recientemente, el discurso del partido político PRTPLTC ha tenido relación con este ODS. [ExplicaciónDiscurso]”
                    Donde [NumODS] debe ser sustituido por el número del ODS, [NombreODS] debe ser sustituido por el nombre del ODS, [ExplicaciónODS] debe ser sustituido por una muy breve explicación de en qué consiste el ODS y [ExplicaciónDiscurso] debe explicar lo que se menciona en el discurso en relación al ODS.

                    El objeto JSON deberá tener el siguiente formato:
                    {"Tema presente en el texto": true/false, "Explicación":"No presente"/"[string]"}
                    Es muy importante que el output sea exclusivamente este JSON. No será correcto añadir nada más.

                    En todo momento deberás seguir las siguientes normas a la hora de devolver un resultado:
                    - Tienes totalmente prohibido considerar frases en las que no se hable explícitamente del tema.
                    - Tienes prohibido inventarte el significado de una frase. Solo se usará información que haya en el propio texto.
                    - Se devolverá un único JSON que deberá seguir la estructura marcada. No se devolverá nada más.
                    
                    Ejemplos:
                    Input: '[Número ODS]: '13', [Nombre ODS]: 'Acción por el Clima', [Discurso]: 'El mayor logro que ha conseguido nuestro gobierno es la reforestación de un gran número de hectáreas de bosque. Esto aumenta significativamente el número de zonas verdes de la ciudad. También ha arreglado las carreteras que estaban en mal estado.'
                    Output: {"Tema presente en el texto": true, "Explicación": "El ODS 13 de las Naciones Unidas, Acción por el Clima, se centra en tomar medidas urgentes contra el cambio climático y sus impactos, promoviendo la reducción de emisiones, la resiliencia y la educación climática. Recientemente, el discurso del partido político PRTPLTC ha tenido relación con este ODS. El partido ha mencionado que su gobierno ha reforestado un gran número de hectáreas de bosque aumentando el número de zonas verdes de la ciudad. Esto se alinea con lo que intenta promover el ODS 13."}

                    Input: '[Número ODS]: '1', [Nombre ODS]: 'Fin de la Pobreza', [Discurso]: 'La subida de impuestos ha provocado crispación entre ciertos colectivos. Sin embargo, con la ayuda del dinero que hemos conseguido, se han proporcionado múltiples ayudas económicas que se repartirán entre los más necesitados para que puedan llevar una vida digna.'
                    Output: {"Tema presente en el texto": true, "Explicación": "El ODS 1 de las Naciones Unidas, Fin de la Pobreza, busca erradicar la pobreza en todas sus formas, garantizando el acceso a recursos económicos y servicios básicos, y protegiendo a los vulnerables de desastres y crisis. Recientemente, el discurso del partido político PRTPLTC ha tenido relación con este ODS. El partido ha mencionado que la subida de impuestos ha conseguido que puedan proporcionar ayudas económicas que repartirán a los más necesitados con la intención de que puedan llevar una vida digna. Esto se alinea con lo que intenta promover el ODS 1."}

                    Input: '[Número ODS]: '13', [Nombre ODS]: 'Acción por el Clima', [Discurso]: 'Nuestro partido político tiene como objetivo ayudar a todos los que lo necesitan sin excepción.'
                    Output: {"Tema presente en el texto": false, "Explicación": "No presente"}
                    
                    Input: '[Número ODS]: '13', [Nombre ODS]: 'Acción por el Clima', [Discurso]: 'Desde que este grupo llegó al poder, las emisiones de dióxido de carbono se han duplicado.'
                    Output: {"Tema presente en el texto": true, "Explicación": "El ODS 13 de las Naciones Unidas, Acción por el Clima, se centra en tomar medidas urgentes contra el cambio climático y sus impactos, promoviendo la reducción de emisiones, la resiliencia y la educación climática. Recientemente, el discurso del partido político PRTPLTC ha tenido relación con este ODS. El partido político menciona que desde que llegaron al poder, las emisiones de dióxido de carbono se han duplicado lo cual va en contra del ODS 13."}"""},
                    {
                        "role": "user",
                        "content": "[Número ODS]: '{numODS}', [Nombre ODS]: {nombreODS}, [Discurso]: '{texto}'".format(numODS=ods.split()[1], nombreODS=nombre, texto=texto)
                    }
                ],
                    temperature=0,
                )
            
            # Se valida el JSON obtenido
            deteccion = self.validar_resultado(resultado.choices[0].message.content)
            # Si su formato es válido se carga en el diccionario
            if deteccion:
                # Se transforma la cadena
                obj_json = json.loads(resultado.choices[0].message.content)
                self.dict_ods_resultado[ods][0] = obj_json["Tema presente en el texto"]
                self.dict_ods_resultado[ods][1] = obj_json["Explicación"]
            
            print("El análisis del ODS {} ha terminado".format(ods.split()[1]))
 
        print("El análisis de ODS del partido {} se ha generado correctamente".format(partido))
        
        # Creamos el directorio para guardar el archivo
        os.makedirs(ruta_resultado, exist_ok=True)
        # Se guarda el resultado en un archivo de texto y se devuelve
        self.guardar_resultado(nombre_archivo)
        return self.dict_ods_resultado


    def devolver_discurso(self, transcripciones, id_video):
        """Función para completar el prompt con las transcripciones obtenidas"""
        # Se transforma a un diccionario de Python si no está ya en ese formato
        if type(transcripciones) == str:
             transcripciones = ast.literal_eval(transcripciones)

        # Se devuelve solo el texto a analizar
        return transcripciones[id_video][1]


    def guardar_resultado(self,nombre_archivo):
        """Función para guardar el resultado en un archivo de texto"""
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
                json.dump(self.dict_ods_resultado, archivo, ensure_ascii=False)


    def validar_resultado(self,resultado):
        """Función para validar el formato de un JSON obtenido por el modelo"""
        try:
            # Se transforma la cadena a un diccionario
            obj_json = json.loads(resultado)

            # Se comprueba que es del tipo adecuado
            if type(obj_json) != dict:
                print("Error con ID 1")
                return False
            
            # Se hace una lista de las claves posibles y necesarias y se compara con las existentes
            claves_esperadas = ["Tema presente en el texto", "Explicación"]
            claves_json = list(obj_json.keys())

            for clave_esperada in claves_esperadas:
                if clave_esperada not in claves_json:
                    print("Error con ID 2")
                    return False

            # Se comprueba que no hay claves extras
            if len(claves_json) != 2:
                print("Error con ID 3")
                return False
            
            # Se comprueba el carácter booleano del primer valor y string del segundo
            if type(obj_json["Tema presente en el texto"]) != bool or type(obj_json["Explicación"]) != str:
                print("Error con ID 4")
                return False
            
            return True
        
        except:
            print("Error con ID 5")
            return False


    def restablecer_directorio(self, partido):
        """Función que borra todos los contenidos del directorio de resultados de un partido """
        try:
            # Nombre de la carpeta del partido a resetear
            carpeta = os.path.join(self.ruta_carpeta,partido)
            # Se elimina el directorio de resultados
            shutil.rmtree(carpeta)

            # Se vuelve a crear
            os.makedirs(carpeta)

            print("Se restableció el repositorio de resultados del partido")

        except OSError as e:
            print("[ERROR] No se pudo eliminar el directorio de resultados del partido")
            exit(-1)
    
    
    def leer_resultados(self, nombre_archivo):
        """Función que lee un archivo de resultados ya presente"""
        # Se lee el archivo
        with open(nombre_archivo, "r", encoding="utf-8") as archivo:
            contenido = archivo.read()
        
        try:
            # Se convierte de nuevo a un diccionario
            contenido_dict = json.loads(contenido)
            return contenido_dict
        except:
            # Si falla devuelve None
            print("[ERROR] Ha habido un problema convirtiendo el contenido del archivo de resultados")
            return None


    def restablecer_diccionario(self):
        """Función para restablecer los valores iniciales del diccionario de resultados"""
        self.dict_ods_resultado = {
            "ODS 1": [False, None],
            "ODS 2": [False, None],
            "ODS 3": [False, None],
            "ODS 4": [False, None],
            "ODS 5": [False, None],
            "ODS 6": [False, None],
            "ODS 7": [False, None],
            "ODS 8": [False, None],
            "ODS 9": [False, None],
            "ODS 10": [False, None],
            "ODS 11": [False, None],
            "ODS 12": [False, None],
            "ODS 13": [False, None],
            "ODS 14": [False, None],
            "ODS 15": [False, None],
            "ODS 16": [False, None],
            "ODS 17": [False, None]
        }   