# Se importa la librería para hacer unit tests
import unittest
# Librería para variables de entorno
from dotenv import load_dotenv
import os
# Se importan los módulos desarrollados
from App.App import App
from App.video_downloader import Video_Downloader
from App.extractor_texto import Extractor_Texto
from App.analizador_llama import Analizador_Llama

class Unit_Tests(unittest.TestCase):
    """Clase para realizar unit tests de algunas de las funciones desarrolladas en los diferentes módulos"""

    @classmethod
    def setUpClass(self):
        """Función que se ejecuta antes de los tests"""
        # Ruta a la carpeta para audio
        ruta_audio = "testing/audio_test"
        ruta_completa_audio_correcta = os.path.join(ruta_audio,"PSOE")
        ruta_completa_audio_vacia = os.path.join(ruta_audio,"SUMAR")
        ruta_completa_audio_incorrecta = os.path.join(ruta_audio,"NO_EXISTE")
        # Ruta a la carpeta para transcripciones
        ruta_transcripcion = "testing/transcripciones_test"
        # Ruta a la carpeta para resultados
        ruta_resultado = "testing/resultados_test"
        # Clave de la API de Youtube
        load_dotenv("secrets.env")
        api_key = os.getenv("YOUTUBE_API_KEY")
        # Ids de los canales de YouTube de los partidos políticos
        ids_canales = {"PSOE": "UCB75fTm3weGTmtnitiZcdBw","PP": "UCPECDsPyGRW5b5E4ibCGhww","SUMAR":"UCEg-oyYjgbOL0NG5qjtuRFA","VOX": "UCRvpumrJs0qY1xLzeU0Ss1Q"}

        # Se crean las instancias de los módulos
        self.video_downloader_correcto = Video_Downloader(api_key,ids_canales["PSOE"],61,ruta_completa_audio_correcta,10)
        self.video_downloader_vacio = Video_Downloader(api_key,ids_canales["SUMAR"],61,ruta_completa_audio_vacia,10)
        self.video_downloader_incorrecto = Video_Downloader(api_key,ids_canales["PSOE"],61,ruta_completa_audio_incorrecta,10)

        self.extractor_texto = Extractor_Texto(ruta_transcripcion,"PSOE",ruta_audio)

        self.analizador_llama = Analizador_Llama(ruta_resultado)


    def test_V1(self):
        # Se pide la lista de vídeos habiendo 2 descargados
        self.video_downloader_correcto.generar_lista_videos()
        resultado = self.video_downloader_correcto.videos_descargados
        resultado_esperado = {"6wVumYewhbU":"Declaraciones de María Jesús Montero","yBD7s66KRoU":"PSOE  Conoce a Yai Machine"}
        self.assertEqual(resultado, resultado_esperado, "El resultado no coincide con el esperado")

    def test_V2(self):
        # Se pide la lista de vídeos estando vacía la carpeta
        self.video_downloader_vacio.generar_lista_videos()
        resultado = self.video_downloader_vacio.videos_descargados
        resultado_esperado = {}
        self.assertEqual(resultado, resultado_esperado, "El resultado no coincide con el esperado")

    def test_NV1(self):
        # Se pide la lista de vídeos con una carpeta incorrecta
        self.video_downloader_incorrecto.generar_lista_videos()
        resultado = self.video_downloader_incorrecto.videos_descargados
        resultado_esperado = {}
        self.assertEqual(resultado, resultado_esperado, "El resultado no coincide con el esperado")

    
    def test_V3(self):
        # Se lee un archivo de transcripciones válido
        nombre_archivo = os.path.join(os.getcwd(), "testing", "transcripciones_test", "PSOE", "fmZ8CbTwd88", "Transcripciones-PSOE-fmZ8CbTwd88.txt")
        resultado = self.extractor_texto.leer_transcripciones(nombre_archivo)
        resultado_esperado = {'fmZ8CbTwd88': ['Vídeo de prueba', 'Esto es una transcripción de prueba']}
        self.assertEqual(resultado, resultado_esperado, "El resultado no coincide con el esperado")
    
    def test_NV2(self):
        # Se lee un archivo de transcripciones con contenido de formato diferente al esperado
        nombre_archivo = os.path.join(os.getcwd(), "testing", "transcripciones_test", "PSOE", "LQ35fbllIRM", "Transcripciones-PSOE-LQ35fbllIRM.txt")
        resultado = self.extractor_texto.leer_transcripciones(nombre_archivo)    
        resultado_esperado = None
        self.assertEqual(resultado, resultado_esperado, "El resultado no coincide con el esperado")

    def test_V4(self):
        # Se valida un JSON válido
        json_input = '{"Tema presente en el texto": false, "Explicación": "No presente"}'
        resultado = self.analizador_llama.validar_resultado(json_input)
        resultado_esperado = True
        self.assertEqual(resultado, resultado_esperado, "El resultado no coincide con el esperado")

    def test_NV3(self):
        # Se valida una string que no es formato JSON
        json_input = '{"Tema presente en el texto": false, "Explicación": "No presente"'
        resultado = self.analizador_llama.validar_resultado(json_input)
        resultado_esperado = False
        self.assertEqual(resultado, resultado_esperado, "El resultado no coincide con el esperado")

    def test_NV4(self):
        # Se valida un JSON que no tiene un booleano en la primera clave
        json_input = '{"Tema presente en el texto": "prueba", "Explicación": "No presente"}'
        resultado = self.analizador_llama.validar_resultado(json_input)
        resultado_esperado = False
        self.assertEqual(resultado, resultado_esperado, "El resultado no coincide con el esperado")

    def test_NV5(self):
        # Se valida un JSON que no tiene una cadena en la segunda clave
        json_input = '{"Tema presente en el texto": false, "Explicación": 1}'
        resultado = self.analizador_llama.validar_resultado(json_input)
        resultado_esperado = False
        self.assertEqual(resultado, resultado_esperado, "El resultado no coincide con el esperado")

    def test_NV6(self):
        # Se valida un JSON que tiene una clave extra
        json_input = '{"Tema presente en el texto": false, "Explicación": "No presente", "Detectado": "Sí"}'
        resultado = self.analizador_llama.validar_resultado(json_input)
        resultado_esperado = False
        self.assertEqual(resultado, resultado_esperado, "El resultado no coincide con el esperado")

    def test_NV7(self):
        # Se valida un JSON que solo tiene una de las claves
        json_input = '{"Explicación": "No presente"}'
        resultado = self.analizador_llama.validar_resultado(json_input)
        resultado_esperado = False
        self.assertEqual(resultado, resultado_esperado, "El resultado no coincide con el esperado")

    def test_NV8(self):
        # Se valida un JSON que tiene una clave diferente
        json_input = '{"Tema presente en el texto": false, "Explicación del texto": "No presente"}'
        resultado = self.analizador_llama.validar_resultado(json_input)
        resultado_esperado = False
        self.assertEqual(resultado, resultado_esperado, "El resultado no coincide con el esperado")

    def test_V5(self):
        # Se lee un archivo de resultados válido
        nombre_archivo = os.path.join(os.getcwd(), "testing", "resultados_test", "PSOE", "fmZ8CbTwd88", "Resultados-PSOE-fmZ8CbTwd88.txt")
        resultado = self.analizador_llama.leer_resultados(nombre_archivo) 
        resultado_esperado = {"ODS 1": [False, "No presente"], "ODS 2": [False, "No presente"], "ODS 3": [False, "No presente"], "ODS 4": [False, "No presente"], "ODS 5": [False, "No presente"], "ODS 6": [False, "No presente"], "ODS 7": [False, "No presente"], "ODS 8": [False, "No presente"], "ODS 9": [False, "No presente"], "ODS 10": [False, "No presente"], "ODS 11": [False, "No presente"], "ODS 12": [False, "No presente"], "ODS 13": [False, "No presente"], "ODS 14": [False, "No presente"], "ODS 15": [False, "No presente"], "ODS 16": [False, "No presente"], "ODS 17": [False, "No presente"]}
        self.assertEqual(resultado, resultado_esperado, "El resultado no coincide con el esperado")

    def test_NV9(self):
        # Se lee un archivo de resultados con contenido de formato diferente al esperado
        nombre_archivo = os.path.join(os.getcwd(), "testing", "resultados_test", "PSOE", "LQ35fbllIRM", "Resultados-PSOE-LQ35fbllIRM.txt")
        resultado = self.analizador_llama.leer_resultados(nombre_archivo) 
        resultado_esperado = None
        self.assertEqual(resultado, resultado_esperado, "El resultado no coincide con el esperado")


if __name__ == '__main__':
    unittest.main()
