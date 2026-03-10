import logging, asyncio, os, sqlite3, sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo
from aiohttp import web
import json
import db # Предполагаем, что там функции работы с БД

# Пытаемся импортировать базу данных. Если db.py содержит синтаксическую ошибку,
# это вызовет ImportError и выведет сообщение.
try:
    from db import init_db, get_user, create_user, DB_NAME, do_spins_logic, get_all_pets_data
except ImportError as e:
    print(f"КРИТИЧЕСКАЯ ОШИБКА: Не удалось импортировать db.py. Проверьте db.py на синтаксические ошибки. Ошибка: {e}", file=sys.stderr)
    sys.exit(1)

TOKEN = "8226800067:AAH3KAaK4-VIcXh8GijTRd5sCRKQQ2MJ510" # !!! ЗАМЕНИ НА СВОЙ ТОКЕН !!!
ADMIN_USER_ID = 1562471251 # !!! ЗАМЕНИ НА СВОЙ ID !!!
app = web.Application()
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Уровни улучшений кликера
UPGRADE_COSTS = {
    1: [0, 1],    # Уровень 1: 0 клубники, +1 за клик
    2: [10, 2],   # Уровень 2: 10 клубники, +2 за клик
    3: [40, 3],   # Уровень 3: 40 клубники, +3 за клик
    4: [90, 4], 
    5: [160, 5], 
    6: [250, 6], 
    7: [360, 7], 
    8: [490, 8], 
    9: [640, 9], 
    10: [810, 10],
    11: [4000, 100] # Максимальный уровень
}

# --- API ЭНДПОИНТЫ ---

async def get_user_data(request):
    user_id = int(request.match_info['user_id'])
    user = db.get_user(user_id)
    
    if not user:
        # Если пользователя нет, создаем его с дефолтными статами
        db.create_user(user_id)
        user = db.get_user(user_id)
        
    return web.json_response(user)

async def update_user_data(request):
    data = await request.json()
    user_id = data.get('user_id')
    clicks = data.get('clicks')
    level = data.get('level')
    
    db.update_stats(user_id, clicks, level)
    return web.json_response({"status": "ok"})

async def api_click(request):
    try:
        uid = (await request.json()).get('user_id')
        u = get_user(uid)
        if not u: 
            # Создаем пользователя, если его нет. Хотя api_get_user должен сделать это раньше.
            create_user(uid, "Игрок")
            u = get_user(uid)
        
        power = UPGRADE_COSTS.get(u.get('click_level', 1), [0, 1])[1]
        conn = sqlite3.connect(DB_NAME)
        # Обновляем клубнику и total_clicks
        conn.execute("UPDATE users SET strawberry=strawberry+?, total_clicks=total_clicks+1 WHERE user_id=?", (power, uid))
        conn.commit()
        conn.close()
        return web.json_response({"success": True})
    except Exception as e:
        logging.error(f"API ERROR in /click: {e}", exc_info=True)
        return web.json_response({"success": False, "error": "Серверная ошибка при клике"}, status=500)

async def api_get_inventory(request):
    try:
        uid = (await request.json()).get('user_id')
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        items = conn.execute("SELECT pet_name, pet_rarity, pet_image FROM user_inventory WHERE user_id = ? ORDER BY id DESC", (uid,)).fetchall()
        conn.close()
        return web.json_response([dict(ix) for ix in items])
    except Exception as e:
        logging.error(f"API ERROR in /get_inventory: {e}", exc_info=True)
        return web.json_response([], status=200) # Возвращаем пустой список при ошибке, чтобы фронтенд не падал

