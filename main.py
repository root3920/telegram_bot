import os
import random
import re
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, ContextTypes, filters
)

# === CARGAR VARIABLES DE ENTORNO ===
load_dotenv()

# === CONFIGURACIÓN ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ACTIVE_CAMPAIGN_API_URL = os.getenv("ACTIVE_CAMPAIGN_API_URL")
ACTIVE_CAMPAIGN_API_TOKEN = os.getenv("ACTIVE_CAMPAIGN_API_TOKEN")
CODIGO_CAMPO_ID = os.getenv("CODIGO_CAMPO_ID")
TAG_ID = os.getenv("TAG_ID")
AUTOMATION_ID = int(os.getenv("AUTOMATION_ID"))

# === ESTADOS DE CONVERSACIÓN ===
ASK_EMAIL, ASK_CODIGO, ASK_EMAIL_CONFIRMACION = range(3)

# === VARIABLES TEMPORALES ===
codigo_temp = {}
curso_seleccionado = {}
intentos_codigo = {}

# === MENSAJES PERSONALIZADOS POR CURSO (si no hay submenú) ===
MENSAJES_FINAL = {
    "curso_mente": (
        "✅ Acceso otorgado a Membresía Mente Cuántica.\n"
        "Ingresa con este enlace:\n"
        "https://t.me/+nK7IjKHXsHw3NzIx"
    ),
    "curso_diplomatura": (
        "✅ Acceso otorgado a Diplomatura QM-M.\n"
        "Ingresa con este enlace:\n"
        "https://t.me/+6d8N1Si4N0EwMTMx"
    ),
    "curso_avanzadas": (
        "✅ Acceso otorgado a Clases Avanzadas.\n"
        "Ingresa con este enlace:\n"
        "https://t.me/+Pdkdc4Jc2Zo3OThh"
    )
}

# === FUNCIONES ACTIVE CAMPAIGN ===

