import sqlite3
import random
import time

DATABASE_NAME = 'gacha_game.db'

# --- Конфигурация игры ---
# Шансы выпадения редкостей (в %%)
RARITY_CHANCES = {
    "Фиолетовое": 40,  # Самое частое
    "Синее": 25,
    "Голубое": 15,
    "Зеленое": 10,
    "Жёлтое": 5,
    "Оранжевое": 3,
    "Красное": 2,  # Самое редкое
}

# Стоимость улучшений кликера
CLICKER_UPGRADES = {
    1: {"cost": 0, "per_click": 1},
    2: {"cost": 10, "per_click": 2},
    3: {"cost": 40, "per_click": 3},
    4: {"cost": 90, "per_click": 4},
    5: {"cost": 160, "per_click": 5},
    6: {"cost": 250, "per_click": 6},
    7: {"cost": 360, "per_click": 7},
    8: {"cost": 490, "per_click": 8},
    9: {"cost": 640, "per_click": 9},
    10: {"cost": 810, "per_click": 10},
}
MAX_CLICKER_LEVEL = max(CLICKER_UPGRADES.keys())

# Гаранты на крутки
GATCHA_GUARANTEES = {
    "Красное": 40,
    "Оранжевое": 30,
    "Жёлтое": 15,
    "Зеленое": 10,
    "Голубое": 5,
    "Синее": 3,
}

# Стоимость одной крутки
SPIN_COST = 100

# Текущий баннерный питомец (красная редкость)
# Важно: это должен быть один из питомцев, добавленных в базу данных
CURRENT_BANNER_PET_ID = 1 # ID дракона, например

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row # Позволяет получать строки как объекты с доступом по имени колонки
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            strawberry_balance INTEGER DEFAULT 0,
            clicks_total INTEGER DEFAULT 0,
            spins_total INTEGER DEFAULT 0,
            clicker_level INTEGER DEFAULT 1,
            -- Счетчик для гарантов
            pity_red INTEGER DEFAULT 0,
            pity_orange INTEGER DEFAULT 0,
            pity_yellow INTEGER DEFAULT 0,
            pity_green INTEGER DEFAULT 0,
            pity_lightblue INTEGER DEFAULT 0,
            pity_blue INTEGER DEFAULT 0,
            -- Гарант 50/50 на баннерного питомца
            banner_pity_soft INTEGER DEFAULT 0, -- До любой красной
            banner_pity_hard INTEGER DEFAULT 0  -- До баннерной, если проиграл 50/50
        )
    ''')

    # Таблица питомцев (справочник)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pets (
            pet_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            rarity TEXT NOT NULL,
            image_url TEXT NOT NULL
        )
    ''')

    # Таблица инвентаря пользователя
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_pets (
            user_pet_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            pet_id INTEGER,
            obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (pet_id) REFERENCES pets(pet_id)
        )
    ''')

    # Таблица промокодов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS promocodes (
            code TEXT PRIMARY KEY,
            reward_strawberries INTEGER DEFAULT 0,
            reward_spins INTEGER DEFAULT 0,
            uses_left INTEGER DEFAULT 1,
            expires_at TEXT, -- YYYY-MM-DD HH:MM:SS
            created_by INTEGER
        )
    ''')
    
    # Таблица для отслеживания использования промокодов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_promocodes (
            user_id INTEGER,
            code TEXT,
            redeemed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, code),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (code) REFERENCES promocodes(code)
        )
    ''')

    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def create_user(user_id, username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (user_id, username, strawberry_balance) VALUES (?, ?, ?)',
                   (user_id, username, 0))
    conn.commit()
    conn.close()
    return get_user(user_id)

def update_user(user_id, **kwargs):
    conn = get_db_connection()
    cursor = conn.cursor()
    set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values())
    values.append(user_id)
    cursor.execute(f'UPDATE users SET {set_clause} WHERE user_id = ?', tuple(values))
    conn.commit()
    conn.close()

def get_user_pets(user_id):
    conn = get_db_connection()
    pets = conn.execute('''
        SELECT p.name, p.rarity, p.image_url
        FROM user_pets up
        JOIN pets p ON up.pet_id = p.pet_id
        WHERE up.user_id = ?
        ORDER BY up.obtained_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return pets

def add_pet_to_inventory(user_id, pet_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_pets (user_id, pet_id) VALUES (?, ?)', (user_id, pet_id))
    conn.commit()
    conn.close()

def get_all_pets():
    conn = get_db_connection()
    pets = conn.execute('SELECT * FROM pets').fetchall()
    conn.close()
    return pets

def get_pets_by_rarity(rarity):
    conn = get_db_connection()
    pets = conn.execute('SELECT * FROM pets WHERE rarity = ?', (rarity,)).fetchall()
    conn.close()
    return pets

def add_pet_to_db(name, rarity, image_url):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO pets (name, rarity, image_url) VALUES (?, ?, ?)', (name, rarity, image_url))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"Pet '{name}' already exists.")
        return False
    finally:
        conn.close()

def add_promocode(code, strawberries, spins, uses_left, expires_at, created_by):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO promocodes (code, reward_strawberries, reward_spins, uses_left, expires_at, created_by) VALUES (?, ?, ?, ?, ?, ?)',
            (code, strawberries, spins, uses_left, expires_at, created_by)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"Promocode '{code}' already exists.")
        return False
    finally:
        conn.close()

