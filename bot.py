import logging, asyncio, os, sys, sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo # <-- Убедись, что это импортировано
from aiohttp import web
from db import init_db, get_user, create_user, do_spins_logic

# --- КОНФИГУРАЦИЯ ---
TOKEN = "8120653173:AAHA5SGMXg0ejb2hSJ4NMmh4P13130_PeKs" # !!! ОБЯЗАТЕЛЬНО ЗАМЕНИ НА СВОЙ ТОКЕН !!!
ADMIN_USER_ID = 1562471251 # !!! ОБЯЗАТЕЛЬНО ЗАМЕНИ НА СВОЙ ID !!!
WEB_APP_URL = "https://gacha2-5ng0.onrender.com" # !!! ПРОВЕРЬ СВОЙ АДРЕС НА RENDER.COM !!!

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Инициализируем базу данных при старте
init_db()

# --- СЛОВАРЬ УРОВНЕЙ ДЛЯ КЛИКЕРА ---
UPGRADES = {
    2: [10, 2], 3: [40, 3], 4: [90, 4], 5: [160, 5], 6: [250, 6], 
    7: [360, 7], 8: [490, 8], 9: [640, 9], 10: [810, 10], 11: [4000, 100]
}

# --- ОБРАБОТЧИКИ КОМАНД БОТА ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Создаем пользователя, если его нет
    create_user(message.from_user.id, message.from_user.username)
    
    # Кнопка для запуска Web App
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🚀 Запустить игру", web_app=WebAppInfo(url=WEB_APP_URL))]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    await message.answer("Привет! Нажми кнопку ниже, чтобы начать играть в гачу.", reply_markup=kb)

@dp.message(Command("add_pet"))
async def add_pet(m: types.Message):
    if m.from_user.id != ADMIN_USER_ID: return
    try:
        a = m.text.split(maxsplit=1)[1].split(', ')
        conn = sqlite3.connect('gacha_game.db')
        conn.execute("INSERT INTO pets (name, rarity, image_url, is_event) VALUES (?,?,?,?)", (a[0], a[1], a[2], int(a[3])))
        conn.commit()
        await m.answer(f"✅ Питомец {a[0]} ({a[1]}) добавлен!")
    except Exception as e: 
        await m.answer(f"Ошибка! Формат: Имя, Красное, url, 1\nОшибка: {e}")

@dp.message(Command("add_promo"))
async def add_promo(m: types.Message):
    if m.from_user.id != ADMIN_USER_ID: return
    try:
        a = m.text.split(maxsplit=1)[1].split(', ')
        conn = sqlite3.connect('gacha_game.db')
        conn.execute("INSERT INTO promocodes VALUES (?,?,?,?)", (a[0], int(a[1]), int(a[2]), int(a[3])))
        conn.commit()
        await m.answer(f"✅ Промокод {a[0]} добавлен!")
    except Exception as e:
        await m.answer(f"Ошибка! Формат: КОД, клубника, крутки, кол-во\nОшибка: {e}")

# --- API ЭНДПОИНТЫ ДЛЯ WEB APP ---

async def api_get_user(request):
    try:
        uid = (await request.json()).get('user_id')
        u = get_user(uid)
        if not u: 
            create_user(uid, "Игрок")
            u = get_user(uid)
        return web.json_response(u)
    except Exception as e:
        logging.error(f"Ошибка в api_get_user: {e}")
        return web.json_response({"success": False, "error": str(e)}, status=500)

async def api_click(request):
    try:
        uid = (await request.json()).get('user_id')
        u = get_user(uid)
        
        power = 1 # Дефолтная сила клика для 1 уровня
        if u['click_level'] in UPGRADES:
            power = UPGRADES[u['click_level']][1]
        elif u['click_level'] >= 11:
            power = 100

        conn = sqlite3.connect('gacha_game.db')
        conn.execute("UPDATE users SET strawberry = strawberry + ? WHERE user_id = ?", (power, uid))
        conn.commit()
        conn.close()
        return web.json_response({"success": True})
    except Exception as e:
        logging.error(f"Ошибка в api_click: {e}")
        return web.json_response({"success": False, "error": str(e)}, status=500)

async def api_buy(request):
    try:
        data = await request.json()
        uid, count = data.get('user_id'), data.get('count')
        cost = count * 100
        u = get_user(uid)
        if u and u['strawberry'] >= cost:
            conn = sqlite3.connect('gacha_game.db')
            conn.execute("UPDATE users SET strawberry=strawberry-?, spins=spins+? WHERE user_id=?", (cost, count, uid))
            conn.commit()
            return web.json_response({"success": True})
        return web.json_response({"success": False, "error": "Недостаточно клубники!"})
    except Exception as e:
        logging.error(f"Ошибка в api_buy: {e}")
        return web.json_response({"success": False, "error": str(e)}, status=500)

async def api_upgrade(request):
    try:
        uid = (await request.json()).get('user_id')
        u = get_user(uid)
        nxt = u['click_level'] + 1
        if nxt in UPGRADES and u['strawberry'] >= UPGRADES[nxt][0]:
            conn = sqlite3.connect('gacha_game.db')
            conn.execute("UPDATE users SET strawberry=strawberry-?, click_level=? WHERE user_id=?", (UPGRADES[nxt][0], nxt, uid))
            conn.commit()
            return web.json_response({"success": True})
        return web.json_response({"success": False, "error": "Недостаточно клубники или достигнут макс. уровень."})
    except Exception as e:
        logging.error(f"Ошибка в api_upgrade: {e}")
        return web.json_response({"success": False, "error": str(e)}, status=500)

async def api_spin(request):
    try:
        data = await request.json()
        uid = data.get('user_id')
        count = int(data.get('count', 1))
        
        result = do_spins_logic(uid, count)
        return web.json_response(result)
    except Exception as e:
        logging.error(f"Ошибка в api_spin: {e}")
        return web.json_response({"success": False, "error": str(e)}, status=500)


# --- ЗАПУСК СЕРВЕРА И БОТА ---
async def main():
    # Настраиваем логирование, чтобы видеть ошибки в консоли Render
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Настройка AIOHTTP веб-сервера
    app = web.Application()
    app.router.add_post('/api/get_user', api_get_user)
    app.router.add_post('/api/click', api_click)
    app.router.add_post('/api/buy', api_buy)
    app.router.add_post('/api/upgrade', api_upgrade)
    app.router.add_post('/api/spin', api_spin)
    # Подача статических файлов из папки webapp
    app.router.add_static('/', path='./webapp', show_index=True)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    
    # Запускаем веб-сервер и бот-polling одновременно!
    # asyncio.gather ждет завершения всех указанных задач.
    # Так как обе задачи работают бесконечно, они будут работать параллельно.
    await asyncio.gather(
        site.start(),          # Задача для запуска веб-сервера
        dp.start_polling(bot)  # Задача для запуска бота
    )

if __name__ == "__main__":
    asyncio.run(main())

