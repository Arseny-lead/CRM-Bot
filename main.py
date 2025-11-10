from aiogram import Bot, Dispatcher

from handlers.commands import router as commands_router
from database import create_tables
from config import BOT_TOKEN


create_tables()

BOT_TOKEN = BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(commands_router)

if __name__ == '__main__':
    print("Бот запускается...")
    dp.run_polling(bot)
