import os
import re
import random
import base64
import requests
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, ContextTypes, filters
)

load_dotenv()

# Variables de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ACTIVE_CAMPAIGN_API_URL = os.getenv("ACTIVE_CAMPAIGN_API_URL")
ACTIVE_CAMPAIGN_API_TOKEN = os.getenv("ACTIVE_CAMPAIGN_API_TOKEN")
CODIGO_CAMPO_ID = os.getenv("CODIGO_CAMPO_ID")
TAG_ID = os.getenv("TAG_ID")
AUTOMATION_ID = int(os.getenv("AUTOMATION_ID"))
HOTMART_CLIENT_ID = os.getenv("HOTMART_CLIENT_ID")
HOTMART_CLIENT_SECRET = os.getenv("HOTMART_CLIENT_SECRET")

# Estados para la conversación
ASK_EMAIL, ASK_CODIGO, ASK_EMAIL_CONFIRMACION = range(3)

# Variables temporales en memoria
codigo_temp = {}
curso_seleccionado = {}
intentos_codigo = {}

# Mensajes finales por curso (mensaje, enlace)
MENSAJES_FINAL = {
    "curso_mente": (
        "Únete al grupo de Membresía Mente Cuántica ¡Te esperamos adentro!",
        "https://t.me/+nK7IjKHXsHw3NzIx"
    ),
    "curso_googlear": (
        "Únete al grupo de Método Googlear al Inconsciente ¡Te esperamos adentro!",
        "https://t.me/+58wyo4985tFhZjZh"
    ),
    "curso_guerreros": (
        "Únete al grupo de Especialización Guerreros Galácticos ¡Te esperamos adentro!",
        "https://t.me/+uuRFBU2cDG4yOWRh"
    ),
    "curso_avanzadas": (
        "Únete al grupo de Clases Avanzadas ¡Te esperamos adentro!",
        "https://t.me/+Pdkdc4Jc2Zo3OThh"
    ),
    "curso_qmm360": (
        "Únete al grupo de Formación QMM 360 ¡Te esperamos adentro!",
        "https://t.me/+NzM3K8X9MfwyMDhh"
    ),
    "curso_diplomatura": (
        "Únete al grupo de Diplomatura QM-M ¡Te esperamos adentro!",
        "https://t.me/+6d8N1Si4N0EwMTMx"
    ),
    "curso_herramientas": (
        "Únete al grupo de Las 8 Herramientas ¡Te esperamos adentro!",
        "https://t.me/+eJF-LF5Mq8AwNDMx"
    )
}

