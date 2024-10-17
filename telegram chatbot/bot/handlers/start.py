from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.utils.decorators import log_command
from database.db_connection import get_db_connection
from .localization import get_message, get_user_language

def insert_new_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (uid, language) VALUES (%s, 'en') ON CONFLICT DO NOTHING", (user_id,))
    
    conn.commit()
    cursor.close()
    conn.close()

@log_command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    # insert user if they don't exist
    insert_new_user(user_id)

    # get user language 
    user_language = get_user_language(user_id)

    # get localized welcome message
    welcome_message = get_message("welcome", user_language)
    
    # send the localized message
    await update.message.reply_text(welcome_message)


    # keyboard = [
    #     [InlineKeyboardButton("English", callback_data='en')],
    #     [InlineKeyboardButton("Farsi", callback_data='fa')],
    # ]
    # reply_markup = InlineKeyboardMarkup(keyboard)

    # choose_language_message_en = get_message("choose_language", "en")
    # choose_language_message_fa = get_message("choose_language", "fa")


    # choose_language_message = f"{choose_language_message_en}\n{choose_language_message_fa}"
    # await update.message.reply_text(choose_language_message, reply_markup=reply_markup)