from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                           QLineEdit, QDateEdit, QComboBox, QPushButton,
                           QMessageBox, QSpinBox)
from PyQt6.QtCore import QDate
import asyncio
from typing import Optional, Dict, List
import asyncpg

class UserDialog(QDialog):
    def __init__(self, pool: asyncpg.Pool, user_data: Dict = None, parent=None):
        super().__init__(parent)
        self.pool = pool
        self.user_data = user_data
        self.setWindowTitle("Пользователь")
        layout = QVBoxLayout(self)
        
        # Поля ввода
        self.name_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("+7XXXXXXXXXX")
        
        # Заполняем данные если это редактирование
        if user_data:
            self.name_edit.setText(user_data['имя_пользователя'])
            self.phone_edit.setText(user_data['номер_телефона'])
        
        # Добавляем поля в layout
        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Имя:"))
        form_layout.addWidget(self.name_edit)
        form_layout.addWidget(QLabel("Телефон:"))
        form_layout.addWidget(self.phone_edit)
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Отмена")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)
    
    def get_data(self) -> Dict:
        return {
            'имя_пользователя': self.name_edit.text(),
            'номер_телефона': self.phone_edit.text()
        }

class CarDialog(QDialog):
    def __init__(self, pool: asyncpg.Pool, car_data: Dict = None, parent=None):
        super().__init__(parent)
        self.pool = pool
        self.car_data = car_data
        self.setWindowTitle("Автомобиль")
        layout = QVBoxLayout(self)
        
        # Поля ввода
        self.plate_edit = QLineEdit()
        self.user_combo = QComboBox()
        self.brand_combo = QComboBox()
        self.model_combo = QComboBox()
        self.year_spin = QSpinBox()
        self.year_spin.setRange(1900, 2024)
        self.color_combo = QComboBox()
        self.wrap_combo = QComboBox()
        self.paint_combo = QComboBox()
        
        # Настраиваем поля
        self.year_spin.setValue(2024)
        
        # Добавляем поля в layout
        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Номер:"))
        form_layout.addWidget(self.plate_edit)
        form_layout.addWidget(QLabel("Владелец:"))
        form_layout.addWidget(self.user_combo)
        form_layout.addWidget(QLabel("Бренд:"))
        form_layout.addWidget(self.brand_combo)
        form_layout.addWidget(QLabel("Модель:"))
        form_layout.addWidget(self.model_combo)
        form_layout.addWidget(QLabel("Год выпуска:"))
        form_layout.addWidget(self.year_spin)
        form_layout.addWidget(QLabel("Цвет:"))
        form_layout.addWidget(self.color_combo)
        form_layout.addWidget(QLabel("Оклейка:"))
        form_layout.addWidget(self.wrap_combo)
        form_layout.addWidget(QLabel("Перекрас:"))
        form_layout.addWidget(self.paint_combo)
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Отмена")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)
        
        # Загружаем данные для комбобоксов
        asyncio.get_event_loop().run_until_complete(self.load_data())
        
        # Заполняем данные если это редактирование
        if car_data:
            self.plate_edit.setText(car_data['номер_авто'])
            self.year_spin.setValue(car_data['год_выпуска'])
            
            # Устанавливаем значения комбобоксов
            self.set_combo_value(self.brand_combo, car_data['бренд'])
            self.set_combo_value(self.model_combo, car_data['модель'])
            self.set_combo_value(self.color_combo, car_data['цвет'])
            self.set_combo_value(self.wrap_combo, car_data['статус_оклейки'])
            self.set_combo_value(self.paint_combo, car_data['статус_перекраса'])
    
    def set_combo_value(self, combo: QComboBox, value: str):
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)
    
    async def load_data(self):
        async with self.pool.acquire() as conn:
            # Загружаем пользователей
            users = await conn.fetch("SELECT id, имя_пользователя FROM пользователи ORDER BY имя_пользователя")
            self.user_combo.clear()
            for user in users:
                self.user_combo.addItem(user['имя_пользователя'], user['id'])
            
            # Загружаем бренды
            brands = await conn.fetch("SELECT DISTINCT бренд FROM бренд_авто ORDER BY бренд")
            self.brand_combo.clear()
            for brand in brands:
                self.brand_combo.addItem(brand['бренд'])
            
            # Загружаем цвета
            colors = await conn.fetch("SELECT DISTINCT цвет FROM цвет_авто ORDER BY цвет")
            self.color_combo.clear()
            for color in colors:
                self.color_combo.addItem(color['цвет'])
            
            # Загружаем статусы оклейки
            wraps = await conn.fetch("SELECT статус_оклейки FROM оклейка_авто ORDER BY id")
            self.wrap_combo.clear()
            for wrap in wraps:
                self.wrap_combo.addItem(wrap['статус_оклейки'])
            
            # Загружаем статусы перекраса
            paints = await conn.fetch("SELECT статус_перекраса FROM перекрас_авто ORDER BY id")
            self.paint_combo.clear()
            for paint in paints:
                self.paint_combo.addItem(paint['статус_перекраса'])
    
    def get_data(self) -> Dict:
        return {
            'номер_авто': self.plate_edit.text(),
            'id_пользователя': self.user_combo.currentData(),
            'бренд': self.brand_combo.currentText(),
            'модель': self.model_combo.currentText(),
            'год_выпуска': self.year_spin.value(),
            'цвет': self.color_combo.currentText(),
            'статус_оклейки': self.wrap_combo.currentText(),
            'статус_перекраса': self.paint_combo.currentText()
        }

