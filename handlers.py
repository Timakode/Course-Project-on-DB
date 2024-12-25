import os
import asyncio
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InputFile, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command, state
from aiogram.types import CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.state import StateFilter

import db
import keyboard
from decouple import config
from db import *
import re
from aiogram.fsm.context import FSMContext
from utils.states import *
from aiogram.utils.markdown import hlink


router = Router()

admin_ids = list(map(int, config('ADMINS').split(',')))
phone_number = None

@router.message(CommandStart())
async def start_command(message:Message) -> None:
    telegram_id = message.from_user.id
    user_data = await get_user_by_id(telegram_id)
    if user_data:
        user_id = user_data["id"]

    if user_data is None:
        if telegram_id in admin_ids:
            await message.answer(
                f"<b>{message.from_user.first_name}</b>\nДобро пожаловать!\n\nНапоминаю, что вы являетесь администратором\nПеред началом работы с ботом необходимо зарегистрироваться",
                reply_markup=keyboard.admin_start_kb)
        else:
            await message.answer(f"<b>{message.from_user.first_name}</b>\nДетейлинг студия {'818'} приветствует вас!\n\nПеред началом работы с ботом необходимо зарегистрироваться",
                                 reply_markup=keyboard.start_kb)
    else:
        if telegram_id in admin_ids:
            await message.answer(
                f"<b>{message.from_user.first_name}</b>\nДобро пожаловать!\n\nНапоминаю, что вы являетесь администратором",
                reply_markup=keyboard.after_start_admin_kb)
        else:
            await message.answer(f"<b>{message.from_user.first_name}</b>\nДетейлинг студия {'818'} приветствует вас!",
                                 reply_markup=keyboard.after_start_kb)



@router.message(Command('help'))
@router.message(F.text.lower() == "помощь")
async def help_command(message:Message) -> None:
    await message.answer(f"""Список команд, доступных в боте:\n/start - запуск бота\n/help - помощь""")


@router.message(F.text.lower() == "регистрация")
async def registration(message:Message, state: FSMContext) -> None:
    global phone_number


    await message.answer("Пожалуйста, введите Ваш номер телефона в формате +79491234567")
    await state.set_state(UserData.phone)



@router.message(UserData.phone)
async def form_phone(message:Message, state:FSMContext):
    # Проверка формата номера телефона (например, +71234567890)
    phone_pattern = re.compile(r"^\+?\d{11,15}$")
    phone_number = message.text

    user_data = await get_user_by_phone(phone_number)
    if user_data is not None:
        await state.clear()  # Завершение стейта
        await message.answer(f"Клиент с таким номером уже зарегистрирован",
                             reply_markup=keyboard.after_start_kb)
        return

    if phone_pattern.match(phone_number):
        await state.update_data(phone=phone_number)
        await message.answer(f"Номер телефона {phone_number} сохранён")

        await state.set_state(UserData.name)
        await message.answer("Пожалуйста, введите Ваше имя")
    else:
        await message.answer("Номер телефона введен неверно, попробуйте ещё раз")
        await registration_admin(message, state)





