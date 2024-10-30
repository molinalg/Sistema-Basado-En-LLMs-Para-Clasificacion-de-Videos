### ---------------- Clase Analizador_Llama para el análisis de un texto en torno a un ODS ----------------

# Importamos la librería de OpenAI
from openai import OpenAI
import json

class Analizador_Llama:
    """Clase para el análisis de un texto en torno a un ODS"""
    def __init__(self):
        self.client = OpenAI(base_url="http://localhost:1234/v1", api_key="")

    def obtener_resultado(self,numero,nombre,texto):
        """Función para obtener un análisis de un texto en torno a un ODS"""
        completion = self.client.chat.completions.create(
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
              "content": "[Número ODS]: '{numODS}', [Nombre ODS]: {nombreODS}, [Discurso]: '{texto}'".format(numODS=numero, nombreODS=nombre, texto=texto)
          }
      ],
            temperature=0,
        )

        # Se valida lo recibido y se devuelve el resultado
        correcto = self.validar_resultado(completion.choices[0].message.content)
        if correcto:
            obj_json = json.loads(completion.choices[0].message.content)
    
            return {"Resultado": obj_json["Tema presente en el texto"]}
        else:
            return {"Resultado": None}

    def validar_resultado(self,resultado):
        """Función para validar el output de llama 3"""
        try:
            # Se transforma la cadena
            obj_json = json.loads(resultado)

            # Se comprueba que es del tipo adecuado
            if type(obj_json) != dict:
                print("1")
                return False
            
            # Se hace una lista de las claves posibles y necesarias y se compara con la existente
            claves_esperadas = ["Tema presente en el texto", "Explicación"]
            claves_json = list(obj_json.keys())

            for clave_esperada in claves_esperadas:
                if clave_esperada not in claves_json:
                    print("2")
                    return False

            if len(claves_json) != 2:
                print("3")
                return False
            
            # Se comprueba el carácter booleano del primer valor y string del segundo
            if type(obj_json["Tema presente en el texto"]) != bool or type(obj_json["Explicación"]) != str:
                print("4")
                return False
            
            return True
        
        except:
            print("5")
            return False
