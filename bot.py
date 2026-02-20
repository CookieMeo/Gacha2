import logging
import asyncio
import os
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

# --- ИМПОРТ ИЗ ТВОЕЙ БД ---
try:
    from db import init_db, get_user, create_user
except ImportError:
    def init_db(): pass
    def get_user(x): return None
    def create_user(x, y): pass

# --- КОНФИГУРАЦИЯ ---
TOKEN = "8120653173:AAGIVbVAbbENlSvDt7ZOlsuSbtNRMDt1H-A" 
WEB_APP_URL = "https://gacha2-5ng0.onrender.com" # Убедись, что это адрес из настроек Render

# Настройка путей
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEBAPP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webapp")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- ЛОГИКА БОТА ---

def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    # Отправляем пользователя строго на корень сайта
    builder.row(types.InlineKeyboardButton(
        text="🎮 Играть", 
        web_app=WebAppInfo(url=f"{WEB_APP_URL}/"))
    )
    return builder.as_markup()

@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    user = get_user(user_id)
    if not user:
        create_user(user_id, username)
    await message.answer(f"Привет, {username}! Жми кнопку:", reply_markup=get_main_keyboard())

# --- ВЕБ-СЕРВЕР ---

async def handle_index(request):
    """Этот обработчик отвечает за главную страницу"""
    path = os.path.join(WEBAPP_PATH, "index.html")
    if os.path.exists(path):
        return web.FileResponse(path)
    return web.Response(text=f"Файл index.html не найден по пути: {path}", status=404)

async def health_check(request):
    return web.Response(text="OK")

async def start_web_server():
    app = web.Application()
    
    # 1. Сначала добавляем health check
    app.router.add_get('/health', health_check)
    
    # 2. Главная магия: делаем так, чтобы ВСЕ файлы из папки webapp 
    # были доступны по прямому адресу (без /webapp/)
    # Это исправит 404 для картинок
    app.router.add_static('/', path=WEBAPP_PATH, name='static', follow_symlinks=True, show_index=True)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"✅ Сервер раздает файлы из {WEBAPP_PATH} на порту {port}")

# --- ЗАПУСК ---

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # ОТЛАДКА: Проверяем файлы перед стартом
    logging.info(f"Текущая папка: {os.getcwd()}")
    if os.path.exists(WEBAPP_PATH):
        logging.info(f"Содержимое webapp: {os.listdir(WEBAPP_PATH)}")
    else:
        logging.error(f"❌ ПАПКА {WEBAPP_PATH} НЕ НАЙДЕНА!")

    init_db()
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