@router.message(UserData.name)
async def form_name(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    user_data = await get_user_by_id(telegram_id)

    await state.update_data(name=message.text)
    data = await state.get_data()
    await state.clear()  # Завершение стейта
    first_name = data.get("name")
    phone_number = data.get("phone")

    if user_data is None:
        # Если пользователь не найден, добавляем его в базу данных
        await add_user(
            telegram_id=telegram_id,
            username=message.from_user.username,
            first_name=first_name,
            phone_number=phone_number
        )

    dbname = await get_user_by_id(telegram_id)
    if dbname is not None:
        db_name = dbname.get("name")
    else:
        db_name = first_name

    if telegram_id in admin_ids:
        await message.answer(f"Поздравляю, {db_name}, регистрация прошла успешно!",
                             reply_markup=keyboard.after_start_admin_kb)
    else:
        await message.answer(f"Поздравляю, {db_name}, регистрация прошла успешно!",
                             reply_markup=keyboard.after_start_kb)


@router.message(lambda message: message.text.lower() == "назад")
async def back_to_main_menu(message: Message, state: FSMContext):
    # Очищаем текущее состояние
    await state.clear()
    # Возвращаем пользователя в главное меню
    await message.answer("Вы вернулись в главное меню.", reply_markup=keyboard.after_start_admin_kb)


@router.message(F.text.lower() == "зарегистрировать клиента")
async def registration_admin(message: Message, state: FSMContext):
    # Начало регистрации клиента
    await message.answer("Пожалуйста, введите номер телефона Клиента в формате +79491234567",
                         reply_markup=keyboard.user_reg_kb)
    await state.set_state(UserDataforAdmin.phone)

@router.message(UserDataforAdmin.phone)
async def form_phone_admin(message:Message, state:FSMContext):
    # Проверка формата номера телефона (например, +71234567890)
    phone_pattern = re.compile(r"^\+?\d{11,15}$")
    phone_number = message.text

    user_data = await get_user_by_phone(phone_number)
    if user_data is not None:
        await state.clear()  # Завершение стейта
        await message.answer(f"Клиент с таким номером уже зарегистрирован",
                             reply_markup=keyboard.after_start_admin_kb)
        return

    if phone_pattern.match(phone_number):
        await state.update_data(phone=phone_number)
        await message.answer(f"Номер телефона клиента {phone_number} сохранён")

        await state.set_state(UserDataforAdmin.name)
        await message.answer("Пожалуйста, введите имя Клиента")
    else:
        await message.answer("Номер телефона введен неверно, попробуйте ещё раз")
        await registration_admin(message, state)


@router.message(UserDataforAdmin.name)
async def form_name_admin(message: Message, state: FSMContext):
    first_name = message.text
    data = await state.get_data()
    phone_number = data.get("phone")

    await add_user(
        telegram_id=None,
        username=None,
        first_name=first_name,
        phone_number=phone_number
    )

    # Завершаем состояние после добавления
    await state.clear()

    await message.answer(f"Поздравляю, регистрация Клиента прошла успешно!",
                        reply_markup=keyboard.after_start_admin_kb)


@router.message(F.text.lower() == "редактировать профиль")
async def editProfile(message: Message, state: FSMContext):
    await message.answer(f"Что Вы хотите изменить?", reply_markup=keyboard.edit_kb)
    await state.set_state(EditProfile.start)


@router.message(EditProfile.start)
async def editorStart(message: Message, state: FSMContext):
    if message.text.lower() == "изменить номер телефона":
        await state.set_state(EditProfile.phone)
        await message.answer("Введите новый номер телефона:", reply_markup=None)
    elif message.text.lower() == "добавить авто":
        await state.set_state(EditProfile.addAuto)
        await message.answer("Введите регистрационный номер авто: ", reply_markup=None)
    elif message.text.lower() == "редактировать авто":
        await state.set_state(EditProfile.editAuto)
        await message.answer("РЕДАКТИРОВАНИЕ АВТО: ", reply_markup=None)
    elif message.text.lower() == "назад":
        await state.clear()
        telegram_id = message.from_user.id
        if telegram_id in admin_ids:
            await message.answer(f"Вы вернулись в главное меню",
                                 reply_markup=keyboard.after_start_admin_kb)
        else:
            await message.answer(f"Вы вернулись в главное меню",
                                 reply_markup=keyboard.after_start_kb)

@router.message(EditProfile.phone)
async def editPhone(message: Message, state: FSMContext):
    if message.text.lower() == "назад":
        await state.set_state(EditProfile.start)
        telegram_id = message.from_user.id
        if telegram_id in admin_ids:
            await message.answer(f"Вы вернулись в меню редактирования профиля",
                                 reply_markup=keyboard.edit_kb)
        else:
            await message.answer(f"Вы вернулись в меню редактирования профиля",
                                 reply_markup=keyboard.edit_kb)
        return

    # Проверка формата номера телефона (например, +71234567890)
    phone_pattern = re.compile(r"^\+?\d{11,15}$")
    phone_number = message.text

    telegram_id = message.from_user.id
    user = await get_user_by_id(telegram_id)
    if user is None:
        await message.answer("Пользователь не найден в базе данных.")
        return
    old_phone_number = user.get("phone_number")

    if phone_pattern.match(phone_number):
        await state.update_data(phone=phone_number)
        data = await state.get_data()
        phone_number = data.get("phone")
        await db.update_phone(old_phone_number, phone_number)

        if telegram_id in admin_ids:
            await message.answer(f"Номер телефона успешно обновлен. Новый номер: {phone_number}",
                                 reply_markup=keyboard.after_start_admin_kb)
        else:
            await message.answer(f"Номер телефона успешно обновлен. Новый номер: {phone_number}",
                                 reply_markup=keyboard.after_start_kb)

        await state.clear()
    else:
        await message.answer("Номер телефона введен неверно, попробуйте ещё раз")
        await editPhone(message, state)



@router.message(EditProfile.addAuto)
async def car_number(message: Message, state: FSMContext):
    car_number = message.text

    car = await get_car_by_number(car_number)
    if car is not None:
        telegram_id = message.from_user.id
        if telegram_id in admin_ids:
            await message.answer(f"Такой номер авто уже зарегистрирован",
                                 reply_markup=keyboard.after_start_admin_kb)
        else:
            await message.answer(f"Такой номер авто уже зарегистрирован",
                                 reply_markup=keyboard.after_start_kb)
        await state.clear()
        return

    await state.update_data(car_number=car_number)

    await state.set_state(EditProfile.car_brand)
    await message.answer("Введите марку авто: ", reply_markup=None)

@router.message(EditProfile.car_brand)
async def car_brand(message: Message, state: FSMContext):
    car_brand = message.text
    await state.update_data(car_brand=car_brand)

    await state.set_state(EditProfile.car_model)
    await message.answer("Введите модель авто: ", reply_markup=None)

@router.message(EditProfile.car_model)
async def car_model(message: Message, state: FSMContext):
    car_model = message.text
    await state.update_data(car_model=car_model)

    await state.set_state(EditProfile.car_year)
    await message.answer("Введите год выпуска авто: ", reply_markup=None)

@router.message(EditProfile.car_year)
async def car_year(message: Message, state: FSMContext):
    car_year = message.text
    await state.update_data(car_year=car_year)

    await state.set_state(EditProfile.car_color)
    await message.answer("Введите цвет авто: ", reply_markup=None)

@router.message(EditProfile.car_color)
async def car_color(message: Message, state: FSMContext):
    car_color = message.text
    await state.update_data(car_color=car_color)

    await state.set_state(EditProfile.wrapped_car)
    await message.answer(
        "Выберите, оклеен ли авто пленкой:",
        reply_markup=keyboard.wrap_car_kb()
    )


@router.callback_query(StateFilter(EditProfile.wrapped_car))
async def wrapped_car_callback(call: CallbackQuery, state: FSMContext):
    if call.data == "wrap_yes":
        await state.update_data(wrapped_car="Полностью")
    elif call.data == "wrap_50":
        await state.update_data(wrapped_car="Частично")
    elif call.data == "wrap_no":
        await state.update_data(wrapped_car="Нет")

    # Переход к следующему состоянию
    await state.set_state(EditProfile.repainted_car)
    await call.message.answer(
        "Есть ли на авто крашеные элементы:",
        reply_markup=keyboard.repaint_car_kb()
    )
    await call.answer()


# Обработчик для выбора, есть ли крашеные элементы
@router.callback_query(StateFilter(EditProfile.repainted_car))
async def repainted_car_callback(call: CallbackQuery, state: FSMContext):
    if call.data == "repaint_yes":
        await state.update_data(repainted_car="Да")
    elif call.data == "repaint_no":
        await state.update_data(repainted_car="Нет")

    # Получаем user_id из таблицы users
    user_id = (await get_user_by_id(call.from_user.id))['id']
    if user_id is None:
        await call.message.answer("Ошибка! Пользователь не найден.")
        return

    # Сохранение данных в базу
    data = await state.get_data()
    await state.clear()  # Завершение FSM

    car_number = data.get("car_number")
    car_brand = data.get("car_brand")
    car_model = data.get("car_model")
    car_year = data.get("car_year")
    car_color = data.get("car_color")
    wrapped_car = data.get("wrapped_car")
    repainted_car = data.get("repainted_car")

    await add_car(
        car_number=car_number,
        user_id=user_id,
        car_brand=car_brand,
        car_model=car_model,
        car_year=car_year,
        car_color=car_color,
        wrapped_car=wrapped_car,
        repainted_car=repainted_car
    )

    # Ответ пользователю
    telegram_id = call.from_user.id
    if telegram_id in admin_ids:
        await call.message.answer("Поздравляю, авто успешно добавлено!",
                                   reply_markup=keyboard.after_start_admin_kb)
    else:
        await call.message.answer("Поздравляю, авто успешно добавлено!",
                                   reply_markup=keyboard.after_start_kb)
    await call.answer()


@router.message(F.text.lower() == "поиск")
async def search_handler(message: types.Message, state: FSMContext):
    await state.set_state(SearchData.search_input)
    await message.answer("Введите номер телефона в формате +79491234567 или номер автомобиля:",
                         reply_markup=keyboard.user_reg_kb)


@router.message(SearchData.search_input)
async def process_input(message: types.Message, state: FSMContext):
    user_input = message.text.strip()

    # Проверяем, является ли ввод номером телефона или номером автомобиля
    phone_pattern = re.compile(r"^\+?\d{11,15}$")

    if phone_pattern.match(user_input):
        client_info = await get_client_and_cars_by_phone(user_input)
        if client_info:
            response = f"Пользователь найден:\n" \
                       f"Имя: {client_info['user']['first_name']}\n" \
                       f"Телефон: {client_info['user']['phone_number']}\n" \
                       f"Автомобили:\n"
            for car in client_info['cars']:
                response += f"- {car['car_brand']} {car['car_model']} ({car['car_year']}) - {car['car_number']}\n"
            await message.answer(response)
        else:
            await message.answer("Пользователь не найден.")

    elif len(user_input) > 0:  # Предположим, что номер автомобиля не пустой
        car_info = await get_car_and_owner_by_number(user_input)
        if car_info:
            response = f"Автомобиль найден:\n" \
                       f"Марка: {car_info['car']['car_brand']}\n" \
                       f"Модель: {car_info['car']['car_model']}\n" \
                       f"Год: {car_info['car']['car_year']}\n" \
                       f"Цвет: {car_info['car']['car_color']}\n" \
                       f"Номер: {car_info['car']['car_number']}\n" \
                       f"Владелец:\n" \
                       f"Имя: {car_info['owner']['first_name']}\n" \
                       f"Телефон: {car_info['owner']['phone_number']}\n"
            await message.answer(response)
        else:
            await message.answer("Автомобиль не найден.")
    else:
        await message.answer("Некорректный ввод. Пожалуйста, введите номер телефона или номер автомобиля.")

    await state.clear()  # Завершаем состояние после обработки ввода


@router.message(F.text.lower() == "запись")
async def book_handler(message: Message, state: FSMContext):
    await message.answer("Выберите действие", reply_markup=keyboard.sign_up_kb)
    await state.set_state(BookingStates.start)


@router.message(BookingStates.start)
async def booking_start(message: Message, state: FSMContext):
    if message.text.lower() == "новая запись":
        # Получаем список доступных дат из БД
        available_dates = await get_available_dates()
        if not available_dates:
            await message.answer("К сожалению, нет доступных дат для записи на ближайшие 30 дней.")
            return
        # Создаём инлайн-клавиатуру с доступными датами
        inline_kb = keyboard.get_booking_keyboard(available_dates)
        await message.answer("Выберите дату для записи:", reply_markup=inline_kb)
        await state.set_state(BookingStates.select_date)

    elif message.text.lower() == "завершение работы":
        all_bookings = await get_all_active_bookings()

        if not all_bookings:
            await message.answer("Нет активных записей, которые можно завершить.")
            await state.clear()
            return

        for booking in all_bookings:
            booking_id, booking_date, service_description, car_brand, car_number, first_name, phone_number = booking
            message_text = (
                f"ID записи: {booking_id}\n"
                f"Дата: {booking_date}\n"
                f"Услуга: {service_description}\n"
                f"Авто: {car_brand}, Номер: {car_number}\n"
                f"Клиент: {first_name}, Телефон: {phone_number}"
            )
            await message.answer(message_text, reply_markup=keyboard.complete_work_keyboard(booking_id))

        await state.set_state(BookingStates.complete_work)

    elif message.text.lower() == "отмена записи":
        # Получаем все активные записи
        all_bookings = await get_all_active_bookings()

        if not all_bookings:
            await message.answer("Нет активных записей, которые можно отменить.")
            await state.clear()
            return

        # Выводим информацию о каждой записи
        for booking in all_bookings:
            booking_id, booking_date, service_description, car_brand, car_number, first_name, phone_number = booking
            message_text = (
                f"ID записи: {booking_id}\n"
                f"Дата: {booking_date}\n"
                f"Услуга: {service_description}\n"
                f"Авто: {car_brand}, Номер: {car_number}\n"
                f"Клиент: {first_name}, Телефон: {phone_number}"
            )
            await message.answer(message_text, reply_markup=keyboard.cancel_booking_keyboard(booking_id))
        await state.set_state(BookingStates.cancel)

    elif message.text.lower() == "перенос записи":
        bookings = await get_scheduled_bookings()

        if not bookings:
            await message.answer("Нет записей со статусом 'запланировано'.")
            await state.clear()
            return

        for booking in bookings:
            booking_id, booking_date, service_description, car_brand, car_number, first_name, phone_number = booking
            message_text = (
                f"ID записи: {booking_id}\n"
                f"Дата: {booking_date}\n"
                f"Услуга: {service_description}\n"
                f"Авто: {car_brand}, Номер: {car_number}\n"
                f"Клиент: {first_name}, Телефон: {phone_number}"
            )
            await message.answer(message_text, reply_markup=keyboard.reschedule_booking_keyboard(booking_id))
        await state.set_state(BookingStates.select_reschedule)
    elif message.text.lower() == "список записей":
        bookings = await get_active_bookings()

        if not bookings:
            await message.answer("Нет активных записей.")
            return

        for booking in bookings:
            status, booking_date, service_description, car_brand, car_model, car_year, car_color, car_number, first_name, phone_number, username = booking

            car_info = f"Марка: {car_brand}, Модель: {car_model}, Год: {car_year}, Цвет: {car_color}, Номер: {car_number}"
            client_info = f"Имя: {first_name}, Телефон: {phone_number}, Username: @{username}" if username else f"Имя: {first_name}, Телефон: {phone_number}"

            message_text = f"""Статус: {status}
Дата: {booking_date}
Услуга: {service_description}
Авто: {car_info}
Клиент: {client_info}"""

            await message.answer(message_text, reply_markup=keyboard.after_start_admin_kb)


@router.callback_query(StateFilter(BookingStates.select_date))
async def select_date_callback(call: CallbackQuery, state: FSMContext):
    date = call.data.split("_")[1]
    await state.update_data(booking_date=date)
    await call.message.answer("Введите номер телефона или номер автомобиля:")
    await state.set_state(BookingStates.input_client_data)


@router.message(BookingStates.input_client_data)
async def input_client_data(message: Message, state: FSMContext):
    user_input = message.text.strip()

    phone_pattern = re.compile(r"^\+?\d{10,15}$")  # Шаблон для номера телефона

    if phone_pattern.match(user_input):
        client_info = await get_client_and_cars_by_phone(user_input)
        if client_info:
            cars = client_info['cars']
            await state.update_data(client_id=client_info['user']['id'])  # Сохраняем client_id в состоянии
            if not cars:
                await message.answer("У вас нет добавленных автомобилей. Пожалуйста, добавьте автомобиль.",
                                     reply_markup=keyboard.after_start_admin_kb)
                await state.clear()
                #await state.set_state(EditProfile.addAuto)
                return

            # Формируем клавиатуру с номерами автомобилей
            inline_kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=car["car_number"], callback_data=f"car_{car['car_number']}")]
                    for car in cars
                ]
            )

            response = f"Пользователь найден:\n" \
                       f"Имя: {client_info['user']['first_name']}\n" \
                       f"Телефон: {client_info['user']['phone_number']}\n" \
                       f"Выберите автомобиль:"
            await message.answer(response, reply_markup=inline_kb)
            await state.set_state(BookingStates.select_car)
        else:
            await message.answer("Пользователь не найден. Пожалуйста, зарегистрируйтесь.",
                                 reply_markup=keyboard.after_start_admin_kb)
            await state.clear()
            #await state.set_state(UserData.phone)

    elif len(user_input) > 0:  # Обработка номера автомобиля
        car_info = await get_car_and_owner_by_number(user_input)
        if car_info:
            owner = car_info["owner"]
            car = car_info["car"]
            response = f"Автомобиль найден:\n" \
                       f"Марка: {car['car_brand']}\n" \
                       f"Модель: {car['car_model']}\n" \
                       f"Год: {car['car_year']}\n" \
                       f"Цвет: {car['car_color']}\n" \
                       f"Номер: {car['car_number']}\n" \
                       f"Владелец:\n" \
                       f"Имя: {owner['first_name']}\n" \
                       f"Телефон: {owner['phone_number']}\n"
            await message.answer(response)

            await state.update_data(car_number=user_input, client_id=owner["id"])
            await message.answer("Введите описание услуги:")
            await state.set_state(BookingStates.input_service)
        else:
            await message.answer("Автомобиль не найден.", reply_markup=keyboard.after_start_admin_kb)
            await state.clear()
    else:
        await message.answer("Некорректный ввод. Пожалуйста, введите номер телефона или номер автомобиля.")
        await state.clear()  # Завершаем состояние после некорректного ввода


