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
    name = State()
    addAuto = State()
    car_brand = State()
    car_model = State()
    car_year = State()
    car_color = State()
    wrapped_car = State()
    repainted_car = State()
    editAuto = State()
    selectCarToEdit = State()
    editCarOption = State()
    editCarColor = State()
    editCarNumber = State()
    editCarWrapped = State()
    editCarRepainted = State()


class SearchData(StatesGroup):
    search_input = State()


class BookingStates(StatesGroup):
    start = State()
    sign_up = State()  # Для бронирования
    select_date = State()
    input_client_data = State()
    select_car = State()
    input_service = State()
    cancel = State()  # Для отмены бронирования
    select_booking_to_cancel = State()
    complete_work = State()  # Для завершения работы
    reschedule = State()  # Для переноса бронирования
    waiting_for_service_description = State()  # Для описания услуги
    waiting_for_new_date = State()
    select_reschedule = State()
    select_new_date = State()


class States(StatesGroup):
    search_start = State()
    start_date = State()
    end_date = State()
    car_number = State()
    car_brand = State()
    date = State()
    pattern = State()
    telegram_ids = State()
    waiting_for_car_brands = State()


class EditClientProfile(StatesGroup):
    phone = State()
    start = State()
    new_phone = State()
    addAuto = State()
    car_brand = State()
    car_model = State()
    car_year = State()
    car_color = State()
    wrapped_car = State()
    repainted_car = State()
    editAuto = State()
    editCarOption = State()
    editCarColor = State()
    editCarNumber = State()
    editCarWrapped = State()
    editCarRepainted = State()
