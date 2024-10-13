from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.decorators import log_command
from database.db_connection import get_db_connection
from datetime import date, timedelta

@log_command
async def coin_rank_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #input user and make it uppercase
    coin_symbol = context.args[0].upper()

    conn = get_db_connection()
    cursor = conn.cursor()

    # get dates for today, last week, month, last year and last tree years
    today = date.today()
    last_week_date = today - timedelta(days=7)
    last_month_date = today.replace(month=today.month - 1 if today.month > 1 else 12, year=today.year - (1 if today.month == 1 else 0))
    last_year_date = today.replace(year=today.year - 1)
    last_three_years_date = today.replace(year=today.year - 3)

    # query to get rank for a specific date range
    def get_rank_before_date(symbol, target_date):
        cursor.execute("""
            SELECT rank 
            FROM historical_data 
            WHERE symbol = %s AND date <= %s
            ORDER BY date DESC
        """, (symbol, target_date))
        return cursor.fetchone()

    # fetch rank records for each time period
    last_week_record = get_rank_before_date(coin_symbol, last_week_date)
    last_month_record = get_rank_before_date(coin_symbol, last_month_date)
    last_year_record = get_rank_before_date(coin_symbol, last_year_date)
    last_three_years_record = get_rank_before_date(coin_symbol, last_three_years_date)

    msg = f"Rank history for {coin_symbol}:\n"
    
    if last_week_record and len(last_week_record) == 2:  # Ensure the record exists and has rank and date
        msg += f"Last week: {last_week_record[0]} (date: {last_week_record[1]})\n"
    else:
        msg += "No record found for last week.\n"

    if last_month_record and len(last_month_record) == 2:
        msg += f"Last month: {last_month_record[0]} (date: {last_month_record[1]})\n"
    else:
        msg += "No record found for last month.\n"

    if last_year_record and len(last_year_record) == 2:
        msg += f"Last year: {last_year_record[0]} (date: {last_year_record[1]})\n"
    else:
        msg += "No record found for last year.\n"

    if last_three_years_record and len(last_three_years_record) == 2:
        msg += f"Last three years: {last_three_years_record[0]} (date: {last_three_years_record[1]})\n"
    else:
        msg += "No record found for last three years.\n"

    await update.message.reply_text(msg)

    cursor.close()
    conn.close()