@router.callback_query(StateFilter(BookingStates.select_car))
async def select_car_callback(call: CallbackQuery, state: FSMContext):
    car_number = call.data.split("_")[1]
    await state.update_data(car_number=car_number)
    await call.message.answer("Введите описание услуги:")
    await state.set_state(BookingStates.input_service)


@router.message(BookingStates.input_service)
async def input_service(message: Message, state: FSMContext):
    service_description = message.text.strip()  # Описание услуги
    data = await state.get_data()

    # Получаем данные из состояния
    booking_date = data.get("booking_date")  # Дата записи
    car_number = data.get("car_number")  # Номер автомобиля
    client_id = data.get("client_id")  # ID клиента

    # Очистим booking_date от лишнего текста "date:"
    if booking_date:
        booking_date = booking_date.replace("date:", "").strip()  # Удаляем "date:" и лишние пробелы

    # Если все необходимые данные есть, создаём запись
    if booking_date and car_number and client_id:
        success = await add_booking(booking_date, car_number, client_id, service_description)
        if success:
            # Получаем информацию о машине и владельце
            car_info = await get_car_and_owner_by_number(car_number)

            if car_info is None:
                await message.answer("Не удалось найти информацию о автомобиле.")
                return

            # Форматируем информацию об автомобиле и владельце
            car = car_info["car"]
            owner = car_info["owner"]

            car_info_text = f"Марка: {car['car_brand']}, Модель: {car['car_model']}, Год: {car['car_year']}, Цвет: {car['car_color']}, Номер: {car['car_number']}"
            owner_info_text = f"Имя: {owner['first_name']}, Телефон: {owner['phone_number']}, Username: @{owner['username']}"

            # Формируем сообщение для отправки
            message_text = f"""Новая запись!
Дата: {booking_date}
Услуга: {service_description}
Авто: {car_info_text}
Клиент: {owner_info_text}"""

            await message.answer(message_text, reply_markup=keyboard.after_start_admin_kb)
        else:
            await message.answer(
                f"К сожалению, на дату {booking_date} все посты заняты. Пожалуйста, выберите другую дату.")
        await state.clear()
    else:
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")


