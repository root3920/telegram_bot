from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def seleccionar_grupo_herramientas(update, context):
    keyboard = [
        [InlineKeyboardButton("Las 8 Herramientas (#27)", url="https://t.me/+kdclZgGhr5JhMTkx")],
        [InlineKeyboardButton("Las 8 Herramientas (#28)", url="https://t.me/+tFJ3rECCPuAxMTAx")],
        [InlineKeyboardButton("Las 8 Herramientas (#29)", url="https://t.me/+SRSGg3cA8wVkOWNh")],
        [InlineKeyboardButton("Las 8 Herramientas (#30)", url="https://t.me/+t3l__l5gEbk0ZWIx")],
        [InlineKeyboardButton("Las 8 Herramientas (#31)", url="https://t.me/+eJF-LF5Mq8AwNDMx")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎯 Escoge el grupo de 8 Herramientas al que perteneces:",
        reply_markup=reply_markup
    )
    return -1  # Finaliza conversación

async def seleccionar_grupo_googlear(update, context):
    keyboard = [
        [InlineKeyboardButton("Método Googlear al Inconsciente (#23)", url="https://t.me/+NwqLxwUDpKA5ZThh")],
        [InlineKeyboardButton("Método Googlear al Inconsciente (#24)", url="https://t.me/+lP9kZHBqE1VjYzM5")],
        [InlineKeyboardButton("Método Googlear al Inconsciente (#25)", url="https://t.me/+E2OZLu95-qIxMWRh")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎯 Escoge tu grupo de Método Googlear al Inconsciente:",
        reply_markup=reply_markup
    )
    return -1

async def seleccionar_grupo_guerreros(update, context):
    keyboard = [
        [InlineKeyboardButton("Especialización Guerreros Galácticos (#10)", url="https://t.me/+6XxTuQXYPuJmNzgx")],
        [InlineKeyboardButton("Especialización Guerreros Galácticos (#11)", url="https://t.me/+4H-VAFU9Y9w3YWJh")],
        [InlineKeyboardButton("Especialización Guerreros Galácticos (#12)", url="https://t.me/+uuRFBU2cDG4yOWRh")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎯 Escoge tu grupo de Especialización Guerreros Galácticos:",
        reply_markup=reply_markup
    )
    return -1

async def seleccionar_grupo_qmm360(update, context):
    keyboard = [
        [InlineKeyboardButton("Formación QMM 360 (#01)", url="https://t.me/+CddrQ59ZuQgwZmQx")],
        [InlineKeyboardButton("Formación QMM 360 (#02)", url="https://t.me/+NzM3K8X9MfwyMDhh")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎯 Escoge tu grupo de Formación QMM 360:",
        reply_markup=reply_markup
    )
    return -1
