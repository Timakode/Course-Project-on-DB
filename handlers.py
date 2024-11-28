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


@router.message(F.text.lower() == "зарегистрировать клиента")
async def registration_admin(message: Message, state: FSMContext):
    # Начало регистрации клиента
    await message.answer("Пожалуйста, введите номер телефона Клиента в формате +79491234567")
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
    await message.answer("Введите номер телефона в формате +79491234567 или номер автомобиля:")


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