@router.callback_query(BookingStates.complete_work)
async def complete_work_selection(callback_query: CallbackQuery, state: FSMContext):
    data = callback_query.data

    if data.startswith("complete_"):
        # Получаем ID записи
        booking_id = int(data.split("_")[1])

        # Обновляем статус записи
        await complete_booking(booking_id)

        # Уведомляем администратора
        await callback_query.message.answer(f"Работа с записью ID {booking_id} успешно завершена.", reply_markup=keyboard.after_start_admin_kb)

        await state.clear()
    else:
        await callback_query.message.answer("Некорректный выбор.", reply_markup=keyboard.after_start_admin_kb)


@router.callback_query(BookingStates.cancel)
async def booking_cancel_selection(callback_query: CallbackQuery, state: FSMContext):
    data = callback_query.data

    if data.startswith("cancel_"):
        # Получаем ID записи
        booking_id = int(data.split("_")[1])

        # Отменяем запись в базе данных
        await cancel_booking(booking_id)

        # Уведомляем администратора
        await callback_query.message.answer(f"Запись с ID {booking_id} успешно отменена.", reply_markup=keyboard.after_start_admin_kb)

        await state.clear()
    else:
        await callback_query.message.answer("Некорректный выбор.", reply_markup=keyboard.after_start_admin_kb)


