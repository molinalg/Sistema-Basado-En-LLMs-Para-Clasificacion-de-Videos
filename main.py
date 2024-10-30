### ---------------- Script para la creación y ejecución del bot y el proyecto general ----------------

# Librería para hacer logging
import logging

# Librería para variables de entorno
from dotenv import load_dotenv
import os

# Imports necesarios para manejar el bot
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters

# Importamos la app
from App.App import App

# Variables globales
lista_partidos = ["PSOE","PP","SUMAR","VOX"]
ods_info = {
    1: ["ODS 1", "Fin de la Pobreza"],
    2: ["ODS 2", "Hambre Cero"],
    3: ["ODS 3", "Salud y Bienestar"],
    4: ["ODS 4", "Educación de Calidad"],
    5: ["ODS 5", "Igualdad de Género"],
    6: ["ODS 6", "Agua Limpia y Saneamiento"],
    7: ["ODS 7", "Energía Asequible y No Contaminante"],
    8: ["ODS 8", "Trabajo Decente y Crecimiento Económico"],
    9: ["ODS 9", "Industria, Innovación e Infraestructura"],
    10: ["ODS 10", "Reducción de las Desigualdades"],
    11: ["ODS 11", "Ciudades y Comunidades Sostenibles"],
    12: ["ODS 12", "Producción y Consumo Responsables"],
    13: ["ODS 13", "Acción por el Clima"],
    14: ["ODS 14", "Vida Submarina"],
    15: ["ODS 15", "Vida de Ecosistemas Terrestres"],
    16: ["ODS 16", "Paz, Justicia e Instituciones Sólidas"],
    17: ["ODS 17", "Alianzas para Lograr los Objetivos"]
}

