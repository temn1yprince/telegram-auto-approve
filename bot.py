import asyncio
import json
import logging
import os
import time
from datetime import datetime

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.types import ChatJoinRequest
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# --- НАСТРОЙКИ ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS = [int(admin_id) for admin_id in os.getenv("ADMINS", "0").split(",") if admin_id.strip().isdigit()]

router = Router()

# --- СИСТЕМНЫЕ ПЕРЕМЕННЫЕ ---
START_TIME = time.time()
COUNTER_FILE = "counter.json"

# --- ФУНКЦИИ ДЛЯ РАБОТЫ СО СЧЕТЧИКОМ ---
def load_counter():
    try:
        with open(COUNTER_FILE, "r") as f:
            return json.load(f).get("count", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

def save_counter(count):
    with open(COUNTER_FILE, "w") as f:
        json.dump({"count": count}, f)

# --- ФУНКЦИЯ UPTIME ---
def get_uptime():
    delta = int(time.time() - START_TIME)
    days, remainder = divmod(delta, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0: parts.append(f"{days}д")
    if hours > 0: parts.append(f"{hours}ч")
    if minutes > 0: parts.append(f"{minutes}м")
    parts.append(f"{seconds}с")
    
    return " ".join(parts)

# --- ФИЛЬТР ДЛЯ АДМИНОВ ---
def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

# --- ОБРАБОТКА ЗАЯВОК В КАНАЛ ---
@router.chat_join_request()
async def process_join_request(request: ChatJoinRequest, bot: Bot):
    # 1. Автоматически одобряем заявку
    await request.approve()
    
    # 2. Обновляем счетчик
    current_count = load_counter() + 1
    save_counter(current_count)
    
    # 3. Собираем информацию о пользователе
    user_id = request.from_user.id
    username = request.from_user.username or "Отсутствует"
    first_name = request.from_user.first_name or "Без имени"
    chat_name = request.chat.title or "Приватный чат"
    date_str = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    
    # 4. Красивый лог в консоль Railway
    log_msg = (
        f"✅ ЗАЯВКА ОДОБРЕНА | ID: {user_id} | Имя: {first_name} | "
        f"Username: @{username} | Канал: {chat_name} | Всего принято: {current_count}"
    )
    logging.info(log_msg)
    
    # 5. Уведомление админу в ЛС
    notify_text = (
        "🔔 <b>Новая заявка одобрена</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Имя:</b> {first_name}\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        f"🔗 <b>Username:</b> @{username}\n"
        f"💬 <b>Канал:</b> {chat_name}\n"
        f"🕐 <b>Время:</b> {date_str}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Всего принято:</b> <code>{current_count}</code>"
    )
    
    for admin_id in ADMINS:
        try:
            await bot.send_message(admin_id, notify_text)
        except Exception as e:
            logging.error(f"Не удалось отправить ЛС админу {admin_id}. Ошибка: {e}")

# --- КОМАНДА /start ---
@router.message(CommandStart())
async def cmd_start(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("✅ Бот запущен и работает. Используй /stats для просмотра статистики.")

# --- КОМАНДА /stats ---
@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    
    count = load_counter()
    uptime = get_uptime()
    
    text = (
        "📊 <b>Статистика бота</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>Принято заявок:</b> <code>{count}</code>\n"
        f"⏳ <b>Время работы:</b> <code>{uptime}</code>\n"
        f"🤖 <b>Статус:</b> Активен ✅\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    await message.answer(text)
    
    # --- ЗАПУСК БОТА ---
async def main():
    # Настройка логов для красивого вывода в Railway
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    bot = Bot(
        token=BOT_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(router)
    
    logging.info("🚀 Бот успешно запущен!")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