async def api_buy(request):
    try:
        data = await request.json()
        uid, count = data.get('user_id'), data.get('count')
        # Словарь стоимости круток
        costs = {1: 100, 5: 500, 10: 1000, 40: 4000, 100: 10000}
        cost = costs.get(count, 99999999) # Очень большое число, если count некорректный
        
        u = get_user(uid)
        if u and u.get('strawberry', 0) >= cost:
            conn = sqlite3.connect(DB_NAME)
            # Обновляем клубнику, крутки и spent_strawberry
            conn.execute("UPDATE users SET strawberry=strawberry-?, spins=spins+?, spent_strawberry=spent_strawberry+? WHERE user_id=?", 
                         (cost, count, cost, uid))
            conn.commit()
            conn.close()
            return web.json_response({"success": True})
        return web.json_response({"success": False, "error": "Недостаточно клубники"})
    except Exception as e:
        logging.error(f"API ERROR in /buy: {e}", exc_info=True)
        return web.json_response({"success": False, "error": "Серверная ошибка при покупке"}, status=500)

async def api_upgrade(request):
    try:
        uid = (await request.json()).get('user_id')
        u = get_user(uid)
        if not u: return web.json_response({"success": False, "error": "Пользователь не найден"})

        current_level = u.get('click_level', 1)
        next_level = current_level + 1
        
        # Проверяем, не достигнут ли максимальный уровень
        if next_level > max(UPGRADE_COSTS.keys()):
            return web.json_response({"success": False, "error": "Достигнут максимальный уровень!"})

        cost = UPGRADE_COSTS.get(next_level, [99999999, 0])[0] # Стоимость следующего уровня
        
        if u.get('strawberry', 0) >= cost:
            conn = sqlite3.connect(DB_NAME)
            # Обновляем клубнику и уровень клика
            conn.execute("UPDATE users SET strawberry=strawberry-?, click_level=? WHERE user_id=?", (cost, next_level, uid))
            conn.commit()
            conn.close()
            return web.json_response({"success": True})
        return web.json_response({"success": False, "error": "Недостаточно клубники!"})
    except Exception as e:
        logging.error(f"API ERROR in /upgrade: {e}", exc_info=True)
        return web.json_response({"success": False, "error": "Серверная ошибка при улучшении"}, status=500)

async def api_spin(request):
    try:
        data = await request.json()
        uid = data.get('user_id')
        count = int(data.get('count', 1))
        banner_id = int(data.get('banner_id', 1)) # Получаем ID баннера
        
        result = do_spins_logic(uid, count, banner_id) # Передаем banner_id
        return web.json_response(result)
    except Exception as e:
        logging.error(f"API ERROR in /spin: {e}", exc_info=True)
        return web.json_response({"success": False, "error": "Серверная ошибка при крутке"}, status=500)

async def api_claim_promo(request):
    try:
        data = await request.json()
        uid, code = data.get('user_id'), data.get('code')
        conn = sqlite3.connect(DB_NAME)
        
        promo = conn.execute("SELECT reward_type, reward_amount FROM promo_codes WHERE code=?", (code,)).fetchone()
        if not promo:
            conn.close()
            return web.json_response({"success": False, "error": "Промокод не найден"})
        
        used = conn.execute("SELECT 1 FROM used_promos WHERE user_id=? AND code=?", (uid, code)).fetchone()
        if used:
            conn.close()
            return web.json_response({"success": False, "error": "Промокод уже использован"})
        
        # Начисляем награду
        col = "spins" if promo[0] == "spins" else "strawberry" # reward_type: "spins" или "strawberry"
        conn.execute(f"UPDATE users SET {col}={col}+? WHERE user_id=?", (promo[1], uid))
        conn.execute("INSERT INTO used_promos (user_id, code) VALUES (?, ?)", (uid, code))
        conn.commit()
        conn.close()
        return web.json_response({"success": True, "msg": f"Получено: {promo[1]} {promo[0]}"})
    except Exception as e:
        logging.error(f"API ERROR in /claim_promo: {e}", exc_info=True)
        return web.json_response({"success": False, "error": "Серверная ошибка при активации промокода"}, status=500)

async def api_get_all_pets(request):
    try:
        # Эта функция не требует user_id, возвращает список всех возможных питомцев
        all_pets = get_all_pets_data()
        return web.json_response(all_pets)
    except Exception as e:
        logging.error(f"API ERROR in /get_all_pets: {e}", exc_info=True)
        return web.json_response([], status=500)

