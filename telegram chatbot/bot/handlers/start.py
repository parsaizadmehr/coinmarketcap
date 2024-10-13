from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.decorators import log_command
from database.db_connection import get_db_connection

def insert_new_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (uid) VALUES (%s) ON CONFLICT DO NOTHING", (user_id,))
    
    conn.commit()
    cursor.close()
    conn.close()

@log_command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    insert_new_user(user_id)

    await update.message.reply_text("Welcome to the Telegram Bot Starter Kit!")
