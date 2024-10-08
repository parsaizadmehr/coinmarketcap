# Telegram Bot Starter Kit

Telegram Bot Starter Kit provides a flexible and extensible foundation for building Telegram bots with Python. It includes command handling, utility functions, and optional database integration to help you get started quickly.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Feature](#features)
- [Quickstart (Folder Structure and Setup)](#quickstart-folder-structure-and-setup)
- [Running the Bot](#running-the-bot)
- [Customizing the Bot](#customizing-the-bot)
- [Adding New Commands](#adding-new-commands)
- [Database Usage](#database-usage)
- [Contributing](#contributing)

## Prerequisites
- Knowledge of Python
- Familiarity with the [`python-telegram-bot`](https://docs.python-telegram-bot.org/en/v21.5/) package
- Basic knowledge of building a telegram bot
- Postgres database such as [Neon](https://neon.tech/)
- Python 3.7 or higher
- pip (Python package manager)

## Features
Telegram Bot Starter Kit provides the following features:
- Modular structure for easy extension and maintenance
- Optional database integration using SQLAlchemy
- Environment variable management with python-dotenv
- Command handling and logging
- Echo functionality for non-command messages

## Quickstart (Folder structure and setup)

### Folder Structure
Here's an overview of the project's folder structure:
```
telegram_bot_starter_kit/
├── bot/
│   ├── __init__.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py
│   │   └── echo.py
│   └── utils/
│       ├── __init__.py
│       └── decorators.py
├── database/
│   ├── __init__.py
│   └── models.py
├── config.py
├── main.py
├── requirements.txt
└── .env
```

### Project Setup
Follow these steps to setup and use the starter kit.

1. Clone the repository:
    ```
    git clone https://github.com/ade555/telegram-bot-starter-kit.git
    cd telegram-bot-starter-kit
    ```
2. Create a virtual environment (optional but recommended):
    ```
    python -m venv env
    ```
    You can activate your virtual envirnment differently depending on your OS.<br><br>
    For windows:
    ```
    env\scripts\activate
    ```
    For Unix systems (Linux, Mac):
    ```
    source env/bin/activate
    ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file and copy the contents of the `.env_sample` file. Ensure you include real values. Note that the Datbase URL is optional.
    ```
    TELEGRAM_BOT_TOKEN=your_bot_token
    USE_DATABASE=False
    DATABASE_URL=postgresql://john_doe:secure_password@db.neon.tech:5432/my_app_database
    ```
    Rep;ace `your_bot_token` with your actual bot token from BotFather. Set `USE_DATABASE` to `True` and provide a  `DATABASE_URL` if your project requires a database.

## Running the Bot
To run the bot, open your CLI in the `telegram-bot-starter-kit` directory and run this command:
```
python main.py
```

## Customizing the Bot

### config.py
This file manages configuration settings for the bot. You can add more configuration variables here as needed.

### main.py
This is the entry point of your bot. It sets up logging, initializes the bot, and registers command handlers. To add new features, do the following:

- Import new handlers at the top of the file.
- Add new handlers to the `application` object in the `main()` function.

### bot/handlers/
This directory contains handler functions for bot commands and messages. Each file typically corresponds to a specific command or group of related commands. Currently, this directory contains the following files:

- `start.py`: Handles the /start command
- `echo.py`: Echoes non-command messages back to the use

### bot/utils/
This directory contains utility functions and decorators:

- `decorators.py`: Contains the log_command decorator for logging command usage

## Adding New Commands
To add a new command, do the following:

1. Create a new file in the `bot/handlers/` directory, e.g., custom_command.py.
2. Define your command handler function in this file.
3. Import the new handler in `main.py`.
4. Add the new handler to the `application` object in the `main()` function of main.py.

### Example:
```python
# In bot/handlers/custom_command.py
from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.decorators import log_command

@log_command
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command!")

# In main.py
from bot.handlers.custom_command import custom_command

def main():
    # ... existing code ...
    application.add_handler(CommandHandler("custom", custom_command))
    # ... existing code ...
```

## Database Usage
The starter kit includes optional database functionality using SQLAlchemy. To use the database, follow these steps:
1. Set `USE_DATABASE=True` in your `.env` file.
2. Ensure the `DATABASE_URL` in your `.env` file is set correctly. You can get a free postgres database from [Neon](https://neon.tech/)
3. The User model in `database/models.py` provides a basic structure for storing user information. You can modify this model or add new models as needed.

You can interact with the database in your command handlers. Here's an example:
```python
from database.models import User, init_db

Session = init_db()

async def some_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with Session() as session:
        user = session.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            user = User(telegram_id=update.effective_user.id, username=update.effective_user.username)
            session.add(user)
            session.commit()
        # Use the user object as needed
```

## Contributing
Contributions are welcome for this project! Feel free to submit a pull request if you have an idea to improve this project. You can follow these steps to contribute to the project:
1. Fork the repository
2. Create your feature branch (git checkout -b feature/newFeature)
3. Commit your changes (git commit -m 'Add a new feature')
4. Push to the branch (git push origin feature/newFeature)
5. Open a Pull Request