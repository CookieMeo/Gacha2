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

# Импортируем функции из твоего файла db.py
# ВНИМАНИЕ: Если в db.py эти функции называются иначе, проверь названия.
from db import (
    init_db, get_user, create_user, add_pet_to_db, add_promocode
)

# --- КОНФИГУРАЦИЯ ---
# Рекомендую вставить токен прямо сюда, если не используешь Environment Variables на Render
TOKEN = "8226800067:AAH3KAaK4-VIcXh8GijTRd5sCRKQQ2MJ510" 
ADMIN_USER_ID = 1562471251  # ЗАМЕНИ НА СВОЙ ID (узнай в @userinfobot)
WEB_APP_URL = "https://gacha2.onrender.com" # Твой URL на Render

# Настройка бота с учетом новых требований aiogram 3.7+
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- ЛОГИКА БОТА ---

def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    # Кнопки будут открывать мини-аппку
    builder.row(types.InlineKeyboardButton(text="🏠 Играть", web_app=WebAppInfo(url=WEB_APP_URL)))
    return builder.as_markup()

@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    user = get_user(user_id)
    if not user:
        create_user(user_id, username)
        await message.answer(f"Привет, {username}! Добро пожаловать в Гачу!", reply_markup=get_main_keyboard())
    else:
        await message.answer(f"С возвращением, {username}!", reply_markup=get_main_keyboard())

# Пример админ-команды
@dp.message(Command("admin"))
async def admin_command(message: types.Message):
    if message.from_user.id != ADMIN_USER_ID:
        return await message.answer("У вас нет прав.")
    await message.answer("Команды админа: /admin_add_pet, /admin_create_promo")

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---

async def handle_index(request):
    # Отдает главную страницу игры
    return web.FileResponse('./webapp/index.html')

async def health_check(request):
    return web.Response(text="OK")

async def start_web_server():
    app = web.Application()
    
    # Чтобы Render не выдавал заставку "Welcome to Render", вешаем игру на корень /
    app.router.add_get('/', handle_index)
    app.router.add_get('/health', health_check)
    
    # Раздаем остальные файлы (js, css, картинки) из папки webapp
    app.router.add_static('/webapp/', path='./webapp', name='webapp')
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Порт, который требует Render
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"✅ Web-server started on port {port}")

# --- ЗАПУСК ---

async def main():
    # Настройка логирования
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # 1. Инициализация базы данных
    # УБРАЛ await, так как в db.py функция обычная (судя по ошибке в логах)
    try:
        init_db() 
        logging.info("✅ Database initialized")
    except Exception as e:
        logging.error(f"❌ DB Error: {e}")

    # 2. Запуск веб-сервера (для Render)
    await start_web_server()

    # 3. Запуск бота
    logging.info("🚀 Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
