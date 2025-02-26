import sys
import os
import asyncio
import asyncpg
from dotenv import load_dotenv
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
                           QPushButton, QMessageBox, QDialog, QHeaderView)
from dialogs import AddUserDialog
import threading
from PyQt6.QtCore import QMetaObject, Qt, Q_ARG, QObject, pyqtSlot, pyqtSignal, QTimer

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.pool = None
        
    async def connect(self):
        self.pool = await asyncpg.create_pool(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 5432))
        )
        
    async def close(self):
        if self.pool:
            await self.pool.close()

class TableTab(QWidget):
    # Сигналы для безопасного обновления GUI из другого потока
    show_success_signal = pyqtSignal()
    show_error_signal = pyqtSignal(str)
    refresh_table_signal = pyqtSignal()
    # Добавляем новый сигнал для показа предупреждения
    show_warning_signal = pyqtSignal(str)

    def __init__(self, db, table_name, headers):
        super().__init__()
        self.db = db
        self.table_name = table_name
        self.headers = headers
        
        layout = QVBoxLayout(self)
        
        # Кнопки управления (неактивные)
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.edit_btn = QPushButton("Изменить")
        self.delete_btn = QPushButton("Удалить")
        self.refresh_btn = QPushButton("Обновить")
        
        for btn in [self.add_btn, self.edit_btn, self.delete_btn, self.refresh_btn]:
            btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)
        
        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        # Настраиваем автоматическую подстройку размера колонок под контент
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # Подключаем только обновление данных
        self.refresh_btn.clicked.connect(self.refresh_data)

        # Активируем кнопку добавления
        self.add_btn.clicked.connect(self.add_record)

        # Активируем кнопку изменения
        self.edit_btn.clicked.connect(self.edit_record)

        # Подключаем сигналы к слотам
        self.show_success_signal.connect(self._show_success_dialog)
        self.show_error_signal.connect(self._show_error_dialog)
        self.refresh_table_signal.connect(self.refresh_data)
        self.show_warning_signal.connect(self._show_warning_dialog)

        # Добавляем таймер для автообновления
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(5000)  # Обновление каждые 5 секунд

    def refresh_data(self):
        self.window().loop.create_task(self._refresh_data())

    async def _refresh_data(self):
        try:
            async with self.db.pool.acquire() as conn:
                data = await conn.fetch(f'SELECT * FROM {self.table_name}')
                
                self.table.setRowCount(len(data))
                for row, record in enumerate(data):
                    for col, value in enumerate(record):
                        item = QTableWidgetItem(str(value))
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # Центрируем текст
                        self.table.setItem(row, col, item)
                
                # Устанавливаем высоту строк
                for row in range(self.table.rowCount()):
                    self.table.setRowHeight(row, 25)
                
                # Подгоняем размер колонок под содержимое
                self.table.resizeColumnsToContents()
        except Exception as e:
            print(f"Error refreshing data: {str(e)}")

    def add_record(self):
        if self.table_name == 'users':
            dialog = AddUserDialog(self)
            while dialog.exec() == QDialog.DialogCode.Accepted:
                print("User data accepted, starting database operation...")
                user_data = dialog.get_data()
                print(f"User data to add: {user_data}")
                
                loop = self.window().loop
                if loop and loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        self._add_user(user_data), 
                        loop
                    )
                    try:
                        result = future.result()
                        if result.get('success'):
                            QMessageBox.information(self, "Успех", "Пользователь успешно добавлен")
                            break
                        elif result.get('error') == 'phone_exists':
                            continue  # Продолжаем цикл для повторного ввода
                        else:
                            QMessageBox.critical(self, "Ошибка", 
                                              f"Не удалось добавить пользователя: {result.get('error')}")
                            break
                    except Exception as e:
                        print(f"Error: {str(e)}")
                        QMessageBox.critical(self, "Ошибка", str(e))
                        break

    def edit_record(self):
        if self.table_name == 'users':
            # Получаем выбранные строки
            selected_items = self.table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Предупреждение", "Выберите пользователя для изменения")
                return

            # Получаем данные выбранной строки
            row = selected_items[0].row()
            user_id = int(self.table.item(row, 0).text())

            dialog = AddUserDialog(self)
            # Заполняем поля текущими данными
            dialog.name_edit.setText(self.table.item(row, 1).text())
            dialog.phone_edit.setText(self.table.item(row, 2).text())

            while dialog.exec() == QDialog.DialogCode.Accepted:
                new_data = dialog.get_data()
                print(f"User data to update: {new_data}")

                if not new_data['username'] or not new_data['phone_number']:
                    QMessageBox.warning(self, "Предупреждение", 
                        "Необходимо указать новое имя пользователя и номер телефона.")
                    continue

                loop = self.window().loop
                if loop and loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        self._update_user(
                            user_id,
                            new_data['username'],
                            new_data['phone_number']
                        ),
                        loop
                    )
                    try:
                        result = future.result()
                        if result.get('success'):
                            QMessageBox.information(self, "Успех", 
                                "Данные пользователя успешно обновлены")
                            break
                        else:
                            if result.get('error') == 'phone_exists':
                                continue  # Продолжаем цикл для повторного ввода
                            QMessageBox.warning(self, "Предупреждение", 
                                f"Ошибка при обновлении данных пользователя: {result.get('error')}")
                            break
                    except Exception as e:
                        print(f"Error: {str(e)}")
                        QMessageBox.critical(self, "Ошибка", str(e))
                        break

    def _on_task_complete(self, future):
        try:
            result = future.result()
            if isinstance(result, dict):
                if 'success' in result:
                    self.show_success_signal.emit()
                elif 'error' in result:
                    if result['error'] == 'phone_exists':
                        dialog = self.sender().parent()  # Получаем диалог
                        QMessageBox.warning(dialog, "Ошибка", 
                            "Этот номер телефона уже зарегистрирован. Пожалуйста, введите другой номер.")
                        return  # Не закрываем диалог
                    else:
                        self.show_error_signal.emit(str(result['error']))
        except Exception as e:
            print(f"Error in task completion: {str(e)}")
            self.show_error_signal.emit(str(e))

    @pyqtSlot()
    def _show_success_dialog(self):
        QMessageBox.information(self, "Успех", "Пользователь успешно добавлен")

    @pyqtSlot(str)
    def _show_error_dialog(self, message):
        QMessageBox.critical(self, "Ошибка", f"Не удалось добавить пользователя: {message}")

    @pyqtSlot(str)
    def _show_warning_dialog(self, message):
        QMessageBox.warning(self, "Предупреждение", message)

    async def _add_user(self, user_data):
        try:
            username = user_data['username'].strip()
            phone = user_data['phone_number'].strip()
            
            async with self.db.pool.acquire() as conn:
                # Сначала проверяем существование телефона
                existing_user = await conn.fetchrow(
                    'SELECT * FROM users WHERE phone_number = $1',
                    phone
                )
                
                if (existing_user):
                    # Отправляем сигнал вместо прямого вызова QMessageBox
                    self.show_warning_signal.emit(
                        "Такой номер телефона уже есть в базе данных. Введите другой."
                    )
                    return {'error': 'phone_exists'}

                # Если телефона нет, добавляем пользователя
                await conn.execute('CALL add_user($1, $2)', username, phone)
                user = await conn.fetchrow(
                    'SELECT * FROM users WHERE username = $1 AND phone_number = $2',
                    username, phone
                )
                
                if user:
                    print(f"User successfully added with ID: {user['id']}")
                    await self._refresh_data()
                    return {'success': True}
                else:
                    return {'error': 'not_added'}

        except Exception as e:
            print(f"Error in _add_user: {str(e)}")
            return {'error': str(e)}

    async def _update_user(self, user_id, new_username, new_phone_number):
        try:
            new_username = new_username.strip()
            new_phone_number = new_phone_number.strip()

            async with self.db.pool.acquire() as conn:
                # Проверяем существование пользователя с таким ID
                existing_user = await conn.fetchrow(
                    'SELECT * FROM users WHERE id = $1',
                    user_id
                )

                if not existing_user:
                    self.show_warning_signal.emit(
                        "Пользователь с таким ID не найден."
                    )
                    return {'error': 'user_not_found'}

                # Проверяем, не занят ли новый номер телефона другим пользователем
                phone_in_use = await conn.fetchrow(
                    'SELECT 1 FROM users WHERE phone_number = $1 AND id != $2',
                    new_phone_number, user_id
                )

                if phone_in_use:
                    self.show_warning_signal.emit(
                        "Новый номер телефона уже используется другим пользователем."
                    )
                    return {'error': 'phone_in_use'}

                # Вызываем процедуру для обновления данных пользователя
                await conn.execute('CALL update_user($1, $2, $3)', user_id, new_username, new_phone_number)

                # Проверяем, что данные пользователя обновлены
                updated_user = await conn.fetchrow(
                    'SELECT * FROM users WHERE id = $1',
                    user_id
                )

                if updated_user:
                    print(f"User successfully updated with ID: {updated_user['id']}")
                    await self._refresh_data()
                    return {'success': True}
                else:
                    return {'error': 'not_updated'}

        except Exception as e:
            print(f"Error in _update_user: {str(e)}")
            return {'error': str(e)}

    def closeEvent(self, event):
        self.refresh_timer.stop()  # Останавливаем таймер при закрытии
        super().closeEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseConnection()
        self.setWindowTitle("Детейлинг-студия")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        self.tables = {
            'Work Status': TableTab(self.db, 'work_status', ['ID', 'Status']),
            'Car Brands': TableTab(self.db, 'car_brands', ['ID', 'Brand']),
            'Car Models': TableTab(self.db, 'car_models', ['ID', 'Model', 'Brand ID']),
            'Car Colors': TableTab(self.db, 'car_colors', ['ID', 'Color']),
            'Car Wraps': TableTab(self.db, 'car_wraps', ['ID', 'Status']),
            'Car Repaints': TableTab(self.db, 'car_repaints', ['ID', 'Status']),
            'Service Boxes': TableTab(self.db, 'service_boxes', ['ID', 'Type']),
            'Services': TableTab(self.db, 'services', ['ID', 'Name']),
            'Users': TableTab(self.db, 'users', ['ID', 'Username', 'Phone']),
            'Cars': TableTab(self.db, 'cars', ['Plate', 'User ID', 'Model ID', 'Year', 'Color ID', 'Wrap ID', 'Repaint ID']),
            'Appointments': TableTab(self.db, 'appointments', ['ID', 'Box ID', 'User ID', 'Plate', 'Date', 'Status ID']),
            'Appointment Services': TableTab(self.db, 'appointment_services', ['Appointment ID', 'Service ID'])
        }
        
        for name, widget in self.tables.items():
            tabs.addTab(widget, name)
        
        # Создаем и запускаем event loop
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # Запускаем loop в отдельном потоке
        self._thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()
        
        # Ждем инициализации базы данных
        asyncio.run_coroutine_threadsafe(self.init_db(), self.loop).result()

    def _run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
        
    def closeEvent(self, event):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self._thread.join()
        super().closeEvent(event)
        
    async def init_db(self):
        print("Initializing database...")
        await self.db.connect()
        print("Database connection established")
        
        # Список SQL файлов для выполнения
        sql_files = [
            'database/init.sql',
            'database/procedures.sql',
            'database/triggers.sql',
            'database/views.sql'
        ]
        
        # Последовательно выполняем каждый файл
        async with self.db.pool.acquire() as conn:
            for sql_file in sql_files:
                try:
                    print(f"Executing {sql_file}...")
                    with open(sql_file, 'r', encoding='utf-8') as file:
                        sql = file.read()
                        await conn.execute(sql)
                    print(f"Successfully executed {sql_file}")
                except Exception as e:
                    print(f"Error executing {sql_file}: {str(e)}")
                    raise
        
        print("Database initialization completed")
        await self.refresh_all_tables()
        print("All tables refreshed")
        
    async def refresh_all_tables(self):
        for widget in self.tables.values():
            await widget._refresh_data()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
