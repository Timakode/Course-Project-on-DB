from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


class UserData(StatesGroup):
    phone = State()
    name = State()


class UserDataforAdmin(StatesGroup):
    phone = State()
    name = State()


class EditProfile(StatesGroup):
    start = State()
    phone = State()
    addAuto = State()
    editAuto = State()
    car_number = State()
    car_brand = State()
    car_model = State()
    car_year = State()
    car_color = State()
    wrapped_car = State()
    repainted_car = State()
