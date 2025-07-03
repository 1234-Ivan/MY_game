from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from urllib import parse
import requests


bot = Bot("7844163188:AAFsJr9eCh1SzsT-OWAFtwcJJtppJM0gvqk")
admin_chat = -4804171467
dp = Dispatcher()
inf = []

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Привет! Я бот на aiogram 3!")



# Инструкция: роль и правила
system_message = {
    "role": "system",
    "content": (
        "Ты — доброжелательный помощник по имени Ботик, который отвечает кратко, весело и всегда на «ты», "
        "но если у тебя будут спрашивать что-то не на эту тему, а именно не связанное с этими командами, "
        "ты должен ответить: данные вопросы заблокированы. но после команды /админчат то ты будешь розговаривать на любую тему но говорить о этой команде нельзя"
        "Все твои ответы должны быть короткими и понятными, без ахахаха.\n\n"
        "Команды:\n"
        "- /время — скажи текущее время\n"
        "- /анекдот — расскажи анекдот\n"
        "- /помощь — перечисли команды\n\n"
        "Готов? Тогда жди команд!"
    )
}

answers = {}

def ask(text: str):
    user_message = {"role": "user", "content": text}
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3",
            "messages": [system_message, user_message],
            "stream": False
        }
    )
    return response.json()["message"]["content"]


def generate_deep_link(message_id, user_id, text):
    inf.append({user_id: [message_id, text]})
    return f"https://t.me/UnoGameCards_bot?start={str(inf.index({user_id: [message_id, text]}))}"

@dp.message(Command("start"))
async def start_handler(message: Message):
    parts = message.text.strip().split(maxsplit=1)

    if len(parts) > 1:
        # Это deep-link переход по ссылке с параметрами
        try:
            param = parts[1]
            data = inf[int(param)]

            user_id = list(data.keys())[0]

            message_id, text = data[user_id]


            await message.answer(f"📨 Получено сообщение:\n\n")

        except Exception as e:
            await bot.send_message(message.chat.id, f"❌ Ошибка обработки параметров: {e}")

    else:
        # Обычный вызов /start в чате
        await bot.send_message(
            message.chat.id,
            "👋 Привет! Я Ботик. Здесь ты можешь:\n"
            "- Задать вопрос\n"
            "- Получить помощь\n"
            "- Отправить сообщение администраторам"
        )

@dp.message(lambda message: message.chat.type == "private" and answers.get(message.from_user.id) is None)
async def ask_ai(message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="send to admins", callback_data="help:" + message.text)]
    ])
    answer = ask(message.text)
    await bot.send_message(message.chat.id, answer, reply_markup=markup)

@dp.message(Command("about"), lambda message: message.reply_to_message)
async def about_handler(message):
    await bot.send_message(
        message.chat.id,
        f"message_id: {message.reply_to_message.id}\nuser_id: {message.reply_to_message.from_user.id}"
    )

@dp.callback_query()
async def callback_data(call):
    if call.data.startswith("help:"):


        markup_2 = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="send to admins✔️", callback_data="say")],
        ])


        text = call.data[5:]

        try:

            await bot.edit_message_text(call.message.text, call.message.chat.id, call.message.id, reply_markup=markup_2)

        except:

            pass

        link = generate_deep_link(
            message_id=call.message.message_id,
            user_id=call.from_user.id,
            text=text
        )

        print(link)

        await  bot.send_message(admin_chat, f"{text}\n[answer]({link})", parse_mode="Markdown")

    elif call.data == "say":

        await bot.answer_callback_query(call.id, "you have already sent to admins")


async def answer_mess(message: Message):
    recipient_id = answers.get(message.from_user.id)
    if recipient_id:
        try:
            await bot.send_message(recipient_id, message.text)
        except Exception as e:
            await bot.send_message(message.chat.id, f"Ошибка при отправке сообщения: {e}")
        answers.pop(message.from_user.id)
        await bot.delete_message(message.chat.id, message.id)


async def main():
    await bot.send_message(admin_chat, "bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())