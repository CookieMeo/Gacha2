import logging
import asyncio
import os
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo
from aiohttp import web # Для обслуживания статических файлов Mini App
import json
from datetime import datetime

# Импортируем функции для работы с БД
from db import (
    init_db, get_user, create_user, update_user, get_user_pets, get_all_pets,
    add_pet_to_db, add_promocode, get_promocode, use_promocode,
    calculate_gacha_result, CLICKER_UPGRADES, MAX_CLICKER_LEVEL, SPIN_COST
)

# --- Настройки бота ---
TOKEN = "8226800067:AAH3KAaK4-VIcXh8GijTRd5sCRKQQ2MJ510" # ЗАМЕНИТЕ НА ВАШ ТОКЕН
WEB_APP_URL = "https://gacha2-5ng0.onrender.com" # ЗАМЕНИТЕ НА URL ВАШЕГО СЕРВЕРА
                                                                # (например, для локального теста: http://localhost:8080/webapp/index.html)
ADMIN_USER_ID = 1562471251 # ЗАМЕНИТЕ НА ВАШ ID (для админ-команд)

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- Вспомогательные функции для Mini App ---
def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🏠 Дом", web_app=WebAppInfo(url=WEB_APP_URL)))
    builder.row(types.InlineKeyboardButton(text="🎰 Гача", web_app=WebAppInfo(url=WEB_APP_URL + "?page=gacha")))
    builder.row(types.InlineKeyboardButton(text="🍓 Игра", web_app=WebAppInfo(url=WEB_APP_URL + "?page=game")))
    builder.row(types.InlineKeyboardButton(text="👤 Профиль", web_app=WebAppInfo(url=WEB_APP_URL + "?page=profile")))
    return builder.as_markup()

# --- Обработчики команд ---
@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    user = get_user(user_id)
    if not user:
        create_user(user_id, username)
        await message.answer(f"Привет, {username}! Добро пожаловать в нашу гача-игру с животными! "
                             f"Начни собирать клубнику, чтобы крутить гачу.",
                             reply_markup=get_main_keyboard())
    else:
        await message.answer(f"С возвращением, {username}!", reply_markup=get_main_keyboard())

# --- Обработка данных от Mini App ---
@dp.message()
async def web_app_data_handler(message: types.Message):
    if message.web_app_data:
        user_id = message.from_user.id
        data = json.loads(message.web_app_data.data)
        action = data.get("action")
        
        # Защита от подделки запросов: проверяем, что user_id из Mini App совпадает с user_id сообщения
        # (В реальных проектах используется более строгая валидация initData)
        if user_id != data.get("user_id"):
            logging.warning(f"Security alert: User ID mismatch! Message user: {user_id}, WebApp user: {data.get('user_id')}")
            await bot.send_message(user_id, "Ошибка безопасности. Пожалуйста, перезапустите игру.")
            return

        response_data = {}

        if action == "get_user_data":
            user = get_user(user_id)
            if user:
                user_pets = get_user_pets(user_id)
                response_data = {
                    "user": dict(user), # Преобразуем Row в dict
                    "pets": [dict(p) for p in user_pets],
                    "clicker_info": CLICKER_UPGRADES.get(user['clicker_level']),
                    "next_clicker_upgrade_cost": CLICKER_UPGRADES.get(user['clicker_level'] + 1, {}).get("cost") if user['clicker_level'] < MAX_CLICKER_LEVEL else None,
                    "max_clicker_level": MAX_CLICKER_LEVEL
                }
            else:
                response_data = {"error": "Пользователь не найден."}

        elif action == "click_strawberry":
            user = get_user(user_id)
            if user:
                current_level = user['clicker_level']
                strawberries_per_click = CLICKER_UPGRADES.get(current_level, {"per_click": 1})["per_click"]
                
                new_balance = user['strawberry_balance'] + strawberries_per_click
                new_clicks_total = user['clicks_total'] + 1
                update_user(user_id, strawberry_balance=new_balance, clicks_total=new_clicks_total)
                
                response_data = {
                    "new_balance": new_balance,
                    "strawberries_gained": strawberries_per_click
                }
            else:
                response_data = {"error": "Пользователь не найден."}

        elif action == "upgrade_clicker":
            user = get_user(user_id)
            if user:
                current_level = user['clicker_level']
                if current_level >= MAX_CLICKER_LEVEL:
                    response_data = {"error": "Достигнут максимальный уровень кликера."}
                else:
                    next_level_cost = CLICKER_UPGRADES.get(current_level + 1, {}).get("cost")
                    if next_level_cost is None: # На всякий случай
                        response_data = {"error": "Информация об уровне не найдена."}
                    elif user['strawberry_balance'] >= next_level_cost:
                        new_balance = user['strawberry_balance'] - next_level_cost
                        new_level = current_level + 1
                        update_user(user_id, strawberry_balance=new_balance, clicker_level=new_level)
                        
                        response_data = {
                            "new_balance": new_balance,
                            "new_level": new_level,
                            "next_level_cost": CLICKER_UPGRADES.get(new_level + 1, {}).get("cost") if new_level < MAX_CLICKER_LEVEL else None,
                            "strawberries_per_click": CLICKER_UPGRADES.get(new_level)["per_click"]
                        }
                    else:
                        response_data = {"error": "Недостаточно клубники для улучшения."}
            else:
                response_data = {"error": "Пользователь не найден."}

        elif action == "spin_gacha":
            num_spins = data.get("num_spins", 1)
            result = calculate_gacha_result(user_id, num_spins)
            if "error" in result:
                response_data = {"error": result["error"]}
            else:
                # Получаем обновленные данные пользователя после крутки для профиля
                updated_user = get_user(user_id)
                response_data = {
                    "pets_obtained": result["pets_obtained"],
                    "new_balance": result["new_balance"],
                    "next_guarantees": result["next_guarantees"],
                    "user_stats": {
                        "spins_total": updated_user['spins_total'],
                        "strawberry_balance": updated_user['strawberry_balance'],
                        "strawberry_spent": updated_user['spins_total'] * SPIN_COST, # Приближенно, если тратится только на крутки
                        "pity_red": updated_user['pity_red'],
                        "banner_pity_soft": updated_user['banner_pity_soft'],
                        "banner_pity_hard": updated_user['banner_pity_hard'],
                    }
                }
        
        elif action == "apply_promocode":
            code = data.get("code")
            if not code:
                response_data = {"error": "Код промокода не может быть пустым."}
            else:
                promo = get_promocode(code)
                if not promo:
                    response_data = {"error": "Промокод не найден."}
                elif promo['uses_left'] <= 0:
                    response_data = {"error": "Этот промокод больше недоступен."}
                elif promo['expires_at'] and datetime.strptime(promo['expires_at'], "%Y-%m-%d %H:%M:%S") < datetime.now():
                    response_data = {"error": "Срок действия промокода истёк."}
                else:
                    use_result = use_promocode(user_id, code)
                    if use_result == "success":
                        user = get_user(user_id)
                        new_balance = user['strawberry_balance'] + promo['reward_strawberries']
                        new_spins = user['spins_total'] + promo['reward_spins'] # Если промокод дает доп. крутки
                        update_user(user_id, strawberry_balance=new_balance)
                        # TODO: если промокод дает крутки, то нужно будет обновить и этот счетчик в user_stats
                        
                        response_data = {
                            "success": True,
                            "message": f"Промокод '{code}' успешно активирован! Вы получили {promo['reward_strawberries']} клубники.",
                            "new_balance": new_balance
                        }
                    elif use_result == "already_used":
                        response_data = {"error": "Вы уже использовали этот промокод."}
                    else:
                        response_data = {"error": "Не удалось активировать промокод."}

        # Отправляем ответ обратно в Mini App
        await bot.answer_web_app_query(message.web_app_data.query_id, json.dumps(response_data))

    else:
        # Если это обычное текстовое сообщение, ничего не делаем или обрабатываем как-то иначе
        pass

