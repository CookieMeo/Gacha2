import sqlite3
import random

DB_NAME = 'gacha_v30.db' # Увеличиваем версию, чтобы гарантировать чистую базу

PETS_DATA = [
    # Ивентовые (is_event 1 для Феникса, 2 для Единорога)
    ("Феникс", "Красное", "assets/pets/phoenix.png", 1, "Возрождение"), 
    ("Цербер", "Красное", "assets/pets/cerberus.png", 2, ""),
    
    # Стандартные красные (is_event 0, для проигрыша 50/50)
    ("Единорог", "Красное", "assets/pets/unicorn.png", 0, ""),
    ("Дракон", "Красное", "assets/pets/dragon.png", 0, ""),
    
    # Обычные редкости
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
    ("Паук", "Красное", "assets/pets/spider.png", 0, "")

]

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, username TEXT, strawberry INTEGER DEFAULT 0, spins INTEGER DEFAULT 0,
        click_level INTEGER DEFAULT 1, 
        pity_red INTEGER DEFAULT 50, pity_orange INTEGER DEFAULT 30, pity_yellow INTEGER DEFAULT 15,
        pity_green INTEGER DEFAULT 10, pity_lightblue INTEGER DEFAULT 5, pity_blue INTEGER DEFAULT 3,
        guaranteed_event INTEGER DEFAULT 0, -- 0 = нет гаранта на ивентового, 1 = есть гарант на ивентового
        total_clicks INTEGER DEFAULT 0, 
        spent_strawberry INTEGER DEFAULT 0, 
        spent_spins INTEGER DEFAULT 0,
        red_wins INTEGER DEFAULT 0, 
        red_losses INTEGER DEFAULT 0,
        total_pulls_for_avg_red INTEGER DEFAULT 0, -- Сумма всех пити, когда выпал красный
        red_count INTEGER DEFAULT 0 -- Сколько раз выпал красный (для средней)
        )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS pets (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, rarity TEXT, image_url TEXT, 
        is_event INTEGER DEFAULT 0, skill TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, pet_name TEXT, 
        pet_rarity TEXT, pet_image TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS promo_codes (
        code TEXT PRIMARY KEY, reward_type TEXT, reward_amount INTEGER)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS used_promos (
        user_id INTEGER, code TEXT, PRIMARY KEY(user_id, code))''')
    
    conn.commit()
    seed_pets(cursor)
    conn.close()

def seed_pets(cursor):
    # Добавляем питомцев только если таблица пуста
    if cursor.execute("SELECT COUNT(×) FROM pets").fetchone()[0] == 0:
        # ВНИМАНИЕ: Проверь, что PETS_DATA не содержит синтаксических ошибок
        # Например, у тебя было: ('"Цербер"', "Красное", "assets/pets/cerberus.png", 2, "")
        # А должно быть: ('Цербер', "Красное", "assets/pets/cerberus.png", 2, "") - без кавычек внутри строки
        cursor.executemany("INSERT INTO pets (name, rarity, image_url, is_event, skill) VALUES (?,?,?,?,?)", PETS_DATA)
    cursor.connection.commit() # Сохраняем изменения после добавления питомцев

def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(user_id, username):
    conn = sqlite3.connect(DB_NAME)
    # Убеждаемся, что username всегда строка, чтобы не было ошибок
    conn.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, str(username)))
    conn.commit()
    conn.close()

def do_spins_logic(user_id, count=1, banner_id=1):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    u = get_user(user_id)
    if not u or u['spins'] < count:
        conn.close()
        return {"success": False, "error": "Недостаточно круток!"}

    results = []
    # Используем .get() с дефолтными значениями для безопасности
    p = {'red': u.get('pity_red', 50), 'orange': u.get('pity_orange', 30), 'yellow': u.get('pity_yellow', 15),
         'green': u.get('pity_green', 10), 'lightblue': u.get('pity_lightblue', 5), 'blue': u.get('pity_blue', 3)}
    
    guar = u.get('guaranteed_event', 0) # 0: нет гаранта на ивентового, 1: есть гарант на ивентового
    
    red_wins = 0
    red_losses = 0
    new_pulls_sum = 0
    new_red_count = 0

    for _ in range(count):
        res_rarity = "Фиолетовое" # Дефолтная редкость
        
        # Уменьшаем все счетчики пити
        for k in p: p[k] -= 1

        is_red = False
        # Проверка на выпадение редкости по пити
        if p['red'] <= 0:
            res_rarity = "Красное"
            is_red = True
            new_pulls_sum += (50 - p['red']) # Сколько круток до красного
            new_red_count += 1
            p['red'] = 50 # Сбрасываем пити
        elif p['orange'] <= 0: res_rarity, p['orange'] = "Оранжевое", 30
        elif p['yellow'] <= 0: res_rarity, p['yellow'] = "Жёлтое", 15
        elif p['green'] <= 0: res_rarity, p['green'] = "Зеленое", 10
        elif p['lightblue'] <= 0: res_rarity, p['lightblue'] = "Голубое", 5
        elif p['blue'] <= 0: res_rarity, p['blue'] = "Синее", 3

        pet = None
        if is_red:
            # Логика 50/50 для красных
            if guar == 1 or random.random() < 0.5: # 50% шанс или гарант
                # Выигрыш 50/50: получаем ивентового питомца с текущего баннера
                pet = cursor.execute("SELECT name, image_url FROM pets WHERE rarity='Красное' AND is_event=?", (banner_id,)).fetchone()
                guar = 0 # Сбрасываем гарант
                red_wins += 1
            else:
                # Проигрыш 50/50: получаем стандартного красного питомца
                pet = cursor.execute("SELECT name, image_url FROM pets WHERE rarity='Красное' AND is_event=0 ORDER BY RANDOM() LIMIT 1").fetchone()
                guar = 1 # Устанавливаем гарант на следующий раз
                red_losses += 1
        else:
            # Для не-красных просто выбираем случайного питомца нужной редкости
            pet = cursor.execute("SELECT name, image_url FROM pets WHERE rarity=? ORDER BY RANDOM() LIMIT 1", (res_rarity,)).fetchone()
        
        # Если вдруг питомец не найден (крайний случай, если база пуста или криво заполнена)
        if not pet:
            pet = cursor.execute("SELECT name, image_url FROM pets ORDER BY RANDOM() LIMIT 1").fetchone() # Берем любого
        
        if pet: # Убеждаемся, что питомец точно есть
            cursor.execute("INSERT INTO user_inventory (user_id, pet_name, pet_rarity, pet_image) VALUES (?, ?, ?, ?)",
                           (user_id, pet[0], res_rarity, pet[1]))
            results.append({"name": pet[0], "rarity": res_rarity, "image_url": pet[1]})

    # Обновляем все статистические поля
    cursor.execute('''UPDATE users SET spins=spins-?, spent_spins=spent_spins+?, 
                      pity_red=?, pity_orange=?, pity_yellow=?, pity_green=?, pity_lightblue=?, pity_blue=?,
                      guaranteed_event=?, red_wins=red_wins+?, red_losses=red_losses+?,
                      total_pulls_for_avg_red=total_pulls_for_avg_red+?, red_count=red_count+?
                      WHERE user_id=?''',
                   (count, count, p['red'], p['orange'], p['yellow'], p['green'], p['lightblue'], p['blue'], 
                    guar, red_wins, red_losses, new_pulls_sum, new_red_count, user_id))
    conn.commit()
    conn.close()
    return {"success": True, "pets": results}

def get_all_pets_data():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    pets = conn.execute("SELECT name, rarity, image_url, is_event, skill FROM pets ORDER BY is_event DESC, rarity DESC").fetchall()
    conn.close()
    return [dict(ix) for ix in pets]
