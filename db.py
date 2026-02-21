import sqlite3

def init_db():
    conn = sqlite3.connect('gacha_game.db')
    cursor = conn.cursor()
    
    # Таблица пользователей с новыми полями
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
            name TEXT,
            rarity TEXT,
            image_url TEXT,
            is_event INTEGER DEFAULT 0
        )
    ''')
    
    # Таблица промокодов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS promocodes (
            code TEXT PRIMARY KEY,
            reward_strawberry INTEGER,
            reward_spins INTEGER,
            uses_left INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Функция получения данных пользователя
def get_user(user_id):
    conn = sqlite3.connect('gacha_game.db')
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

# --- ЛОГИКА ГАЧИ С ГАРАНТОМ ---
def process_spin(user_id):
    conn = sqlite3.connect('gacha_game.db')
    cursor = conn.cursor()
    user = get_user(user_id)
    
    if user['spins'] < 1:
        return {"success": False, "error": "Нет круток"}

    # Уменьшаем крутки и все счетчики гаранта
    new_spins = user['spins'] - 1
    pity = {
        'red': user['pity_red'] - 1,
        'orange': user['pity_orange'] - 1,
        'yellow': user['pity_yellow'] - 1,
        'green': user['pity_green'] - 1,
        'lightblue': user['pity_lightblue'] - 1,
        'blue': user['pity_blue'] - 1
    }

    rarity_to_give = "Фиолетовое" # Обычный по умолчанию
    
    # Проверка приоритета гаранта (от высшего к низшему)
    if pity['red'] <= 0: rarity_to_give = "Красное"
    elif pity['orange'] <= 0: rarity_to_give = "Оранжевое"
    elif pity['yellow'] <= 0: rarity_to_give = "Жёлтое"
    elif pity['green'] <= 0: rarity_to_give = "Зеленое"
    elif pity['lightblue'] <= 0: rarity_to_give = "Голубое"
    elif pity['blue'] <= 0: rarity_to_give = "Синее"
    else:
        # Если гаранта нет, можно добавить рандом, но по условию 
        # здесь мы просто ждем выполнения гаранта или даем дефолт
        import random
        if random.random() < 0.01: rarity_to_give = "Красное" # 1% шанс случайно

    # Сброс счетчика выпавшей редкости
    resets = {"Красное": 50, "Оранжевое": 30, "Жёлтое": 15, "Зеленое": 10, "Голубое": 5, "Синее": 3}
    if rarity_to_give in resets:
        pity[rarity_to_give.lower()] = resets[rarity_to_give]

    # Логика 50/50 для красного
    pet_query = "SELECT * FROM pets WHERE rarity = ? "
    is_guaranteed = user['guaranteed_event']
    new_guaranteed = is_guaranteed

    if rarity_to_give == "Красное":
        import random
        if is_guaranteed or random.random() < 0.5:
            pet_query += "AND is_event = 1"
            new_guaranteed = 0
        else:
            pet_query += "AND is_event = 0"
            new_guaranteed = 1
    
    pet = conn.execute(pet_query + " ORDER BY RANDOM() LIMIT 1", (rarity_to_give,)).fetchone()
    
    if not pet: # Если в базе нет питомца такой редкости
        pet = {"name": "Загадочное существо", "rarity": rarity_to_give, "image_url": ""}
    else:
        pet = dict(pet)

    cursor.execute('''
        UPDATE users SET spins = ?, pity_red = ?, pity_orange = ?, pity_yellow = ?, 
        pity_green = ?, pity_lightblue = ?, pity_blue = ?, guaranteed_event = ?
        WHERE user_id = ?
    ''', (new_spins, pity['red'], pity['orange'], pity['yellow'], pity['green'], 
          pity['lightblue'], pity['blue'], new_guaranteed, user_id))
    
    conn.commit()
    conn.close()
    return {"success": True, "pet": pet, "user": get_user(user_id)}