# Обработчик для выбора записи для переноса
@router.callback_query(StateFilter(BookingStates.select_reschedule))
async def select_reschedule_callback(call: CallbackQuery, state: FSMContext):
    booking_id = int(call.data.split("_")[1])
    await state.update_data(booking_id=booking_id)

    # Получаем список доступных дат из БД
    available_dates = await get_available_dates()
    if not available_dates:
        await call.message.answer("К сожалению, нет доступных дат для записи на ближайшие 30 дней.")
        await state.clear()
        return

    # Создаём инлайн-клавиатуру с доступными датами в три столбца
    inline_kb = keyboard.get_booking_keyboard(available_dates)
    await call.message.answer("Выберите новую дату для записи:", reply_markup=inline_kb)
    await state.set_state(BookingStates.select_new_date)

# Обработчик для выбора новой даты
@router.callback_query(StateFilter(BookingStates.select_new_date))
async def select_new_date_callback(call: CallbackQuery, state: FSMContext):
    new_date = call.data.split("_")[1]
    data = await state.get_data()
    booking_id = data.get("booking_id")

    # Убираем "date:" из даты
    if new_date.startswith("date:"):
        new_date = new_date[len("date:"):]

    # Получаем данные о текущей записи
    booking = await get_booking_by_id(booking_id)

    if booking:
        # Удаляем старую запись
        await delete_booking(booking_id)

        # Вставляем новую запись с новой датой
        success = await add_booking(new_date, booking[1], booking[5], booking[4])
        if success:
            await call.message.answer(f"Запись успешно перенесена на новую дату: {new_date}",
                                      reply_markup=keyboard.after_start_admin_kb)
        else:
            await call.message.answer("Произошла ошибка при переносе записи.",
                                      reply_markup=keyboard.after_start_admin_kb)
    else:
        await call.message.answer("Произошла ошибка при переносе записи.",
                                  reply_markup=keyboard.after_start_admin_kb)

    # Прекращаем выполнение инлайн-клавиатуры и очищаем состояние
    await state.clear()
    await call.message.edit_reply_markup()


