from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt


class ResultDetailsDialog(QDialog):
    def __init__(self, parent=None, result_data=None):
        super().__init__(parent)
        self.setWindowTitle("Детали расчета мощности")
        self.setFixedSize(600, 600)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Заголовок
        title = QLabel("Подробный расчет потребления")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Создаем область прокрутки для деталей
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setSpacing(10)
        
        if result_data:
            # Компоненты и их потребление
            self._add_component_row(details_layout, "CPU", 
                                  result_data.get("cpu_name", "Не выбран"), 
                                  result_data.get("cpu_w", 0))
            
            self._add_component_row(details_layout, "GPU", 
                                  result_data.get("gpu_name", "Не выбран"), 
                                  result_data.get("gpu_w", 0))
            
            # RAM с количеством модулей
            ram_name = result_data.get("ram_name", "Не выбран")
            ram_modules = result_data.get("ram_modules", 1)
            ram_w_single = result_data.get("ram_w_single", 0)
            ram_w_total = result_data.get("ram_w", 0)
            
            ram_display = f"{ram_name} x{ram_modules} модуля" if ram_modules > 1 else ram_name
            ram_power_display = f"{ram_w_total}W ({ram_w_single}W x {ram_modules})" if ram_modules > 1 else f"{ram_w_total}W"
            
            self._add_component_row(details_layout, "RAM", ram_display, ram_power_display)
            
            # Storage - может быть несколько дисков
            storage_details = result_data.get("storage_details", [])
            total_storage_w = result_data.get("storage_w", 0)
            
            if storage_details:
                # Показываем каждый диск отдельно
                for i, storage in enumerate(storage_details):
                    storage_name = storage.get("name", "Неизвестный диск")
                    storage_power = storage.get("consumption", 0)
                    label = f"Диск {i+1}" if len(storage_details) > 1 else "Storage"
                    self._add_component_row(details_layout, label, storage_name, storage_power)
                
                # Если дисков больше одного, показываем общее потребление
                if len(storage_details) > 1:
                    self._add_component_row(details_layout, "Всего дисков", 
                                          f"{len(storage_details)} шт.", 
                                          f"{total_storage_w}W")
            else:
                self._add_component_row(details_layout, "Storage", "Не выбран", 0)
            
            # Новые компоненты
            self._add_component_row(details_layout, "Охлаждение", 
                                  result_data.get("cooling_name", "Не выбрано"), 
                                  result_data.get("cooling_w", 0))
            
            self._add_component_row(details_layout, "Оптический привод", 
                                  result_data.get("drive_name", "Не выбран"), 
                                  result_data.get("drive_w", 0))
            
            self._add_component_row(details_layout, "Материнская плата", 
                                  result_data.get("motherboard_name", "Не выбрана"), 
                                  result_data.get("motherboard_w", 0))
            
            # Разделитель
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setStyleSheet("color: #bdc3c7;")
            details_layout.addWidget(separator)
            
            # Промежуточные расчеты
            overhead = result_data.get("overhead", 200)
            raw_total = result_data.get("raw_total", 0)
            power_margin = result_data.get("power_margin", 20)
            required = result_data.get("required", 0)
            
            self._add_calculation_row(details_layout, "Накладные расходы", f"{overhead}W")
            self._add_calculation_row(details_layout, "Итого без запаса", f"{raw_total}W")
            self._add_calculation_row(details_layout, f"Запас мощности (+{power_margin}%)", 
                                    f"+{required - raw_total}W")
            
            # Финальный результат
            final_separator = QFrame()
            final_separator.setFrameShape(QFrame.Shape.HLine)
            final_separator.setStyleSheet("color: #34495e; border-width: 2px;")
            details_layout.addWidget(final_separator)
            
            final_layout = QHBoxLayout()
            final_label = QLabel("Рекомендуемая мощность БП:")
            final_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
            final_value = QLabel(f"{required}W")
            final_value.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c;")
            
            final_layout.addWidget(final_label)
            final_layout.addStretch()
            final_layout.addWidget(final_value)
            details_layout.addLayout(final_layout)
        
        scroll.setWidget(details_widget)
        layout.addWidget(scroll)
        
        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        close_btn.clicked.connect(self.accept)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
    
    def _add_component_row(self, layout, component_type, name, power):
        row_layout = QHBoxLayout()
        
        type_label = QLabel(f"{component_type}:")
        type_label.setStyleSheet("font-weight: bold; color: #34495e; min-width: 80px;")
        
        name_label = QLabel(name if name else "Не выбран")
        name_label.setStyleSheet("color: #2c3e50;")
        
        if isinstance(power, str):
            power_label = QLabel(power)
        else:
            power_label = QLabel(f"{power}W" if power > 0 else "0W")
        power_label.setStyleSheet("font-weight: bold; color: #e67e22; min-width: 60px;")
        power_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        row_layout.addWidget(type_label)
        row_layout.addWidget(name_label, 1)
        row_layout.addWidget(power_label)
        
        layout.addLayout(row_layout)
    
    def _add_calculation_row(self, layout, description, value):
        row_layout = QHBoxLayout()
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-weight: bold; color: #95a5a6;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        row_layout.addWidget(desc_label)
        row_layout.addStretch()
        row_layout.addWidget(value_label)
        
        layout.addLayout(row_layout)