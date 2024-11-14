import os
import asyncio
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InputFile, FSInputFile
from aiogram.filters import CommandStart, Command, state
import keyboard
from decouple import config
from db import get_user_by_id, add_user, get_user_by_phone
import re
from aiogram.fsm.context import FSMContext
from utils.states import UserData, UserDataforAdmin
from aiogram.utils.markdown import hlink


router = Router()

admin_ids = list(map(int, config('ADMINS').split(',')))
phone_number = None

@router.message(CommandStart())
async def start_command(message:Message) -> None:
    telegram_id = message.from_user.id
    user_data = await get_user_by_id(telegram_id)

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
    db_name = dbname.get("name")

    if telegram_id in admin_ids:
        await message.answer(f"Поздравляю, {db_name}, регистрация прошла успешно!",
                             reply_markup=keyboard.after_start_admin_kb)
    else:
        await message.answer(f"Поздравляю, {db_name}, регистрация прошла успешно!",
                             reply_markup=keyboard.after_start_kb)


@router.message(F.text.lower() == "зарегистрировать клиента")
async def registration_admin(message: Message, state: FSMContext) -> None:
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