from aiogram import Bot, Dispatcher

from handlers.commands import router as commands_router
from database import create_tables


create_tables()

BOT_TOKEN = "8338523679:AAHXepAqIA576owkhAJkKcu1HzPSmYdHhj4"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(commands_router)

if __name__ == '__main__':
    print("Бот запускается...")
    dp.run_polling(bot)