from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.decorators import log_command

@log_command
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)