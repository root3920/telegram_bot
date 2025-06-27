from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters
)
from dotenv import load_dotenv
import os

from handlers.commands import start_command, canales_command
from handlers.conversation import (
    seleccionar_curso, recibir_correo, verificar_codigo,
    confirmar_nuevo_correo, cancel
)
from utils.state import ASK_EMAIL, ASK_CODIGO, ASK_EMAIL_CONFIRMACION

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
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

async def mensaje_fuera_de_flujo(update, context):
    await update.message.reply_text("🔄 Usa el comando /canales para comenzar de nuevo.")

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_fuera_de_flujo))

application.run_polling()