# Formateo de los mensajes log
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Configuración del logger para evitar excesivos mensajes de log
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# ---------------------------------- FUNCIONES PRINCIPALES DEL BOT ----------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envía un mensaje de bienvenida junto a las opciones de partidos disponibles."""
    nombre = update.message.from_user.first_name
    opciones = [
        [
            InlineKeyboardButton("PSOE", callback_data="PSOE"),
            InlineKeyboardButton("PP", callback_data="PP"),
            InlineKeyboardButton("SUMAR", callback_data="SUMAR"),
            InlineKeyboardButton("VOX", callback_data="VOX")
        ]
    ]
    await update.message.reply_text("¡Hola {}! 👋 Bienvenidx al sistema analizador de ODS.\n\nEstás a punto de averiguar cuánto le importan los ODS a los partidos políticos de España.\n\nPara ello, presiona el partido del que quieras generar el análisis aquí abajo:".format(nombre), reply_markup=InlineKeyboardMarkup(opciones))

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envía un mensaje junto a las opciones de partidos disponibles"""
    opciones = [
        [
            InlineKeyboardButton("PSOE", callback_data="PSOE"),
            InlineKeyboardButton("PP", callback_data="PP"),
            InlineKeyboardButton("SUMAR", callback_data="SUMAR"),
            InlineKeyboardButton("VOX", callback_data="VOX")
        ]
    ]
    
    # Se debe comprobar si el mensaje es una respuesta a otro mensaje o a uno propio de selección con botones
    if update.message:
        await update.message.reply_text("¿Con ganas de saber qué opina cada partido sobre los ODS? 🤔\n\nPresiona el partido del que quieras generar el análisis de entre las opciones de abajo:", reply_markup=InlineKeyboardMarkup(opciones))
    elif update.callback_query:
        await update.callback_query.message.reply_text("¿Con ganas de saber qué opina cada partido sobre los ODS? 🤔\n\nPresiona el partido del que quieras generar el análisis de entre las opciones de abajo:", reply_markup=InlineKeyboardMarkup(opciones))


async def menu_videos(update: Update, context: ContextTypes.DEFAULT_TYPE, videos, partido):
    """Envía un mensaje junto a las opciones de vídeos disponibles"""
    if len(videos) != 0:
        # Se inicia el mensaje que se va a enviar
        mensaje = "Se ha revisado el canal de YouTube del partido político y se han encontrado los siguientes vídeos recientes que pueden ser analizados:\n\n"

        # Se añaden los videos que corresponde
        count = 0
        lista_titulos = []
        for id_video, titulo in videos.items():
            count += 1
            def_msg = "{numero}: {titulo}\n".format(numero=count, titulo=titulo)
            mensaje += def_msg
            lista_titulos.append(titulo)
        
        # Se termina el mensaje
        final_msg = "\n🔽 Selecciona un vídeo para el análisis 🔽" 
        mensaje += final_msg

        # Creamos el menú de opciones con los ids
        opciones = [[]]
        if len(videos) > 5:
            opciones.append([])

        lista_ids = list(videos.keys())

        for i in range(1, count+1):
            # Telegram prohibe generar filas de más de 8 botones por lo que se dividirán en 2 filas
            if i <= 5:
                opciones[0].append(InlineKeyboardButton(str(i), callback_data="{partido}.{id_video}.{video}".format(partido=partido, id_video=lista_ids[i-1], video=i)))
            else:
                opciones[1].append(InlineKeyboardButton(str(i), callback_data="{partido}.{id_video}.{video}".format(partido=partido, id_video=lista_ids[i-1], video=i)))

        # Añadimos el botón de cancelar
        opciones.append([InlineKeyboardButton("Cancelar", callback_data="Cancelar")])

        await update.callback_query.message.reply_text(mensaje, reply_markup=InlineKeyboardMarkup(opciones))
    else:
       # Si no se encuentra ningun video se pide probar con otro partido
       opciones = [
            [
                InlineKeyboardButton("PSOE", callback_data="PSOE"),
                InlineKeyboardButton("PP", callback_data="PP"),
                InlineKeyboardButton("SUMAR", callback_data="SUMAR"),
                InlineKeyboardButton("VOX", callback_data="VOX")
            ]
        ]
       
       await update.callback_query.message.reply_text("Tras revisar el canal de YouTube del partido político, no se ha podido encontrar ningun vídeo apropiado para el análisis. 😥\n\nPrueba con otro partido:", reply_markup=InlineKeyboardMarkup(opciones)) 


async def menu_ods(update: Update, context: ContextTypes.DEFAULT_TYPE, ods, partido, id_video):
    """Envía un mensaje junto a las opciones de ODS disponibles"""
    # Se separan los ODS que han sido detectados
    ods_validos = {}
    for ods_id, datos in ods.items():
        if datos[0]:
            ods_validos[ods_id] = datos

    # Si se ha detectado alguno se continúa, si no se termina el proceso
    if len(ods_validos) != 0:
        # Se inicia el mensaje que se va a enviar
        mensaje = "Tras analizar las últimas declaraciones del partido político, se han relacionado con un total de {} ODS:\n\n".format(len(ods_validos))

        # Se añaden los ODS que corresponde
        for ods_id, datos in ods_validos.items():
            def_msg = "- {ODS}: {titulo}\n".format(ODS = ods_id, titulo = ods_info[int(ods_id.split()[1])][1])
            mensaje += def_msg
        
        # Se termina el mensaje
        final_msg = "\n🔽 Selecciona el número del ODS que quieras saber más 🔽"
        mensaje += final_msg

        # Creamos el menú de opciones con los ids
        opciones = [[]]
        if len(ods_validos) > 8:
            opciones.append([])
        if len(ods_validos) > 16:
            opciones.append([])
        
        count = 1
        for ods_id, datos in ods_validos.items():
            if count <= 8:
                opciones[0].append(InlineKeyboardButton(ods_id.split()[1], callback_data="{partido}.{ods}.{id_video}".format(partido=partido, ods=ods_id, id_video=id_video)))
            elif count > 8 and count <= 16:
                opciones[1].append(InlineKeyboardButton(ods_id.split()[1], callback_data="{partido}.{ods}.{id_video}".format(partido=partido, ods=ods_id, id_video=id_video)))
            else:
                opciones[2].append(InlineKeyboardButton(ods_id.split()[1], callback_data="{partido}.{ods}.{id_video}".format(partido=partido, ods=ods_id, id_video=id_video)))
            count += 1
        
        # Añadimos el botón de cancelar
        opciones.append([InlineKeyboardButton("Cancelar", callback_data="Cancelar")])

        await update.callback_query.message.reply_text(mensaje, reply_markup=InlineKeyboardMarkup(opciones))
    else:
       # Si no se encuentra ningun ODS se pide probar con otro partido
       opciones = [
            [
                InlineKeyboardButton("PSOE", callback_data="PSOE"),
                InlineKeyboardButton("PP", callback_data="PP"),
                InlineKeyboardButton("SUMAR", callback_data="SUMAR"),
                InlineKeyboardButton("VOX", callback_data="VOX")
            ]
        ]
       
       await update.callback_query.message.reply_text("Tras analizar el vídeo, no se ha encontrado ninguna relación con los ODS. 😥\n\nPrueba con otro análisis:", reply_markup=InlineKeyboardMarkup(opciones)) 


async def devolver_analisis_ods(update: Update, context: ContextTypes.DEFAULT_TYPE, partido, ods, id_video):
    """Envía el análisis de un ODS sobre un vídeo"""
    # Se recibe el JSON de resultados
    resultados = analizador.devolver_analisis_ods(partido, id_video)
    if resultados is None:
        await error(update, context)
    else:
        # Se extrae el ODS en concreto
        contenido = resultados[ods][1]
        # Se crea el mensaje a enviar y se envía
        mensaje = contenido.replace("PRTPLTC", partido)
        mensaje_final = "➖Análisis del {}:\n\n".format(ods) + mensaje.replace(" Recientemente", "\n\nRecientemente", 1)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=mensaje_final)

    # Finalmente se envía de nuevo el menú principal
    await menu_ods(update, context, resultados, partido, id_video)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Controla el uso de las opciones del InlineKeyboardMarkup"""
    # Obtenemos la información de los botones
    query = update.callback_query

    # Obtenemos la respuesta presionada
    await query.answer()

    # Se analiza la respuesta para saber si se está recibiendo una solicitud de partido, de vídeo o de ODS
    if query.data in lista_partidos:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Examinando el partido {} en busca de vídeos disponibles...\n\nATENCIÓN: Esta operación puede tardar ⏳".format(query.data))
        await generar_videos(update,context,str(query.data))

    elif query.data == "Cancelar":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Operación cancelada ❌")
        await menu(update, context)

    else:
        # Se separan las dos partes de la información
        partido = str(query.data).split(".")[0]
        dato = str(query.data).split(".")[1]
        # Creamos una lista con los posibles ODS
        ods_ids = [lista[0] for lista in ods_info.values()]
        # Se diferencia entre análisis ya generados y no generados
        if dato not in ods_ids:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Generando el análisis de ODS del partido {partido} en torno al vídeo {video}...\n\nATENCIÓN: Esta operación puede tardar ⏳".format(partido=partido, video=str(query.data).split(".")[2]))
            await generar_analisis_ods(update,context,[partido,dato])
        else:
            await devolver_analisis_ods(update, context, partido, dato, str(query.data).split(".")[2])


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manda un mensaje de error si algo falla"""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Algo ha salido mal durante el proceso. 😓\n\n ¿Te importaría probar con otra opción?")
    await menu(update, context)

# ---------------------------------- FUNCIONES INTERNAS ----------------------------------

async def generar_videos(update: Update, context: ContextTypes.DEFAULT_TYPE,partido):
    """Recibe una lista de vídeos disponibles para el análisis"""
    # Obtenemos los vídeos
    videos = analizador.generar_videos(partido)

    # Generamos el menú de selección de vídeos
    await menu_videos(update, context, videos, partido)


async def generar_analisis_ods(update: Update, context: ContextTypes.DEFAULT_TYPE,datos):
    """Llama a la App para obtener un análisis del ODS para el partido requerido"""
    # Obtenemos el análisis
    resultado = analizador.generar_analisis_ods(datos[0],datos[1])
    
    if resultado == None:
        # Se lanza un error si no se ha recibido nada
        await error(update, context)
    else:
        # Se genera el selector de ods
        await menu_ods(update, context, resultado, datos[0], datos[1])

    
# ---------------------------------- MAIN ----------------------------------

if __name__ == '__main__':
    # Se introducen las variables de entorno y se carga el token del bot
    load_dotenv("secrets.env")
    token = os.environ.get("TOKEN")
    # Creacion de la instancia de App
    analizador = App()
    # Creación de la aplicación
    application = Application.builder().token(token).build()

    # Handlers para cada comando
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), menu))
    application.add_handler(MessageHandler(filters.COMMAND, menu))

    # Poner en funcionamiento el bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)