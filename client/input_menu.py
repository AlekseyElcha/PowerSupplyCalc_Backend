from PyQt6.QtWidgets import (
    QFormLayout, QDialog, QWidget, QLineEdit, QListWidget, QListWidgetItem,
    QVBoxLayout, QDialogButtonBox, QSizePolicy, QSpinBox, QLabel, QHBoxLayout, QSlider,
    QPushButton, QFrame, QScrollArea, QTabWidget, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer


class StorageListWidget(QWidget):
    """Виджет для управления списком дисков"""
    
    def __init__(self, parent=None, storages: list = None):
        super().__init__(parent)
        self._all_storages = list(storages or [])
        self._storage_items = []  # Список добавленных дисков
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Только кнопка добавления (заголовок теперь на уровне других меток)
        header_layout = QHBoxLayout()
        
        self.add_storage_btn = QPushButton("+ Добавить накопитель")
        self.add_storage_btn.setMinimumWidth(150)
        self.add_storage_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #229954;
            }
            QPushButton:pressed {
                background: #1e8449;
            }
        """)
        self.add_storage_btn.clicked.connect(self._add_storage_item)
        
        header_layout.addStretch()  # Выравниваем кнопку по правому краю
        header_layout.addWidget(self.add_storage_btn)
        layout.addLayout(header_layout)
        
        # Контейнер для списка дисков БЕЗ скроллируемой области
        # Элементы будут просто добавляться вниз, и прокручиваться будет вся форма
        storage_outer_container = QWidget()
        storage_outer_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        storage_outer_container.setStyleSheet("""
            QWidget { 
                border: 2px solid #dee2e6; 
                background: white; 
                border-radius: 8px;
            }
        """)
        storage_outer_layout = QVBoxLayout(storage_outer_container)
        storage_outer_layout.setContentsMargins(0, 0, 0, 0)
        storage_outer_layout.setSpacing(0)
        
        self.storage_container = QWidget()
        self.storage_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.storage_container.setStyleSheet("background: white;")
        self.storage_layout = QVBoxLayout(self.storage_container)
        self.storage_layout.setContentsMargins(8, 8, 8, 8)  # Минимальные отступы
        self.storage_layout.setSpacing(5)  # Минимальное расстояние между элементами
        self.storage_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Выравниваем по верху
        # НЕ добавляем stretch - пусть элементы располагаются естественно
        
        storage_outer_layout.addWidget(self.storage_container)
        layout.addWidget(storage_outer_container)
        
        # Добавляем первый диск по умолчанию
        self._add_storage_item()
    
    def _add_storage_item(self):
        """Добавляет новый элемент диска"""
        item_widget = QFrame()
        item_widget.setFrameStyle(QFrame.Shape.Box)
        item_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        item_widget.setFixedHeight(140)  # Максимально уменьшенная высота
        item_widget.setStyleSheet("""
            QFrame { 
                border: 1px solid #dee2e6; 
                border-radius: 4px; 
                padding: 5px; 
                background: #f8f9fa; 
                margin: 2px;
                min-height: 140px;
                max-height: 140px;
            }
            QFrame:hover {
                border-color: #3498db;
                background: #e3f2fd;
            }
        """)
        
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(5, 5, 5, 5)  # Минимальные отступы
        item_layout.setSpacing(5)  # Минимальное расстояние
        item_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Выравниваем весь layout по верху
        
        # Поле выбора диска
        storage_widget = InlineSearchWidget(self, [s.get("name", "") for s in self._all_storages], is_storage=True)
        storage_widget.setMinimumWidth(450)  # Оптимальная ширина
        storage_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Используем QTimer для отложенного показа списка после создания элемента
        def show_list_delayed():
            storage_widget.show_list_immediately()
            storage_widget.le.setFocus()
        
        QTimer.singleShot(100, show_list_delayed)  # Показываем список через 100мс
        
        # Кнопка удаления
        remove_btn = QPushButton("✕")
        remove_btn.setMinimumSize(25, 25)  # Минимальный размер кнопки
        remove_btn.setMaximumSize(25, 25)
        remove_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        remove_btn.setStyleSheet("""
            QPushButton { 
                background: #dc3545; 
                color: white; 
                border: none; 
                border-radius: 12px; 
                font-weight: bold; 
                font-size: 12px;
            }
            QPushButton:hover {
                background: #c82333;
            }
            QPushButton:pressed {
                background: #bd2130;
            }
        """)
        remove_btn.clicked.connect(lambda: self._remove_storage_item(item_widget))
        
        # Простое горизонтальное расположение с правильным выравниванием
        disk_label = QLabel("Накопитель:")
        disk_label.setStyleSheet("""
            color: #2c3e50; 
            font-weight: 600; 
            font-size: 11px; 
            min-width: 80px;
            border: none;
            background: transparent;
        """)
        disk_label.setAlignment(Qt.AlignmentFlag.AlignTop)  # Выравниваем по верху
        
        item_layout.addWidget(disk_label)
        item_layout.addWidget(storage_widget, 1)
        item_layout.addWidget(remove_btn)
        
        # Добавляем в конец layout
        self.storage_layout.addWidget(item_widget)
        
        # Сохраняем ссылки
        storage_item = {
            'widget': item_widget,
            'storage_widget': storage_widget,
            'remove_btn': remove_btn
        }
        self._storage_items.append(storage_item)
        
        # Обновляем видимость кнопок удаления
        self._update_remove_buttons()
    
    def _remove_storage_item(self, item_widget):
        """Удаляет элемент диска"""
        # Находим и удаляем из списка
        for i, item in enumerate(self._storage_items):
            if item['widget'] == item_widget:
                self.storage_layout.removeWidget(item_widget)
                item_widget.setParent(None)
                item_widget.deleteLater()
                del self._storage_items[i]
                break
        
        self._update_remove_buttons()
    
    def _update_remove_buttons(self):
        """Обновляет видимость кнопок удаления (скрывает если только один диск)"""
        show_remove = len(self._storage_items) > 1
        for item in self._storage_items:
            item['remove_btn'].setVisible(show_remove)
    
    def get_storages(self):
        """Возвращает список выбранных дисков"""
        storages = []
        for item in self._storage_items:
            storage_name = item['storage_widget'].currentText().strip()
            if storage_name:
                storages.append(storage_name)
        return storages
    
    def set_storages(self, storage_names: list):
        """Устанавливает список дисков"""
        # Очищаем текущий список
        for item in self._storage_items[:]:
            self._remove_storage_item(item['widget'])
        
        # Добавляем новые диски
        for storage_name in storage_names or ['']:
            self._add_storage_item()
            if storage_name and self._storage_items:
                self._storage_items[-1]['storage_widget'].setText(storage_name)


class InlineSearchWidget(QWidget):
    def __init__(self, parent=None, items: list[str] | None = None, is_storage=False):
        super().__init__(parent)
        self._all_items = list(items or [])
        self._is_storage = is_storage  # Флаг для дисков

        l = QVBoxLayout(self)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(2)

        self.le = QLineEdit(self)
        self.le.setPlaceholderText("Поиск...")
        
        # Нормальные размеры полей для основных компонентов
        if not self._is_storage:
            # Для основных компонентов - удобные поля
            self.le.setStyleSheet("""
                QLineEdit {
                    background: white;
                    color: #000000;
                    border: 2px solid #dee2e6;
                    border-radius: 6px 6px 0 0;
                    padding: 12px 16px;
                    font-size: 16px;
                    min-height: 25px;
                    min-width: 400px;
                }
                QLineEdit:focus {
                    border-color: #3498db;
                    outline: none;
                }
                QLineEdit::placeholder {
                    color: #6c757d;
                }
            """)
        else:
            # Для накопителей - компактные поля
            self.le.setStyleSheet("""
                QLineEdit {
                    background: white;
                    color: #000000;
                    border: 2px solid #dee2e6;
                    border-radius: 6px 6px 0 0;
                    padding: 12px 16px;
                    font-size: 15px;
                    min-height: 25px;
                }
                QLineEdit:focus {
                    border-color: #3498db;
                    outline: none;
                }
                QLineEdit::placeholder {
                    color: #6c757d;
                }
            """)
        l.addWidget(self.le)

        self.listw = QListWidget(self)
        self.listw.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.listw.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
        # Устанавливаем размеры списка - показываем 2-3 элемента, остальные прокручиваются
        if self._is_storage:
            # Для накопителей - показываем 3 элемента
            self.listw.setMinimumHeight(220)
            self.listw.setMaximumHeight(220)
        else:
            # Для основных компонентов - показываем 4 элемента
            # Увеличиваем размер для лучшей видимости
            self.listw.setMinimumHeight(350)
            self.listw.setMaximumHeight(350)
            
        # Стили для списка
        if not self._is_storage:
            # Нормальные стили для основных компонентов
            self.listw.setStyleSheet("""
                QListWidget {
                    background: white;
                    color: #000000;
                    border: 2px solid #dee2e6;
                    border-top: none;
                    border-radius: 0 0 6px 6px;
                    font-size: 16px;
                }
                QListWidget::item {
                    padding: 10px 16px;
                    border-bottom: 1px solid #e9ecef;
                    color: #000000;
                    min-height: 25px;
                }
                QListWidget::item:hover {
                    background: #e3f2fd;
                    color: #000000;
                }
                QListWidget::item:selected {
                    background: #3498db;
                    color: white;
                }
            """)
        else:
            # Компактные стили для накопителей
            self.listw.setStyleSheet("""
                QListWidget {
                    background: white;
                    color: #000000;
                    border: 2px solid #dee2e6;
                    border-top: none;
                    border-radius: 0 0 6px 6px;
                    font-size: 14px;
                }
                QListWidget::item {
                    padding: 8px 15px;
                    border-bottom: 1px solid #e9ecef;
                    color: #000000;
                    min-height: 25px;
                }
                QListWidget::item:hover {
                    background: #e3f2fd;
                    color: #000000;
                }
                QListWidget::item:selected {
                    background: #3498db;
                    color: white;
                }
            """)
        l.addWidget(self.listw)

        # Инициализируем список данными
        self._repopulate(self._all_items)

        self.le.textEdited.connect(self._on_text_edited)
        self.le.returnPressed.connect(self._on_return_pressed)
        self.le.installEventFilter(self)
        self.listw.itemClicked.connect(self._on_item_clicked)
        
        # Добавляем обработчик фокуса
        self.le.focusInEvent = self._on_focus_in

        # Принудительно показываем список и все элементы при создании
        self._update_list_visibility()
        # Убеждаемся что все элементы видны с самого начала
        if self._all_items:
            self._repopulate(self._all_items)
    
    def show_all_items(self):
        """Показывает все доступные элементы"""
        self._repopulate(self._all_items)
        self._update_list_visibility()

    def show_list_immediately(self):
        """Принудительно показывает список (для новых элементов)"""
        self.show_all_items()  # Показываем все элементы
        self._update_list_visibility()

    def set_items(self, items: list[str]):
        self._all_items = list(items or [])
        self._repopulate(self._all_items)
        self._update_list_visibility()
        # Принудительно показываем все элементы
        self.show_all_items()

    def currentText(self) -> str:
        return self.le.text().strip()

    def setText(self, text: str):
        self.le.setText(text or "")

    def _repopulate(self, items: list[str]):
        self.listw.clear()
        for s in items:
            QListWidgetItem(s, self.listw)

    def _on_text_edited(self, text: str):
        txt = (text or "").strip().lower()
        if not txt:
            # Если поле пустое - показываем ВСЕ элементы
            matches = self._all_items[:]
        else:
            # Фильтруем только если есть текст
            matches = [s for s in self._all_items if txt in s.lower()]
        
        self._repopulate(matches)
        self._update_list_visibility()
        self.le.setCursorPosition(len(text))
        
        # Если список пустой после фильтрации, все равно показываем его
        if not matches and txt:
            # Показываем сообщение "Ничего не найдено" или все элементы
            self._repopulate(["Ничего не найдено - попробуйте другой запрос"] if txt else self._all_items)

    def _on_item_clicked(self, item: QListWidgetItem):
        self.le.setText(item.text())
        self._update_list_visibility()
        self.le.setFocus()

    def _on_focus_in(self, event):
        """Показывает все элементы при получении фокуса"""
        from PyQt6.QtWidgets import QLineEdit
        QLineEdit.focusInEvent(self.le, event)
        # Если поле пустое, показываем все элементы
        if not self.le.text().strip():
            self.show_all_items()
        # Принудительно обновляем видимость списка
        self._update_list_visibility()

    def _on_return_pressed(self):
        current = self.listw.currentItem()
        if current:
            self.le.setText(current.text())
        self._update_list_visibility()
        self.le.setFocus()

    def _update_list_visibility(self):
        # Всегда показываем список, даже если он пустой
        self.listw.setVisible(True)

    def eventFilter(self, watched, event):
        if watched is self.le and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Down:
                if self.listw.count() == 0:
                    return True
                cur = self.listw.currentRow()
                if cur < 0:
                    self.listw.setCurrentRow(0)
                else:
                    nxt = min(self.listw.count() - 1, cur + 1)
                    self.listw.setCurrentRow(nxt)
                return True
            elif event.key() == Qt.Key.Key_Up:
                if self.listw.count() == 0:
                    return True
                cur = self.listw.currentRow()
                if cur <= 0:
                    self.listw.setCurrentRow(self.listw.count() - 1)
                else:
                    self.listw.setCurrentRow(cur - 1)
                return True
            elif event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
                current = self.listw.currentItem()
                if current:
                    self.le.setText(current.text())
                    self.le.setFocus()
                return True
        return super().eventFilter(watched, event)


class InputMenu(QDialog):
    def __init__(self, parent=None, cpus: list = None, gpus: list = None, rams: list = None, storages: list = None, cooling: list = None, drives: list = None, motherboards: list = None):
        super().__init__(parent)
        self.setWindowTitle("Новая конфигурация")
        self.setFixedSize(1150, 950)  # Увеличиваем размер для больших списков
        
        # Сохраняем данные СНАЧАЛА
        self.cpus = cpus or []
        self.gpus = gpus or []
        self.rams = rams or []
        self.storages = storages or []
        self.cooling = cooling or []
        self.drives = drives or []
        self.motherboards = motherboards or []

        self.cpu_names = [c.get("name", "") for c in self.cpus if c.get("name")]
        self.gpu_names = [g.get("name", "") for g in self.gpus if g.get("name")]
        self.ram_names = [r.get("name", "") for r in self.rams if r.get("name")]
        self.storage_names = [s.get("name", "") for s in self.storages if s.get("name")]
        self.cooling_names = [c.get("name", "") for c in self.cooling if c.get("name") and c.get("name").strip()]
        self.drive_names = [d.get("name", "") for d in self.drives if d.get("name")]
        self.motherboard_names = [m.get("name", "") for m in self.motherboards if m.get("name") and m.get("name").strip()]
        
        # Улучшаем стиль самого диалога
        self.setStyleSheet("""
            QDialog {
                background: #f8f9fa;
            }
        """)

        # Создаем основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Заголовок
        title_label = QLabel("Конфигурация компонентов ПК")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background: white;
                border-radius: 8px;
                border: 2px solid #3498db;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Создаем вкладки
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                background: #e9ecef;
                color: #495057;
                padding: 8px 16px;
                margin-right: 2px;
                border-radius: 4px 4px 0 0;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background: #6c757d;
                color: white;
            }
        """)
        
        # Теперь создаем вкладки - каждый компонент на отдельной вкладке
        self.create_cpu_tab()
        self.create_gpu_tab()
        self.create_ram_tab()
        self.create_cooling_tab()
        self.create_drive_tab()
        self.create_motherboard_tab()
        self.create_storage_tab()
        self.create_settings_tab()
        
        main_layout.addWidget(self.tab_widget)

        # Кнопки внизу
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                        QDialogButtonBox.StandardButton.Cancel)
        self.buttons.setStyleSheet("""
            QDialogButtonBox {
                background: white;
                padding: 15px;
                border-top: 3px solid #3498db;
                margin-top: 10px;
            }
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
                min-height: 40px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
            QPushButton:pressed {
                background: #21618c;
            }
            QPushButton[text="Cancel"] {
                background: #e74c3c;
            }
            QPushButton[text="Cancel"]:hover {
                background: #c0392b;
            }
        """)
        main_layout.addWidget(self.buttons)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def create_cpu_tab(self):
        """Создает вкладку для выбора процессора"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Заголовок
        header_label = QLabel("Выбор процессора (CPU)")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                background: #e8f4fd;
                border-radius: 12px;
                border: 3px solid #3498db;
            }
        """)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Контейнер для поиска
        search_container = QWidget()
        search_container.setStyleSheet("""
            QWidget {
                background: white;
                border: 2px solid #dee2e6;
                border-radius: 12px;
                padding: 30px;
            }
        """)
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(30, 30, 30, 30)
        search_layout.setSpacing(20)
        
        # Описание
        desc_label = QLabel("Найдите и выберите процессор для вашей конфигурации:")
        desc_label.setStyleSheet("""
            color: #2c3e50; 
            font-size: 16px; 
            font-weight: 500;
            margin-bottom: 10px;
        """)
        search_layout.addWidget(desc_label)
        
        # Поле поиска процессора
        self.cpu_widget = InlineSearchWidget(self, self.cpu_names)
        # Увеличиваем размеры для отдельной вкладки
        self.cpu_widget.le.setStyleSheet("""
            QLineEdit {
                background: white;
                color: #000000;
                border: 3px solid #dee2e6;
                border-radius: 8px 8px 0 0;
                padding: 20px 25px;
                font-size: 20px;
                min-height: 40px;
                min-width: 600px;
            }
            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
                box-shadow: 0 0 15px rgba(52, 152, 219, 0.3);
            }
            QLineEdit::placeholder {
                color: #6c757d;
                font-size: 18px;
            }
        """)
        # Увеличиваем список
        self.cpu_widget.listw.setMinimumHeight(400)
        self.cpu_widget.listw.setMaximumHeight(400)
        self.cpu_widget.listw.setStyleSheet("""
            QListWidget {
                background: white;
                color: #000000;
                border: 3px solid #dee2e6;
                border-top: none;
                border-radius: 0 0 8px 8px;
                font-size: 18px;
            }
            QListWidget::item {
                padding: 18px 25px;
                border-bottom: 1px solid #e9ecef;
                color: #000000;
                min-height: 40px;
            }
            QListWidget::item:hover {
                background: #e3f2fd;
                color: #000000;
            }
            QListWidget::item:selected {
                background: #3498db;
                color: white;
            }
        """)
        
        search_layout.addWidget(self.cpu_widget)
        layout.addWidget(search_container)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Процессор")

    def create_gpu_tab(self):
        """Создает вкладку для выбора видеокарты"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Заголовок
        header_label = QLabel("Выбор видеокарты (GPU)")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                background: #fff3cd;
                border-radius: 12px;
                border: 3px solid #ffc107;
            }
        """)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Контейнер для поиска
        search_container = QWidget()
        search_container.setStyleSheet("""
            QWidget {
                background: white;
                border: 2px solid #dee2e6;
                border-radius: 12px;
                padding: 30px;
            }
        """)
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(30, 30, 30, 30)
        search_layout.setSpacing(20)
        
        # Описание
        desc_label = QLabel("Найдите и выберите видеокарту для вашей конфигурации:")
        desc_label.setStyleSheet("""
            color: #2c3e50; 
            font-size: 16px; 
            font-weight: 500;
            margin-bottom: 10px;
        """)
        search_layout.addWidget(desc_label)
        
        # Поле поиска видеокарты
        self.gpu_widget = InlineSearchWidget(self, self.gpu_names)
        # Увеличиваем размеры для отдельной вкладки
        self.gpu_widget.le.setStyleSheet("""
            QLineEdit {
                background: white;
                color: #000000;
                border: 3px solid #dee2e6;
                border-radius: 8px 8px 0 0;
                padding: 20px 25px;
                font-size: 20px;
                min-height: 40px;
                min-width: 600px;
            }
            QLineEdit:focus {
                border-color: #ffc107;
                outline: none;
                box-shadow: 0 0 15px rgba(255, 193, 7, 0.3);
            }
            QLineEdit::placeholder {
                color: #6c757d;
                font-size: 18px;
            }
        """)
        # Увеличиваем список
        self.gpu_widget.listw.setMinimumHeight(400)
        self.gpu_widget.listw.setMaximumHeight(400)
        self.gpu_widget.listw.setStyleSheet("""
            QListWidget {
                background: white;
                color: #000000;
                border: 3px solid #dee2e6;
                border-top: none;
                border-radius: 0 0 8px 8px;
                font-size: 18px;
            }
            QListWidget::item {
                padding: 18px 25px;
                border-bottom: 1px solid #e9ecef;
                color: #000000;
                min-height: 40px;
            }
            QListWidget::item:hover {
                background: #fff3cd;
                color: #000000;
            }
            QListWidget::item:selected {
                background: #ffc107;
                color: white;
            }
        """)
        
        search_layout.addWidget(self.gpu_widget)
        layout.addWidget(search_container)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Видеокарта")

    def create_ram_tab(self):
        """Создает вкладку для выбора оперативной памяти"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Заголовок
        header_label = QLabel("Выбор оперативной памяти (RAM)")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                background: #d1ecf1;
                border-radius: 12px;
                border: 3px solid #17a2b8;
            }
        """)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # КОМПАКТНЫЙ ползунок для количества планок - НАД поиском
        modules_container = QWidget()
        modules_container.setStyleSheet("""
            QWidget {
                background: #f8f9fa;
                border: 2px solid #17a2b8;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        modules_layout = QHBoxLayout(modules_container)  # Горизонтальный layout для компактности
        modules_layout.setContentsMargins(15, 10, 15, 10)
        modules_layout.setSpacing(15)
        
        # Заголовок
        modules_title = QLabel("Количество планок:")
        modules_title.setStyleSheet("""
            color: #2c3e50; 
            font-size: 14px; 
            font-weight: 600;
        """)
        
        # Компактный ползунок
        self.ram_modules_slider = QSlider(Qt.Orientation.Horizontal)
        self.ram_modules_slider.setMinimum(1)
        self.ram_modules_slider.setMaximum(4)
        self.ram_modules_slider.setValue(2)
        self.ram_modules_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.ram_modules_slider.setTickInterval(1)
        self.ram_modules_slider.setMaximumWidth(200)  # Ограничиваем ширину
        self.ram_modules_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: #e9ecef;
                height: 12px;
                border-radius: 6px;
            }
            QSlider::handle:horizontal {
                background: #17a2b8;
                border: 2px solid #138496;
                width: 20px;
                height: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #138496;
            }
            QSlider::sub-page:horizontal {
                background: #17a2b8;
                border-radius: 6px;
            }
        """)
        
        # Компактное отображение значения
        self.ram_modules_value_label = QLabel("2")
        self.ram_modules_value_label.setStyleSheet("""
            QLabel {
                font-weight: bold; 
                color: #17a2b8;
                font-size: 16px;
                padding: 5px 12px;
                background: #d1ecf1;
                border-radius: 6px;
                border: 2px solid #17a2b8;
                min-width: 25px;
            }
        """)
        self.ram_modules_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        modules_layout.addWidget(modules_title)
        modules_layout.addWidget(self.ram_modules_slider)
        modules_layout.addWidget(self.ram_modules_value_label)
        modules_layout.addStretch()
        
        # Подключаем обновление значения
        self.ram_modules_slider.valueChanged.connect(self._update_ram_modules_label)
        
        layout.addWidget(modules_container)
        
        # ОСНОВНОЙ контейнер для поиска RAM - ТОЧНО КАК У ПРОЦЕССОРА
        search_container = QWidget()
        search_container.setStyleSheet("""
            QWidget {
                background: white;
                border: 2px solid #dee2e6;
                border-radius: 12px;
                padding: 30px;
            }
        """)
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(30, 30, 30, 30)
        search_layout.setSpacing(20)
        
        # Описание
        desc_label = QLabel("Найдите и выберите тип оперативной памяти:")
        desc_label.setStyleSheet("""
            color: #2c3e50; 
            font-size: 16px; 
            font-weight: 500;
            margin-bottom: 10px;
        """)
        search_layout.addWidget(desc_label)
        
        # Поле поиска RAM - ТОЧНО КАК У ПРОЦЕССОРА
        self.ram_widget = InlineSearchWidget(self, self.ram_names)
        self.ram_widget.le.setStyleSheet("""
            QLineEdit {
                background: white;
                color: #000000;
                border: 3px solid #dee2e6;
                border-radius: 8px 8px 0 0;
                padding: 20px 25px;
                font-size: 20px;
                min-height: 40px;
                min-width: 600px;
            }
            QLineEdit:focus {
                border-color: #17a2b8;
                outline: none;
                box-shadow: 0 0 15px rgba(23, 162, 184, 0.3);
            }
            QLineEdit::placeholder {
                color: #6c757d;
                font-size: 18px;
            }
        """)
        # БОЛЬШОЙ список как у процессора
        self.ram_widget.listw.setMinimumHeight(400)
        self.ram_widget.listw.setMaximumHeight(400)
        self.ram_widget.listw.setStyleSheet("""
            QListWidget {
                background: white;
                color: #000000;
                border: 3px solid #dee2e6;
                border-top: none;
                border-radius: 0 0 8px 8px;
                font-size: 18px;
            }
            QListWidget::item {
                padding: 18px 25px;
                border-bottom: 1px solid #e9ecef;
                color: #000000;
                min-height: 40px;
            }
            QListWidget::item:hover {
                background: #d1ecf1;
                color: #000000;
            }
            QListWidget::item:selected {
                background: #17a2b8;
                color: white;
            }
        """)
        
        search_layout.addWidget(self.ram_widget)
        layout.addWidget(search_container)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Память")

    def _update_ram_modules_label(self, value):
        """Обновляет отображение количества планок RAM"""
        self.ram_modules_value_label.setText(str(value))

    def create_cooling_tab(self):
        """Создает вкладку для выбора системы охлаждения"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Заголовок
        header_label = QLabel("Выбор системы охлаждения")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                background: #d4edda;
                border-radius: 12px;
                border: 3px solid #28a745;
            }
        """)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Контейнер для поиска
        search_container = QWidget()
        search_container.setStyleSheet("""
            QWidget {
                background: white;
                border: 2px solid #dee2e6;
                border-radius: 12px;
                padding: 30px;
            }
        """)
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(30, 30, 30, 30)
        search_layout.setSpacing(20)
        
        # Описание
        desc_label = QLabel("Найдите и выберите систему охлаждения для вашей конфигурации:")
        desc_label.setStyleSheet("""
            color: #2c3e50; 
            font-size: 16px; 
            font-weight: 500;
            margin-bottom: 10px;
        """)
        search_layout.addWidget(desc_label)
        
        # Поле поиска системы охлаждения
        # Используем ВАШИ реальные данные
        self.cooling_widget = InlineSearchWidget(self, self.cooling_names)
        # Увеличиваем размеры для отдельной вкладки
        self.cooling_widget.le.setStyleSheet("""
            QLineEdit {
                background: white;
                color: #000000;
                border: 3px solid #dee2e6;
                border-radius: 8px 8px 0 0;
                padding: 20px 25px;
                font-size: 20px;
                min-height: 40px;
                min-width: 600px;
            }
            QLineEdit:focus {
                border-color: #28a745;
                outline: none;
                box-shadow: 0 0 15px rgba(40, 167, 69, 0.3);
            }
            QLineEdit::placeholder {
                color: #6c757d;
                font-size: 18px;
            }
        """)
        # Увеличиваем список - делаем так чтобы все 4 элемента помещались без прокрутки
        self.cooling_widget.listw.setMinimumHeight(200)  # Достаточно для 4 элементов
        self.cooling_widget.listw.setMaximumHeight(200)
        self.cooling_widget.listw.setStyleSheet("""
            QListWidget {
                background: white;
                color: #000000;
                border: 3px solid #dee2e6;
                border-top: none;
                border-radius: 0 0 8px 8px;
                font-size: 18px;
            }
            QListWidget::item {
                padding: 18px 25px;
                border-bottom: 1px solid #e9ecef;
                color: #000000;
                min-height: 40px;
            }
            QListWidget::item:hover {
                background: #d4edda;
                color: #000000;
            }
            QListWidget::item:selected {
                background: #28a745;
                color: white;
            }
        """)
        
        search_layout.addWidget(self.cooling_widget)
        layout.addWidget(search_container)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Охлаждение")

    def create_drive_tab(self):
        """Создает вкладку для выбора оптического привода"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Заголовок
        header_label = QLabel("Выбор оптического привода")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                background: #f8d7da;
                border-radius: 12px;
                border: 3px solid #dc3545;
            }
        """)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Контейнер для поиска
        search_container = QWidget()
        search_container.setStyleSheet("""
            QWidget {
                background: white;
                border: 2px solid #dee2e6;
                border-radius: 12px;
                padding: 30px;
            }
        """)
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(30, 30, 30, 30)
        search_layout.setSpacing(20)
        
        # Описание
        desc_label = QLabel("Выберите оптический привод (DVD/Blu-ray):")
        desc_label.setStyleSheet("""
            color: #2c3e50; 
            font-size: 16px; 
            font-weight: 500;
            margin-bottom: 10px;
        """)
        search_layout.addWidget(desc_label)
        
        # Поле поиска
        self.drive_widget = InlineSearchWidget(self, self.drive_names)
        self.drive_widget.le.setStyleSheet("""
            QLineEdit {
                background: white;
                color: #000000;
                border: 3px solid #dee2e6;
                border-radius: 8px 8px 0 0;
                padding: 20px 25px;
                font-size: 20px;
                min-height: 40px;
                min-width: 600px;
            }
            QLineEdit:focus {
                border-color: #dc3545;
                outline: none;
                box-shadow: 0 0 15px rgba(220, 53, 69, 0.3);
            }
            QLineEdit::placeholder {
                color: #6c757d;
                font-size: 18px;
            }
        """)
        self.drive_widget.listw.setMinimumHeight(400)
        self.drive_widget.listw.setMaximumHeight(400)
        self.drive_widget.listw.setStyleSheet("""
            QListWidget {
                background: white;
                color: #000000;
                border: 3px solid #dee2e6;
                border-top: none;
                border-radius: 0 0 8px 8px;
                font-size: 18px;
            }
            QListWidget::item {
                padding: 18px 25px;
                border-bottom: 1px solid #e9ecef;
                color: #000000;
                min-height: 40px;
            }
            QListWidget::item:hover {
                background: #f8d7da;
                color: #000000;
            }
            QListWidget::item:selected {
                background: #dc3545;
                color: white;
            }
        """)
        
        search_layout.addWidget(self.drive_widget)
        layout.addWidget(search_container)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Привод")

    def create_motherboard_tab(self):
        """Создает вкладку для выбора материнской платы"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Заголовок
        header_label = QLabel("Выбор материнской платы")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                background: #e2e3e5;
                border-radius: 12px;
                border: 3px solid #6c757d;
            }
        """)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Контейнер для поиска
        search_container = QWidget()
        search_container.setStyleSheet("""
            QWidget {
                background: white;
                border: 2px solid #dee2e6;
                border-radius: 12px;
                padding: 30px;
            }
        """)
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(30, 30, 30, 30)
        search_layout.setSpacing(20)
        
        # Описание
        desc_label = QLabel("Найдите и выберите материнскую плату для вашей конфигурации:")
        desc_label.setStyleSheet("""
            color: #2c3e50; 
            font-size: 16px; 
            font-weight: 500;
            margin-bottom: 10px;
        """)
        search_layout.addWidget(desc_label)
        
        # Поле поиска материнской платы
        # Используем ВАШИ реальные данные
        self.motherboard_widget = InlineSearchWidget(self, self.motherboard_names)
        # Увеличиваем размеры для отдельной вкладки
        self.motherboard_widget.le.setStyleSheet("""
            QLineEdit {
                background: white;
                color: #000000;
                border: 3px solid #dee2e6;
                border-radius: 8px 8px 0 0;
                padding: 20px 25px;
                font-size: 20px;
                min-height: 40px;
                min-width: 600px;
            }
            QLineEdit:focus {
                border-color: #6c757d;
                outline: none;
                box-shadow: 0 0 15px rgba(108, 117, 125, 0.3);
            }
            QLineEdit::placeholder {
                color: #6c757d;
                font-size: 18px;
            }
        """)
        # Увеличиваем список - делаем так чтобы все 4 элемента помещались без прокрутки
        self.motherboard_widget.listw.setMinimumHeight(200)  # Достаточно для 4 элементов
        self.motherboard_widget.listw.setMaximumHeight(200)
        self.motherboard_widget.listw.setStyleSheet("""
            QListWidget {
                background: white;
                color: #000000;
                border: 3px solid #dee2e6;
                border-top: none;
                border-radius: 0 0 8px 8px;
                font-size: 18px;
            }
            QListWidget::item {
                padding: 18px 25px;
                border-bottom: 1px solid #e9ecef;
                color: #000000;
                min-height: 40px;
            }
            QListWidget::item:hover {
                background: #e2e3e5;
                color: #000000;
            }
            QListWidget::item:selected {
                background: #6c757d;
                color: white;
            }
        """)
        
        search_layout.addWidget(self.motherboard_widget)
        layout.addWidget(search_container)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Мат. плата")
    
    def create_storage_tab(self):
        """Создает вкладку с накопителями"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Заголовок в стиле CPU
        header_label = QLabel("Выбор накопителей (HDD/SSD)")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                background: #e1f5fe;
                border-radius: 12px;
                border: 3px solid #00bcd4;
            }
        """)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Контейнер для накопителей в стиле CPU
        storage_container = QWidget()
        storage_container.setStyleSheet("""
            QWidget {
                background: white;
                border: 2px solid #dee2e6;
                border-radius: 12px;
                padding: 30px;
            }
        """)
        storage_layout = QVBoxLayout(storage_container)
        storage_layout.setContentsMargins(30, 30, 30, 30)
        storage_layout.setSpacing(20)
        
        # Описание
        desc_label = QLabel("Добавьте один или несколько накопителей для вашей конфигурации:")
        desc_label.setStyleSheet("""
            color: #2c3e50; 
            font-size: 16px; 
            font-weight: 500;
            margin-bottom: 10px;
        """)
        storage_layout.addWidget(desc_label)
        
        # Создаем StorageListWidget с обновленными стилями
        self.storage_widget = StorageListWidget(self, self.storages)
        # Обновляем стили StorageListWidget под новый дизайн
        self.storage_widget.setStyleSheet("""
            StorageListWidget {
                background: transparent;
                border: none;
            }
        """)
        
        storage_layout.addWidget(self.storage_widget)
        layout.addWidget(storage_container)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Накопители")
    
    def create_settings_tab(self):
        """Создает вкладку с настройками"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(30, 30, 30, 30)  # Увеличиваем отступы
        layout.setSpacing(30)  # Увеличиваем расстояние
        
        # Заголовок
        header_label = QLabel("Настройки расчета")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                background: #fff3cd;
                border-radius: 12px;
                border: 3px solid #ffc107;
            }
        """)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Ползунок запаса мощности
        power_margin_container = QWidget()
        power_margin_container.setStyleSheet("""
            QWidget {
                background: white;
                border: 3px solid #dee2e6;
                border-radius: 12px;
                padding: 30px;
            }
        """)
        power_margin_layout = QVBoxLayout(power_margin_container)
        power_margin_layout.setContentsMargins(30, 30, 30, 30)
        power_margin_layout.setSpacing(25)
        
        # Заголовок и значение
        margin_header_layout = QHBoxLayout()
        margin_label = QLabel("Запас мощности:")
        margin_label.setStyleSheet("color: #2c3e50; font-weight: 600; font-size: 20px;")
        
        self.margin_value_label = QLabel("20%")
        self.margin_value_label.setStyleSheet("""
            QLabel {
                font-weight: bold; 
                color: #3498db;
                font-size: 32px;
                padding: 15px 30px;
                background: #e3f2fd;
                border-radius: 12px;
                border: 3px solid #3498db;
                min-width: 100px;
            }
        """)
        margin_header_layout.addWidget(margin_label)
        margin_header_layout.addStretch()
        margin_header_layout.addWidget(self.margin_value_label)
        
        # Ползунок
        self.power_margin_slider = QSlider(Qt.Orientation.Horizontal)
        self.power_margin_slider.setMinimum(10)
        self.power_margin_slider.setMaximum(50)
        self.power_margin_slider.setValue(20)
        self.power_margin_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.power_margin_slider.setTickInterval(10)
        self.power_margin_slider.setMinimumHeight(50)  # Увеличиваем высоту ползунка
        self.power_margin_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 2px solid #bbb;
                background: #e9ecef;
                height: 20px;
                border-radius: 10px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                border: 4px solid #2980b9;
                width: 35px;
                height: 35px;
                margin: -12px 0;
                border-radius: 17px;
            }
            QSlider::handle:horizontal:hover {
                background: #2980b9;
                transform: scale(1.1);
            }
            QSlider::sub-page:horizontal {
                background: #3498db;
                border-radius: 10px;
            }
        """)
        
        # Подписи к ползунку
        slider_labels_layout = QHBoxLayout()
        
        def create_slider_label(text):
            label = QLabel(text)
            label.setStyleSheet("color: #6c757d; font-size: 18px; font-weight: 600;")
            return label
        
        slider_labels_layout.addWidget(create_slider_label("10%"))
        slider_labels_layout.addStretch()
        slider_labels_layout.addWidget(create_slider_label("30%"))
        slider_labels_layout.addStretch()
        slider_labels_layout.addWidget(create_slider_label("50%"))
        
        power_margin_layout.addLayout(margin_header_layout)
        power_margin_layout.addWidget(self.power_margin_slider)
        power_margin_layout.addLayout(slider_labels_layout)
        
        # Подключаем обновление значения
        self.power_margin_slider.valueChanged.connect(self._update_margin_label)
        
        layout.addWidget(power_margin_container)
        layout.addStretch()  # Добавляем растяжку внизу
        
        self.tab_widget.addTab(tab, "Настройки")

    def _update_margin_label(self, value):
        """Обновляет отображение значения запаса мощности"""
        self.margin_value_label.setText(f"{value}%")

    def get_data(self):
        return {
            "CPU": self.cpu_widget.currentText(),
            "GPU": self.gpu_widget.currentText(),
            "RAM": self.ram_widget.currentText(),
            "RAM_modules": self.ram_modules_slider.value(),
            "Storages": self.storage_widget.get_storages(),
            "Cooling": self.cooling_widget.currentText(),
            "Drive": self.drive_widget.currentText(),
            "Motherboard": self.motherboard_widget.currentText(),
            "power_margin": self.power_margin_slider.value()
        }