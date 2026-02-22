import sqlite3
import random
import os

# ИМЯ НОВОЙ БАЗЫ (изменили, чтобы создалась с нуля)
DB_NAME = 'gacha_v2.db'

# --- ТВОЙ СКЛАД ПЕРСОНАЖЕЙ ---
PETS_DATA = [
    ("Собака", "Фиолетовое", "assets/pets/dog.png", 0, ""),
    ("Кролик", "Фиолетовое", "assets/pets/bunny.png", 0, ""),
]

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, username TEXT, strawberry INTEGER DEFAULT 0, spins INTEGER DEFAULT 0,
        click_level INTEGER DEFAULT 1, pity_red INTEGER DEFAULT 50, pity_orange INTEGER DEFAULT 30,
        pity_yellow INTEGER DEFAULT 15, pity_green INTEGER DEFAULT 10, pity_lightblue INTEGER DEFAULT 5,
        pity_blue INTEGER DEFAULT 3, guaranteed_event INTEGER DEFAULT 0)''')
    
    # Таблица персонажей (со всеми колонками!)
    cursor.execute('''CREATE TABLE IF NOT EXISTS pets (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, rarity TEXT, image_url TEXT, 
        is_event INTEGER DEFAULT 0, skill TEXT)''')
    
    # Таблица инвентаря
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, pet_name TEXT, 
        pet_rarity TEXT, pet_image TEXT, pet_skill TEXT)''')
    
    conn.commit()
    seed_pets(cursor)
    conn.close()

def seed_pets(cursor):
    count = cursor.execute("SELECT COUNT(*) FROM pets").fetchone()[0]
    if count == 0:
        cursor.executemany("INSERT INTO pets (name, rarity, image_url, is_event, skill) VALUES (?,?,?,?,?)", PETS_DATA)
        print("Новая база заполнена персонажами!")

def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(user_id, username):
    conn = sqlite3.connect(DB_NAME)
    conn.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
    conn.commit()
    conn.close()

def do_spins_logic(user_id, count=1):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    u = get_user(user_id)
    if not u or u['spins'] < count: return {"success": False, "error": "Нет круток!"}
    results = []
    p = {'red': u['pity_red'], 'orange': u['pity_orange'], 'yellow': u['pity_yellow'], 
         'green': u['pity_green'], 'lightblue': u['pity_lightblue'], 'blue': u['pity_blue']}
    total_spins = u['spins']
    guar = u['guaranteed_event']

    for _ in range(count):
        total_spins -= 1
        for k in p: p[k] -= 1
        res_rarity = "Фиолетовое"
        if p['red'] <= 0: res_rarity = "Красное"
        elif p['orange'] <= 0: res_rarity = "Оранжевое"
        elif p['yellow'] <= 0: res_rarity = "Жёлтое"
        elif p['green'] <= 0: res_rarity = "Зеленое"
        elif p['lightblue'] <= 0: res_rarity = "Голубое"
        elif p['blue'] <= 0: res_rarity = "Синее"

        rmap = {"Красное":'red',"Оранжевое":'orange',"Жёлтое":'yellow',"Зеленое":'green',"Голубое":'lightblue',"Синее":'blue'}
        rval = {"Красное":50,"Оранжевое":30,"Жёлтое":15,"Зеленое":10,"Голубое":5,"Синее":3}
        if res_rarity in rmap: p[rmap[res_rarity]] = rval[res_rarity]

        pet = cursor.execute("SELECT name, rarity, image_url, skill FROM pets WHERE rarity=? ORDER BY RANDOM() LIMIT 1", (res_rarity,)).fetchone()
        
        if pet:
            cursor.execute("INSERT INTO user_inventory (user_id, pet_name, pet_rarity, pet_image, pet_skill) VALUES (?, ?, ?, ?, ?)",
                           (user_id, pet[0], pet[1], pet[2], pet[3]))
            results.append({"name": pet[0], "rarity": pet[1], "image_url": pet[2], "skill": pet[3]})
        else:
            results.append({"name": "Заглушка", "rarity": res_rarity, "image_url": "assets/strawberry.png", "skill": ""})

    cursor.execute('''UPDATE users SET spins=?, pity_red=?, pity_orange=?, pity_yellow=?, 
                      pity_green=?, pity_lightblue=?, pity_blue=? WHERE user_id=?''',
                   (total_spins, p['red'], p['orange'], p['yellow'], p['green'], p['lightblue'], p['blue'], user_id))
    conn.commit()
    conn.close()
    return {"success": True, "pets": results}
