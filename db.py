import sqlite3
import random

def init_db():
    conn = sqlite3.connect('gacha_game.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, username TEXT, strawberry INTEGER DEFAULT 0, spins INTEGER DEFAULT 0,
        click_level INTEGER DEFAULT 1, pity_red INTEGER DEFAULT 50, pity_orange INTEGER DEFAULT 30,
        pity_yellow INTEGER DEFAULT 15, pity_green INTEGER DEFAULT 10, pity_lightblue INTEGER DEFAULT 5,
        pity_blue INTEGER DEFAULT 3, guaranteed_event INTEGER DEFAULT 0)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS pets (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, rarity TEXT, image_url TEXT, is_event INTEGER DEFAULT 0)''')
    
    # ТАБЛИЦА ИНВЕНТАРЯ
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, pet_name TEXT, pet_rarity TEXT, pet_image TEXT)''')
    
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

def do_spins_logic(user_id, count=1):
    conn = sqlite3.connect('gacha_game.db')
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

        # Сброс гарантов
        rmap = {"Красное":'red',"Оранжевое":'orange',"Жёлтое":'yellow',"Зеленое":'green',"Голубое":'lightblue',"Синее":'blue'}
        rval = {"Красное":50,"Оранжевое":30,"Жёлтое":15,"Зеленое":10,"Голубое":5,"Синее":3}
        if res_rarity in rmap: p[rmap[res_rarity]] = rval[res_rarity]

        pet = cursor.execute("SELECT name, rarity, image_url FROM pets WHERE rarity=? ORDER BY RANDOM() LIMIT 1", (res_rarity,)).fetchone()
        
        if pet:
            # СОХРАНЯЕМ В ИНВЕНТАРЬ (строго соблюдай отступы - 12 пробелов здесь)
            cursor.execute("INSERT INTO user_inventory (user_id, pet_name, pet_rarity, pet_image) VALUES (?, ?, ?, ?)",
                           (user_id, pet[0], pet[1], pet[2]))
            results.append({"name": pet[0], "rarity": pet[1], "image_url": pet[2]})
        else:
            results.append({"name": "Обычный Кот", "rarity": res_rarity, "image_url": "assets/strawberry.png"})

    cursor.execute('''UPDATE users SET spins=?, pity_red=?, pity_orange=?, pity_yellow=?, 
                      pity_green=?, pity_lightblue=?, pity_blue=? WHERE user_id=?''',
                   (total_spins, p['red'], p['orange'], p['yellow'], p['green'], p['lightblue'], p['blue'], user_id))
    conn.commit()
    conn.close()
    return {"success": True, "pets": results}
