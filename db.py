import sqlite3
import random

DB_NAME = 'gacha_v21.db'

PETS_DATA = [
    ("Собака", "Фиолетовое", "assets/pets/dog.png", 0, ""),
    ("Кошка", "Фиолетовое", "assets/pets/cat.png", 0, ""),
    ("Божья коровка", "Фиолетовое", "assets/pets/ladybag.png", 0, ""),
    
    ("Мышь", "Синее", "assets/pets/mouse.png", 0, ""),
    ("Хомяк", "Синее", "assets/pets/hamster.png", 0, ""),
    
    ("Кролик", "Голубое", "assets/pets/bunny.png", 0, ""),
    ("Улитка", "Голубое", "assets/pets/snail.png", 0, ""),
    ("Пчела", "Голубое", "assets/pets/bee.png", 0, ""),
    
    ("Черепаха", "Зеленое", "assets/pets/turtle.png", 0, ""),
    ("Слон", "Зеленое", "assets/pets/elephant.png", 0, ""),
    ("Медведь", "Зеленое", "assets/pets/bear.png", 0, ""),
    
    ("Змея", "Желтое", "assets/pets/snake.png", 0, ""),
    ("Попугай", "Желтое", "assets/pets/parrot.png", 0, ""),
    ("Жираф", "Желтое", "assets/pets/giraffe.png", 0, ""),
    
    ("Летучая мышь", "Оранжевое", "assets/pets/bat.png", 0, ""),
    ("Акула", "Оранжевое", "assets/pets/shark.png", 0, ""),
    
    ("Единорог", "Красное", "assets/pets/unicorn.png", 0, ""),
    ("Дракон", "Красное", "assets/pets/dragon.png", 0, ""),
    ("Паук", "Красное", "assets/pets/spider.png", 0, ""),
    ("Феникс", "Красное", "assets/pets/phoenix.png", 1, ""),
    ("Цербер", "Красное", "assets/pets/cerberus.png", 1, "")
]

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, username TEXT, strawberry INTEGER DEFAULT 0, spins INTEGER DEFAULT 0,
        click_level INTEGER DEFAULT 1, pity_red INTEGER DEFAULT 50, pity_orange INTEGER DEFAULT 30, 
        pity_yellow INTEGER DEFAULT 15, pity_green INTEGER DEFAULT 10, pity_lightblue INTEGER DEFAULT 5, 
        pity_blue INTEGER DEFAULT 3, guaranteed_event INTEGER DEFAULT 0,
        total_clicks INTEGER DEFAULT 0, total_spent INTEGER DEFAULT 0, total_spins_bought INTEGER DEFAULT 0,
        total_gacha_pulls INTEGER DEFAULT 0, total_pets_obtained INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS pets (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, rarity TEXT, image_url TEXT, 
        is_event INTEGER DEFAULT 0, skill TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, pet_name TEXT, 
        pet_rarity TEXT, pet_image TEXT, pet_skill TEXT)''')
    conn.commit()
    # Заполнение персонажами
    if cursor.execute("SELECT COUNT(*) FROM pets").fetchone()[0] == 0:
        cursor.executemany("INSERT INTO pets (name, rarity, image_url, is_event, skill) VALUES (?,?,?,?,?)", PETS_DATA)
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(user_id, username):
    conn = sqlite3.connect(DB_NAME)
    conn.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, str(username)))
    conn.commit()
    conn.close()

def do_spins_logic(user_id, count=1):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    u = get_user(user_id)
    if not u or u['spins'] < count:
        conn.close()
        return {"success": False, "error": "Недостаточно круток!"}
    
    results = []
    p = {'red': u.get('pity_red', 50), 'orange': u.get('pity_orange', 30), 'yellow': u.get('pity_yellow', 15),
         'green': u.get('pity_green', 10), 'lightblue': u.get('pity_lightblue', 5), 'blue': u.get('pity_blue', 3)}

    for _ in range(count):
        res_rarity = "Фиолетовое"
        for k in p: p[k] -= 1
        if p['red'] <= 0: res_rarity, p['red'] = "Красное", 50
        elif p['orange'] <= 0: res_rarity, p['orange'] = "Оранжевое", 30
        elif p['yellow'] <= 0: res_rarity, p['yellow'] = "Жёлтое", 15
        elif p['green'] <= 0: res_rarity, p['green'] = "Зеленое", 10
        elif p['lightblue'] <= 0: res_rarity, p['lightblue'] = "Голубое", 5
        elif p['blue'] <= 0: res_rarity, p['blue'] = "Синее", 3
        
        pet = cursor.execute("SELECT name, rarity, image_url, skill FROM pets WHERE rarity=? ORDER BY RANDOM() LIMIT 1", (res_rarity,)).fetchone()
        if not pet: pet = cursor.execute("SELECT name, rarity, image_url, skill FROM pets ORDER BY RANDOM() LIMIT 1").fetchone()
        
        if pet:
            cursor.execute("INSERT INTO user_inventory (user_id, pet_name, pet_rarity, pet_image, pet_skill) VALUES (?, ?, ?, ?, ?)",
                           (user_id, pet[0], pet[1], pet[2], pet[3]))
            results.append({"name": pet[0], "rarity": pet[1], "image_url": pet[2]})

    cursor.execute('''UPDATE users SET spins=spins-?, pity_red=?, pity_orange=?, pity_yellow=?, 
                      pity_green=?, pity_lightblue=?, pity_blue=?, 
                      total_gacha_pulls=total_gacha_pulls+?, total_pets_obtained=total_pets_obtained+? WHERE user_id=?''',
                   (count, p['red'], p['orange'], p['yellow'], p['green'], p['lightblue'], p['blue'], count, count, user_id))
    conn.commit()
    conn.close()
    return {"success": True, "pets": results}
