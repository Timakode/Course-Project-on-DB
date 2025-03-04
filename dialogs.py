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

class CarInputDialog(QDialog):
    def __init__(self, pool, parent=None):
        super().__init__(parent)
        self.pool = pool
        self.parent = parent  # Сохраняем ссылку на родителя
        self.setWindowTitle("Добавление автомобиля")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Основные поля
        form = QFormLayout()
        self.plate_edit = QLineEdit()
        self.user_combo = QComboBox()
        self.model_combo = QComboBox()
        self.year_spin = QSpinBox()
        self.color_combo = QComboBox()
        self.wrap_combo = QComboBox()
        
        form.addRow("Номер авто:", self.plate_edit)
        form.addRow("Владелец:", self.user_combo)
        form.addRow("Модель:", self.model_combo)
        form.addRow("Год выпуска:", self.year_spin)
        form.addRow("Цвет:", self.color_combo)
        form.addRow("Оклейка:", self.wrap_combo)
        
        # Секция перекраса
        repaint_group = QGroupBox("Перекрас")
        repaint_layout = QVBoxLayout()
        self.repaint_combo = QComboBox()
        self.additional_repaint_combo = QComboBox()
        self.additional_repaint_check = QCheckBox("Добавить дополнительный элемент")
        repaint_layout.addWidget(self.repaint_combo)
        repaint_layout.addWidget(self.additional_repaint_check)
        repaint_layout.addWidget(self.additional_repaint_combo)
        self.additional_repaint_combo.setEnabled(False)
        repaint_group.setLayout(repaint_layout)
        
        layout.addLayout(form)
        layout.addWidget(repaint_group)
        
        # Кнопки
        self.setup_buttons(layout)
        
        # Настройка полей и загрузка данных
        self.setup_fields()
        
        # Сигналы
        self.additional_repaint_check.stateChanged.connect(
            lambda state: self.additional_repaint_combo.setEnabled(state == Qt.CheckState.Checked)
        )
        
        # Загружаем данные асинхронно через event loop
        loop = parent.window().loop
        if loop and loop.is_running():
            future = asyncio.run_coroutine_threadsafe(
                self.load_initial_data(),
                loop
            )
            try:
                future.result()
            except Exception as e:
                print(f"Error loading initial data: {str(e)}")
                QMessageBox.critical(self, "Ошибка", 
                    "Не удалось загрузить начальные данные")

    async def load_initial_data(self):
        try:
            async with self.pool.acquire() as conn:
                # Загружаем пользователей
                users = await conn.fetch('SELECT * FROM get_all_users()')
                self.user_combo.clear()
                for user in users:
                    self.user_combo.addItem(
                        f"{user['username']} ({user['phone_number']})", 
                        user['id']
                    )
                
                # Загружаем модели
                models = await conn.fetch('SELECT * FROM get_models_with_brands()')
                self.model_combo.clear()
                for model in models:
                    self.model_combo.addItem(
                        f"{model['brand_name']} {model['model_name']}", 
                        model['model_id']
                    )
                
                # Загружаем цвета
                colors = await conn.fetch('SELECT * FROM car_colors ORDER BY color')
                self.color_combo.clear()
                for color in colors:
                    self.color_combo.addItem(color['color'])
                
                # Загружаем элементы оклейки
                wraps = await conn.fetch('SELECT * FROM get_all_wraps()')
                self.wrap_combo.clear()
                for wrap in wraps:
                    self.wrap_combo.addItem(wrap['status'], wrap['id'])
                
                # Загружаем элементы перекраса
                repaints = await conn.fetch('SELECT * FROM get_all_repaints()')
                for combo in [self.repaint_combo, self.additional_repaint_combo]:
                    combo.clear()
                    for repaint in repaints:
                        combo.addItem(repaint['status'], repaint['id'])
        
        except Exception as e:
            print(f"Error loading initial data: {str(e)}")
            QMessageBox.critical(self, "Ошибка", 
                "Не удалось загрузить начальные данные")

    def get_data(self):
        # Собираем ID элементов перекраса
        repaint_ids = [self.repaint_combo.currentData()]
        if self.additional_repaint_check.isChecked():
            repaint_ids.append(self.additional_repaint_combo.currentData())
        
        return {
            'plate_number': self.plate_edit.text().strip(),
            'user_id': self.user_combo.currentData(),
            'model_id': self.model_combo.currentData(),
            'year': self.year_spin.value(),
            'color': self.color_combo.currentText().strip(),
            'wrap_id': self.wrap_combo.currentData(),
            'repaint_ids': repaint_ids
        }

    def setup_fields(self):
        current_year = QDate.currentDate().year()
        self.year_spin.setRange(1900, current_year)
        self.year_spin.setValue(current_year)
        
        self.user_combo.setEditable(True)
        self.color_combo.setEditable(True)
        
        self.user_combo.addItem("Новый пользователь", -1)
        self.model_combo.addItem("Новая модель", -1)

    def setup_buttons(self, layout):
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        save_btn.clicked.connect(self.validate_and_save)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def connect_signals(self):
        self.phone_search.textChanged.connect(self.search_users)
        self.user_combo.currentIndexChanged.connect(self.on_user_selected)

    async def search_users(self, phone):
        if not phone:
            return
        
        async with self.pool.acquire() as conn:
            users = await conn.fetch('SELECT * FROM get_users_by_phone($1)', phone)
            self.user_combo.clear()
            self.user_combo.addItem("Новый пользователь", -1)
            for user in users:
                self.user_combo.addItem(
                    f"{user['username']} ({user['phone_number']})", 
                    user['id']
                )

    def on_user_selected(self, index):
        if self.user_combo.currentData() == -1:
            dialog = AddUserDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                user_data = dialog.get_data()
                # Добавляем нового пользователя
                loop = self.parent.window().loop
                if loop and loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        self._add_new_user(user_data),
                        loop
                    )
                    try:
                        result = future.result()
                        if result.get('success'):
                            QMessageBox.information(self, "Успех", 
                                "Пользователь успешно добавлен")
                            # Обновляем список пользователей
                            self.search_users(user_data['phone_number'])
                        else:
                            QMessageBox.warning(self, "Ошибка", 
                                result.get('error'))
                    except Exception as e:
                        QMessageBox.critical(self, "Ошибка", str(e))

    async def _add_new_user(self, user_data):
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow(
                    'SELECT * FROM add_user($1, $2)',
                    user_data['username'],
                    user_data['phone_number']
                )
                return {'success': True, 'id': result['id']}
        except Exception as e:
            return {'error': str(e)}

    def validate_and_save(self):
        # Проверяем обязательные поля
        if not self.plate_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите номер автомобиля")
            return
        
        if self.user_combo.currentData() == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя")
            return
        
        if self.model_combo.currentData() == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите модель")
            return
        
        # Если все проверки пройдены, сохраняем данные
        loop = self.parent.window().loop
        if loop and loop.is_running():
            future = asyncio.run_coroutine_threadsafe(
                self._save_car(),
                loop
            )
            try:
                result = future.result()
                if result.get('success'):
                    self.accept()
                else:
                    QMessageBox.warning(self, "Ошибка", 
                        result.get('error', 'Неизвестная ошибка'))
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def get_data(self):
        return {
            'plate_number': self.plate_edit.text().strip(),
            'user_id': self.user_combo.currentData(),
            'model_id': self.model_combo.currentData(),
            'year': self.year_spin.value(),
            'color': self.color_combo.currentText().strip(),  # Передаем строку с цветом
            'wrap_id': self.wrap_combo.currentData(),
            'repaint_ids': [self.repaint_combo.currentData()]
            if not self.additional_repaint_check.isChecked()
            else [self.repaint_combo.currentData(), self.additional_repaint_combo.currentData()]
        }

    async def _get_color_id(self, color_name):  # Add color_name parameter
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                'SELECT get_or_create_color($1)',
                color_name
            )

    def on_color_changed(self, text):
        # Этот метод можно использовать для валидации или 
        # автоматического создания нового цвета
        pass
