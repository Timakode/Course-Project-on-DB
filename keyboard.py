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
            KeyboardButton(text="Редактировать профиль"),
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
            KeyboardButton(text="Записать клиента"),
            KeyboardButton(text="Зарегистрировать клиента")
        ],
        [
            KeyboardButton(text="Поиск")
        ],
        [
            KeyboardButton(text="Редактировать профиль"),
            KeyboardButton(text="Редактировать профиль клиента")
        ],
        [
            KeyboardButton(text="Наши контакты"),
            KeyboardButton(text="Помощь")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню",
    selective=True
)


edit_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Изменить номер телефона"),
        ],
        [
            KeyboardButton(text="Добавить авто"),
            KeyboardButton(text="Редактировать авто")
        ],
        [
            KeyboardButton(text="Назад")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню",
    selective=True
)


def wrap_car_kb():
    # Создаём кнопки
    button_yes = InlineKeyboardButton(text="Да, полностью", callback_data="wrap_yes")
    button_50 = InlineKeyboardButton(text="Да, частично", callback_data="wrap_50")
    button_no = InlineKeyboardButton(text="Нет", callback_data="wrap_no")
    # Создаём клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [button_yes],
        [button_50],
        [button_no]
    ])
    return keyboard

def repaint_car_kb():
    # Создаём кнопки
    button_yes = InlineKeyboardButton(text="Да", callback_data="repaint_yes")
    button_no = InlineKeyboardButton(text="Нет", callback_data="repaint_no")
    # Создаём клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [button_yes, button_no]  # Добавляем кнопки в одну строку
    ])
    return keyboard