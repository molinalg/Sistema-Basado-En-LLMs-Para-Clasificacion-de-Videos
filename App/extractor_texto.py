### ---------------- Clase Extractor_Texto encargada de generar transcripciones de los vídeos solicitados a partir de su audio ----------------

# Librerías de uso general
import os, shutil, nltk, ast
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
from math import ceil
import numpy as np

# Libreías para la generación de resúmenes
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

class Extractor_Texto:
    """Clase para la generación de transcripciones de audios"""
    def __init__(self, ruta_carpeta,canal,ruta_carpeta_audio):
        # Variables necesarias
        self.ruta_carpeta = ruta_carpeta
        self.partido = canal

        # Ruta a la carpeta de transcripciones
        self.ruta_actual = os.getcwd()
        self.ruta_carpeta = os.path.join(self.ruta_actual, ruta_carpeta)
        # Ruta a la carpeta de audios
        self.ruta_carpeta_audio = ruta_carpeta_audio
    
    def extraer_contenido(self, restablecer, model, id_video):
        """Función para generación de una transcripción a partir del id de un vídeo"""
        # Se completa la ruta a la carpeta específica de transcripciones del vídeo
        ruta_transcripcion = os.path.join(self.ruta_carpeta, id_video)
        
        # Nombre del archivo donde está/estará la transcripción
        nombre_archivo = os.path.join(ruta_transcripcion, "Transcripciones-{partido}-{id}.txt".format(partido=self.partido, id=id_video))

        # Solo se lee si ya existe y solo se restablece el directorio cuando se pide
        if not restablecer:
            if os.path.isfile(nombre_archivo):
                return self.leer_transcripciones(nombre_archivo)
        else:
            # Se limpia el directorio de transcipciones
            self.restablecer_directorio()

        # Variable para mantener control de las keys del diccionario
        count = 0
        # Variable para mantener el recuento de tokens
        tokens_totales = 0
        # Diccionario para guardar los resultados
        textos_obtenidos = {}

        # Obtenemos el contenido del directorio de audios
        contenido = os.listdir(self.ruta_carpeta_audio)

        # Comprobamos que no está vacío el directorio
        if len(contenido) == 0:
            print("No hay audios que transcribir")
            return None

        # Transcribimos cada arhivo .mp4 y lo guardamos en el diccionario junto al título del vídeo
        for archivo in contenido:
            if archivo.endswith(".mp4"):
                print("Comenzando la transcripción de: {}".format(archivo))
                path = os.path.join(self.ruta_carpeta_audio, archivo)
                # Se genera la transcripción
                transcripcion = model.transcribe(path, language="es")["text"]
                # Se genera el resumen
                resumen = self.resumir_transcripciones(transcripcion)
                # Se guarda el nombre del vídeo con su transcripción resumida
                textos_obtenidos[id_video] = [archivo.replace(".mp4",""), resumen]
                count += 1
                # Se recalculan los tokens totales de las transcripciones
                tokens_totales += self.contar_tokens(resumen)
        
        # Creamos el directorio para guardar el archivo
        os.makedirs(ruta_transcripcion, exist_ok=True)
        # Guardamos el archivo
        self.guardar_resultado(str(textos_obtenidos), nombre_archivo)
        print("El resumen de la transcripción que se usará es de {} tokens".format(tokens_totales))
        return textos_obtenidos
    

    def leer_transcripciones(self, nombre_archivo):
        """Función para leer una transcripción ya existente"""
        # Se lee el contenido del archivo
        with open(nombre_archivo, "r", encoding="utf-8") as archivo:
            contenido = archivo.read()
        
        try:
            # Se convierte de nuevo a un diccionario
            contenido_dict = ast.literal_eval(contenido)
            return contenido_dict
        except:
            # Si falla devuelve None
            print("[ERROR] Ha habido un problema convirtiendo el contenido del archivo de transcripciones")
            return None


    def guardar_resultado(self,resultado, nombre_archivo):
        """Función para guardar el resultado en un archivo de texto"""
        # Se escribe el resultado en el archivo
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
                archivo.write(resultado)
    

    def restablecer_directorio(self):
        """Función para borrar el contenido del directorio de transcripciones de un partido político"""
        try:
            # Se elimina el directorio de transcripciones
            shutil.rmtree(self.ruta_carpeta)

            # Se vuelve a crear
            os.makedirs(self.ruta_carpeta)

            print("Se restableció el repositorio de transcripciones del partido")

        except OSError as e:
            print("[ERROR] No se pudo eliminar el directorio de transcripciones del partido")
            exit(-1)

    def resumir_transcripciones(self, transcripcion):
        """Función para generar resúmenes de un texto"""
        # Se cuentan los tokens de la transcripción
        tokens = self.contar_tokens(transcripcion)

        # Se calculan las frases que tiene la transcripción
        numero_frases = len(sent_tokenize(transcripcion))

        # Si la transcripción tiene 120 tokens o menos no se resume
        if tokens <= 120 or numero_frases <= 3:
            return transcripcion

        # Factor de reducción de tamaño (más agresivo con textos largos y menos con los cortos)
        factor_reduccion = min(0.60, 0.75 * (1-np.log(tokens/400)))

        # Se pone un mínimo posible en 0.2
        if factor_reduccion < 0.2:
            factor_reduccion = 0.2

        # Se modifica el factor cuando llega a menos de 0.5 para disminuir su decrecimiento
        # El tope mínimo acaba siendo 0.275
        if factor_reduccion < 0.5:
            # Cuanto más bajo es el factor más alto es el número que se resta
            factor_reduccion = 0.5 - 0.75 * (0.5 - factor_reduccion)

        # Cálculo de la longitud del resumen en frases
        longitud_resumen = int(max(3, ceil(numero_frases*factor_reduccion)))

        # Se genera el resumen
        parser = PlaintextParser.from_string(transcripcion, Tokenizer("spanish"))
        summarizer = LsaSummarizer()
        resumen = summarizer(parser.document, longitud_resumen)
        resultado = ' '.join([str(sentence) for sentence in resumen])
        
        # Se recalcula el número de tokens
        tokens = self.contar_tokens(resultado)

        # Bucle que sigue resumiendo hasta que el tamaño es menor o igual a 300 tokens si corresponde
        while tokens > 300:
            # Se recalculan las frases que tiene el resumen
            numero_frases = len(sent_tokenize(resultado))

            # Si ya se ha llegado al número mínimo de frases se corta el bucle
            if numero_frases == 3:
                break

            # Factor fijo de 0.75
            # Cálculo de la longitud del resumen
            longitud_resumen = int(max(3, ceil(numero_frases*0.75)))

            # Generación del nuevo resumen
            parser = PlaintextParser.from_string(resultado, Tokenizer("spanish"))
            summarizer = LsaSummarizer()
            resumen = summarizer(parser.document, longitud_resumen)
            resultado = ' '.join([str(sentence) for sentence in resumen])

            # Se recalcula el número de tokens
            tokens = self.contar_tokens(resultado)

        return resultado
    
    def contar_tokens(self, transcripcion):
        """Función para contar los tokens de una string"""
        # Se tokeniza la transcripción y se retorna su longitud
        tokenizada = nltk.word_tokenize(transcripcion)
        tokens = len(tokenizada)

        return tokens