def asignar_etiqueta(contact_id, tag_id):
    url = f"{ACTIVE_CAMPAIGN_API_URL}/api/3/contactTags"
    headers = {
        "Api-Token": ACTIVE_CAMPAIGN_API_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {"contactTag": {"contact": contact_id, "tag": tag_id}}
    response = requests.post(url, headers=headers, json=payload)
    print("🏷️ Asignando etiqueta:", response.status_code, response.text)

def agregar_a_automatizacion(contact_id, automation_id=AUTOMATION_ID):
    url = f"{ACTIVE_CAMPAIGN_API_URL}/api/3/contactAutomations"
    headers = {
        "Api-Token": ACTIVE_CAMPAIGN_API_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "contactAutomation": {
            "contact": str(contact_id),
            "automation": str(automation_id)
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    print("📩 Agregando a automatización:", response.status_code, response.text)

# === COMANDO /start ===
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Escribe /canales para ingresar a tu grupo de Telegram."
    )

# === COMANDO /canales ===
async def canales_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Membresía Mente Cuántica", callback_data="curso_mente")],
        [InlineKeyboardButton("Método Googlear al Inconsciente (#25)", callback_data="curso_googlear")],
        [InlineKeyboardButton("Especialización Guerreros Galácticos", callback_data="curso_guerreros")],
        [InlineKeyboardButton("Clases Avanzadas", callback_data="curso_avanzadas")],
        [InlineKeyboardButton("Formación QMM 360", callback_data="curso_qmm360")],
        [InlineKeyboardButton("Diplomatura QM-M", callback_data="curso_diplomatura")],
        [InlineKeyboardButton("Las 8 Herramientas", callback_data="curso_herramientas")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Selecciona el curso para ingresar al canal de Telegram:", reply_markup=reply_markup
    )

# === MENÚS PERSONALIZADOS POR CURSO ===

async def seleccionar_grupo_herramientas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Las 8 Herramientas (#27)", url="https://t.me/+kdclZgGhr5JhMTkx")],
        [InlineKeyboardButton("Las 8 Herramientas (#28)", url="https://t.me/+tFJ3rECCPuAxMTAx")],
        [InlineKeyboardButton("Las 8 Herramientas (#29)", url="https://t.me/+SRSGg3cA8wVkOWNh")],
        [InlineKeyboardButton("Las 8 Herramientas (#30)", url="https://t.me/+t3l__l5gEbk0ZWIx")],
        [InlineKeyboardButton("Las 8 Herramientas (#31)", url="https://t.me/+eJF-LF5Mq8AwNDMx")]
    ]
    await update.message.reply_text(
        "🎯 Escoge el grupo de 8 Herramientas al que perteneces:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END

async def seleccionar_grupo_googlear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Googlear al Inconsciente (#23)", url="https://t.me/+NwqLxwUDpKA5ZThh")],
        [InlineKeyboardButton("Googlear al Inconsciente (#24)", url="https://t.me/+lP9kZHBqE1VjYzM5")],
        [InlineKeyboardButton("Googlear al Inconsciente (#25)", url="https://t.me/+E2OZLu95-qIxMWRh")]
    ]
    await update.message.reply_text(
        "🎯 Escoge tu grupo de Método Googlear al Inconsciente:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END

async def seleccionar_grupo_guerreros(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Guerreros Galácticos (#10)", url="https://t.me/+6XxTuQXYPuJmNzgx")],
        [InlineKeyboardButton("Guerreros Galácticos (#11)", url="https://t.me/+4H-VAFU9Y9w3YWJh")],
        [InlineKeyboardButton("Guerreros Galácticos (#12)", url="https://t.me/+uuRFBU2cDG4yOWRh")]
    ]
    await update.message.reply_text(
        "🎯 Escoge tu grupo de Especialización Guerreros Galácticos:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END

async def seleccionar_grupo_qmm360(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Formación QMM 360 (#01)", url="https://t.me/+CddrQ59ZuQgwZmQx")],
        [InlineKeyboardButton("Formación QMM 360 (#02)", url="https://t.me/+NzM3K8X9MfwyMDhh")]
    ]
    await update.message.reply_text(
        "🎯 Escoge tu grupo de Formación QMM 360:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END

# === FLUJO DE CONVERSACIÓN ===

async def seleccionar_curso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    curso_seleccionado[user_id] = query.data
    await query.message.reply_text("Por favor ingresa tu correo electrónico para continuar:")
    return ASK_EMAIL

async def recibir_correo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    correo = update.message.text.strip()
    user_id = update.effective_user.id

    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", correo):
        await update.message.reply_text("❌ Correo inválido. Ingresa un email válido:")
        return ASK_EMAIL

    codigo = str(random.randint(1000, 9999))
    codigo_temp[user_id] = codigo
    intentos_codigo[user_id] = 0

    url = f"{ACTIVE_CAMPAIGN_API_URL}/api/3/contact/sync"
    headers = {
        "Api-Token": ACTIVE_CAMPAIGN_API_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "contact": {
            "email": correo,
            "fieldValues": [{"field": CODIGO_CAMPO_ID, "value": codigo}]
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    print("📤 Enviando código:", response.status_code, response.text)

    if response.status_code in (200, 201):
        contact_data = response.json().get("contact", {})
        contact_id = contact_data.get("id")
        if contact_id:
            asignar_etiqueta(contact_id, TAG_ID)
            agregar_a_automatizacion(contact_id)

        await update.message.reply_text(
            "📩 Te enviamos un correo con tu código de acceso.\n"
            "Por favor ingrésalo aquí:"
        )
        return ASK_CODIGO
    else:
        await update.message.reply_text("❌ Error con ActiveCampaign. Intenta más tarde.")
        return ConversationHandler.END

async def verificar_codigo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    codigo_usuario = update.message.text.strip()
    curso_id = curso_seleccionado.get(user_id)

    if user_id in codigo_temp and codigo_usuario == codigo_temp[user_id]:
        # Limpiar
        codigo_temp.pop(user_id, None)
        intentos_codigo.pop(user_id, None)

        # Submenús personalizados
        if curso_id == "curso_herramientas":
            return await seleccionar_grupo_herramientas(update, context)
        elif curso_id == "curso_googlear":
            return await seleccionar_grupo_googlear(update, context)
        elif curso_id == "curso_guerreros":
            return await seleccionar_grupo_guerreros(update, context)
        elif curso_id == "curso_qmm360":
            return await seleccionar_grupo_qmm360(update, context)
        else:
            mensaje = MENSAJES_FINAL.get(curso_id, "✅ Acceso otorgado.")
            await update.message.reply_text(mensaje)
            curso_seleccionado.pop(user_id, None)
            return ConversationHandler.END
    else:
        intentos_codigo[user_id] += 1
        if intentos_codigo[user_id] >= 3:
            await update.message.reply_text("⛔ 3 intentos incorrectos.\n¿Deseas corregir tu correo electrónico? (sí / no)")
            return ASK_EMAIL_CONFIRMACION
        else:
            await update.message.reply_text(f"⛔ Código incorrecto. Intento {intentos_codigo[user_id]} de 3. Intenta nuevamente:")
            return ASK_CODIGO

async def confirmar_nuevo_correo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    respuesta = update.message.text.strip().lower()
    user_id = update.effective_user.id

    if respuesta in ("sí", "si", "s"):
        await update.message.reply_text("Por favor, ingresa tu nuevo correo electrónico:")
        return ASK_EMAIL
    else:
        await update.message.reply_text("🚫 Proceso cancelado.")
        codigo_temp.pop(user_id, None)
        curso_seleccionado.pop(user_id, None)
        intentos_codigo.pop(user_id, None)
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operación cancelada.")
    return ConversationHandler.END

# === INICIALIZACIÓN DEL BOT ===
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(seleccionar_curso)],
    states={
        ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_correo)],
        ASK_CODIGO: [MessageHandler(filters.TEXT & ~filters.COMMAND, verificar_codigo)],
        ASK_EMAIL_CONFIRMACION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmar_nuevo_correo)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("canales", canales_command))
application.add_handler(conv_handler)

application.run_polling()