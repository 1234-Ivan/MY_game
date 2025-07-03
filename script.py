import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, URLInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from pathlib import Path

# Настройки бота
BOT_TOKEN = "7844163188:AAFpw69SKoBc6y0OdV2pqNW70FuqMoxKJNE"
MANAGER_GROUP_ID = -4804171467  # ID группы менеджеров
ADMINS = [596786513]  # ID администраторов

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ====== БАЗА ДАННЫХ ======
def init_db():
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute('''
           CREATE TABLE IF NOT EXISTS users (
               user_id INTEGER  PRIMARY KEY,
               username TEXT,
               first_name TEXT,
               last_name TEXT,
               phone TEXT
        )
    ''')
    conn.commit()
    conn.close()


init_db()


def save_user(user_id, username, first_name, last_name):
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users 
        (user_id, username, first_name, last_name) 
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, first_name, last_name))
    conn.commit()
    conn.close()


def get_all_users():
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = cursor.fetchall()
    conn.close()
    return [user[0] for user in users]


# ====== FSM ДЛЯ РАССЫЛКИ ======
class BroadcastStates(StatesGroup):
    topic = State()
    description = State()
    image = State()
    link = State()
    confirm = State()


# ====== ОСНОВНЫЕ КОМАНДЫ ======
@dp.message(Command("start"))
async def start(message: types.Message):
    save_user(message.from_user.id,
              message.from_user.username,
              message.from_user.first_name,
              message.from_user.last_name)
    await message.answer("Привет! Напишите ваш вопрос.")


@dp.message(F.chat.type == "private")
async def handle_client_message(message: types.Message):
    save_user(message.from_user.id,
              message.from_user.username,
              message.from_user.first_name,
              message.from_user.last_name)

    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(
        text="Ответить клиенту",
        url=f"tg://user?id={message.from_user.id}"
    ))

    user_info = f"👤 Клиент:\nID: {message.from_user.id}\n"
    if message.from_user.username:
        user_info += f"Username: @{message.from_user.username}\n"
    user_info += f"Имя: {message.from_user.first_name}"
    if message.from_user.last_name:
        user_info += f" {message.from_user.last_name}"

    await bot.send_message(
        chat_id=MANAGER_GROUP_ID,
        text=f"{user_info}\n\n📩 Сообщение:\n{message.text}",
        reply_markup=keyboard.as_markup()
    )
    await message.answer("Ваше сообщение отправлено менеджерам!")


# ====== РАССЫЛКА ======
@dp.message(Command("broadcast"))
async def start_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return await message.answer("Доступ запрещен")

    await state.set_state(BroadcastStates.topic)
    await message.answer("Введите тему рассылки:")


@dp.message(BroadcastStates.topic)
async def process_topic(message: types.Message, state: FSMContext):
    await state.update_data(topic=message.text)
    await state.set_state(BroadcastStates.description)
    await message.answer("Введите описание:")


@dp.message(BroadcastStates.description)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(BroadcastStates.image)
    await message.answer("Отправьте изображение (или /skip чтобы пропустить)")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())