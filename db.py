import sqlite3
import random

def init_db():
    conn = sqlite3.connect('gacha_game.db')
    cursor = conn.cursor()
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
    cursor.execute('CREATE TABLE IF NOT EXISTS pets (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, rarity TEXT, image_url TEXT, is_event INTEGER DEFAULT 0)')
    cursor.execute('CREATE TABLE IF NOT EXISTS promocodes (code TEXT PRIMARY KEY, reward_strawberry INTEGER, reward_spins INTEGER, uses INTEGER)')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('gacha_game.db')
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def do_gacha_spin(user_id):
    conn = sqlite3.connect('gacha_game.db')
    cursor = conn.cursor()
    u = get_user(user_id)
    
    # Уменьшаем счетчики
    p = {
        'red': u['pity_red'] - 1, 'orange': u['pity_orange'] - 1, 
        'yellow': u['pity_yellow'] - 1, 'green': u['pity_green'] - 1,
        'lightblue': u['pity_lightblue'] - 1, 'blue': u['pity_blue'] - 1
    }
    
    res_rarity = "Фиолетовое"
    # Приоритет редкостей
    if p['red'] <= 0: res_rarity = "Красное"
    elif p['orange'] <= 0: res_rarity = "Оранжевое"
    elif p['yellow'] <= 0: res_rarity = "Жёлтое"
    elif p['green'] <= 0: res_rarity = "Зеленое"
    elif p['lightblue'] <= 0: res_rarity = "Голубое"
    elif p['blue'] <= 0: res_rarity = "Синее"

    # Сброс только выпавшей редкости
    resets = {"Красное":'red', "Оранжевое":'orange', "Жёлтое":'yellow', "Зеленое":'green', "Голубое":'lightblue', "Синее":'blue'}
    if res_rarity in resets:
        p[resets[res_rarity]] = {"Красное":50, "Оранжевое":30, "Жёлтое":15, "Зеленое":10, "Голубое":5, "Синее":3}[res_rarity]

    # Логика 50/50 для красного
    guar = u['guaranteed_event']
    is_event_pull = 0
    if res_rarity == "Красное":
        if guar == 1 or random.random() < 0.5:
            is_event_pull = 1
            guar = 0
        else:
            guar = 1

    pet = cursor.execute("SELECT * FROM pets WHERE rarity=? AND is_event=? ORDER BY RANDOM() LIMIT 1", (res_rarity, is_event_pull)).fetchone()
    if not pet: pet = cursor.execute("SELECT * FROM pets WHERE rarity=? ORDER BY RANDOM() LIMIT 1", (res_rarity,)).fetchone()
    
    cursor.execute('''UPDATE users SET pity_red=?, pity_orange=?, pity_yellow=?, pity_green=?, 
                      pity_lightblue=?, pity_blue=?, guaranteed_event=? WHERE user_id=?''',
                   (p['red'], p['orange'], p['yellow'], p['green'], p['lightblue'], p['blue'], guar, user_id))
    conn.commit()
    conn.close()
    return dict(pet) if pet else {"name": f"Пусто ({res_rarity})", "rarity": res_rarity}