@router.message(lambda message: message.text == "Статистика")
async def show_statistics(message: types.Message, state: FSMContext):
    total_bookings = await get_total_bookings()
    completed_bookings = await get_completed_bookings()
    cancelled_bookings = await get_cancelled_bookings()

    response = (
        f"Общая статистика:\n"
        f"Всего записей: {total_bookings}\n"
        f"Завершено: {completed_bookings}\n"
        f"Отменено: {cancelled_bookings}\n"
    )

    await message.answer(response, reply_markup=keyboard.stats_kb)
    await state.set_state(States.search_start)


@router.message(States.search_start)
async def booking_start(message: Message, state: FSMContext):
    if message.text.lower() == "по диапазону дат":
        await message.answer("Введите начальную дату (ГГГГ-ММ-ДД):")
        await state.set_state(States.start_date)
    elif message.text.lower() == "по номеру авто":
        await message.answer("Введите номер автомобиля:")
        await state.set_state(States.car_number)
    elif message.text.lower() == "частое авто":
        most_frequent_car = await get_most_frequent_car()
        if most_frequent_car:
            response = f"Самое частое авто: {most_frequent_car[0]} ({most_frequent_car[1]} раз)"
        else:
            response = "Нет данных о записях."

        await message.answer(response, reply_markup=keyboard.stats_kb)
        await state.search_start()
    else:
        await state.clear()