class AppointmentDialog(QDialog):
    def __init__(self, pool: asyncpg.Pool, appointment_data: Dict = None, parent=None):
        super().__init__(parent)
        self.pool = pool
        self.appointment_data = appointment_data
        self.setWindowTitle("Запись")
        layout = QVBoxLayout(self)
        
        # Поля ввода
        self.user_combo = QComboBox()
        self.car_combo = QComboBox()
        self.date_edit = QDateEdit()
        self.date_edit.setMinimumDate(QDate.currentDate())
        self.services_combo = QComboBox()
        self.services_combo.setEditable(True)
        self.services_combo.setInsertPolicy(QComboBox.InsertPolicy.InsertAtBottom)
        
        # Добавляем поля в layout
        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Клиент:"))
        form_layout.addWidget(self.user_combo)
        form_layout.addWidget(QLabel("Автомобиль:"))
        form_layout.addWidget(self.car_combo)
        form_layout.addWidget(QLabel("Дата:"))
        form_layout.addWidget(self.date_edit)
        form_layout.addWidget(QLabel("Услуги:"))
        form_layout.addWidget(self.services_combo)
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Отмена")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)
        
        # Загружаем данные для комбобоксов
        asyncio.get_event_loop().run_until_complete(self.load_data())
        
        # Заполняем данные если это редактирование
        if appointment_data:
            self.date_edit.setDate(QDate.fromString(appointment_data['дата_записи'], 'yyyy-MM-dd'))
            
            # Устанавливаем значения комбобоксов
            self.set_combo_value(self.user_combo, appointment_data['имя_пользователя'])
            self.set_combo_value(self.car_combo, appointment_data['номер_авто'])
    
    def set_combo_value(self, combo: QComboBox, value: str):
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)
    
    async def load_data(self):
        async with self.pool.acquire() as conn:
            # Загружаем пользователей
            users = await conn.fetch("SELECT id, имя_пользователя FROM пользователи ORDER BY имя_пользователя")
            self.user_combo.clear()
            for user in users:
                self.user_combo.addItem(user['имя_пользователя'], user['id'])
            
            # Загружаем услуги
            services = await conn.fetch("SELECT id, название_услуги FROM услуги ORDER BY название_услуги")
            self.services_combo.clear()
            for service in services:
                self.services_combo.addItem(service['название_услуги'], service['id'])
    
    async def update_cars(self, user_id: int):
        async with self.pool.acquire() as conn:
            cars = await conn.fetch("""
                SELECT номер_авто 
                FROM автомобили 
                WHERE id_пользователя = $1
                ORDER BY номер_авто
            """, user_id)
            
            self.car_combo.clear()
            for car in cars:
                self.car_combo.addItem(car['номер_авто'])
    
    def get_data(self) -> Dict:
        return {
            'id_пользователя': self.user_combo.currentData(),
            'номер_авто': self.car_combo.currentText(),
            'дата_записи': self.date_edit.date().toString('yyyy-MM-dd'),
            'услуги': [self.services_combo.currentData()]
        } 