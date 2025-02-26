from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                           QLineEdit, QPushButton, QFormLayout, QMessageBox)

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
    def __init__(self, table_name, fields, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Add record to {table_name}")
        self.table_name = table_name
        layout = QVBoxLayout(self)

        # Create form
        form = QFormLayout()
        self.fields = {}

        for field in fields:
            if field.lower() == 'phone':
                line_edit = QLineEdit()
                line_edit.setInputMask('+7999999999999')
                line_edit.setPlaceholderText('+7XXXXXXXXXX')
            else:
                line_edit = QLineEdit()

            form.addRow(f"{field}:", line_edit)
            self.fields[field.lower()] = line_edit

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
        if self.table_name == 'users':
            values = {
                'username': self.fields['username'].text(),
                'phone_number': self.fields['phone'].text()
            }
            print(f"Dialog returning user values: {values}")
            return values
        return {name: widget.text() for name, widget in self.fields.items()}

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