async def handle_index(request):
    # Указываем путь к индексу внутри папки webapp
    return web.FileResponse('webapp/index.html')



# --- КОМАНДЫ БОТА ---

@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    # Если username пользователя не доступен, используем "Игрок"
    username_to_set = m.from_user.username if m.from_user.username else "Игрок"
    create_user(m.from_user.id, username_to_set)
    # URL для WebApp должен быть тот, который дает Render (твоя ссылка gacha-iifj.onrender.com)
    kb = types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="🚀 Играть", web_app=WebAppInfo(url="https://gacha-iifj.onrender.com"))]], resize_keyboard=True)
    await m.answer(f"Привет, {username_to_set}! Добро пожаловать в гача-игру.", reply_markup=kb)

@dp.message(Command("add_promo"))
async def add_promo_command(m: types.Message):
    if m.from_user.id != ADMIN_ID: # Проверяем, что команду вводит админ
        await m.answer("У вас нет прав для этой команды.")
        return
    try:
        # Пример: /add_promo MYCODE spins 100
        parts = m.text.split()
        if len(parts) != 4:
            await m.answer("Неверный формат. Используйте: /add_promo КОД ТИП_НАГРАДЫ КОЛИЧЕСТВО (пример: /add_promo FREEBIE spins 50)")
            return
        
        _, code, reward_type, amount_str = parts
        amount = int(amount_str)
        if reward_type not in ["spins", "strawberry"]:
            await m.answer("Тип награды может быть только 'spins' или 'strawberry'.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO promo_codes (code, reward_type, reward_amount) VALUES (?, ?, ?)", (code, reward_type, amount))
        conn.commit()
        conn.close()
        await m.answer(f"✅ Промокод '{code}' создан: {amount} {reward_type}.")
    except Exception as e:
        logging.error(f"Error in /add_promo command: {e}", exc_info=True)
        await m.answer(f"Произошла ошибка при создании промокода: {e}")

# --- ЗАПУСК СЕРВЕРА И БОТА ---

async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        init_db() # Инициализируем базу данных
        
        # Проверяем наличие папки webapp
        if not os.path.exists('./webapp'):
            logging.critical("ОШИБКА: Папка './webapp' не найдена! Убедитесь, что она существует в корне проекта.")
            sys.exit(1)
        if not os.path.exists('./webapp/index.html'):
            logging.critical("ОШИБКА: Файл './webapp/index.html' не найден!")
            sys.exit(1)

        # Регистрация всех маршрутов API
        app.router.add_get('/', lambda r: web.FileResponse('./webapp/index.html'))
        app.router.add_get('/', handle_index)
        app.router.add_static('/', path='webapp', name='static')
        app.router.add_get('/api/user/{user_id}', get_user_handler)
        app.router.add_get('/', index)
        app.router.add_post('/api/update', update_user_data)
        app.router.add_post('/api/update', update_user_handler)
        app.router.add_post('/api/click', api_click)
        app.router.add_post('/api/buy', api_buy)
        app.router.add_post('/api/upgrade', api_upgrade)
        app.router.add_post('/api/spin', api_spin)
        app.router.add_post('/api/get_inventory', api_get_inventory)
        app.router.add_post('/api/claim_promo', api_claim_promo)
        app.router.add_post('/api/get_all_pets', api_get_all_pets) # <-- ЭТО ОЧЕНЬ ВАЖНО

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        # Используем название твоей папки - 'webapp'
        webapp_path = os.path.join(BASE_DIR, 'webapp')

        # Регистрация статических файлов (CSS, JS, картинки)
        app.router.add_static('/', path='./webapp', show_index=False)
        app.router.add_static('/webapp/', webapp_path, name='webapp') 
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        port = int(os.environ.get("PORT", 10000))
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        
        logging.info(f"--- WEB SERVER STARTED ON PORT {port} ---")
        await dp.start_polling(bot) # Запускаем бота
    except Exception as e:
        logging.critical(f"КРИТИЧЕСКАЯ ОШИБКА ПРИ ЗАПУСКЕ БОТА: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Server started on port {port}")
    web.run_app(app, port=port)






