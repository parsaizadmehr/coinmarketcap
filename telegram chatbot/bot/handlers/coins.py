from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.decorators import log_command
from database.db_connection import get_db_connection
from datetime import date, timedelta
from .localization import get_message, get_user_language 

@log_command
async def coin_rank_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_language = get_user_language(user_id)
    
    coin_symbol = context.args[0].upper()

    conn = get_db_connection()
    cursor = conn.cursor()

    today = date.today()
    last_week_date = today - timedelta(days=7)
    last_month_date = today - timedelta(days=30)
    last_year_date = today - timedelta(days=365)
    last_three_years_date = today - timedelta(days=1095)

    def get_rank_before_date(symbol, target_date):
        cursor.execute("""
            SELECT rank 
            FROM historical_data 
            WHERE symbol = %s AND date <= %s
            ORDER BY date DESC
        """, (symbol, target_date))
        return cursor.fetchone()

    last_week_record = get_rank_before_date(coin_symbol, last_week_date)
    last_month_record = get_rank_before_date(coin_symbol, last_month_date)
    last_year_record = get_rank_before_date(coin_symbol, last_year_date)
    last_three_years_record = get_rank_before_date(coin_symbol, last_three_years_date)

    msg = get_message('rank_history', user_language, coin_symbol=coin_symbol) + "\n"

    if last_week_record:
        msg += f"{get_message('last_week_msg', user_language)} {last_week_record[0]}\n"
    else:
        msg += get_message('no_record_week', user_language) + "\n"

    if last_month_record:
        msg += f"{get_message('last_month_msg', user_language)} {last_month_record[0]}\n"
    else:
        msg += get_message('no_record_month', user_language) + "\n"

    if last_year_record:
        msg += f"{get_message('last_year_msg', user_language)} {last_year_record[0]}\n"
    else:
        msg += get_message('no_record_year', user_language) + "\n"

    if last_three_years_record:
        msg += f"{get_message('last_three_years_msg', user_language)} {last_three_years_record[0]}\n"
    else:
        msg += get_message('no_record_three_years', user_language) + "\n"

    await update.message.reply_text(msg)

    cursor.close()
    conn.close()