@router.message(States.start_date)
async def process_start_date(message: types.Message, state: FSMContext):
    start_date = message.text.strip()
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД.")
        return

    await state.update_data(start_date=start_date)
    await message.answer("Введите конечную дату (ГГГГ-ММ-ДД):")
    await state.set_state(States.end_date)

@router.message(States.end_date)
async def process_end_date(message: types.Message, state: FSMContext):
    end_date = message.text.strip()
    try:
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД.")
        return

    data = await state.get_data()
    start_date = data.get("start_date")

    if start_date > end_date:
        await message.answer("Конечная дата должна быть позже начальной даты.")
        return

    bookings, most_frequent_car = await get_bookings_by_date_range(start_date, end_date)

    if not bookings:
        await message.answer(f"За период с {start_date} по {end_date} записей не найдено.")
        await state.finish()
        return

    # Подсчёт статусов
    total_bookings = len(bookings)
    planned_bookings = sum(1 for booking in bookings if booking[0] == 'запланировано')
    in_progress_or_completed = sum(1 for booking in bookings if booking[0] in ('в работе', 'завершено'))
    cancelled_bookings = sum(1 for booking in bookings if booking[0] == 'отменено')

    # Процентные соотношения
    planned_percentage = round(planned_bookings / total_bookings * 100, 2) if total_bookings else 0
    in_progress_or_completed_percentage = round(in_progress_or_completed / total_bookings * 100, 2) if total_bookings else 0
    cancelled_percentage = round(cancelled_bookings / total_bookings * 100, 2) if total_bookings else 0

    # Формирование основного ответа
    response = (
        f"Статистика по датам с {start_date} по {end_date}:\n"
        f"Всего записей: {total_bookings}\n"
        f"Запланировано: {planned_bookings} ({planned_percentage}%)\n"
        f"В работе или завершено: {in_progress_or_completed} ({in_progress_or_completed_percentage}%)\n"
        f"Отменено: {cancelled_bookings} ({cancelled_percentage}%)\n"
    )

    # Информация о наиболее частом авто
    if most_frequent_car and most_frequent_car[1] > 1:  # Если авто записывалось более одного раза
        car_number, count, car_brand, car_model, owner_name, owner_phone = most_frequent_car
        response += (
            f"\nНаиболее частое авто за этот период:\n"
            f"Номер: {car_number}\n"
            f"Марка: {car_brand}\n"
            f"Модель: {car_model}\n"
            f"Посещений: {count}\n"
            f"Владелец: {owner_name}\n"
            f"Телефон: {owner_phone}\n"
        )

    await message.answer(response, reply_markup=keyboard.stats_kb)
    await state.search_start()