# --- Админ-команды ---
@dp.message(Command("admin_add_pet"))
async def admin_add_pet_handler(message: types.Message):
    if message.from_user.id != ADMIN_USER_ID:
        return await message.reply("У вас нет прав для этой команды.")
    
    args = message.get_args().split(maxsplit=2) # name rarity image_url
    if len(args) != 3:
        return await message.reply("Использование: /admin_add_pet <название> <редкость> <url_картинки>")
    
    name, rarity, image_url = args
    # Проверка редкости на валидность
    if rarity not in ["Красное", "Оранжевое", "Жёлтое", "Зеленое", "Голубое", "Синее", "Фиолетовое"]:
        return await message.reply("Неверная редкость. Доступные: Красное, Оранжевое, Жёлтое, Зеленое, Голубое, Синее, Фиолетовое.")

    if add_pet_to_db(name, rarity, image_url):
        await message.reply(f"Питомец '{name}' ({rarity}) успешно добавлен.")
    else:
        await message.reply(f"Ошибка: Питомец с именем '{name}' уже существует или произошла ошибка БД.")

@dp.message(Command("admin_create_promo"))
async def admin_create_promo_handler(message: types.Message):
    if message.from_user.id != ADMIN_USER_ID:
        return await message.reply("У вас нет прав для этой команды.")
    
    args = message.get_args().split() # code strawberries spins uses_left expires_at (optional)
    if len(args) < 4:
        return await message.reply("Использование: /admin_create_promo <код> <клубника> <крутки> <использований> [дата_окончания_гггг-мм-дд_чч:мм:сс]")

    code = args[0]
    try:
        strawberries = int(args[1])
        spins = int(args[2])
        uses_left = int(args[3])
    except ValueError:
        return await message.reply("Клубника, крутки и использования должны быть числами.")

    expires_at = None
    if len(args) == 5:
        try:
            expires_at = datetime.strptime(args[4], "%Y-%m-%d_%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return await message.reply("Неверный формат даты. Используйте: ГГГГ-ММ-ДД_ЧЧ:ММ:СС")

    if add_promocode(code, strawberries, spins, uses_left, expires_at, message.from_user.id):
        await message.reply(f"Промокод '{code}' успешно создан. Награда: {strawberries} клубники, {spins} круток. Использований: {uses_left}. Срок: {expires_at or 'без срока'}.")
    else:
        await message.reply(f"Ошибка: Промокод '{code}' уже существует или произошла ошибка БД.")


# --- Веб-сервер для Mini App ---
async def start_web_server():
    async def start_web_server():
        app = web.Application()
        app.router.add_get('/health', health_check) # Добавь эту строку
        app.router.add_static('/webapp/', path=os.path.join(os.getcwd(), 'webapp'), name='webapp')
    
        runner = web.AppRunner(app)
        await runner.setup()
        # Render сам назначит порт через переменную окружения PORT
        port = int(os.environ.get("PORT", 8080)) 
        site = web.TCPSite(runner, '0.0.0.0', port) 
        await site.start()
        logging.info("Web server started on http://localhost:8080")

async def main():
    init_db() # Инициализация базы данных
    await start_web_server() # Запуск веб-сервера
    await dp.start_polling(bot) # Запуск бота

async def health_check(request):
    return web.Response(text="I'm alive")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout) # Убедимся, что логи идут в stdout
    asyncio.run(main())





