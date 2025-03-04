import sys
import os
import asyncio
import asyncpg
from dotenv import load_dotenv
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
                           QPushButton, QMessageBox, QDialog, QHeaderView,
                           QInputDialog)
from PyQt6.QtCore import (QMetaObject, Qt, Q_ARG, QObject, pyqtSlot, 
                         pyqtSignal, QTimer, QDate)  # Добавляем QDate
from dialogs import (AddUserDialog, SimpleInputDialog, BoxInputDialog, 
                     ServiceInputDialog, CarModelDialog, BoxDialog)
import threading

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
    # Добавляем новый сигнал для создания диалога
    get_box_capacity_signal = pyqtSignal(str, name='getBoxCapacity')

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
        # Подключаем новый сигнал
        self.get_box_capacity_signal.connect(self._get_box_capacity)

        # Добавляем таймер для автообновления
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(5000)  # Обновление каждые 5 секунд

    def refresh_data(self):
        self.window().loop.create_task(self._refresh_data())

    async def _refresh_data(self):
        try:
            async with self.db.pool.acquire() as conn:
                # Специальная обработка для таблицы services
                if self.table_name == 'services':
                    data = await conn.fetch('SELECT * FROM get_services_list()')
                    
                    self.table.setRowCount(len(data))
                    for row, record in enumerate(data):
                        # ID и Name отображаем как обычно
                        self.table.setItem(row, 0, QTableWidgetItem(str(record['id'])))
                        self.table.setItem(row, 1, QTableWidgetItem(record['name']))
                        
                        # Форматируем duration в зависимости от unit
                        duration_text = (
                            f"{record['duration_value']} дней" 
                            if record['duration_unit'] == 'days'
                            else f"{record['duration_value']} минут"
                        )
                        self.table.setItem(row, 2, QTableWidgetItem(duration_text))
                else:
                    # Стандартная обработка для других таблиц
                    data = await conn.fetch(f'SELECT * FROM {self.table_name}')
                    self.table.setRowCount(len(data))
                    for row, record in enumerate(data):
                        for col, value in enumerate(record):
                            item = QTableWidgetItem(str(value))
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            self.table.setItem(row, col, item)

            # Устанавливаем высоту строк и подгоняем размер колонок
            for row in range(self.table.rowCount()):
                self.table.setRowHeight(row, 25)
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
        elif self.table_name in ['work_status', 'car_brands', 'car_colors', 'car_wraps', 'car_repaints']:
            dialog = SimpleInputDialog(f"Добавление записи", "Название")
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                loop = self.window().loop
                if loop and loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        self._add_simple_record(data['name']), 
                        loop
                    )
                    try:
                        result = future.result()
                        if result.get('success'):
                            QMessageBox.information(self, "Успех", "Запись успешно добавлена")
                        else:
                            QMessageBox.warning(self, "Ошибка", result.get('error'))
                    except Exception as e:
                        QMessageBox.critical(self, "Ошибка", str(e))

        elif self.table_name == 'boxes':
            dialog = BoxDialog(parent=self)
            while dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                if not data['type']:
                    QMessageBox.warning(self, "Предупреждение", 
                        "Необходимо указать тип бокса.")
                    continue

                loop = self.window().loop
                if loop and loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        self._add_box(data),
                        loop
                    )
                    try:
                        result = future.result()
                        if result.get('success'):
                            QMessageBox.information(self, "Успех", 
                                "Бокс успешно добавлен")
                            break
                        else:
                            if result.get('error') == 'type_exists':
                                continue  # Продолжаем цикл для повторного ввода
                            QMessageBox.warning(self, "Ошибка", 
                                result.get('error'))
                            break
                    except Exception as e:
                        print(f"Error: {str(e)}")
                        QMessageBox.critical(self, "Ошибка", str(e))
                        break

        elif self.table_name == 'services':
            dialog = ServiceInputDialog(self.db.pool, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                # Изменяем проверку на новые поля
                if not data['name'] or (
                    (data['duration_unit'] == 'minutes' and data['duration_value'] < 15) or
                    (data['duration_unit'] == 'days' and data['duration_value'] < 1)
                ):
                    QMessageBox.warning(self, "Предупреждение", 
                        "Необходимо указать название услуги и корректную длительность"
                    )
                    return

                loop = self.window().loop
                if loop and loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        self._add_service(data), 
                        loop
                    )
                    try:
                        result = future.result()
                        if result and result.get('success'):
                            # Создаем новую задачу для обновления данных
                            refresh_future = asyncio.run_coroutine_threadsafe(
                                self._refresh_data(),
                                loop
                            )
                            refresh_future.result()  # Ждем завершения обновления
                            QMessageBox.information(self, "Успех", 
                                "Услуга успешно добавлена")
                        else:
                            QMessageBox.warning(self, "Ошибка", 
                                result.get('error', 'Неизвестная ошибка'))
                    except Exception as e:
                        print(f"Error in service addition: {str(e)}")
                        QMessageBox.critical(self, "Ошибка", str(e))

        elif self.table_name == 'car_models':
            dialog = CarModelDialog(self.db.pool, parent=self)
            
            # Загружаем бренды перед показом диалога
            loop = self.window().loop
            if loop and loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    self._load_brands_for_dialog(dialog.brand_combo),
                    loop
                )
                try:
                    future.result()
                except Exception as e:
                    print(f"Error loading brands: {str(e)}")
                    QMessageBox.critical(self, "Ошибка", 
                        "Не удалось загрузить список брендов")
                    return
            
            while dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                if not data['model'] or not data['brand']:
                    QMessageBox.warning(self, "Предупреждение",
                        "Необходимо указать модель и бренд автомобиля.")
                    continue

                loop = self.window().loop
                if loop and loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        self._add_car_model(data),
                        loop
                    )
                    try:
                        result = future.result()
                        if result.get('success'):
                            QMessageBox.information(self, "Успех", 
                                "Модель успешно добавлена")
                            break
                        else:
                            QMessageBox.warning(self, "Ошибка", 
                                result.get('error'))
                            continue
                    except Exception as e:
                        print(f"Error: {str(e)}")
                        QMessageBox.critical(self, "Ошибка", str(e))
                        break

        elif self.table_name == 'cars':
            from dialogs import CarInputDialog
            dialog = CarInputDialog(self.db.pool, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                
                loop = self.window().loop
                if loop and loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        self._add_car(data),
                        loop
                    )
                    try:
                        result = future.result()
                        if result.get('success'):
                            # Обновляем таблицу сразу после успешного добавления
                            refresh_future = asyncio.run_coroutine_threadsafe(
                                self._refresh_data(),
                                loop
                            )
                            # Ждем завершения обновления
                            refresh_future.result()
                            
                            QMessageBox.information(self, "Успех", 
                                "Автомобиль успешно добавлен")
                        else:
                            QMessageBox.warning(self, "Ошибка", 
                                result.get('error', 'Неизвестная ошибка'))
                    except Exception as e:
                        print(f"Error in car addition: {str(e)}")
                        QMessageBox.critical(self, "Ошибка", str(e))

    async def _load_brands_for_dialog(self, combo_box):
        async with self.db.pool.acquire() as conn:
            brands = await conn.fetch('SELECT * FROM get_car_brands()')
            combo_box.clear()
            for brand in brands:
                combo_box.addItem(brand['brand'])

    def edit_record(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись для изменения")
            return

        row = selected_items[0].row()
        record_id = int(self.table.item(row, 0).text())

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
        
        elif self.table_name == 'work_status':
            dialog = SimpleInputDialog(
                "Изменение статуса", 
                "Статус",
                self.table.item(row, 1).text()
            )
            
            while dialog.exec() == QDialog.DialogCode.Accepted:
                new_data = dialog.get_data()
                if not new_data['name']:
                    QMessageBox.warning(self, "Предупреждение", 
                        "Необходимо указать статус.")
                    continue

                loop = self.window().loop
                if loop and loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        self._update_work_status(record_id, new_data['name']),
                        loop
                    )
                    try:
                        result = future.result()
                        if result.get('success'):
                            QMessageBox.information(self, "Успех", 
                                "Статус успешно обновлен")
                            break
                        else:
                            QMessageBox.warning(self, "Предупреждение", 
                                f"Ошибка при обновлении статуса: {result.get('error')}")
                            break
                    except Exception as e:
                        print(f"Error: {str(e)}")
                        QMessageBox.critical(self, "Ошибка", str(e))
                        break

        elif self.table_name == 'car_brands':
            dialog = SimpleInputDialog(
                "Изменение бренда", 
                "Название бренда",
                self.table.item(row, 1).text()
            )
            
            while dialog.exec() == QDialog.DialogCode.Accepted:
                new_data = dialog.get_data()
                if not new_data['name']:
                    QMessageBox.warning(self, "Предупреждение", 
                        "Необходимо указать название бренда.")
                    continue

                loop = self.window().loop
                if loop and loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        self._update_car_brand(record_id, new_data['name']),
                        loop
                    )
                    try:
                        result = future.result()
                        if result.get('success'):
                            QMessageBox.information(self, "Успех", 
                                "Бренд успешно обновлен")
                            break
                        else:
                            QMessageBox.warning(self, "Предупреждение", 
                                f"Ошибка при обновлении бренда: {result.get('error')}")
                            break
                    except Exception as e:
                        print(f"Error: {str(e)}")
                        QMessageBox.critical(self, "Ошибка", str(e))
                        break

        elif self.table_name == 'car_models':
            # Загружаем данные модели
            loop = self.window().loop
            if loop and loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    self._get_model_details(record_id),
                    loop
                )
                try:
                    model_data = future.result()
                    if not model_data:
                        QMessageBox.warning(self, "Ошибка", 
                            "Не удалось загрузить данные модели")
                        return
                except Exception as e:
                    print(f"Error loading model details: {str(e)}")
                    QMessageBox.critical(self, "Ошибка", 
                        "Не удалось загрузить данные модели")
                    return

            dialog = CarModelDialog(self.db.pool, model_data, self)
            
            # Загружаем бренды перед показом диалога
            future = asyncio.run_coroutine_threadsafe(
                self._load_brands_for_dialog(dialog.brand_combo),
                loop
            )
            try:
                future.result()
            except Exception as e:
                print(f"Error loading brands: {str(e)}")
                QMessageBox.critical(self, "Ошибка", 
                    "Не удалось загрузить список брендов")
                return
            
            while dialog.exec() == QDialog.DialogCode.Accepted:
                new_data = dialog.get_data()
                if not new_data['model'] or not new_data['brand']:
                    QMessageBox.warning(self, "Предупреждение", 
                        "Необходимо указать модель и бренд автомобиля.")
                    continue

                future = asyncio.run_coroutine_threadsafe(
                    self._update_car_model(record_id, new_data),
                    loop
                )
                try:
                    result = future.result()
                    if result.get('success'):
                        QMessageBox.information(self, "Успех", 
                            "Модель успешно обновлена")
                        break
                    else:
                        QMessageBox.warning(self, "Ошибка", 
                            result.get('error'))
                        continue
                except Exception as e:
                    print(f"Error: {str(e)}")
                    QMessageBox.critical(self, "Ошибка", str(e))
                    break

        elif self.table_name == 'car_colors':
            dialog = SimpleInputDialog(
                "Изменение цвета", 
                "Название цвета",
                self.table.item(row, 1).text()
            )
            
            while dialog.exec() == QDialog.DialogCode.Accepted:
                new_data = dialog.get_data()
                if not new_data['name']:
                    QMessageBox.warning(self, "Предупреждение", 
                        "Необходимо указать название цвета.")
                    continue

                loop = self.window().loop
                if loop and loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        self._update_car_color(record_id, new_data['name']),
                        loop
                    )
                    try:
                        result = future.result()
                        if result.get('success'):
                            QMessageBox.information(self, "Успех", 
                                "Цвет успешно обновлен")
                            break
                        else:
                            QMessageBox.warning(self, "Предупреждение", 
                                f"Ошибка при обновлении цвета: {result.get('error')}")
                            continue
                    except Exception as e:
                        print(f"Error: {str(e)}")
                        QMessageBox.critical(self, "Ошибка", str(e))
                        break

        elif self.table_name in ['car_wraps', 'car_repaints']:
            dialog = SimpleInputDialog(
                f"Изменение статуса", 
                "Статус",
                self.table.item(row, 1).text()
            )
            
            while dialog.exec() == QDialog.DialogCode.Accepted:
                new_data = dialog.get_data()
                if not new_data['name']:
                    QMessageBox.warning(self, "Предупреждение", 
                        "Необходимо указать статус.")
                    continue

                loop = self.window().loop
                if loop and loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        self._update_status(self.table_name, record_id, new_data['name']),
                        loop
                    )
                    try:
                        result = future.result()
                        if result.get('success'):
                            QMessageBox.information(self, "Успех", 
                                "Статус успешно обновлен")
                            break
                        else:
                            if result.get('error') == 'status_exists':
                                continue # Продолжаем цикл для повторного ввода
                            QMessageBox.warning(self, "Предупреждение", 
                                f"Ошибка при обновлении статуса: {result.get('error')}")
                            break
                    except Exception as e:
                        print(f"Error: {str(e)}")
                        QMessageBox.critical(self, "Ошибка", str(e))
                        break

        elif self.table_name == 'boxes':
            dialog = BoxDialog(
                {
                    'type': self.table.item(row, 1).text(),
                    'capacity': int(self.table.item(row, 2).text())
                }, 
                self
            )
            
            while dialog.exec() == QDialog.DialogCode.Accepted:
                new_data = dialog.get_data()
                if not new_data['type']:
                    QMessageBox.warning(self, "Предупреждение", 
                        "Необходимо указать тип бокса.")
                    continue

                loop = self.window().loop
                if loop and loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        self._update_box(record_id, new_data),
                        loop
                    )
                    try:
                        result = future.result()
                        if result.get('success'):
                            QMessageBox.information(self, "Успех", 
                                "Бокс успешно обновлен")
                            break
                        else:
                            if result.get('error') == 'type_exists':
                                continue  # Продолжаем цикл для повторного ввода
                            QMessageBox.warning(self, "Ошибка", 
                                result.get('error'))
                            break
                    except Exception as e:
                        print(f"Error: {str(e)}")
                        QMessageBox.critical(self, "Ошибка", str(e))
                        break

        elif self.table_name == 'services':
            # Загружаем данные сервиса
            loop = self.window().loop
            if loop and loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    self._get_service_details(record_id),
                    loop
                )
                try:
                    service_data = future.result()
                    if not service_data:
                        QMessageBox.warning(self, "Ошибка", 
                            "Не удалось загрузить данные услуги")
                        return
                except Exception as e:
                    print(f"Error loading service details: {str(e)}")
                    QMessageBox.critical(self, "Ошибка", 
                        "Не удалось загрузить данные услуги")
                    return

            dialog = ServiceInputDialog(self.db.pool, service_data, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                # Изменяем проверку на новые поля
                if not data['name'] or (
                    (data['duration_unit'] == 'minutes' and data['duration_value'] < 15) or
                    (data['duration_unit'] == 'days' and data['duration_value'] < 1)
                ):
                    QMessageBox.warning(self, "Предупреждение", 
                        "Необходимо указать название услуги и корректную длительность")
                    return

                future = asyncio.run_coroutine_threadsafe(
                    self._update_service(record_id, data),
                    loop
                )
                try:
                    result = future.result()
                    if result.get('success'):
                        QMessageBox.information(self, "Успех", 
                            "Услуга успешно обновлена")
                    else:
                        QMessageBox.warning(self, "Ошибка", 
                            result.get('error', 'Неизвестная ошибка'))
                except Exception as e:
                    print(f"Error: {str(e)}")
                    QMessageBox.critical(self, "Ошибка", str(e))

    async def _get_model_details(self, model_id):
        async with self.db.pool.acquire() as conn:
            return await conn.fetchrow(
                'SELECT * FROM get_car_model_details($1)',
                model_id
            )

    async def _update_car_model(self, model_id, new_data):
        try:
            async with self.db.pool.acquire() as conn:
                await conn.execute(
                    'CALL update_car_model($1, $2, $3)',
                    model_id, new_data['model'], new_data['brand']
                )
                
                # Обновляем данные во всех связанных таблицах
                for tab_name, tab_widget in self.window().tables.items():
                    if tab_name in ['Car Models', 'Car Brands']:
                        await tab_widget._refresh_data()
                
                return {'success': True}
        except Exception as e:
            return {'error': str(e)}

    async def _update_car_color(self, color_id, new_color):
        try:
            async with self.db.pool.acquire() as conn:
                # Проверяем существование с учетом регистра
                existing_color = await conn.fetchrow(
                    'SELECT * FROM check_car_color_exists_except($1, $2)',
                    new_color, color_id
                )

                if existing_color:
                    self.show_warning_signal.emit(
                        "Такой цвет уже существует (без учета регистра)."
                    )
                    return {'error': 'color_exists'}

                # Вызываем процедуру обновления
                await conn.execute(
                    'CALL update_car_color($1, $2)', 
                    color_id, new_color
                )

                await self._refresh_data()
                return {'success': True}

        except Exception as e:
            print(f"Error in _update_car_color: {str(e)}")
            return {'error': str(e)}

    async def _update_status(self, table_name, record_id, new_status):
        try:
            async with self.db.pool.acquire() as conn:
                if table_name == 'car_wraps':
                    # Проверяем существование с учетом регистра
                    existing = await conn.fetchrow(
                        'SELECT * FROM check_car_wrap_exists_except($1, $2)',
                        new_status, record_id
                    )
                    if existing:
                        self.show_warning_signal.emit(
                            "Такой статус оклейки уже существует (без учета регистра)."
                        )
                        return {'error': 'status_exists'}
                    await conn.execute('CALL update_car_wrap($1, $2)', record_id, new_status)

                elif table_name == 'car_repaints':
                    existing = await conn.fetchrow(
                        'SELECT * FROM check_car_repaint_exists_except($1, $2)',
                        new_status, record_id
                    )
                    if existing:
                        self.show_warning_signal.emit(
                            "Такой статус перекраса уже существует (без учета регистра)."
                        )
                        return {'error': 'status_exists'}
                    await conn.execute('CALL update_car_repaint($1, $2)', record_id, new_status)

                await self._refresh_data()
                return {'success': True}
        except Exception as e:
            print(f"Error in _update_status: {str(e)}")
            return {'error': str(e)}

    async def _update_box(self, box_id, new_data):
        try:
            async with self.db.pool.acquire() as conn:
                # Проверяем существование с учетом регистра
                existing = await conn.fetchrow(
                    'SELECT * FROM check_box_exists_except($1, $2)',
                    new_data['type'],
                    box_id
                )
                if existing:
                    self.show_warning_signal.emit(
                        "Такой тип бокса уже существует (без учета регистра)."
                    )
                    return {'error': 'type_exists'}

                # Обновляем бокс
                await conn.execute(
                    'CALL update_box($1, $2, $3)',
                    box_id,
                    new_data['type'],
                    new_data['capacity']
                )
                
                await self._refresh_data()
                return {'success': True}
        except Exception as e:
            print(f"Error in _update_box: {str(e)}")
            return {'error': str(e)}

    async def _get_service_details(self, service_id):
        async with self.db.pool.acquire() as conn:
            return await conn.fetchrow(
                'SELECT * FROM get_service_details($1)',
                service_id
            )

    async def _update_service(self, service_id, data):
        try:
            async with self.db.pool.acquire() as conn:
                await conn.execute(
                    'CALL update_service($1, $2, $3, $4)',
                    service_id,
                    data['name'],
                    data['duration_value'],
                    data['duration_unit']
                )
                await self._refresh_data()
                return {'success': True}
        except Exception as e:
            print(f"Error in _update_service: {str(e)}")
            return {'error': str(e)}

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

    @pyqtSlot(str)
    def _get_box_capacity(self, box_type):
        """Показывает диалог для ввода вместимости бокса в главном потоке"""
        capacity, ok = QInputDialog.getInt(
            self,
            "Новый бокс",
            f"Укажите вместимость для нового типа бокса '{box_type}':",
            1, 1, 10
        )
        # Сохраняем результат для использования в асинхронном методе
        self.dialog_result = (capacity, ok) if ok else None

    async def _add_user(self, user_data):
        try:
            username = user_data['username'].strip()
            phone = user_data['phone_number'].strip()
            
            async with self.db.pool.acquire() as conn:
                # Используем функцию из queries.sql для проверки
                existing_user = await conn.fetchrow(
                    'SELECT * FROM check_phone_exists($1)',
                    phone
                )
                
                if existing_user:
                    self.show_warning_signal.emit(
                        "Такой номер телефона уже есть в базе данных. Введите другой."
                    )
                    return {'error': 'phone_exists'}

                # Если телефона нет, добавляем пользователя
                await conn.execute('CALL add_user($1, $2)', username, phone)
                user = await conn.fetchrow(
                    'SELECT * FROM find_user_by_credentials($1, $2)',
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
                    'SELECT * FROM check_user_exists($1)',
                    user_id
                )

                if not existing_user:
                    self.show_warning_signal.emit(
                        "Пользователь с таким ID не найден."
                    )
                    return {'error': 'user_not_found'}

                # Проверяем, не занят ли новый номер телефона другим пользователем
                phone_in_use = await conn.fetchrow(
                    'SELECT * FROM check_phone_used_by_other($1, $2)',
                    new_phone_number, user_id
                )

                if phone_in_use:
                    self.show_warning_signal.emit(
                        "Новый номер телефона уже используется другим пользователем."
                    )
                    return {'error': 'phone_in_use'}

                # Вызываем процедуру обновления
                await conn.execute(
                    'CALL update_user($1, $2, $3)', 
                    user_id, new_username, new_phone_number
                )

                # Проверяем обновление
                updated_user = await conn.fetchrow(
                    'SELECT * FROM check_user_exists($1)',
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

    async def _update_work_status(self, status_id, new_status):
        try:
            async with self.db.pool.acquire() as conn:
                # Проверяем существование с учетом регистра
                existing_status = await conn.fetchrow(
                    'SELECT * FROM check_status_exists_except($1, $2)',
                    new_status, status_id
                )

                if existing_status:
                    self.show_warning_signal.emit(
                        "Такой статус уже существует (без учета регистра)."
                    )
                    return {'error': 'status_exists'}

                # Вызываем процедуру обновления
                await conn.execute(
                    'CALL update_work_status($1, $2)', 
                    status_id, new_status
                )

                await self._refresh_data()
                return {'success': True}

        except Exception as e:
            return {'error': str(e)}

    async def _update_car_brand(self, brand_id, new_brand):
        try:
            async with self.db.pool.acquire() as conn:
                # Проверяем существование с учетом регистра
                existing_brand = await conn.fetchrow(
                    'SELECT * FROM check_car_brand_exists_except($1, $2)',
                    new_brand, brand_id
                )

                if existing_brand:
                    self.show_warning_signal.emit(
                        "Такой бренд уже существует."
                    )
                    return {'error': 'brand_exists'}

                # Вызываем процедуру обновления
                await conn.execute(
                    'CALL update_car_brand($1, $2)', 
                    brand_id, new_brand
                )

                await self._refresh_data()
                return {'success': True}

        except Exception as e:
            return {'error': str(e)}

    async def _add_simple_record(self, name):
        try:
            async with self.db.pool.acquire() as conn:
                # Определяем процедуру и параметр в зависимости от таблицы
                if self.table_name == 'work_status':
                    await conn.execute('CALL add_work_status($1)', name)
                elif self.table_name == 'car_brands':
                    await conn.execute('CALL add_car_brand($1)', name)
                elif self.table_name == 'car_colors':
                    await conn.execute('CALL add_car_color($1)', name)
                elif self.table_name == 'car_wraps':
                    await conn.execute('CALL add_car_wrap($1)', name)
                elif self.table_name == 'car_repaints':
                    await conn.execute('CALL add_car_repaint($1)', name)
                
                await self._refresh_data()
                return {'success': True}
        except Exception as e:
            return {'error': str(e)}

    async def _add_car_model(self, data):
        try:
            async with self.db.pool.acquire() as conn:
                await conn.execute(
                    'CALL add_car_model($1, $2)',
                    data['model'], data['brand']
                )
                
                # Обновляем данные во всех связанных таблицах
                for tab_name, tab_widget in self.window().tables.items():
                    if tab_name in ['Car Models', 'Car Brands']:
                        await tab_widget._refresh_data()
                        
                return {'success': True}
        except Exception as e:
            return {'error': str(e)}

    async def _add_box(self, data):
        try:
            async with self.db.pool.acquire() as conn:
                # Проверяем существование с учетом регистра
                existing = await conn.fetchrow(
                    'SELECT * FROM check_box_exists_except($1, -1)',
                    data['type']
                )
                if existing:
                    self.show_warning_signal.emit(
                        "Такой тип бокса уже существует (без учета регистра)."
                    )
                    return {'error': 'type_exists'}

                # Добавляем бокс
                await conn.execute(
                    'CALL add_box($1, $2)',
                    data['type'],
                    data['capacity']
                )
                
                await self._refresh_data()
                return {'success': True}
        except Exception as e:
            print(f"Error in _add_box: {str(e)}")
            return {'error': str(e)}

    async def _add_service(self, data):
        try:
            async with self.db.pool.acquire() as conn:
                await conn.execute(
                    'CALL add_service($1, $2, $3)',
                    data['name'],
                    data['duration_value'],
                    data['duration_unit']
                )
                await self._refresh_data()
                return {'success': True}
        except Exception as e:
            return {'error': str(e)}
            

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Детейлинг-студия")
        self.setGeometry(100, 100, 1200, 800)
        
        # База данных
        self.db = DatabaseConnection()
        
        # Создаем центральный виджет и его layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Создаем TabWidget для вкладок
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Инициализируем все таблицы
        self.tables = {
            'Work Status': TableTab(self.db, 'work_status', ['ID', 'Status']),
            'Car Brands': TableTab(self.db, 'car_brands', ['ID', 'Brand']),
            'Car Models': TableTab(self.db, 'car_models', ['ID', 'Model', 'Brand ID']),
            'Car Colors': TableTab(self.db, 'car_colors', ['ID', 'Color']),
            'Car Wraps': TableTab(self.db, 'car_wraps', ['ID', 'Status']),
            'Car Repaints': TableTab(self.db, 'car_repaints', ['ID', 'Status']),
            'Car Repaint Links': TableTab(self.db, 'car_repaint_links', ['Car ID', 'Repaint ID']),
            'Boxes': TableTab(self.db, 'boxes', ['ID', 'Type', 'Capacity']),
            'Services': TableTab(self.db, 'services', ['ID', 'Name', 'Duration']),
            'Users': TableTab(self.db, 'users', ['ID', 'Username', 'Phone']),
            'Cars': TableTab(self.db, 'cars', ['Plate', 'User ID', 'Model ID', 'Year', 'Color ID', 'Wrap ID', 'Repaint ID']),
            'Bookings': TableTab(self.db, 'bookings', ['ID', 'Box ID', 'User ID', 'Plate', 'Date', 'Status ID']),
            'Book Services': TableTab(self.db, 'book_services', ['Booking ID', 'Service ID'])
        }
        
        # Добавляем все таблицы на вкладки
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
        
        # Список SQL файлов для выполнения (меняем порядок)
        sql_files = [
            'database/init.sql',      # Создание таблиц
            'database/views.sql',     # Создание представлений
            'database/queries.sql',   # Создание функций
            'database/procedures.sql', # Создание процедур
            'database/triggers.sql'   # Создание триггеров
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
