from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                           QLineEdit, QPushButton, QFormLayout, QMessageBox,
                           QSpinBox, QComboBox, QInputDialog, QWidget, QTableWidget, QCheckBox,
                           QDateEdit, QGroupBox)
from PyQt6.QtCore import QDate, Qt  # Добавляем импорт Qt
import asyncio
import json

class BaseDialog(QDialog):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.layout = QVBoxLayout(self)
        self.values = {}

        # Кнопки
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        self.layout.addLayout(btn_layout)

    def get_data(self):
        return self.values

class UserDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Пользователь", parent)

        # Поля ввода
        self.name_edit = QLineEdit()
        self.phone_edit = QLineEdit()

        # Добавляем поля в layout
        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Имя:"))
        form_layout.addWidget(self.name_edit)
        form_layout.addWidget(QLabel("Телефон:"))
        form_layout.addWidget(self.phone_edit)

        # Вставляем форму перед кнопками
        self.layout.insertLayout(0, form_layout)

    def accept(self):
        self.values = {
            'username': self.name_edit.text(),
            'phone_number': self.phone_edit.text()
        }
        super().accept()

class SimpleInputDialog(QDialog):
    def __init__(self, title, field_name, current_value=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        # Input field
        self.text_edit = QLineEdit()
        if current_value:
            self.text_edit.setText(current_value)
        
        # Add widgets to layout
        layout.addWidget(QLabel(f"{field_name}:"))
        layout.addWidget(self.text_edit)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
    
    def get_data(self):
        return {'name': self.text_edit.text().strip()}

class UserInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New User")
        layout = QVBoxLayout(self)

        # Form layout for inputs
        form = QFormLayout()
        self.username_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.phone_edit.setInputMask('+79999999999')  # Phone mask
        self.phone_edit.setPlaceholderText('+7XXXXXXXXXX')

        form.addRow("Username:", self.username_edit)
        form.addRow("Phone:", self.phone_edit)
        layout.addLayout(form)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")

        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def get_values(self):
        values = {
            'username': self.username_edit.text(),
            'phone_number': self.phone_edit.text()
        }
        print(f"Dialog returning values: {values}")  # Debug info
        return values

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление пользователя")
        self.setMinimumWidth(300)
        self.setModal(True)  # Делаем диалог модальным
        
        layout = QVBoxLayout(self)
        
        # Поля ввода
        self.name_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("+7XXXXXXXXXX")
        
        # Создаем форму
        layout.addWidget(QLabel("Имя:"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("Телефон (формат: +7XXXXXXXXXX):"))
        layout.addWidget(self.phone_edit)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        
        self.save_btn.clicked.connect(self.validate_and_accept)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
    
    def validate_and_accept(self):
        name = self.name_edit.text().strip()
        phone = self.phone_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите имя пользователя")
            return False
            
        if not phone.startswith('+7') or len(phone) != 12 or not phone[2:].isdigit():
            QMessageBox.warning(self, "Ошибка", "Введите корректный номер телефона в формате: +7XXXXXXXXXX")
            return False
        
        self.accept()
        return True
    
    def get_data(self):
        return {
            'username': self.name_edit.text().strip(),
            'phone_number': self.phone_edit.text().strip()
        }

class SimpleDataDialog(QDialog):
    def __init__(self, title, field_name, value=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        # Поле ввода
        self.data_edit = QLineEdit()
        if value:
            self.data_edit.setText(value)
        
        layout.addWidget(QLabel(f"{field_name}:"))
        layout.addWidget(self.data_edit)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
    
    def get_data(self):
        return {'name': self.data_edit.text().strip()}

class ServiceDialog(QDialog):
    def __init__(self, pool, service_data=None, parent=None):
        super().__init__(parent)
        self.pool = pool
        self.setWindowTitle("Услуга")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        # Поля ввода
        self.name_edit = QLineEdit()
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(15, 480)  # 15 минут - 8 часов
        self.duration_spin.setSingleStep(15)  # шаг 15 минут
        self.box_combo = QComboBox()
        
        if service_data:
            self.name_edit.setText(service_data['name'])
            self.duration_spin.setValue(service_data['duration'])
        
        # Добавляем поля в layout
        layout.addWidget(QLabel("Название:"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("Длительность (минут):"))
        layout.addWidget(self.duration_spin)
        layout.addWidget(QLabel("Бокс:"))
        layout.addWidget(self.box_combo)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        # Загружаем боксы
        asyncio.get_event_loop().run_until_complete(self.load_boxes())
        
        if service_data and service_data.get('box_id'):
            index = self.box_combo.findData(service_data['box_id'])
            if index >= 0:
                self.box_combo.setCurrentIndex(index)
    
    async def load_boxes(self):
        async with self.pool.acquire() as conn:
            boxes = await conn.fetch("SELECT id, type FROM boxes ORDER BY type")
            self.box_combo.clear()
            self.box_combo.addItem("Не выбран", None)
            for box in boxes:
                self.box_combo.addItem(box['type'], box['id'])
    
    def get_data(self):
        return {
            'name': self.name_edit.text().strip(),
            'duration': self.duration_spin.value(),
            'box_id': self.box_combo.currentData()
        }

class BoxDialog(QDialog):
    def __init__(self, current_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Бокс")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        # Поля ввода
        self.type_edit = QLineEdit()
        self.capacity_spin = QSpinBox()
        self.capacity_spin.setMinimum(1)
        self.capacity_spin.setMaximum(10)
        
        if current_data:
            self.type_edit.setText(current_data.get('type', ''))
            self.capacity_spin.setValue(current_data.get('capacity', 1))
        
        # Add fields to layout
        layout.addWidget(QLabel("Тип бокса:"))
        layout.addWidget(self.type_edit)
        layout.addWidget(QLabel("Вместимость:"))
        layout.addWidget(self.capacity_spin)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
    
    def get_data(self):
        return {
            'type': self.type_edit.text().strip(),
            'capacity': self.capacity_spin.value()
        }

class BoxInputDialog(QDialog):
    def __init__(self, current_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление бокса")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        # Поля ввода
        self.type_edit = QLineEdit()
        self.capacity_spin = QSpinBox()
        self.capacity_spin.setRange(1, 10)
        
        if current_data:
            self.type_edit.setText(current_data.get('type', ''))
            self.capacity_spin.setValue(current_data.get('capacity', 1))
        
        # Add widgets to layout
        layout.addWidget(QLabel("Тип бокса:"))
        layout.addWidget(self.type_edit)
        layout.addWidget(QLabel("Вместимость:"))
        layout.addWidget(self.capacity_spin)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
    
    def get_data(self):
        return {
            'type': self.type_edit.text().strip(),
            'capacity': self.capacity_spin.value()
        }

class ServiceInputDialog(QDialog):
    def __init__(self, pool, service_data=None, parent=None):
        super().__init__(parent)
        self.pool = pool
        self.setWindowTitle("Услуга")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        # Поля ввода
        self.name_edit = QLineEdit()
        self.duration_spin = QSpinBox()
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(['минуты', 'дни'])
        
        # Настраиваем спиннер в зависимости от единицы измерения
        self.unit_combo.currentTextChanged.connect(self._on_unit_changed)
        
        # Добавляем поля в layout
        layout.addWidget(QLabel("Название:"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("Длительность:"))
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(self.duration_spin)
        duration_layout.addWidget(self.unit_combo)
        layout.addLayout(duration_layout)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        # Устанавливаем начальные значения
        self._on_unit_changed('минуты')
        
        # Заполняем данные если это редактирование
        if service_data:
            self.name_edit.setText(service_data['name'])
            duration = service_data['duration']
            self.duration_spin.setValue(duration[0])  # value
            self.unit_combo.setCurrentText('минуты' if duration[1] == 'minutes' else 'дни')

    def _on_unit_changed(self, unit):
        if unit == 'минуты':
            self.duration_spin.setRange(15, 480)
            self.duration_spin.setSingleStep(15)
        else:  # дни
            self.duration_spin.setRange(1, 30)
            self.duration_spin.setSingleStep(1)

    def get_data(self):
        return {
            'name': self.name_edit.text().strip(),
            'duration_value': self.duration_spin.value(),
            'duration_unit': 'minutes' if self.unit_combo.currentText() == 'минуты' else 'days'
        }

class CarModelDialog(QDialog):
    def __init__(self, pool, model_data=None, parent=None):
        super().__init__(parent)
        self.pool = pool
        self.setWindowTitle("Модель автомобиля")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        # Поля ввода
        self.model_edit = QLineEdit()
        self.brand_combo = QComboBox()
        self.brand_combo.setEditable(True)
        self.brand_combo.setInsertPolicy(QComboBox.InsertPolicy.InsertAtBottom)
        
        # Добавляем поля в layout
        layout.addWidget(QLabel("Модель:"))
        layout.addWidget(self.model_edit)
        layout.addWidget(QLabel("Бренд:"))
        layout.addWidget(self.brand_combo)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        # Заполняем данные если это редактирование
        if model_data:
            self.model_edit.setText(model_data['model'])
            self.current_brand = model_data['brand']
    
    def _set_current_brand(self):
        if hasattr(self, 'current_brand'):
            index = self.brand_combo.findText(self.current_brand)
            if index >= 0:
                self.brand_combo.setCurrentIndex(index)
    
    def showEvent(self, event):
        super().showEvent(event)
        self._set_current_brand()
    
    def get_data(self):
        return {
            'model': self.model_edit.text().strip(),
            'brand': self.brand_combo.currentText().strip()
        }

class CarPartsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # Создаем кнопки для добавления/удаления статусов перекраса
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить статус")
        self.remove_btn = QPushButton("Удалить статус")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        layout.addLayout(btn_layout)
        
        # Список статусов перекраса
        self.parts_list = []
        self.list_widget = QTableWidget()
        self.list_widget.setColumnCount(2)
        self.list_widget.setHorizontalHeaderLabels(["Статус", "Выбрано"])
        layout.addWidget(self.list_widget)
        
        # Подключаем сигналы
        self.add_btn.clicked.connect(self.add_part)
        self.remove_btn.clicked.connect(self.remove_part)
    
    def add_part(self):
        from_idx = self.list_widget.rowCount()
        self.list_widget.setRowCount(from_idx + 1)
        
        # Добавляем выпадающий список со статусами
        combo = QComboBox()
        combo.addItems(['None', 'Partial', 'Full'])
        self.list_widget.setCellWidget(from_idx, 0, combo)
        
        # Добавляем чекбокс
        check = QCheckBox()
        self.list_widget.setCellWidget(from_idx, 1, check)
    
    def remove_part(self):
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            self.list_widget.removeRow(current_row)
    
    def get_data(self):
        result = {}
        for row in range(self.list_widget.rowCount()):
            combo = self.list_widget.cellWidget(row, 0)
            check = self.list_widget.cellWidget(row, 1)
            if check.isChecked():
                result[f"part_{row}"] = combo.currentText()
        return result

class CarDialog(QDialog):
    def __init__(self, pool, loop, car_data=None, parent=None):  # Add loop parameter
        super().__init__(parent)
        self.pool = pool
        self.loop = loop  # Store the loop
        self.setWindowTitle("Автомобиль")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Поля ввода
        self.plate_edit = QLineEdit()
        self.plate_edit.setPlaceholderText("А000АА000")
        self.user_combo = QComboBox()
        self.model_combo = QComboBox()
        self.year_spin = QSpinBox()
        self.year_spin.setRange(1900, QDate.currentDate().year())
        self.year_spin.setValue(QDate.currentDate().year())
        self.color_combo = QComboBox()
        self.color_combo.setEditable(True)  # Делаем редактируемым
        self.color_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Запрещаем автоматическую вставку
        self.wrap_combo = QComboBox()
        self.wrap_combo.setEditable(True)  # Делаем комбобокс редактируемым
        self.wrap_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.repaint_combo = QComboBox()
        self.repaint_combo.setEditable(True)  # Делаем комбобокс редактируемым
        self.repaint_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Запрещаем автоматическую вставку
        
        # Формируем layout
        form_layout = QFormLayout()
        form_layout.addRow("Номер авто:", self.plate_edit)
        form_layout.addRow("Владелец:", self.user_combo)
        form_layout.addRow("Модель:", self.model_combo)
        form_layout.addRow("Год выпуска:", self.year_spin)
        form_layout.addRow("Цвет:", self.color_combo)
        form_layout.addRow("Статус оклейки:", self.wrap_combo)

        # Создаем контейнер для статусов перекраса
        repaint_group = QGroupBox("Статусы перекраса")
        repaint_group.setObjectName("repaint_group")  # Добавляем имя объекта
        repaint_layout = QVBoxLayout()
        
        # Список для хранения комбобоксов
        self.repaint_combos = []
        
        # Добавляем первый комбобокс
        first_combo = QComboBox()
        first_combo.setEditable(True)
        first_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.repaint_combos.append(first_combo)
        repaint_layout.addWidget(first_combo)
        
        # Кнопки управления статусами
        btn_layout = QHBoxLayout()
        add_status_btn = QPushButton("+")
        remove_status_btn = QPushButton("-")
        add_status_btn.clicked.connect(self.add_repaint_status)
        remove_status_btn.clicked.connect(self.remove_repaint_status)
        btn_layout.addWidget(add_status_btn)
        btn_layout.addWidget(remove_status_btn)
        repaint_layout.addLayout(btn_layout)
        
        repaint_group.setLayout(repaint_layout)
        form_layout.addRow(repaint_group)

        layout.addLayout(form_layout)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        save_btn.clicked.connect(self.validate_and_accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        # Сохраняем данные для установки после загрузки
        self.car_data = car_data
        
        # Используем переданный loop вместо window().loop
        self.loop.create_task(self.load_data())

        # Добавим отладочный вывод
        print("Initializing CarDialog...")
        
        # После создания интерфейса сразу загрузим данные
        future = asyncio.run_coroutine_threadsafe(self.load_data(), self.loop)
        try:
            future.result()  # Дождемся загрузки данных
            print("Data loaded successfully")
        except Exception as e:
            print(f"Error loading data: {str(e)}")

    def add_repaint_status(self):
        """Добавляет новый комбобокс для статуса перекраса"""
        combo = QComboBox()
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        
        # Копируем items из первого комбобокса
        if self.repaint_combos:
            first_combo = self.repaint_combos[0]
            for i in range(first_combo.count()):
                combo.addItem(first_combo.itemText(i), first_combo.itemData(i))
        
        # Используем правильное имя объекта для поиска
        layout = self.findChild(QGroupBox, "repaint_group").layout()
        layout.insertWidget(len(self.repaint_combos), combo)
        self.repaint_combos.append(combo)

    def remove_repaint_status(self):
        """Удаляет последний добавленный комбобокс"""
        if len(self.repaint_combos) > 1:  # Всегда оставляем хотя бы один комбобокс
            combo = self.repaint_combos.pop()
            combo.deleteLater()

    async def load_data(self):
        print("Starting load_data...")
        try:
            async with self.pool.acquire() as conn:
                # Загружаем пользователей
                users = await conn.fetch('SELECT * FROM get_users_for_combo()')
                print(f"Loaded {len(users)} users")
                
                self.user_combo.clear()
                for user in users:
                    print(f"Adding user: {user['display_name']}")
                    self.user_combo.addItem(user['display_name'], user['id'])
                
                # Загружаем модели с брендами
                models = await conn.fetch('SELECT * FROM get_models_for_combo()')
                self.model_combo.clear()
                for model in models:
                    self.model_combo.addItem(model['display_name'], model['id'])
                
                # Загружаем цвета
                colors = await conn.fetch('SELECT * FROM get_colors_for_combo()')
                self.color_combo.clear()
                for color in colors:
                    self.color_combo.addItem(color['color'], color['id'])
                
                # Загружаем статусы оклейки
                wraps = await conn.fetch('SELECT * FROM get_wraps_for_combo()')
                self.wrap_combo.clear()
                for wrap in wraps:
                    self.wrap_combo.addItem(wrap['status'], wrap['id'])
                
                # Загружаем статусы перекраса
                repaints = await conn.fetch('SELECT * FROM get_repaints_for_combo()')
                for combo in self.repaint_combos:
                    combo.clear()
                    for repaint in repaints:
                        combo.addItem(repaint['status'], repaint['id'])
                
                # Если есть данные для редактирования, устанавливаем их
                if self.car_data:
                    self.plate_edit.setText(self.car_data['plate_number'])
                    self.year_spin.setValue(self.car_data['year'])
                    self.set_combo_value(self.user_combo, self.car_data['user_id'])
                    self.set_combo_value(self.model_combo, self.car_data['model_id'])
                    self.set_combo_value(self.color_combo, self.car_data['color_id'])
                    self.set_combo_value(self.wrap_combo, self.car_data['wrap_id'])
                    self.set_combo_value(self.repaint_combo, self.car_data['repaint_id'])
        
        except Exception as e:
            print(f"Error in load_data: {str(e)}")
            raise
    
    def set_combo_value(self, combo: QComboBox, value):
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)
    
    def validate_and_accept(self):
        # Проверяем номер авто
        plate = self.plate_edit.text().strip().upper()
        if not plate or not plate.replace(' ', ''):
            QMessageBox.warning(self, "Ошибка", "Введите номер автомобиля")
            return False
        
        # Проверяем обязательные поля
        if self.user_combo.currentIndex() == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите владельца")
            return False
        
        if self.model_combo.currentIndex() == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите модель")
            return False

        # Обрабатываем цвет
        color_text = self.color_combo.currentText().strip()
        if not color_text:
            QMessageBox.warning(self, "Ошибка", "Введите цвет")
            return False

        try:
            # Пытаемся получить ID цвета или создать новый
            future = asyncio.run_coroutine_threadsafe(
                self._get_or_create_color(color_text),
                self.loop
            )
            result = future.result()
            if result.get('success'):
                # Обновляем комбобокс - находим индекс по ID
                index = self.color_combo.findData(result['id'])
                if index >= 0:
                    self.color_combo.setCurrentIndex(index)
                else:
                    # Если цвет новый - добавляем его в комбобокс
                    self.color_combo.addItem(color_text, result['id'])
                    self.color_combo.setCurrentIndex(self.color_combo.count() - 1)
            else:
                QMessageBox.warning(self, "Ошибка", result.get('error', 'Неизвестная ошибка'))
                return False
        except Exception as e:
            print(f"Error processing color: {str(e)}")
            QMessageBox.critical(self, "Ошибка", str(e))
            return False

        # Обрабатываем статус оклейки
        wrap_text = self.wrap_combo.currentText().strip()
        if not wrap_text:
            QMessageBox.warning(self, "Ошибка", "Введите статус оклейки")
            return False

        try:
            # Пытаемся получить ID статуса оклейки или создать новый
            future = asyncio.run_coroutine_threadsafe(
                self._get_or_create_wrap(wrap_text),
                self.loop
            )
            result = future.result()
            if result.get('success'):
                # Обновляем комбобокс - находим индекс по ID
                index = self.wrap_combo.findData(result['id'])
                if index >= 0:
                    self.wrap_combo.setCurrentIndex(index)
                else:
                    # Если статус новый - добавляем его в комбобокс
                    self.wrap_combo.addItem(wrap_text, result['id'])
                    self.wrap_combo.setCurrentIndex(self.wrap_combo.count() - 1)
            else:
                QMessageBox.warning(self, "Ошибка", result.get('error', 'Неизвестная ошибка'))
                return False
        except Exception as e:
            print(f"Error processing wrap status: {str(e)}")
            QMessageBox.critical(self, "Ошибка", str(e))
            return False

        # Обрабатываем статусы перекраса
        valid_statuses = []
        for combo in self.repaint_combos:
            repaint_text = combo.currentText().strip()
            if repaint_text:
                try:
                    future = asyncio.run_coroutine_threadsafe(
                        self._get_or_create_repaint(repaint_text),
                        self.loop
                    )
                    result = future.result()
                    if result.get('success'):
                        # Обновляем комбобокс
                        index = combo.findData(result['id'])
                        if index >= 0:
                            combo.setCurrentIndex(index)
                        else:
                            combo.addItem(repaint_text, result['id'])
                            combo.setCurrentIndex(combo.count() - 1)
                        valid_statuses.append(result['id'])
                    else:
                        QMessageBox.warning(self, "Ошибка", result.get('error', 'Неизвестная ошибка'))
                        return False
                except Exception as e:
                    print(f"Error processing repaint status: {str(e)}")
                    QMessageBox.critical(self, "Ошибка", str(e))
                    return False

        if not valid_statuses:
            QMessageBox.warning(self, "Ошибка", "Введите хотя бы один статус перекраса")
            return False

        self.accept()
        return True

    async def _get_or_create_color(self, color_name):
        try:
            async with self.pool.acquire() as conn:
                # Пытаемся найти существующий цвет
                existing_color = await conn.fetchrow(
                    'SELECT id FROM car_colors WHERE normalize_string(color) = normalize_string($1)',
                    color_name
                )
                
                if existing_color:
                    return {'success': True, 'id': existing_color['id']}
                
                # Если цвет не найден, создаем новый
                await conn.execute('CALL add_car_color($1)', color_name)
                
                # Получаем ID нового цвета
                new_color = await conn.fetchrow(
                    'SELECT id FROM car_colors WHERE normalize_string(color) = normalize_string($1)',
                    color_name
                )
                
                if new_color:
                    # Обновляем таблицу цветов
                    main_window = self.window()
                    if hasattr(main_window, 'tables'):
                        colors_tab = main_window.tables.get('Car Colors')
                        if colors_tab:
                            await colors_tab._refresh_data()
                    
                    return {'success': True, 'id': new_color['id']}
                else:
                    return {'error': 'Failed to add new color'}

        except Exception as e:
            print(f"Error in _get_or_create_color: {str(e)}")
            return {'error': str(e)}

    async def _get_or_create_wrap(self, wrap_status):
        try:
            async with self.pool.acquire() as conn:
                # Пытаемся найти существующий статус
                existing_wrap = await conn.fetchrow(
                    'SELECT id FROM car_wraps WHERE normalize_string(status) = normalize_string($1)',
                    wrap_status
                )
                
                if existing_wrap:
                    return {'success': True, 'id': existing_wrap['id']}
                
                # Если статус не найден, создаем новый
                await conn.execute('CALL add_car_wrap($1)', wrap_status)
                
                # Получаем ID нового статуса
                new_wrap = await conn.fetchrow(
                    'SELECT id FROM car_wraps WHERE normalize_string(status) = normalize_string($1)',
                    wrap_status
                )
                
                if new_wrap:
                    # Обновляем таблицу статусов оклейки
                    main_window = self.window()
                    if hasattr(main_window, 'tables'):
                        wraps_tab = main_window.tables.get('Car Wraps')
                        if wraps_tab:
                            await wraps_tab._refresh_data()
                    
                    return {'success': True, 'id': new_wrap['id']}
                else:
                    return {'error': 'Failed to add new wrap status'}

        except Exception as e:
            print(f"Error in _get_or_create_wrap: {str(e)}")
            return {'error': str(e)}

    async def _get_or_create_repaint(self, repaint_status):
        try:
            async with self.pool.acquire() as conn:
                # Пытаемся найти существующий статус
                existing_repaint = await conn.fetchrow(
                    'SELECT id FROM car_repaints WHERE normalize_string(status) = normalize_string($1)',
                    repaint_status
                )
                
                if existing_repaint:
                    return {'success': True, 'id': existing_repaint['id']}
                
                # Если статус не найден, создаем новый
                await conn.execute('CALL add_car_repaint($1)', repaint_status)
                
                # Получаем ID нового статуса
                new_repaint = await conn.fetchrow(
                    'SELECT id FROM car_repaints WHERE normalize_string(status) = normalize_string($1)',
                    repaint_status
                )
                
                if new_repaint:
                    # Обновляем таблицу статусов перекраса
                    main_window = self.window()
                    if hasattr(main_window, 'tables'):
                        repaints_tab = main_window.tables.get('Car Repaints')
                        if repaints_tab:
                            await repaints_tab._refresh_data()
                    
                    return {'success': True, 'id': new_repaint['id']}
                else:
                    return {'error': 'Failed to add new repaint status'}

        except Exception as e:
            print(f"Error in _get_or_create_repaint: {str(e)}")
            return {'error': str(e)}

    def get_data(self):
        data = {
            'plate_number': self.plate_edit.text().strip().upper(),
            'user_id': self.user_combo.currentData(),
            'model_id': self.model_combo.currentData(),
            'year': self.year_spin.value(),
            'color_id': self.color_combo.currentData(),
            'wrap_id': self.wrap_combo.currentData(),
            'repaint_statuses': []  # Больше не нужен repaint_id
        }
        for combo in self.repaint_combos:
            if combo.currentText().strip():
                data['repaint_statuses'].append({
                    'text': combo.currentText().strip(),
                    'id': combo.currentData()
                })
        return data