def get_promocode(code):
    conn = get_db_connection()
    promo = conn.execute('SELECT * FROM promocodes WHERE code = ?', (code,)).fetchone()
    conn.close()
    return promo

def use_promocode(user_id, code):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Проверяем, использовал ли пользователь уже этот промокод
        cursor.execute('SELECT 1 FROM user_promocodes WHERE user_id = ? AND code = ?', (user_id, code))
        if cursor.fetchone():
            return "already_used"

        # Уменьшаем количество использований промокода
        cursor.execute('UPDATE promocodes SET uses_left = uses_left - 1 WHERE code = ? AND uses_left > 0', (code,))
        if cursor.rowcount == 0: # Если промокод не найден или закончились использования
            conn.rollback()
            return "not_available"

        # Записываем использование промокода пользователем
        cursor.execute('INSERT INTO user_promocodes (user_id, code) VALUES (?, ?)', (user_id, code))

        conn.commit()
        return "success"
    except Exception as e:
        conn.rollback()
        print(f"Error using promocode: {e}")
        return "error"
    finally:
        conn.close()

def calculate_gacha_result(user_id, num_spins=1):
    user = get_user(user_id)
    if not user:
        return {"error": "User not found"}
    
    current_balance = user['strawberry_balance']
    if current_balance < SPIN_COST * num_spins:
        return {"error": "Недостаточно клубники!"}

    pets_obtained = []
    total_spins_performed = 0

    for _ in range(num_spins):
        total_spins_performed += 1
        
        # Обновляем счетчики жалости
        pity_updates = {
            "pity_red": user['pity_red'] + 1,
            "pity_orange": user['pity_orange'] + 1,
            "pity_yellow": user['pity_yellow'] + 1,
            "pity_green": user['pity_green'] + 1,
            "pity_lightblue": user['pity_lightblue'] + 1,
            "pity_blue": user['pity_blue'] + 1,
            "banner_pity_soft": user['banner_pity_soft'] + 1,
        }
        
        # Проверяем гаранты в порядке от редкого к частому
        guaranteed_rarity = None
        if pity_updates["pity_red"] >= GATCHA_GUARANTEES["Красное"]:
            guaranteed_rarity = "Красное"
        elif pity_updates["pity_orange"] >= GATCHA_GUARANTEES["Оранжевое"]:
            guaranteed_rarity = "Оранжевое"
        elif pity_updates["pity_yellow"] >= GATCHA_GUARANTEES["Жёлтое"]:
            guaranteed_rarity = "Жёлтое"
        elif pity_updates["pity_green"] >= GATCHA_GUARANTEES["Зеленое"]:
            guaranteed_rarity = "Зеленое"
        elif pity_updates["pity_lightblue"] >= GATCHA_GUARANTEES["Голубое"]:
            guaranteed_rarity = "Голубое"
        elif pity_updates["pity_blue"] >= GATCHA_GUARANTEES["Синее"]:
            guaranteed_rarity = "Синее"
            
        pulled_rarity = guaranteed_rarity

        if not pulled_rarity:
            # Если нет гаранта, крутим колесо
            rarities = list(RARITY_CHANCES.keys())
            weights = list(RARITY_CHANCES.values())
            pulled_rarity = random.choices(rarities, weights=weights, k=1)[0]
        
        # Сброс счетчика жалости для выпавшей редкости
        if pulled_rarity == "Красное": pity_updates["pity_red"] = 0
        if pulled_rarity == "Оранжевое": pity_updates["pity_orange"] = 0
        if pulled_rarity == "Жёлтое": pity_updates["pity_yellow"] = 0
        if pulled_rarity == "Зеленое": pity_updates["pity_green"] = 0
        if pulled_rarity == "Голубое": pity_updates["pity_lightblue"] = 0
        if pulled_rarity == "Синее": pity_updates["pity_blue"] = 0
        # Фиолетовый не имеет гаранта, поэтому его счетчик не сбрасывается таким образом

        # --- Логика баннера 50/50 ---
        selected_pet_data = None
        if pulled_rarity == "Красное":
            banner_pet = get_pet_by_id(CURRENT_BANNER_PET_ID)
            
            if user['banner_pity_hard'] == 1: # Если на прошлом красном проиграл 50/50, то сейчас 100% баннер
                selected_pet_data = banner_pet
                pity_updates["banner_pity_soft"] = 0
                pity_updates["banner_pity_hard"] = 0
            else: # Обычный 50/50
                if random.random() < 0.5: # Выиграл 50/50 - получил баннерного
                    selected_pet_data = banner_pet
                    pity_updates["banner_pity_soft"] = 0
                    pity_updates["banner_pity_hard"] = 0
                else: # Проиграл 50/50 - получил другого красного
                    other_red_pets = [p for p in get_pets_by_rarity("Красное") if p['pet_id'] != CURRENT_BANNER_PET_ID]
                    if other_red_pets:
                        selected_pet_data = random.choice(other_red_pets)
                    else: # Если нет других красных, то все равно баннерный
                        selected_pet_data = banner_pet
                        pity_updates["banner_pity_soft"] = 0
                        pity_updates["banner_pity_hard"] = 0 # Сброс, потому что все равно получил баннерного
                    pity_updates["banner_pity_hard"] = 1 # Устанавливаем хард-пити на следующий раз
        else:
            # Выбираем случайного питомца нужной редкости
            available_pets = get_pets_by_rarity(pulled_rarity)
            if available_pets:
                selected_pet_data = random.choice(available_pets)
            else:
                # Fallback, если нет питомцев нужной редкости (не должно происходить при корректном добавлении)
                selected_pet_data = {"pet_id": -1, "name": "Неизвестный питомец", "rarity": pulled_rarity, "image_url": "/assets/pets/placeholder.png"}

        if selected_pet_data:
            add_pet_to_inventory(user_id, selected_pet_data['pet_id'])
            pets_obtained.append({
                "name": selected_pet_data['name'],
                "rarity": selected_pet_data['rarity'],
                "image_url": selected_pet_data['image_url']
            })

        # Обновляем данные пользователя
        current_balance -= SPIN_COST
        user_updates = {
            "strawberry_balance": current_balance,
            "spins_total": user['spins_total'] + 1,
            **pity_updates
        }
        update_user(user_id, **user_updates)
        user = get_user(user_id) # Получаем обновленные данные пользователя для следующей итерации или возврата

    # Рассчитываем оставшиеся крутки до гаранта
    next_guarantees = {}
    for rarity, limit in GATCHA_GUARANTEES.items():
        rarity_key = rarity.replace("ое", "") # для сопоставления с ключами pity_red, pity_orange
        rarity_key = rarity_key.replace(" ", "_").lower()
        if rarity_key == "красн": rarity_key = "red"
        elif rarity_key == "оранжев": rarity_key = "orange"
        elif rarity_key == "жёлт": rarity_key = "yellow"
        elif rarity_key == "зелен": rarity_key = "green"
        elif rarity_key == "голубо": rarity_key = "lightblue"
        elif rarity_key == "син": rarity_key = "blue"

        pity_counter = user[f"pity_{rarity_key}"]
        next_guarantees[rarity] = max(0, limit - pity_counter)

    # Дополнительно для красного 50/50
    if user['banner_pity_hard'] == 1:
        next_guarantees["Красное (баннер)"] = "ГАРАНТ!"
    else:
        next_guarantees["Красное (до 50/50)"] = GATCHA_GUARANTEES["Красное"] - user['banner_pity_soft']


    return {
        "pets_obtained": pets_obtained,
        "new_balance": current_balance,
        "next_guarantees": next_guarantees,
        "user_stats": {
            "pity_red": user['pity_red'],
            "banner_pity_soft": user['banner_pity_soft'],
            "banner_pity_hard": user['banner_pity_hard'],
            # ... можно добавить все остальные pity счетчики, если нужно
        }
    }

