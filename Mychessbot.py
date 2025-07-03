# from aiogram import Bot, Dispatcher, F
# from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
#     InlineKeyboardButton
# from aiogram.enums import ParseMode
# from aiogram.filters import CommandStart
# from aiogram.client.default import DefaultBotProperties
# import asyncio
#
# BOT_TOKEN = "7844163188:AAFsJr9eCh1SzsT-OWAFtwcJJtppJM0gvqk"
#
# bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
# dp = Dispatcher()
#
# # Шахматная доска (8x8)
# # Пустые клетки - '  ', фигуры: 'wP' - белая пешка, 'bK' - черный король и т.д.
# # initial_board = [
# #     ["bR", "bN", "bp", "bQ", "bK", "bp", "bN", "bR"],
# #     ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
# #     ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
# #     ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
# #     ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
# #     ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
# #     ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
# #     ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
# # ]
#
# initial_board = [
#     ["bR", "bN", "bp", "bQ", "bK", "bp", "bN", "bR"],
#     ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
#     ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
#     ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
#     ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
#     ["  ", "  ", "  ", "  ", "  ", "wQ", "  ", "  "],
#     ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
#     ["wR", "wN", "wB", "  ", "wK", "wB", "wN", "wR"]
# ]
#
#
# # Словарь для красивых символов фигур
# piece_symbols = {
#     "wK": "♔", "wQ": "♕", "wR": "♖", "wB": "♗", "wN": "♘", "wP": "♗",
#     "bK": "♚", "bQ": "♛", "bR": "♜", "bp": "♝", "bN": "♞",
#     "bP": "♝",
#     "  ": "·"
# }
#
# # Состояния игры
# user_states = {}
#
# # Главное меню
# main_menu = ReplyKeyboardMarkup(
#     keyboard=[
#         [KeyboardButton(text="🎮 Начать игру")],
#         [KeyboardButton(text="ℹ️ Правила"), KeyboardButton(text="🏆 Рейтинг")]
#     ],
#     resize_keyboard=True
# )
#
#
# # Функция для преобразования доски в HTML
# def board_to_html(board):
#     rows = []
#     for i in range(8):
#         line = f"{8 - i} |"
#         for j in range(8):
#             symbol = piece_symbols.get(board[i][j], ' ')
#             line += f"{symbol} "
#         line += f"| {8 - i}"
#         rows.append(line)
#     body = "\n".join(rows)
#     return (
#         "<pre>"
#         "   a b c d e f g h\n"
#         " +-----------------+\n"
#         f"{body}\n"
#         " +-----------------+\n"
#         "   a b c d e f g h"
#         "</pre>"
#     )
#
#
# @dp.message(CommandStart())
# async def cmd_start(message: Message):
#     await message.answer("♟ Добро пожаловать в шахматного бота! ♟", reply_markup=main_menu)
#
#
# @dp.message(F.text == "🎮 Начать игру")
# async def start_game(message: Message):
#     user_id = message.from_user.id
#     user_states[user_id] = {
#         "board": [row[:] for row in initial_board],
#         "color": "white",  # Игрок играет белыми
#         "waiting_for_move": False,
#         "selected_piece": None
#     }
#
#     await message.answer("Вы играете белыми фигурами. Ваш ход!")
#     await message.answer(
#         board_to_html(user_states[user_id]["board"]),
#         parse_mode="HTML"
#     )
#     await message.answer("Выберите фигуру (например, 'e2'):")
#
#
# @dp.message(F.text.regexp(r'^[a-h][1-8]$'))
# async def process_move(message: Message):
#     user_id = message.from_user.id
#     if user_id not in user_states:
#         await message.answer("Сначала начните игру командой /start")
#         return
#
#     state = user_states[user_id]
#     text = message.text.lower()
#     col = ord(text[0]) - ord('a')
#     row = 8 - int(text[1])
#
#     # Если фигура еще не выбрана
#     if not state["waiting_for_move"]:
#         piece = state["board"][row][col]
#         if piece == "  " or not piece.startswith(state["color"][0]):
#             await message.answer("Выберите свою фигуру!")
#             return
#
#         state["selected_piece"] = (row, col)
#         state["waiting_for_move"] = True
#         await message.answer(f"Выбрана фигура на {text}. Куда походим? (например, 'e4')")
#     else:
#         # Обработка хода
#         from_row, from_col = state["selected_piece"]
#         piece = state["board"][from_row][from_col]
#
#         # Простейшая проверка хода (без учета правил шахмат)
#         if is_valid_move(state["board"], from_row, from_col, row, col):
#             # Выполняем ход
#             state["board"][row][col] = piece
#             state["board"][from_row][from_col] = "  "
#
#             # Передаем ход боту (противнику)
#             state["color"] = "black" if state["color"] == "white" else "white"
#             state["waiting_for_move"] = False
#             state["selected_piece"] = None
#
#             await message.answer(
#                 board_to_html(user_states[user_id]["board"]),
#                 parse_mode="HTML"
#             )
#             await message.answer(f"Фигура перемещена на {text}")
#
#             # Здесь можно добавить ход бота
#             if state["color"] == "black":
#                 await bot_move(message, state)
#         else:
#             await message.answer("Недопустимый ход! Попробуйте еще раз.")
#             state["waiting_for_move"] = False
#             state["selected_piece"] = None
#
#
# # ──────────── вспом. функции ────────────
# def path_clear(board, fr, fc, tr, tc):
#     """Путь пуст? (для ладьи/слона/ферзя)"""
#     dr = (tr-fr) and ((tr-fr)//abs(tr-fr))  # -1,0,1
#     dc = (tc-fc) and ((tc-fc)//abs(tc-fc))
#     r, c = fr+dr, fc+dc
#     while (r, c) != (tr, tc):
#         if board[r][c] != "  ":
#             return False
#         r += dr
#         c += dc
#     return True
#
#
# # Функция для проверки валидности хода
# def is_valid_move(board, fr, fc, tr, tc):
#     """Проверяем корректность хода фигуры (без шаха/рокировки/пеш.превращения)"""
#     if not (0 <= fr < 8 and 0 <= fc < 8 and 0 <= tr < 8 and 0 <= tc < 8):
#         return False
#
#     piece = board[fr][fc]
#     if piece == "  ":
#         return False
#     me, enemy = piece[0], 'b' if piece[0]=='w' else 'w'
#     target = board[tr][tc]
#
#
#
#
#     # нельзя бить свою фигуру
#     if target != "  " and target[0] == me:
#         return False
#
#     dr, dc = tr-fr, tc-fc
#     abs_dr, abs_dc = abs(dr), abs(dc)
#
#     # ─── Пешка ───
#     if piece[1] == 'P':
#         direction = -1 if me=='w' else 1
#         start_row = 6 if me=='w' else 1
#
#         # обычный ход
#         if dc == 0:
#             # шаг на 1 клетку
#             if dr == direction and target == "  ":
#                 return True
#             # стартовый двойной ход
#             if fr == start_row and dr == 2*direction and board[fr+direction][fc] == "  " and target == "  ":
#                 return True
#         # взятие по диагонали
#         if abs_dc == 1 and dr == direction and target != "  " and target[0] == enemy:
#             return True
#         return False
#
#     # ─── Конь ───
#     if piece[1] == 'N':
#         return (abs_dr, abs_dc) in {(1,2),(2,1)}
#
#     # ─── Слон ───
#     if piece[1] == 'B':
#         return abs_dr == abs_dc and path_clear(board, fr, fc, tr, tc)
#
#     # ─── Ладья ───
#     if piece[1] == 'R':
#         if (dr == 0 or dc == 0) and path_clear(board, fr, fc, tr, tc):
#             return True
#         return False
#
#     # ─── Ферзь ───
#     if piece[1] == 'Q':
#         if (abs_dr == abs_dc or dr == 0 or dc == 0) and path_clear(board, fr, fc, tr, tc):
#             return True
#         return False
#
#     # ─── Король ───
#     if piece[1] == 'K':
#         return max(abs_dr, abs_dc) == 1  # без рокировки
#
#     return False
#
#
# # Функция для хода бота
# async def bot_move(message: Message, state):
#     """Простой ход бота (случайный допустимый ход)"""
#     await asyncio.sleep(1)  # Имитация раздумий
#
#     for i in range(8):
#         for j in range(8):
#             if state["board"][i][j] == "bP" and i < 7 and state["board"][i + 1][j] == "  ":
#                 state["board"][i + 1][j] = "bP"
#                 state["board"][i][j] = "  "
#                 state["color"] = "white"
#                 await message.answer("Бот походил пешкой.")
#                 await message.answer(board_to_html(state["board"]), parse_mode="HTML")
#                 await message.answer("Ваш ход!")
#                 return
#
#     await message.answer("Бот не нашел допустимого хода!")
#
#
# async def main():
#     await dp.start_polling(bot)
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
#
# def is_valid_move(board, fr, fc, tr, tc):
#     """Проверяем корректность хода фигуры (без шаха/рокировки/пеш.превращения)"""
#     if not (0 <= fr < 8 and 0 <= fc < 8 and 0 <= tr < 8 and 0 <= tc < 8):
#         return False
#
#     piece = board[fr][fc]
#     if piece == "  ":
#         return False
#     me, enemy = piece[0], 'b' if piece[0]=='w' else 'w'
#     target = board[tr][tc]
#
#     # нельзя бить свою фигуру
#     if target != "  " and target[0] == me:
#         return False
#
#
#     print(tr-fr, tc-fc)
#
#     dr, dc = tr-fr, tc-fc
#     abs_dr, abs_dc = abs(dr), abs(dc)
#
#     # ─── Пешка ───
#     if piece[1] == 'P':
#         direction = -1 if me=='w' else 1
#         start_row = 6 if me=='w' else 1
#
#         # обычный ход
#         if dc == 0:
#             # шаг на 1 клетку
#             if dr == direction and target == "  ":
#                 return True
#             # стартовый двойной ход
#             if fr == start_row and dr == 2*direction and board[fr+direction][fc] == "  " and target == "  ":
#                 return True
#         # взятие по диагонали
#         if abs_dc == 1 and dr == direction and target != "  " and target[0] == enemy:
#             return True
#         return False
#
#     # ─── Конь ───
#     if piece[1] == 'N':
#         return (abs_dr, abs_dc) in {(1,2),(2,1)}
#
#     # ─── Слон ───
#     if piece[1] == 'B':
#         return abs_dr == abs_dc and path_clear(board, fr, fc, tr, tc)
#
#     # ─── Ладья ───
#     if piece[1] == 'R':
#         if (dr == 0 or dc == 0) and path_clear(board, fr, fc, tr, tc):
#             return True
#         return False
#
#     # ─── Ферзь ───
#     if piece[1] == 'Q':
#         if (abs_dr == abs_dc or dr == 0 or dc == 0) and path_clear(board, fr, fc, tr, tc):
#             return True
#         return False
#
#     # ─── Король ───
#     if piece[1] == 'K':
#         return max(abs_dr, abs_dc) == 1  # без рокировки
#
#     return False


