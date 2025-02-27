from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                           QLineEdit, QPushButton, QFormLayout, QMessageBox,
                           QSpinBox, QComboBox, QInputDialog)
import asyncio

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
    def __init__(self, pool, parent=None):
        super().__init__(parent)
        self.pool = pool
        self.setWindowTitle("Добавление услуги")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        # Поля ввода
        self.name_edit = QLineEdit()
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(15, 480)  # 15 минут - 8 часов
        self.duration_spin.setSingleStep(15)  # шаг 15 минут
        self.box_combo = QComboBox()
        self.box_combo.setEditable(True)
        self.box_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        
        layout.addWidget(QLabel("Название:"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("Длительность (минут):"))
        layout.addWidget(self.duration_spin)
        layout.addWidget(QLabel("Тип бокса:"))
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
        
        # Загружаем существующие боксы
        loop = parent.window().loop
        if loop and loop.is_running():
            future = asyncio.run_coroutine_threadsafe(self.load_boxes(), loop)
            try:
                future.result()
            except Exception as e:
                print(f"Error loading boxes: {str(e)}")

    async def load_boxes(self):
        async with self.pool.acquire() as conn:
            boxes = await conn.fetch('SELECT * FROM get_box_types()')
            self.box_combo.clear()
            for box in boxes:
                self.box_combo.addItem(f"{box['type']} ({box['capacity']} мест)", 
                                     {'id': box['id'], 'type': box['type']})

    def accept(self):
        data = self.get_data()
        if data['is_new_box']:
            # Показываем диалог вместимости
            capacity, ok = QInputDialog.getInt(
                self,
                "Новый бокс",
                f"Укажите вместимость для нового типа бокса '{data['box_type']}':",
                1, 1, 10
            )
            if ok:
                # Сохраняем вместимость в data и закрываем диалог
                data['box_capacity'] = capacity
                self._data = data
                super().accept()
            else:
                # Пользователь отменил ввод вместимости - не закрываем основной диалог
                return
        else:
            # Обычное сохранение для существующего бокса
            self._data = data
            super().accept()

    def get_data(self):
        if hasattr(self, '_data'):
            return self._data
            
        box_data = self.box_combo.currentData()
        box_type = self.box_combo.currentText().split(' (')[0] if box_data else self.box_combo.currentText()
        
        is_new_box = not bool(box_data) or self.box_combo.currentText() != self.box_combo.itemText(self.box_combo.currentIndex())
        
        return {
            'name': self.name_edit.text().strip(),
            'duration': self.duration_spin.value(),
            'box_type': box_type,
            'is_new_box': is_new_box,
            'box_capacity': None  # Будет заполнено позже для нового бокса
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
