import subprocess
import sys
import json
import pkg_resources


def get_all_imports():
    """Получить все импорты из проекта"""
    imports = set()

    # Сканируем файлы .py
    for root, dirs, files in os.walk("."):
        # Пропускаем виртуальные окружения и служебные папки
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in
                   ['__pycache__', 'venv', '.venv', 'build', 'dist']]

        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Простой анализ импортов
                        lines = content.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line.startswith('import ') or line.startswith('from '):
                                # Извлекаем имя модуля
                                if line.startswith('import '):
                                    modules = line[7:].split(',')
                                else:  # from X import Y
                                    modules = [line.split()[1]]

                                for mod in modules:
                                    mod = mod.strip().split()[0].split('.')[0]
                                    if mod and not mod.startswith('_'):
                                        imports.add(mod)
                except:
                    pass

    return imports


def get_installed_packages():
    """Получить установленные пакеты"""
    return {pkg.key: pkg.version for pkg in pkg_resources.working_set}


def generate_requirements():
    print("Генерация requirements.txt...")

    # Получаем все импорты
    imports = get_all_imports()
    print(f"Найдено {len(imports)} импортов: {sorted(imports)}")

    # Получаем установленные пакеты
    installed = get_installed_packages()

    # Фильтруем только те, что установлены
    requirements = []
    for imp in imports:
        if imp in installed:
            requirements.append(f"{imp}=={installed[imp]}")
        else:
            # Пробуем найти через pip
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "show", imp],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.startswith('Version:'):
                            version = line.split(':')[1].strip()
                            requirements.append(f"{imp}=={version}")
                            break
            except:
                requirements.append(f"{imp}")  # Без версии

    # Добавляем обязательные для проекта
    essential = [
        "uvicorn[standard]",
        "fastapi",
        "python-multipart",
        "jinja2",
        "sqlalchemy",
        "pydantic",
        "aiofiles"
    ]

    for ess in essential:
        if not any(ess.split('[')[0] in req for req in requirements):
            requirements.append(ess)

    # Сохраняем
    with open("requirements.txt", "w", encoding='utf-8') as f:
        f.write("# Автоматически сгенерированные зависимости\n")
        f.write("# Сгенерировано generate_requirements.py\n\n")
        for req in sorted(set(requirements)):
            f.write(f"{req}\n")

    print(f"✅ Создан requirements.txt с {len(requirements)} зависимостями")
    return requirements


if __name__ == "__main__":
    import os

    requirements = generate_requirements()

    print("\nСодержимое requirements.txt:")
    for req in requirements:
        print(f"  {req}")