def get_pet_by_id(pet_id):
    conn = get_db_connection()
    pet = conn.execute('SELECT * FROM pets WHERE pet_id = ?', (pet_id,)).fetchone()
    conn.close()
    return pet

# Инициализируем базу данных при запуске
init_db()

# Пример добавления питомцев (для тестирования). Выполнить один раз.
# Эти данные должны быть добавлены админом через админ-панель или специальную команду.
# add_pet_to_db("Дракон", "Красное", "/assets/pets/dragon.png") # ID=1
# add_pet_to_db("Феникс", "Оранжевое", "/assets/pets/phoenix.png")
# add_pet_to_db("Единорог", "Жёлтое", "/assets/pets/unicorn.png")
# add_pet_to_db("Грифон", "Зеленое", "/assets/pets/griffin.png")
# add_pet_to_db("Русалка", "Голубое", "/assets/pets/mermaid.png")
# add_pet_to_db("Кентавр", "Синее", "/assets/pets/centaur.png")
# add_pet_to_db("Мопс", "Красное", "/assets/pets/mops.png") # Еще один красный для 50/50
# add_pet_to_db("Кот", "Фиолетовое", "/assets/pets/cat.png")
# add_pet_to_db("Собака", "Фиолетовое", "/assets/pets/dog.png")

