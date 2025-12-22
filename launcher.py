import sys
import os
import time
import socket
from threading import Thread
import runpy

sys.path.insert(0, os.path.dirname(__file__))
# -------------------------------
#  Функция для получения пути к ресурсам внутри exe
# -------------------------------
def resource_path(rel_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, rel_path)
    return os.path.join(os.path.abspath("."), rel_path)

# -------------------------------
#  Проверка занят ли порт
# -------------------------------
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


# -------------------------------
#  Запуск backend (FastAPI + aiosqlite)
# -------------------------------
def start_backend():
    import sys
    import os
    import logging
    
    # Настройка логирования для отладки
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Добавляем путь к backend в sys.path
        backend_path = resource_path("backend")
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        # Добавляем корневую папку в sys.path для импорта backend модулей
        root_path = resource_path("")
        if root_path not in sys.path:
            sys.path.insert(0, root_path)
        
        logger.info(f"Backend path: {backend_path}")
        logger.info(f"Root path: {root_path}")
        
        # Проверяем, что файлы существуют
        main_py_path = os.path.join(backend_path, "main.py")
        logger.info(f"Checking main.py at: {main_py_path}")
        logger.info(f"Main.py exists: {os.path.exists(main_py_path)}")
        
        import uvicorn
        logger.info("Uvicorn imported successfully")
        
        # Импортируем приложение из backend.main
        logger.info("Starting uvicorn server...")
        uvicorn.run(
            "backend.main:app", 
            host="127.0.0.1", 
            port=8000, 
            reload=False, 
            log_level="info",
            access_log=False
        )
    except Exception as e:
        logger.error(f"Ошибка запуска backend: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    return True


# -------------------------------
#  Запуск frontend (client/main.py)
# -------------------------------
def start_frontend(*args, **kwargs):
    import sys
    from PyQt6.QtWidgets import QApplication
    
    # Добавляем пути для корректного импорта модулей клиента
    client_path = resource_path("client")
    root_path = resource_path("")
    
    if client_path not in sys.path:
        sys.path.insert(0, client_path)
    if root_path not in sys.path:
        sys.path.insert(0, root_path)
    
    # Импортируем модули клиента
    from client.main import MainWindow, load_stylesheet
    import client.storage_sql as storage

    app = QApplication(sys.argv)
    storage.setup()

    qss_path = resource_path("client/style.qss")
    stylesheet = load_stylesheet(qss_path)
    if stylesheet:
        app.setStyleSheet(stylesheet)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())




# -------------------------------
#  Ожидание запуска backend
# -------------------------------
def wait_for_backend(host="127.0.0.1", port=8000, timeout=30):
    """Ждем пока backend станет доступен"""
    import time
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if is_port_in_use(port):
            print(f"Backend доступен на {host}:{port}")
            return True
        time.sleep(0.5)
    
    print(f"Backend не запустился за {timeout} секунд")
    return False

# -------------------------------
#  Основной запуск
# -------------------------------
if __name__ == "__main__":
    import threading
    import time
    import logging
    
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    logger.info("Запуск PSU Calculator...")
    
    # Проверяем ресурсы
    logger.info(f"Resource path test: {resource_path('.')}")
    logger.info(f"Backend exists: {os.path.exists(resource_path('backend'))}")
    logger.info(f"Client exists: {os.path.exists(resource_path('client'))}")
    
    # Проверяем, не занят ли порт
    if is_port_in_use(8000):
        logger.info("Порт 8000 уже занят, пытаемся подключиться к существующему backend...")
    else:
        logger.info("Запуск backend сервера...")
        # backend запускаем в отдельном потоке
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()
        
        # Ждем пока backend запустится
        logger.info("Ожидание запуска backend...")
        if not wait_for_backend(timeout=60):  # Увеличиваем таймаут
            logger.error("Не удалось запустить backend. Завершение работы.")
            sys.exit(1)

    logger.info("Запуск frontend...")
    # frontend запускаем в основном потоке
    start_frontend()

