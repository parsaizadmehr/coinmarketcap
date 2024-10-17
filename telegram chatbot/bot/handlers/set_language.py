from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.utils.decorators import log_command
from database.db_connection import get_db_connection
from .localization import get_message

@log_command
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("English", callback_data="en")],
        [InlineKeyboardButton("Farsi", callback_data="fa")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    choose_language_message_en = get_message("choose_language", "en")
    choose_language_message_fa = get_message("choose_language", "fa")
    choose_language_message = f"{choose_language_message_en}\n{choose_language_message_fa}"

    await update.message.reply_text(choose_language_message, reply_markup=reply_markup)

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    language_code = query.data
    user_id = query.from_user.id

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET language = %s WHERE uid = %s", (language_code, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    confirmation_msg = get_message("language_set", language_code)
    await query.edit_message_text(confirmation_msg)