# from aiogram import Bot, Dispatcher, F
# from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton , InlineKeyboardMarkup, \
#     InlineKeyboardButton
# from aiogram.enums import ParseMode
# from aiogram.filters import CommandStart
# from aiogram.client.default import DefaultBotProperties
# import asyncio
#
# BOT_TOKEN = "7844163188:AAFsJr9eCh1SzsT-OWAFtwcJJtppJM0gvqk"
#
# bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
# dp = Dispatcher()
#
# # ]
#
# initial_board = [
#     ["  ", "bp", "  ", "bp", "  ", "bp", "  ", "bp"],
#     ["bp", "  ", "bp", "  ", "bp", "  ", "bp", "  "],
#     ["  ", "bp", "  ", "bp", "  ", "bp", "  ", "bp"],
#     ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
#     ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
#     ["wp", "  ", "wp", "  ", "wp", "  ", "wp", "  "],
#     ["  ", "wp", "  ", "wp", "  ", "wp", "  ", "wp"],
#     ["wp", "  ", "wp", "  ", "wp", "  ", "wp", "  "]
# ]
#
#
# # Словарь для красивых символов фигур
# piece_symbols = {
#     "wp": "⛂", "wP": "♚", "bp": "⛀", "bP": "♔"
# }
# symbls = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
#
# # Состояния игры
# user_states = {}
#
# # Главное меню
# main_menu = ReplyKeyboardMarkup(
#     keyboard=[
#         [KeyboardButton(text="🎮 Начать игру")],
#         [KeyboardButton(text="ℹ️ Правила"), KeyboardButton(text="🏆 Рейтинг")]
#     ],
#     resize_keyboard=True
# )
#
#
# # Функция для преобразования доски в HTML
# def board_to_html(board):
#     keyboard = []
#
#     for i in range(8):
#         line = []
#         for j in range(8):
#             symbol = piece_symbols.get(board[i][j], ' ')
#             line.append(InlineKeyboardButton(text=symbol, callback_data=f"{i}:{j}"))
#         keyboard.append(line)
#     return InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=True)
#
#
# @dp.message(CommandStart())
# async def cmd_start(message: Message):
#     await message.answer("♟ Добро пожаловать в шахматного бота! ♟", reply_markup=main_menu)
#
#
# @dp.message(F.text == "🎮 Начать игру")
# async def start_game(message: Message):
#     user_id = message.from_user.id
#     user_states[user_id] = {
#         "board": [row[:] for row in initial_board],
#         "color": "white",  # Игрок играет белыми
#         "waiting_for_move": False,
#         "selected_piece": None,
#         "message_id": message.message_id
#     }
#
#     await bot.send_message(message.chat.id, "Ваш ход!\nвыберете фигуру которой хотите походить", reply_markup=board_to_html(user_states[user_id]["board"]))
#
#
# @dp.callback_query(lambda data: data is not None)
# async def process_move(data: CallbackQuery):
#     user_id = data.from_user.id
#     if user_id not in user_states:
#         await data.answer("Сначала начните игру командой /start")
#         return
#
#     state = user_states[user_id]
#     text = data.data
#     col = int(text[0])
#     row = int(text[2])
#     message: Message = data.message
#
#     # Если фигура еще не выбрана
#     if not state["waiting_for_move"]:
#         piece = state["board"][row][col]
#         if piece == "  " or not piece.startswith(state["color"][0]):
#             await bot.edit_message_text("выберете СВОЮ(⛂/♚) фигуру что-бы походить:", message_id=message.message_id, chat_id=message.chat.id, reply_markup=board_to_html(user_states[user_id]["board"]))
#             return
#
#         state["selected_piece"] = (row, col)
#         state["waiting_for_move"] = True
#         try:
#             await bot.edit_message_text("выберете фигуру что-бы переместить:", message_id=message.message_id, chat_id=message.chat.id, reply_markup=board_to_html(user_states[user_id]["board"]))
#         except:
#             pass
#     else:
#         # Обработка хода
#         from_row, from_col = state["selected_piece"]
#         piece = state["board"][from_row][from_col]
#
#         # Простейшая проверка хода (без учета правил шахмат)
#         if is_valid_move(state["board"], from_row, from_col, row, col):
#             # Выполняем ход
#             state["board"][row][col] = piece
#             state["board"][from_row][from_col] = "  "
#
#             # Передаем ход боту (противнику)
#             state["color"] = "black" if state["color"] == "white" else "white"
#             state["waiting_for_move"] = False
#             state["selected_piece"] = None
#
#             await bot.edit_message_text("Ход противника:",
#                               reply_markup=board_to_html(user_states[user_id]["board"]),
#                               parse_mode="HTML", chat_id=message.chat.id, message_id=message.message_id)
#
#             if state["color"] == "black":
#                 await bot_move(message, state)
#         else:
#             await data.answer("Недопустимый ход! Попробуйте еще раз.")
#             await bot.edit_message_text("Ваш ход!\nвыберете фигуру которой хотите походить", message_id=message.message_id,
#                                         chat_id=message.chat.id,
#                                         reply_markup=board_to_html(user_states[user_id]["board"]))
#             state["waiting_for_move"] = False
#             state["selected_piece"] = None
#
#
# # ──────────── вспом. функции ────────────
# def path_clear(board, fr, fc, tr, tc):
#     """Путь пуст? (для ладьи/слона/ферзя)"""
#     dr = (tr-fr) and ((tr-fr)//abs(tr-fr))  # -1,0,1
#     dc = (tc-fc) and ((tc-fc)//abs(tc-fc))
#     r, c = fr+dr, fc+dc
#     while (r, c) != (tr, tc):
#         if board[r][c] != "  ":
#             return False
#         r += dr
#         c += dc
#     return True
#
#
# # Функция для проверки валидности хода
# def is_valid_move(board, fr, fc, tr, tc):
#     """Проверяем корректность хода фигуры (без шаха/рокировки/пеш.превращения)"""
#     if not (0 <= fr < 8 and 0 <= fc < 8 and 0 <= tr < 8 and 0 <= tc < 8):
#         return False
#
#     piece = board[fr][fc]
#     if piece == "  ":
#         return False
#     me, enemy = piece[0], 'b' if piece[0]=='w' else 'w'
#     target = board[tr][tc]
#
#
#
#
#     # нельзя бить свою фигуру
#     if target != "  " and target[0] == me:
#         return False
#
#     dr, dc = tr-fr, tc-fc
#     abs_dr, abs_dc = abs(dr), abs(dc)
#
#
#     if piece[1] == 'p':
#         direction = -1 if me=='w' else 1
#         if dc == 0:
#             # шаг на 1 клетку
#             if dr == direction and target == "  ":
#                 return True
#             # стартовый двойной ход
#         # взятие по диагонали
#         if abs_dc == 1 and dr == direction and target != "  " and target[0] == enemy:
#             return True
#         return False
#
#     return False
#
#
# # Функция для хода бота
# async def bot_move(message: Message, state):
#     """Простой ход бота (случайный допустимый ход)"""
#     await asyncio.sleep(1)  # Имитация раздумий
#
#     for i in range(8):
#         for j in range(8):
#             if state["board"][i][j] == "bP" and i < 7 and state["board"][i + 1][j] == "  ":
#                 state["board"][i + 1][j] = "bP"
#                 state["board"][i][j] = "  "
#                 state["color"] = "white"
#                 await bot.edit_message_text("Ваш ход!", chat_id=message.chat.id, message_id=message.message_id, reply_markup=board_to_html(state["board"]), parse_mode="HTML")
#                 return
#
#     await message.answer("Бот не нашел допустимого хода!")
#
#
# async def main():
#     await dp.start_polling(bot)
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
#
# def is_valid_move(board, fr, fc, tr, tc):
#     """Проверяем корректность хода фигуры (без шаха/рокировки/пеш.превращения)"""
#     if not (0 <= fr < 8 and 0 <= fc < 8 and 0 <= tr < 8 and 0 <= tc < 8):
#         return False
#
#     piece = board[fr][fc]
#     if piece == "  ":
#         return False
#     me, enemy = piece[0], 'b' if piece[0]=='w' else 'w'
#     target = board[tr][tc]
#
#     # нельзя бить свою фигуру
#     if target != "  " and target[0] == me:
#         return False
#
#
#     print(tr-fr, tc-fc)
#
#     dr, dc = tr-fr, tc-fc
#     abs_dr, abs_dc = abs(dr), abs(dc)
#
#     # ─── Пешка ───
#     if piece[1] == 'P':
#         direction = -1 if me=='w' else 1
#         start_row = 6 if me=='w' else 1
#
#         # обычный ход
#         if dc == 0:
#             # шаг на 1 клетку
#             if dr == direction and target == "  ":
#                 return True
#             # стартовый двойной ход
#             if fr == start_row and dr == 2*direction and board[fr+direction][fc] == "  " and target == "  ":
#                 return True
#         # взятие по диагонали
#         if abs_dc == 1 and dr == direction and target != "  " and target[0] == enemy:
#             return True
#         return False
#
#
#
#     return False


import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo
import asyncio

TOKEN = "7844163188:AAFsJr9eCh1SzsT-OWAFtwcJJtppJM0gvqk"
WEBAPP_URL = "https://cssgridgarden.com/#ua"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Играть!", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await message.answer("Привет! Нажми кнопку ниже, чтобы начать игру:", reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


