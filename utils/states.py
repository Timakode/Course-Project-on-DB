from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

class UserData(StatesGroup):
    phone = State()
    name = State()

class UserDataforAdmin(StatesGroup):
    phone = State()
    name = State()