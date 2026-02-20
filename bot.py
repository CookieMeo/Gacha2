import logging
import asyncio
import os
import sys
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

# --- ИМПОРТ ИЗ ТВОЕЙ БД ---
try:
    from db import init_db, get_user, create_user
except ImportError:
    logging.error("Файл db.py не найден или в нем нет нужных функций!")

# --- КОНФИГУРАЦИЯ ---
# Вставь сюда свой токен от BotFather
TOKEN = "8120653173:AAGIVbVAbbENlSvDt7ZOlsuSbtNRMDt1H-A" 
# Вставь свой ID (узнай в @userinfobot)
ADMIN_USER_ID = 1562471251  
# Твой URL на Render (БЕЗ слеша в конце)
WEB_APP_URL = "https://gacha2.onrender.com"

# Определение путей (чтобы Render точно нашел папку)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEBAPP_PATH = os.path.join(BASE_DIR, "webapp")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- ЛОГИКА БОТА ---

def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    # Кнопка для открытия Mini App
    builder.row(types.InlineKeyboardButton(
        text="🎮 Играть в Гачу", 
        web_app=WebAppInfo(url=f"{WEB_APP_URL}/"))
    )
    return builder.as_markup()

@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    # Проверка пользователя в БД
    try:
        user = get_user(user_id)
        if not user:
            create_user(user_id, username)
        await message.answer(f"Привет, {username}! Жми на кнопку ниже, чтобы начать.", reply_markup=get_main_keyboard())
    except Exception as e:
        logging.error(f"Ошибка БД в старте: {e}")
        await message.answer("Ошибка при регистрации в игре.")

# --- ВЕБ-СЕРВЕР ---

async def handle_index(request):
    index_path = os.path.join(WEBAPP_PATH, "index.html")
    if os.path.exists(index_path):
        return web.FileResponse(index_path)
    return web.Response(text="Файл index.html не найден в папке webapp!", status=404)

async def health_check(request):
    return web.Response(text="OK")

async def start_web_server():
    app = web.Application()
    
    # Это сделает всё содержимое папки webapp доступным по главному адресу
    # index.html будет открываться автоматически
    app.router.add_static('/', path=WEBAPP_PATH, name='webapp', show_index=True)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000)) # Render обычно дает порт 10000
    site = web.TCPSite(runner, '0.0.0.0', port) 
    await site.start()
    logging.info(f"✅ Веб-сервер запущен на порту {port}")

# --- ЗАПУСК ---

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Инициализация БД (без await, если она обычная)
    try:
        init_db()
        logging.info("✅ База данных готова")
    except Exception as e:
        logging.info(f"Заметка по БД: {e}")

    # Запускаем сервер и бота параллельно
    await start_web_server()
    logging.info("🤖 Бот запущен и слушает сообщения...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



