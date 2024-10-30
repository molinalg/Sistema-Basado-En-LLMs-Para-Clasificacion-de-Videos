### ---------------- Clase Video_Downloader encargada de descargar los vídeos recientes de YouTube de un partido político ----------------

# Librerías de uso general
import os, shutil
# Pytube, librería que nos permite descargar vídeos de Youtube
from pytube import YouTube
# Googleapiclient, librería que nos permite interactuar con la API de Youtube manejando las solicitudes HTTP
from googleapiclient.discovery import build
# Datetime, librería que nos permite trabajar con fechas y horas
from datetime import datetime, timedelta


class Video_Downloader:
    """Clase para descargar los vídeos recientes de un partido político"""
    def __init__(self, api_key, id_canal, dias, ruta_carpeta, max_videos):
        # Clave de la API de YouTube
        self.api_key = api_key
        # ID del canal del que se van a descargar los vídeos
        self.id_canal = id_canal
        # Días en el pasado que se considerarán para la descarga de vídeos
        self.dias = dias
        # Ruta a la carpeta de vídeos del partido
        self.ruta_actual = os.getcwd()
        self.ruta_carpeta = os.path.join(self.ruta_actual, ruta_carpeta)
        # Máximo de vídeos permitidos para la descarga
        self.max_videos = max_videos
        # Diccionario para almacenar los datos de los vídeos descargados
        self.videos_descargados = {}


    def descargar_videos(self,ultimo_id):
        """Función para descargar los vídeos de un canal dado su ID"""
        # Creación de la instancia de la API de Youtube
        youtube = build('youtube', 'v3', developerKey=self.api_key)

        # Se obtiene el id del último video subido al canal
        id_video = self.obtener_id(youtube)
        # Se compara con el último id guardado de los videos descargados
        if id_video == ultimo_id:
            print("El sistema ya cuenta con todos los vídeos necesarios, se omite la descarga")
            # Se genera el diccionario de vídeos para devolverlo con el id
            self.generar_lista_videos()
            return [id_video, self.videos_descargados]

        # Se limpia el directorio de audios
        self.restablecer_directorio()

        # Se obtiene la lista de vídeos subidos en los últimos días
        lista_subidos = self.generar_subidos(youtube)

        # El JSON solo contiene la id de la lista, debemos hacer una nueva solicitud para obtener los vídeos
        # La API de Youtube solo permite obtener un máximo de 50 vídeos por solicitud por lo que debemos paginar
        # Para ello se utilizará el nextPageToken que se obtiene en la respuesta de la solicitud
        next_page_token = None

        # Bucle para obtener todos los vídeos
        finish = False
        while not finish:
            # Realizamos la solicitud
            # Se pide el snippet que incluye el ID de cada vídeo y la fecha de publicación
            # También se incluye el nextPageToken para paginar y el máximo de resultados por página permitido
            videos_subidos = youtube.playlistItems().list(
                part = 'snippet',
                pageToken = next_page_token,
                maxResults = 50,
                playlistId = lista_subidos
            ).execute()

            # Se crea el enlace a cada vídeo obtenido a partir del ID de cada uno presente en el JSON
            for video in videos_subidos['items']:
                # Si se han descargado ya el máximo número de vídeos se para el proceso
                if len(self.videos_descargados) == self.max_videos:
                    break  
                # Se obtiene la fecha de publicación del vídeo
                fecha_publicacion = video['snippet']['publishedAt']
                # Convertir desde el formato ISO 8601 a un objeto datetime
                fecha_publicacion = datetime.fromisoformat(fecha_publicacion[:-1])
                # Se obtiene la fecha hace x días (el parámetro recibido)
                fecha_limite = datetime.now() - timedelta(days=self.dias)
                # Se obtiene el enlace solo si la fecha es igual o posterior a la fecha límite
                if fecha_publicacion >= fecha_limite and fecha_publicacion <= datetime.now():
                    self.obtener_video(video['snippet']['resourceId']['videoId'], youtube)
            
            # Si se han descargado ya el máximo número de vídeos se para el proceso
            if len(self.videos_descargados) == self.max_videos:
                break
            
            # Se extrae el nextPageToken de la respuesta para paginar
            next_page_token = videos_subidos.get('nextPageToken')
            # Si no hay más páginas, se termina el bucle
            if next_page_token == None:
                finish = True
                
        # Se actualiza el id del último video descargado
        return [id_video, self.videos_descargados]


    def generar_subidos(self,youtube):
        """Función para devolver la lista de vídeos subidos por un canal"""
        # Se obtiene la información del canal con el que se quiere trabajar
        # El contenido pedido es el detalle del canal, que incluye la lista de reproducción de los vídeos subidos
        canal = youtube.channels().list(
            part = 'contentDetails',
            id = self.id_canal
        ).execute()

        # A partir del JSON que se obtiene como respuesta, se obtiene una lista con los vídeos subidos
        lista_subidos = canal['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        return lista_subidos


    def obtener_id(self,youtube):
        """Función para otener el id del último vídeo subido por un canal"""
        # Se obtiene la lista de vídeos subidos en los últimos días
        lista_subidos = self.generar_subidos(youtube)

        # Se obtiene el último vídeo subido
        # Se pide el snippet que incluye el ID de cada vídeo
        videos_subidos = youtube.playlistItems().list(
            part = 'snippet',
            maxResults = 1,
            playlistId = lista_subidos
        ).execute()

        # Se devuelve el ID del último vídeo
        return videos_subidos['items'][0]['snippet']['resourceId']['videoId']


    def obtener_video(self, id, youtube):
        """Función para comprobar la validez de un vídeo y descargarlo de ser válido"""
        # Se obtiene la información del video
        video = youtube.videos().list(
            part = 'contentDetails',
            id = id
        ).execute()

        # Se obtiene la duración del video en segundos
        duracion_video = video['items'][0]['contentDetails']['duration']

        # Se descartan los vídeos que duran horas o días
        if "D" in duracion_video or "H" in duracion_video:
            print("Se ha descartado un video por duración sospechosa o excesiva ({})".format(duracion_video))
        else:
            # Se convierte la duración a minutos escogiendo lo de la izquierda de la M 
            duracion_minutos = duracion_video.split('M')[0]
            # Si no había minutos el video solo dura unos segundos y no se puede descargar
            if "S" in duracion_minutos:
                duracion_minutos = 0
            else:
                # Se extrae la duración en minutos de la string
                duracion_minutos = int(duracion_minutos.replace("PT",""))

            # Se descargan aquellos vídeos que duren entre 1 minuto (incluido) y 8 (no incluido)
            if duracion_minutos < 8 and duracion_minutos > 0:
                # Se genera un directorio cuyo nombre es el id del video
                ruta_video = os.path.join(self.ruta_carpeta, "{}".format(id))
                os.makedirs(ruta_video, exist_ok=True)

                # Se cambia la ruta para la descarga
                os.chdir(ruta_video)

                # Generamos el link
                link = "https://www.youtube.com/watch?v={}".format(id)
                
                # Se carga el vídeo
                video = YouTube(link)

                # Debido a la inestabilidad de pytube, se reintentará la descarga si esta falla
                for i in range(3):
                    try:
                        # La librería no permite descargar videos de más de 720p con audio.
                        # Se descarga el audio en su lugar (de paso se ahorra espacio en disco)
                        stream = video.streams.filter(file_extension="mp4").filter(only_audio=True).last()

                        print("Descargando un vídeo...")
                        stream.download()
                        print("Descarga completada")

                        # Obtenemos el título del vídeo y se guarda en el diccionario
                        video = youtube.videos().list(
                            part = 'snippet',
                            id = id
                        ).execute()

                        titulo = video['items'][0]['snippet']['title']
                        self.videos_descargados[id] = titulo
                        break
                    except Exception as e:
                        print("Ha surgido un error en la descarga: {}".format(e))

                # Se restablece la ruta
                os.chdir(self.ruta_actual)

    
    def restablecer_directorio(self):
        """Función que elimina el contenido de la carpeta de audios de un partido en concreto"""
        try:
            # Se elimina el directorio de audios
            shutil.rmtree(self.ruta_carpeta)

            # Se vuelve a crear
            os.makedirs(self.ruta_carpeta)

            print("Se restableció el repositorio de audios del partido")

        except OSError as e:
            print("[ERROR] No se pudo eliminar el directorio de audios del partido")
            exit(-1)
    
    def generar_lista_videos(self):
        """Función que rellena el diccionario de vídeos cuando no se descargan de nuevo"""
        # Iteramos por la carpeta
        for directorio, dir_videos, archivos in os.walk(self.ruta_carpeta):
            # Iteramos por carpeta de vídeo
            for dir in dir_videos:
                videos = os.listdir(os.path.join(directorio, dir))
                # Obtenemos el primer archivo .mp4 en el subdirectorio (solo debería haber uno)
                for video in videos:
                    if video.endswith(".mp4"):
                        audio = video.replace(".mp4", "")
                        self.videos_descargados[dir] = audio
                        break
