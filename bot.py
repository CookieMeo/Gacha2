import logging, asyncio, os, sys, sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo
from aiohttp import web
from db import init_db, get_user, create_user, do_spins

TOKEN = "8120653173:AAGIVbVAbbENlSvDt7ZOlsuSbtNRMDt1H-A"
ADMIN_USER_ID = 1562471251 # ТВОЙ ID
WEB_APP_URL = "https://gacha2-5ng0.onrender.com" # ПРОВЕРЬ СВОЙ URL

bot = Bot(token=TOKEN)
dp = Dispatcher()
init_db()

# --- АДМИН КОМАНДЫ ---
@dp.message(Command("add_pet"))
async def add_pet(m: types.Message):
    if m.from_user.id != ADMIN_USER_ID: return
    # Формат: /add_pet Имя, Редкость, URL, 0(станд)/1(ивент)
    try:
        a = m.text.split(maxsplit=1)[1].split(', ')
        conn = sqlite3.connect('gacha_game.db')
        conn.execute("INSERT INTO pets (name, rarity, image_url, is_event) VALUES (?,?,?,?)", (a[0], a[1], a[2], int(a[3])))
        conn.commit()
        await m.answer("✅ Добавлено!")
    except: await m.answer("Ошибка! Формат: Имя, Красное, url, 1")

@dp.message(Command("add_promo"))
async def add_promo(m: types.Message):
    if m.from_user.id != ADMIN_USER_ID: return
    try:
        a = m.text.split(maxsplit=1)[1].split(', ')
        conn = sqlite3.connect('gacha_game.db')
        conn.execute("INSERT INTO promocodes VALUES (?,?,?,?)", (a[0], int(a[1]), int(a[2]), int(a[3])))
        conn.commit()
        await m.answer("✅ Промокод добавлен!")
    except: await m.answer("Ошибка! Формат: КОД, клубника, крутки, кол-во")

# --- API ДЛЯ МИНИ-АПП ---
async def api_get_user(request):
    uid = (await request.json()).get('user_id')
    return web.json_response(get_user(uid))

async def api_click(request):
    uid = (await request.json()).get('user_id')
    u = get_user(uid)
    power = 100 if u['click_level'] == 11 else u['click_level']
    conn = sqlite3.connect('gacha_game.db')
    conn.execute("UPDATE users SET strawberry = strawberry + ? WHERE user_id = ?", (power, uid))
    conn.commit()
    return web.json_response({"success": True, "strawberry": u['strawberry'] + power})

async def api_spin(request):
    d = await request.json()
    return web.json_response(do_spins(d['user_id'], d.get('count', 1)))

async def api_buy_spins(request):
    d = await request.json()
    cost = d['count'] * 100
    u = get_user(d['user_id'])
    if u['strawberry'] >= cost:
        conn = sqlite3.connect('gacha_game.db')
        conn.execute("UPDATE users SET strawberry=strawberry-?, spins=spins+? WHERE user_id=?", (cost, d['count'], d['user_id']))
        conn.commit()
        return web.json_response({"success": True})
    return web.json_response({"success": False})

async def api_upgrade(request):
    uid = (await request.json()).get('user_id')
    u = get_user(uid)
    costs = {2:10, 3:40, 4:90, 5:160, 6:250, 7:360, 8:490, 9:640, 10:810, 11:4000}
    next_lvl = u['click_level'] + 1
    if next_lvl in costs and u['strawberry'] >= costs[next_lvl]:
        conn = sqlite3.connect('gacha_game.db')
        conn.execute("UPDATE users SET strawberry=strawberry-?, click_level=? WHERE user_id=?", (costs[next_lvl], next_lvl, uid))
        conn.commit()
        return web.json_response({"success": True})
    return web.json_response({"success": False})

# --- ЗАПУСК СЕРВЕРА ---
async def main():
    app = web.Application()
    app.router.add_post('/api/get_user', api_get_user)
    app.router.add_post('/api/click', api_click)
    app.router.add_post('/api/spin', api_spin)
    app.router.add_post('/api/buy', api_buy_spins)
    app.router.add_post('/api/upgrade', api_upgrade)
    app.router.add_static('/', path='./webapp', show_index=True)
    
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