@router.message(States.car_number)
async def process_car_number(message: types.Message, state: FSMContext):
    car_number = message.text.strip()
    bookings, count_last_year, owner_name, owner_phone = await get_bookings_by_car_number(car_number)

    if not bookings:
        await message.answer(f"По авто с номером {car_number} записей не найдено.")
        await state.clear()
        return

    total_bookings = len(bookings)
    completed_bookings = sum(1 for booking in bookings if booking[5] == 'завершено')
    cancelled_bookings = sum(1 for booking in bookings if booking[5] == 'отменено')

    # Формируем ответ с учётом данных о владельце
    owner_info = (
        f"Имя: {owner_name}\nТелефон: {owner_phone}\n"
        if owner_name and owner_phone else "Информация о владельце недоступна.\n"
    )

    response = (
        f"Статистика по авто {car_number}:\n"
        f"Всего записей: {total_bookings}\n"
        f"Завершено: {completed_bookings}\n"
        f"Отменено: {cancelled_bookings}\n"
        f"Записей за последний год: {count_last_year}\n\n"
        f"Информация о владельце:\n{owner_info}"
    )

    await message.answer(response, reply_markup=keyboard.stats_kb)
    await state.search_start()









@router.message(F.text.lower() == "наши контакты")
async def registration(message:Message) -> None:
    text1 = hlink('VKontakte', 'https://vk.com/studia818')
    text2 = hlink('TikTok', 'https://www.tiktok.com/@studia818')
    text3 = hlink('Instagram', 'https://www.instagram.com/studia.818?igsh=ZHE0ZmI2d2FpMnJn')

    photo_path = "D:/Programming/TGBot/818_logo.jpg"

    await message.answer_photo(photo=FSInputFile(photo_path),
                               caption=text1+'\n'+text2+'\n'+text3,
                               disable_web_page_preview=True)


@router.message()
async def dont_understand(message:Message) -> None:
    await message.answer(f"Я не могу распознать данную команду или текст")