# Funciones para ActiveCampaign
def asignar_etiqueta(contact_id, tag_id):
    url = f"{ACTIVE_CAMPAIGN_API_URL}/api/3/contactTags"
    headers = {
        "Api-Token": ACTIVE_CAMPAIGN_API_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {"contactTag": {"contact": contact_id, "tag": tag_id}}
    requests.post(url, headers=headers, json=payload)

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
    requests.post(url, headers=headers, json=payload)

def sync_contact(email: str, codigo: str) -> int:
    url = f"{ACTIVE_CAMPAIGN_API_URL}/api/3/contact/sync"
    headers = {
        "Api-Token": ACTIVE_CAMPAIGN_API_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "contact": {
            "email": email,
            "fieldValues": [{"field": CODIGO_CAMPO_ID, "value": codigo}]
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code

# Verificación de compra en Hotmart
def verificar_compra_hotmart(email: str) -> bool:
    try:
        basic_token = base64.b64encode(f"{HOTMART_CLIENT_ID}:{HOTMART_CLIENT_SECRET}".encode()).decode()
        auth_url = (
            f"https://api-sec-vlc.hotmart.com/security/oauth/token"
            f"?grant_type=client_credentials"
            f"&client_id={HOTMART_CLIENT_ID}"
            f"&client_secret={HOTMART_CLIENT_SECRET}"
        )
        auth_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {basic_token}"
        }
        auth_response = requests.post(auth_url, headers=auth_headers)
        auth_response.raise_for_status()
        access_token = auth_response.json().get("access_token")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        params = {"transaction_status": "APPROVED"}
        url = "https://developers.hotmart.com/payments/api/v1/sales/history"

        while True:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            for venta in data.get("items", []):
                if venta.get("buyer", {}).get("email", "").strip().lower() == email.strip().lower():
                    return True

            next_token = data.get("page_info", {}).get("next_page_token")
            if not next_token:
                break
            params["page_token"] = next_token

    except Exception as e:
        print("❌ Error verificando compra en Hotmart:", e)
    return False

# === Comandos para Telegram ===
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 ¡Hola! Escribe /canales para ingresar a tu grupo de Telegram.")

async def canales_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Membresía Mente Cuántica", callback_data="curso_mente")],
        [InlineKeyboardButton("Método Googlear al Inconsciente", callback_data="curso_googlear")],
        [InlineKeyboardButton("Especialización Guerreros Galácticos", callback_data="curso_guerreros")],
        [InlineKeyboardButton("Clases Avanzadas", callback_data="curso_avanzadas")],
        [InlineKeyboardButton("Formación QMM 360", callback_data="curso_qmm360")],
        [InlineKeyboardButton("Diplomatura QM-M", callback_data="curso_diplomatura")],
        [InlineKeyboardButton("Las 8 Herramientas", callback_data="curso_herramientas")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Selecciona el curso para ingresar al canal de Telegram:", reply_markup=reply_markup)

# === Conversación ===
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

    await update.message.reply_text("🔎 Verificando tu compra en Hotmart...")
    if not verificar_compra_hotmart(correo):
        await update.message.reply_text(
            "❌ No encuentro tu email en la lista de inscriptos del curso.\n"
            "📧 Por favor revisa si escribiste bien tu email.\n"
            "🆘 Si el problema persiste, contactate con el equipo de soporte enviando un email a:\n"
            "**estudiantes@rosannabiglia.com**"
        )
        return ConversationHandler.END

    codigo = str(random.randint(1000, 9999))
    codigo_temp[user_id] = codigo
    intentos_codigo[user_id] = 0

    status = sync_contact(correo, codigo)
    if status in (200, 201):
        url_contact = f"{ACTIVE_CAMPAIGN_API_URL}/api/3/contacts?email={correo}"
        headers = {"Api-Token": ACTIVE_CAMPAIGN_API_TOKEN}
        response = requests.get(url_contact, headers=headers)
        if response.status_code == 200:
            contacts = response.json().get("contacts", [])
            if contacts:
                contact_id = contacts[0].get("id")
                asignar_etiqueta(contact_id, TAG_ID)
                agregar_a_automatizacion(contact_id)
        await update.message.reply_text(
            "✅ Compra verificada, 📩 Te enviamos un correo con tu código de acceso.\n"
            "Puede demorar hasta 5 minutos,\n"
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
        # Limpiar datos temporales
        codigo_temp.pop(user_id, None)
        intentos_codigo.pop(user_id, None)
        curso_seleccionado.pop(user_id, None)

        mensaje, enlace = MENSAJES_FINAL.get(curso_id, ("✅ Acceso otorgado.", None))
        
        if enlace:
            keyboard = [
                [InlineKeyboardButton("👉 Unirme al grupo", url=enlace)],
                [InlineKeyboardButton("💬 Hablar con soporte", url="http://t.me/soporteqmm")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(mensaje, reply_markup=reply_markup)
        else:
            keyboard = [
                [InlineKeyboardButton("💬 Hablar con soporte", url="http://t.me/soporteqmm")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(mensaje, reply_markup=reply_markup)

        return ConversationHandler.END
    else:
        intentos_codigo[user_id] += 1
        if intentos_codigo[user_id] >= 3:
            await update.message.reply_text("⛔ 3 intentos incorrectos. ¿Deseas corregir tu correo electrónico? (sí / no)")
            return ASK_EMAIL_CONFIRMACION
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

async def mensaje_fuera_de_flujo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Usa el comando /canales para comenzar de nuevo.")

# Inicialización y registro de handlers
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(seleccionar_curso)],
    states={
        ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_correo)],
        ASK_CODIGO: [MessageHandler(filters.TEXT & ~filters.COMMAND, verificar_codigo)],
        ASK_EMAIL_CONFIRMACION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmar_nuevo_correo)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("canales", canales_command))
application.add_handler(conv_handler)
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_fuera_de_flujo))

application.run_polling()