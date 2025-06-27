import random, re
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from services.hotmart import verificar_compra_hotmart
from services.active_campaign import sync_contact
from utils.state import (
    ASK_EMAIL, ASK_CODIGO, ASK_EMAIL_CONFIRMACION,
    codigo_temp, curso_seleccionado, intentos_codigo, MENSAJES_FINAL
)
from handlers.menus import (
    seleccionar_grupo_herramientas, seleccionar_grupo_googlear,
    seleccionar_grupo_guerreros, seleccionar_grupo_qmm360
)

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
            "📧 Revisa si escribiste bien tu email o escribe a estudiantes@rosannabiglia.com"
        )
        return ConversationHandler.END

    codigo = str(random.randint(1000, 9999))
    codigo_temp[user_id] = codigo
    intentos_codigo[user_id] = 0

    status = sync_contact(correo, codigo)
    if status in (200, 201):
        await update.message.reply_text(
            "✅ Compra verificada, 📩 Te enviamos un correo con tu código de acceso.\n"
            "Puede demorar hasta 5 minutos, por favor ingrésalo aquí:"
        )
        return ASK_CODIGO
    else:
        await update.message.reply_text("❌ Error con ActiveCampaign.")
        return ConversationHandler.END

async def verificar_codigo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    codigo_usuario = update.message.text.strip()
    curso_id = curso_seleccionado.get(user_id)

    if codigo_usuario == codigo_temp.get(user_id):
        # Limpiar datos temporales
        codigo_temp.pop(user_id, None)
        intentos_codigo.pop(user_id, None)

        # Submenús personalizados según curso
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
            await update.message.reply_text(
                "⛔ 3 intentos incorrectos.\n¿Deseas corregir tu correo electrónico? (sí / no)"
            )
            return ASK_EMAIL_CONFIRMACION
        else:
            await update.message.reply_text(
                f"⛔ Código incorrecto. Intento {intentos_codigo[user_id]} de 3. Intenta nuevamente:"
            )
            return ASK_CODIGO

async def confirmar_nuevo_correo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    respuesta = update.message.text.strip().lower()
    user_id = update.effective_user.id
    if respuesta in ("sí", "si", "s"):
        await update.message.reply_text("Escribe tu nuevo correo:")
        return ASK_EMAIL
    else:
        await update.message.reply_text("🚫 Proceso cancelado.")
        curso_seleccionado.pop(user_id, None)
        codigo_temp.pop(user_id, None)
        intentos_codigo.pop(user_id, None)
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 Operación cancelada.")
    return ConversationHandler.END
