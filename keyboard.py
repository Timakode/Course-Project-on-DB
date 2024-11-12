from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
          KeyboardButton(text="Регистрация")
        ],
        [
            KeyboardButton(text="Помощь"),
            KeyboardButton(text="Наши контакты")
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню",
    selective=True
)

admin_start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Регистрация")
        ],
        [
            KeyboardButton(text="Помощь"),
            KeyboardButton(text="Наши контакты")
        ],
        [
            KeyboardButton(text="Админская кнопка")  # Дополнительная кнопка
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню",
    selective=True
)

after_start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
          KeyboardButton(text="Запись")
        ],
        [
            KeyboardButton(text="Редакатировать профиль"),
            KeyboardButton(text="Мои авто")
        ],
        [
            KeyboardButton(text="Наши контакты")
        ],
        [
            KeyboardButton(text="Помощь")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню",
    selective=True
)


after_start_admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Редакатировать профиль")
        ],
        [
            KeyboardButton(text="Записать клиента"),
            KeyboardButton(text="Помощь")
        ],
        [
            KeyboardButton(text="Наши контакты")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню",
    selective=True
)