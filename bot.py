import asyncio
import logging
!pip install aiogram
from aiogram import Bot
from aiogram.filters.command import Command
from handlers import cmd_quiz, cmd_start, dp
from database import create_table
from config import API_TOKEN

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Замените "YOUR_BOT_TOKEN" на токен, который вы получили от BotFather

# Объект бота
bot = Bot(token=API_TOKEN)

dp.message.register(cmd_start, Command('start'))
dp.message.register(cmd_quiz, Command('quiz'))

# Запуск процесса поллинга новых апдейтов
async def main():
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())