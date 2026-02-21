import sqlite3
import random

def init_db():
    conn = sqlite3.connect('gacha_game.db')
    cursor = conn.cursor()
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            strawberry INTEGER DEFAULT 0,
            spins INTEGER DEFAULT 0,
            click_level INTEGER DEFAULT 1,
            pity_red INTEGER DEFAULT 50,
            pity_orange INTEGER DEFAULT 30,
            pity_yellow INTEGER DEFAULT 15,
            pity_green INTEGER DEFAULT 10,
            pity_lightblue INTEGER DEFAULT 5,
            pity_blue INTEGER DEFAULT 3,
            guaranteed_event INTEGER DEFAULT 0
        )
    ''')
    # Таблица питомцев
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, rarity TEXT, image_url TEXT, is_event INTEGER DEFAULT 0
        )
    ''')
    # Таблица промокодов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS promocodes (
            code TEXT PRIMARY KEY, reward_strawberry INTEGER, reward_spins INTEGER, uses INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('gacha_game.db')
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(user_id, username):
    conn = sqlite3.connect('gacha_game.db')
    conn.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
    conn.commit()
    conn.close()

def do_spins(user_id, count=1):
    conn = sqlite3.connect('gacha_game.db')
    cursor = conn.cursor()
    user = get_user(user_id)
    if user['spins'] < count: return {"success": False, "error": "Недостаточно круток"}

    results = []
    # Копируем текущие счетчики
    spins = user['spins']
    p_red = user['pity_red']
    p_ora = user['pity_orange']
    p_yel = user['pity_yellow']
    p_gre = user['pity_green']
    p_lbu = user['pity_lightblue']
    p_blu = user['pity_blue']
    guar = user['guaranteed_event']

    for _ in range(count):
        spins -= 1
        # Уменьшаем все счетчики
        p_red -= 1; p_ora -= 1; p_yel -= 1; p_gre -= 1; p_lbu -= 1; p_blu -= 1
        
        # Определяем редкость по приоритету
        res_rarity = "Фиолетовое" # Дефолт
        if p_red <= 0: res_rarity = "Красное"
        elif p_ora <= 0: res_rarity = "Оранжевое"
        elif p_yel <= 0: res_rarity = "Жёлтое"
        elif p_gre <= 0: res_rarity = "Зеленое"
        elif p_lbu <= 0: res_rarity = "Голубое"
        elif p_blu <= 0: res_rarity = "Синее"
        
        # Сброс счетчика выпавшей редкости
        if res_rarity == "Красное":
            # Логика 50/50
            is_event = 0
            if guar == 1 or random.random() < 0.5:
                is_event = 1; guar = 0
            else: guar = 1
            pet = cursor.execute("SELECT * FROM pets WHERE rarity='Красное' AND is_event=? ORDER BY RANDOM() LIMIT 1", (is_event,)).fetchone()
            p_red = 50
        else:
            pet = cursor.execute("SELECT * FROM pets WHERE rarity=? ORDER BY RANDOM() LIMIT 1", (res_rarity,)).fetchone()
            # Сброс счетчиков
            if res_rarity == "Оранжевое": p_ora = 30
            if res_rarity == "Жёлтое": p_yel = 15
            if res_rarity == "Зеленое": p_gre = 10
            if res_rarity == "Голубое": p_lbu = 5
            if res_rarity == "Синее": p_blu = 3

        pet_data = dict(pet) if pet else {"name": "Пусто", "rarity": res_rarity}
        results.append(pet_data)

    cursor.execute('''UPDATE users SET spins=?, pity_red=?, pity_orange=?, pity_yellow=?, 
                      pity_green=?, pity_lightblue=?, pity_blue=?, guaranteed_event=? WHERE user_id=?''',
                   (spins, p_red, p_ora, p_yel, p_gre, p_lbu, p_blu, guar, user_id))
    conn.commit()
    conn.close()
    return {"success": True, "pets": results}
