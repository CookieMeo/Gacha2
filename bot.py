import logging, asyncio, os, sys, sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web
from db import init_db, get_user, create_user, do_gacha_spin

TOKEN = "8120653173:AAGIVbVAbbENlSvDt7ZOlsuSbtNRMDt1H-A"
ADMIN_USER_ID = 1562471251 # ТВОЙ ID
WEB_APP_URL = "https://gacha2-5ng0.onrender.com" # ПРОВЕРЬ СВОЙ URL
bot = Bot(token=TOKEN)
dp = Dispatcher()
init_db()

# Цены и сила клика
UPGRADES = {2:[10,2], 3:[40,3], 4:[90,4], 5:[160,5], 6:[250,6], 7:[360,7], 8:[490,8], 9:[640,9], 10:[810,10], 11:[4000,100]}

# 1. Сначала добавим маленькую функцию-обработчик для корня
async def handle_root(request):
    # Указываем путь к index.html
    return web.FileResponse(os.path.join(WEBAPP_PATH, 'index.html'))

async def start_web_server():
    app = web.Application()
    
    # 2. Добавляем ПЕРВЫМ делом обработчик для главной страницы
    # Теперь при заходе на https://.../ будет сразу открываться игра
    app.router.add_get('/', handle_root)
    
    app.router.add_get('/health', health_check)
    
    # 3. Раздаем статику для остальных файлов (js, css, картинки)
    # Убираем параметр show_index=True, чтобы список файлов больше не показывался
    app.router.add_static('/', path=WEBAPP_PATH, name='static')
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"✅ Сервер настроен. index.html открывается автоматически.")

@dp.message(Command("add_pet"))
async def add_pet(m: types.Message):
    if m.from_user.id != ADMIN_USER_ID: return
    try:
        a = m.text.split(maxsplit=1)[1].split(', ')
        conn = sqlite3.connect('gacha_game.db')
        conn.execute("INSERT INTO pets (name, rarity, image_url, is_event) VALUES (?,?,?,?)", (a[0], a[1], a[2], int(a[3])))
        conn.commit()
        await m.answer("✅ Питомец добавлен!")
    except: await m.answer("Формат: Имя, Красное, url, 1")

@dp.message(Command("add_promo"))
async def add_promo(m: types.Message):
    if m.from_user.id != ADMIN_USER_ID: return
    try:
        a = m.text.split(maxsplit=1)[1].split(', ')
        conn = sqlite3.connect('gacha_game.db')
        conn.execute("INSERT INTO promocodes VALUES (?,?,?,?)", (a[0], int(a[1]), int(a[2]), int(a[3])))
        conn.commit()
        await m.answer("✅ Промокод добавлен!")
    except: await m.answer("Формат: КОД, клубника, крутки, кол-во")

async def api_get_user(request):
    d = await request.json()
    u = get_user(d['user_id'])
    if not u: create_user(d['user_id'], "User"); u = get_user(d['user_id'])
    return web.json_response(u)

async def api_click(request):
    data = await request.json()
    uid = data.get('user_id')
    
    # Проверяем, существует ли пользователь, если нет — создаем
    u = get_user(uid)
    if not u:
        create_user(uid, "Игрок")
        u = get_user(uid)
        
    # Считаем силу клика (по твоей таблице)
    # Если уровня нет в списке, даем 1 клубнику (для 1 уровня)
    power = UPGRADES.get(u['click_level'], [0, 1])[1]
    if u['click_level'] >= 11: power = 100

    conn = sqlite3.connect('gacha_game.db')
    conn.execute("UPDATE users SET strawberry = strawberry + ? WHERE user_id = ?", (power, uid))
    conn.commit()
    conn.close()
    return web.json_response({"success": True})


async def api_buy(request):
    d = await request.json(); uid, count = d['user_id'], d['count']
    cost = count * 100
    u = get_user(uid)
    if u['strawberry'] >= cost:
        conn = sqlite3.connect('gacha_game.db')
        conn.execute("UPDATE users SET strawberry=strawberry-?, spins=spins+? WHERE user_id=?", (cost, count, uid))
        conn.commit()
        return web.json_response({"success": True})
    return web.json_response({"success": False})

async def api_upgrade(request):
    uid = (await request.json())['user_id']
    u = get_user(uid)
    nxt = u['click_level'] + 1
    if nxt in UPGRADES and u['strawberry'] >= UPGRADES[nxt][0]:
        conn = sqlite3.connect('gacha_game.db')
        conn.execute("UPDATE users SET strawberry=strawberry-?, click_level=? WHERE user_id=?", (UPGRADES[nxt][0], nxt, uid))
        conn.commit()
        return web.json_response({"success": True})
    return web.json_response({"success": False})

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

async def main():
    app = web.Application()
    app.router.add_post('/api/get_user', api_get_user)
    app.router.add_post('/api/click', api_click)
    app.router.add_post('/api/buy', api_buy)
    app.router.add_post('/api/upgrade', api_upgrade)
    app.router.add_post('/api/spin', api_spin)
    app.router.add_static('/', path='./webapp', show_index=True)
    runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()
    await dp.start_polling(bot)


if __name__ == "__main__": asyncio.run(main()) 








