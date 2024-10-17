from database.db_connection import get_db_connection

MESSAGES = {
    'en': {
        'welcome': "Welcome to the coinmarketcap bot!",
        'choose_language': "Please choose your language:",
        'language_set': "Language set to English.",
        'no_language': "No language preference set.",
        'rank_history': "Rank history for {coin_symbol}:\n",
        'no_record_week': "No record found for last week.",
        'no_record_month': "No record found for last month.",
        'no_record_year': "No record found for last year.",
        'no_record_three_years': "No record found for last three years.",
        'cryptocurrency_rank_changes': "📊 Cryptocurrency Rank Changes:\n\n",
        'top_coins': '📊 Top 50 Cryptocurrencies:',
        'last_week_msg': "📅 Last week:",
        'last_month_msg': "📅 Last month:",
        'last_year_msg': "📅 Last year:",
        'last_three_years_msg': "📅 Last three years:",
    },
    'fa': {
        'welcome': "به ربات خوش آمدید!",
        'choose_language': "لطفا زبان خود را انتخاب کنید:",
        'language_set': "زبان به فارسی تغییر یافت.",
        'no_language': "ترجیح زبانی تنظیم نشده است.",
        'rank_history': "تاریخچه رتبه برای {coin_symbol}:\n",
        'no_record_week': "هیچ رکوردی برای هفته گذشته یافت نشد.",
        'no_record_month': "هیچ رکوردی برای ماه گذشته یافت نشد.",
        'no_record_year': "هیچ رکوردی برای سال گذشته یافت نشد.",
        'no_record_three_years': "هیچ رکوردی برای سه سال گذشته یافت نشد.",
        'cryptocurrency_rank_changes': "📊 تغییرات رتبه ارزهای دیجیتال:\n\n",
        'top_coins': '📊 پنجاه ارز برتر',
        'last_week_msg': "📅 هفته گذشته:",
        'last_month_msg': "📅 ماه گذشته:",
        'last_year_msg': "📅 سال گذشته:",
        'last_three_years_msg': "📅 سه سال گذشته:",
    }
}

def get_message(key, language='en', **kwargs):
    message_template = MESSAGES.get(language, MESSAGES['en']).get(key, MESSAGES['en'].get(key))
    
    # dynamic content replacement using keyword arguments
    if kwargs:
        return message_template.format(**kwargs)
    
    return message_template


def get_user_language(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT language FROM users WHERE uid = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return result[0] if result else "en"