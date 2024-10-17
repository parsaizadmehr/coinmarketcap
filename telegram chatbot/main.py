import logging
from telegram import Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN, USE_DATABASE
from bot.handlers.start import start
from bot.handlers.echo import echo
from bot.handlers.top import top
from bot.handlers.rank_changes import rank_changes
from bot.handlers.coins import coin_rank_history
from bot.handlers.set_language import set_language, language_callback

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def set_commands(bot: Bot):
    commands = [
        ("start", "Welcome message"),
        ("top", "Get the top-ranked items"),
        ("ranks", "View rank changes"),
        ("c", "Get coin rank history"),
        ("set_language", "Set your preferred language"),
    ]
    bot.set_my_commands(commands)

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    set_commands(application.bot)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("top", top))
    application.add_handler(CommandHandler("ranks", rank_changes))
    application.add_handler(CommandHandler("c", coin_rank_history))
    application.add_handler(CommandHandler("set_language", set_language))
    application.add_handler(CallbackQueryHandler(language_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    if USE_DATABASE:
        from database.models import init_db
        init_db()
        logging.info("Database initialized")
    else:
        logging.info("Running without database")

    application.run_polling()

if __name__ == '__main__':
    main()
