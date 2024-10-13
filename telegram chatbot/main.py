import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN, USE_DATABASE
from bot.handlers.start import start
from bot.handlers.echo import echo
from bot.handlers.top import top
from bot.handlers.rank_changes import rank_changes
from bot.handlers.coins import coin_rank_history

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("top", top))
    application.add_handler(CommandHandler("ranks", rank_changes))
    application.add_handler(CommandHandler("c", coin_rank_history))
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