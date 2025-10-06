import os
import re
import random
import base64
import requests
from datetime import datetime
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

# Mensajes finales por curso
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
        "https://t.me/+nWmDrfVb_XZkZmMx"
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
        "https://t.me/+HobEI09THppiNGQ5"
    ),
     "curso_team": (
        "Únete al grupo de Inmersión: QMM Team ¡Te esperamos adentro!",
        "https://t.me/+_ABR51Hd-okzMDE5"
    ),
        "experiencia_cuantica": (
        "Únete al grupo de Experiencias Cuánticas ¡Te esperamos adentro!",
        "https://t.me/+0qT2qhflR0pjNmM5"
    )
}

# Subdominios por curso
SUBDOMINIOS_CURSO = {
    "curso_qmm360": "quantummind360",
    "curso_mente": "mentecuanticaqmm",
    "curso_googlear": "qmmonline",
    "curso_herramientas": "codigoabundancia",
    "curso_guerreros": "guerrerosgalacticosqmm",
    "curso_avanzadas": "comunidadqmm",
    "curso_diplomatura": "diplomaturaterapeutaquantummin",
    "curso_team": "inmersionqmmteamcdmx2026",
    "experiencia_cuantica": "experienciascuanticas"
}

# ==================== FUNCIONES EXTERNAS =====================

def formato_fecha(timestamp_ms):
    if not timestamp_ms:
        return "N/A"
    try:
        return datetime.fromtimestamp(timestamp_ms / 1000).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "Fecha inválida"

def verificar_miembro_hotmart(email: str, subdominio: str) -> bool:
    try:
        basic_token = base64.b64encode(f"{HOTMART_CLIENT_ID}:{HOTMART_CLIENT_SECRET}".encode()).decode()
        auth_url = (
            "https://api-sec-vlc.hotmart.com/security/oauth/token"
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
        token = auth_response.json()["access_token"]

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        params = {
            "subdomain": subdominio,
            "email": email
        }
        url = "https://developers.hotmart.com/club/api/v1/users"
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("items", [])
            if not items:
                return False
            usuario = items[0]
            print(f"\n✅ Usuario en Hotmart Club: {usuario.get('email')} | Estado: {usuario.get('status')}")
            return True
    except Exception as e:
        print("❌ Error en verificación con Hotmart Club:", e)
    return False

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

# ==================== HANDLERS DE TELEGRAM =====================

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
        [InlineKeyboardButton("Las 8 Herramientas", callback_data="curso_herramientas")],
        [InlineKeyboardButton("Inmersión: QMM Team", callback_data="curso_team")],
        [InlineKeyboardButton("Experiencias Cuánticas", callback_data="experiencia_cuantica")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Selecciona el curso para ingresar al canal de Telegram:", reply_markup=reply_markup)

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

    await update.message.reply_text("🔎 Verificando tu acceso en Hotmart Club...")

    curso_id = curso_seleccionado.get(user_id)
    subdominio = SUBDOMINIOS_CURSO.get(curso_id)

    if not subdominio:
        await update.message.reply_text("❌ No se encontró el subdominio para este curso.")
        return ConversationHandler.END

    if not verificar_miembro_hotmart(correo, subdominio):
        await update.message.reply_text(
            "❌ No encontramos tu email en el área de miembros del curso.\n"
            "📧 Verifica que esté bien escrito.\n"
            "🆘 Si el problema persiste, contacta a soporte: **estudiantes@rosannabiglia.com**"
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
            "Puede demorar hasta 5 minutos.\n"
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
        codigo_temp.pop(user_id, None)
        intentos_codigo.pop(user_id, None)
        curso_seleccionado.pop(user_id, None)

        mensaje, enlace = MENSAJES_FINAL.get(curso_id, ("✅ Acceso otorgado.", None))

        if enlace:
            keyboard = [
                [InlineKeyboardButton("👉 Unirme al grupo", url=enlace)],
                [InlineKeyboardButton("💬 Hablar con soporte", url="http://t.me/soporteqmm")]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("💬 Hablar con soporte", url="http://t.me/soporteqmm")]
            ]

        await update.message.reply_text(mensaje, reply_markup=InlineKeyboardMarkup(keyboard))
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

# ==================== INICIALIZACIÓN =====================

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
