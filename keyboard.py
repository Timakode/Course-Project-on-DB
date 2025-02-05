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
            KeyboardButton(text="Генерация данных"),
            KeyboardButton(text="Удаление данных")# Дополнительная кнопка
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
            KeyboardButton(text="Статистика")
        ],
        [
            KeyboardButton(text="Удаление данных")
        ],
        [
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
        [
            KeyboardButton(text="Назад")
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню",
    selective=True
)

user_reg_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Назад")
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
    buttons = []
    for i in range(0, len(free_dates), 3):
        row = []
        for date in free_dates[i:i+3]:
            row.append(InlineKeyboardButton(text=date.strftime("%Y-%m-%d"), callback_data=f"book_date:{date.strftime('%Y-%m-%d')}"))
        buttons.append(row)

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def cancel_booking_keyboard(booking_id: int) -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру с кнопкой для отмены записи.
    """
    # Создаём клавиатуру с одной кнопкой
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отменить эту запись", callback_data=f"cancel_{booking_id}")]
    ])
    return keyboard


def reschedule_booking_keyboard(booking_id):
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Перенести эту запись", callback_data=f"reschedule_{booking_id}")]
    ])
    return inline_kb


def complete_work_keyboard(booking_id: int) -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру с кнопкой для завершения работы.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Завершить эту работу", callback_data=f"complete_{booking_id}")]
    ])
    return keyboard


stats_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="По диапазону дат"),
            KeyboardButton(text="По номеру авто"),
            KeyboardButton(text="Частое авто")
        ],
        [
            KeyboardButton(text="Записи по марке"),
            #KeyboardButton(text="По номеру авто"),
            #KeyboardButton(text="Частое авто")
        ],
        [
            KeyboardButton(text="Назад")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню",
    selective=True
)


edit_client_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Изменить номер телефона")],
        [KeyboardButton(text="Добавить авто"), KeyboardButton(text="Редактировать авто")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)


def edit_car_kb(cars):
    buttons = [
        [InlineKeyboardButton(text=car['car_number'], callback_data=f"edit_car_{car['car_number']}")]
        for car in cars
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def edit_car_options_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Изменить цвет", callback_data="edit_color")],
            [InlineKeyboardButton(text="Изменить номер", callback_data="edit_number")],
            [InlineKeyboardButton(text="Изменить оклейку плёнкой", callback_data="edit_wrapped")],
            [InlineKeyboardButton(text="Изменить крашеные элементы", callback_data="edit_repainted")]
        ]
    )
