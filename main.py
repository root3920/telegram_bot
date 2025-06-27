import base64
import re
import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, ContextTypes, filters
)
from dotenv import load_dotenv
import os

load_dotenv()

# Importa funciones y variables de tus módulos
from handlers.commands import start_command, canales_command
from handlers.conversation import (
    seleccionar_curso, recibir_correo, verificar_codigo,
    confirmar_nuevo_correo, cancel
)
from utils.state import (
    ASK_EMAIL, ASK_CODIGO, ASK_EMAIL_CONFIRMACION,
    codigo_temp, curso_seleccionado, intentos_codigo, MENSAJES_FINAL
)
from services.hotmart import verificar_compra_hotmart
from services.active_campaign import asignar_etiqueta, agregar_a_automatizacion

# Carga variables de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ACTIVE_CAMPAIGN_API_URL = os.getenv("ACTIVE_CAMPAIGN_API_URL")
ACTIVE_CAMPAIGN_API_TOKEN = os.getenv("ACTIVE_CAMPAIGN_API_TOKEN")
CODIGO_CAMPO_ID = os.getenv("CODIGO_CAMPO_ID")
TAG_ID = os.getenv("TAG_ID")
AUTOMATION_ID = int(os.getenv("AUTOMATION_ID"))
HOTMART_CLIENT_ID = os.getenv("HOTMART_CLIENT_ID")
HOTMART_CLIENT_SECRET = os.getenv("HOTMART_CLIENT_SECRET")

# Inicializa aplicación
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Define ConversationHandler con estados y handlers
conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(seleccionar_curso)],
    states={
        ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_correo)],
        ASK_CODIGO: [MessageHandler(filters.TEXT & ~filters.COMMAND, verificar_codigo)],
        ASK_EMAIL_CONFIRMACION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmar_nuevo_correo)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

# Agrega los manejadores al bot
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("canales", canales_command))
application.add_handler(conv_handler)

# Maneja mensajes fuera del flujo principal
async def mensaje_fuera_de_flujo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Usa el comando /canales para comenzar de nuevo.")

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_fuera_de_flujo))

# Ejecuta el bot
application.run_polling()