from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.decorators import log_command
from database.db_connection import get_db_connection
from .localization import get_message, get_user_language

@log_command
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT ON (rank) rank, name FROM cryptocurrencies ORDER BY rank ASC LIMIT 50")

    rows = cursor.fetchall()
    
    conn.commit()
    cursor.close()
    conn.close()

    top_coins = ""
    for rank, name in rows:
        top_coins += f"{rank}. {name}\n"


    language_code = get_user_language(user_id)
    msg = get_message("top_coins", language_code)


    await update.message.reply_text(f"{msg}\n{top_coins}")