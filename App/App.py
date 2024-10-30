### ---------------- Clase App encargada de cohesionar todas las demás clases y hacer que funcionen juntas ----------------

# Script para descargar los vídeos de un canal
from .video_downloader import Video_Downloader
# Script para pasar los audios a texto
from .extractor_texto import Extractor_Texto
# Script para generar el análisis de los ODS
from .analizador_llama import Analizador_Llama
# Librería para variables de entorno
from dotenv import load_dotenv
# Librería para el modelo de transcripciones
import whisper
# Librerías de uso general
import os, json

class App:
    """Clase para controlar las demás clases del proyecto"""
    # Ruta a la carpeta para audio
    ruta_audio = "audio"
    # Ruta a la carpeta para transcripciones
    ruta_transcripcion = "transcripciones"
    # Ruta a la carpeta para resultados
    ruta_resultado = "resultados"
    # Clave de la API de Youtube
    load_dotenv("secrets.env")
    api_key = os.getenv("API")
    # Diccionario para almacenar el contenido final
    textos_obtenidos = {}
    # Ids de los canales de YouTube de los partidos políticos
    ids_canales = {"PSOE": "UCB75fTm3weGTmtnitiZcdBw","PP": "UCPECDsPyGRW5b5E4ibCGhww","SUMAR":"UCEg-oyYjgbOL0NG5qjtuRFA","VOX": "UCRvpumrJs0qY1xLzeU0Ss1Q"}
    # Ids de los últimos vídeos descargados de cada partido
    ids_videos = {"PSOE": None,"PP": None,"SUMAR":None,"VOX": None}
    # Número de días atrás de los que descargar vídeos
    dias = 61
    # Número máximo de vídeos a descargar
    max_videos = 10
    # Variable que se usa para controlar si los directorios de transcripciones y de resultados deben reiniciarse
    restablecer = False

    def __init__(self):
        # Creamos la instancia del analizador
        self.analizador = Analizador_Llama(self.ruta_resultado)
        # Cargamos el modelo Whisper
        self.whisper = whisper.load_model("large")
    
    def generar_videos(self, canal):
        """Función para descargar los vídeos del partido y devolver la lista de títulos"""
        # Generamos parte del path al audio del partido
        ruta_carpeta_audio = os.path.join(self.ruta_audio, canal)

        # Creamos una instancia de la clase que descarga los audios
        video_downloader = Video_Downloader(self.api_key, self.ids_canales[canal], self.dias, ruta_carpeta_audio, self.max_videos)

        # Llamamos a la función para descargar los audios
        print("Descargando videos...")
        datos_recibidos = video_downloader.descargar_videos(self.ids_videos[canal])

        # Se comprueba si el directorio de audios se ha restablecido para restablecer el resto también
        if self.ids_videos[canal] != datos_recibidos[0]:
            self.restablecer = True
        else:
            self.restablecer = False

        # Se actualiza el id del último vídeo descargado
        self.ids_videos[canal] = datos_recibidos[0]

        print("Descarga de vídeos completada")

        return datos_recibidos[1]

    
    def generar_analisis_ods(self, canal, id_video):
        """Función que se encarga de generar la transcripción y análisis de un vídeo"""
        # Generamos parte del path a las transcripciones del partido
        ruta_carpeta_transcripcion = os.path.join(self.ruta_transcripcion, canal)

        # Generamos parte del path al audio del partido
        ruta_carpeta_audio = os.path.join(self.ruta_audio, canal)
        # Completamos el path con el vídeo elegido
        ruta_audio = os.path.join(ruta_carpeta_audio, id_video)

        # Creamos instancia de la clase que pasa los audios a texto
        print("Generando transcripciones...")
        extractor_texto = Extractor_Texto(ruta_carpeta_transcripcion, canal, ruta_audio)

        # Llamamos a la función para la transformación
        texto_obtenido = extractor_texto.extraer_contenido(self.restablecer, self.whisper, id_video)

        # Si ha habido un error se devuelve None
        if texto_obtenido is None:
            return None
        
        print("Transcripción generada")

        # Se llama al script que genera el análisis con Llama 3 y devolvemos el resultado
        print("Generando el análisis de ODS")
        resultado = self.analizador.generar_analisis_ods(canal, texto_obtenido, self.restablecer, id_video)
        print("Análisis generado")

        # Se vuelve a poner restablecer en false si procede
        if self.restablecer:
            self.restablecer = False

        return resultado

    def devolver_analisis_ods(self, partido, id_video):
        """Función para leer análisis ya creados de un vídeo en concreto"""
        # Generamos la ruta al archivo
        ruta_archivo = os.path.join(os.getcwd(), self.ruta_resultado, partido, id_video, "Resultados-{partido}-{id_video}.txt".format(partido=partido, id_video=id_video))

        # Leemos el archivo y lo convertimos a un diccionario para devolverlo
        try:
            with open(ruta_archivo, "r", encoding="utf-8") as archivo:
                contenido = archivo.read()
            
            diccionario_resultados = json.loads(contenido)
            return diccionario_resultados
        
        except:
            print("[ERROR] Ha habido un error obteniendo el JSON de resultados")
            return None

    