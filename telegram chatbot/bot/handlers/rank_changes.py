from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.decorators import log_command
from database.db_connection import get_db_connection
from .localization import get_message, get_user_language

@log_command
async def rank_changes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_language = get_user_language(user_id)

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    WITH ranked_cryptocurrencies AS (
        SELECT
            id,
            rank,
            symbol,
            name,
            ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY last_update DESC) AS rn
        FROM
            cryptocurrencies
    )
    SELECT
        current.symbol,
        current.rank AS current_rank,
        previous.rank AS previous_rank,
        (previous.rank - current.rank) AS rank_change
    FROM
        ranked_cryptocurrencies current
    LEFT JOIN
        ranked_cryptocurrencies previous
    ON
        current.symbol = previous.symbol
        AND previous.rn = 2
    WHERE
        current.rn = 1
        AND (previous.rank - current.rank) <> 0
    ORDER BY
        ABS(previous.rank - current.rank) DESC
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()

    rank_changes_msg = get_message('cryptocurrency_rank_changes', user_language)
    for symbol, current_rank, previous_rank, rank_change in rows:
        rank_changes_msg += f"🪙 {symbol} {previous_rank} to {current_rank} ({rank_change})\n"

    await update.message.reply_text(rank_changes_msg)
