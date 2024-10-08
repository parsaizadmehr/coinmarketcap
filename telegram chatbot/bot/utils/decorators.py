import logging
from functools import wraps

def log_command(func):
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        user = update.effective_user
        logging.info(f"User {user.id} ({user.username}) used command: {update.message.text}")
        return await func(update, context, *args, **kwargs)
    return wrapper