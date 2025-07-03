import sqlite3
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio
import html


# === НАСТРОЙКИ ===
BOT_TOKEN = "7844163188:AAFsJr9eCh1SzsT-OWAFtwcJJtppJM0gvqk"
MANAGER_GROUP_ID = -4804171467 # ID группы менеджеров
ADMINS = [1027932191]  # Список ID админов



# Инициализация
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Словарь для хранения статусов вопросов (в реальном проекте лучше использовать БД)
processing_status = {}

# ===== БАЗА ДАННЫХ =====
def init_db():
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_user(user_id, username, first_name, last_name):
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, first_name, last_name))
    conn.commit()
    conn.close()

init_db()

# ===== FAQ =====
FAQ = {
    "как оплатить": "Вы можете оплатить картой на нашем сайте: https://example.com/pay",
    "где мой заказ": "Уточните, пожалуйста, номер заказа, и мы проверим статус.",
    "какие у вас товары": "Ознакомьтесь с ассортиментом на сайте: https://example.com/catalog",
}

# ===== /start =====
@dp.message(Command("start"))
async def start(message: Message):
    save_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name
    )
    await message.answer("Привет! Напишите ваш вопрос, и я постараюсь помочь.")

# ===== ВОПРОС ОТ ПОЛЬЗОВАТЕЛЯ =====
@dp.message(F.chat.type == "private")
async def handle_client_message(message: Message):
    save_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name
    )

    lower_text = message.text.lower()

    for key, value in FAQ.items():
        if key in lower_text:
            await message.answer(value)
            return

    text = (
        "❓ <b>Новый вопрос от клиента</b>\n\n"
        f"<b>Вопрос:</b> {html.escape(message.text)}\n\n"
        f"<b>Имя:</b> {html.escape(message.from_user.full_name)}\n"
        f"<b>Username:</b> @{html.escape(message.from_user.username or '—')}\n"
        f"<b>ID:</b> <code>{message.from_user.id}</code>"
    )

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="💬 Ответить клиенту",
            callback_data=f"reply_{message.from_user.id}_{message.message_id}"
        ),
        InlineKeyboardButton(
            text="✅ Отмечено как отвеченное",
            callback_data=f"done_{message.from_user.id}_{message.message_id}"
        )
    )

    # Сохраняем сообщение как необработанное
    message_key = f"{message.from_user.id}_{message.message_id}"
    processing_status[message_key] = {
        "is_processing": False,
        "processed_by": None
    }

    await bot.send_message(
        chat_id=MANAGER_GROUP_ID,
        text=text,
        reply_markup=keyboard.as_markup()
    )
    await message.answer("Ваш вопрос передан менеджеру. Ожидайте ответа.")


# ===== ВЗЯТО В ОБРАБОТКУ =====
@dp.callback_query(F.data.startswith("reply_"))
async def handle_reply_click(callback: CallbackQuery):
    _, user_id, msg_id = callback.data.split("_")
    user_id = int(user_id)
    msg_id = int(msg_id)

    message_key = f"{user_id}_{msg_id}"

    # Проверяем, не взят ли уже вопрос в обработку
    if message_key in processing_status and processing_status[message_key]["is_processing"]:
        await callback.answer("Этот вопрос уже взят в обработку другим менеджером.", show_alert=True)
        return

    # Помечаем вопрос как взятый в обработку
    processing_status[message_key] = {
        "is_processing": True,
        "processed_by": callback.from_user.id
    }

    buttons = InlineKeyboardBuilder()
    buttons.row(
        InlineKeyboardButton(
            text="💬 Перейти к клиенту",
            url=f"tg://user?id={user_id}"
        ),
        InlineKeyboardButton(
            text="✅ Отмечено как отвеченное",
            callback_data=f"done_{user_id}_{msg_id}"
        )
    )

    new_text = callback.message.text
    if "🟡 Взято в обработку" not in new_text:
        new_text += f"\n\n🟡 Взято в обработку менеджером: @{callback.from_user.username or callback.from_user.full_name}"

    await callback.message.edit_text(new_text, reply_markup=buttons.as_markup())
    await callback.answer("Вы взяли вопрос в обработку.")


# ===== ОТМЕЧЕНО КАК ОТВЕЧЕННОЕ =====
@dp.callback_query(F.data.startswith("done_"))
async def handle_done_click(callback: CallbackQuery):
    _, user_id, msg_id = callback.data.split("_")
    user_id = int(user_id)
    msg_id = int(msg_id)

    message_key = f"{user_id}_{msg_id}"

    # Проверяем, может ли этот менеджер отмечать как отвеченное
    if (message_key in processing_status and
            processing_status[message_key]["is_processing"] and
            processing_status[message_key]["processed_by"] != callback.from_user.id and
            callback.from_user.id not in ADMINS):
        await callback.answer(
            "Только менеджер, взявший вопрос в обработку, или админ может отметить его как отвеченное.",
            show_alert=True)
        return

    buttons = InlineKeyboardBuilder()
    buttons.row(
        InlineKeyboardButton(
            text="💬 Перейти к клиенту",
            url=f"tg://user?id={user_id}"
        )
    )

    new_text = callback.message.text
    if "✅ Ответ дан" not in new_text:
        new_text += f"\n\n✅ Ответ дан менеджером: @{callback.from_user.username or callback.from_user.full_name}"

    await callback.message.edit_text(new_text, reply_markup=buttons.as_markup())
    await callback.answer("Отметили как отвеченное.")

    # Удаляем запись о статусе обработки
    if message_key in processing_status:
        del processing_status[message_key]


# ===== Запуск =====
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())