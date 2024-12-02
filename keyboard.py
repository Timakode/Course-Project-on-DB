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
            KeyboardButton(text="Запись"),
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


sign_up_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Новая запись"),
        ],
        [
            KeyboardButton(text="Завершение работы")
        ],
        [
            KeyboardButton(text="Список записей")
        ],
        [
            KeyboardButton(text="Отмена записи"),
            KeyboardButton(text="Перенос записи")
        ],
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


def get_booking_keyboard(free_dates):
    # Генерация инлайн-клавиатуры с кнопками на каждую дату
    buttons = [InlineKeyboardButton(text=date, callback_data=f"book_date:{date}") for date in free_dates]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons[i:i + 3] for i in range(0, len(buttons), 3)])
    return keyboard
