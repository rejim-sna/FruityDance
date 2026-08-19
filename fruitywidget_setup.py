import os
import urllib.request
import zipfile
import shutil
import sys
import subprocess
from pathlib import Path

# ============ НАСТРОЙКИ ============
DOCUMENTS_FOLDER = Path(os.path.expanduser("~/Documents/FruityWidget"))
ANIMATIONS_FOLDER = DOCUMENTS_FOLDER / "Animations"
MAIN_SCRIPT_URL = "https://raw.githubusercontent.com/rejim-sna/FruityDance/main/fruitywidget.py"

# 🔥 ПРЯМАЯ ССЫЛКА НА ТВОЙ АРХИВ
GIF_ZIP_URL = "https://github.com/rejim-sna/FruityDance/raw/main/animations.zip"

def download_file(url, dest):
    """Скачивает файл по ссылке"""
    print(f"📥 Скачиваю: {url}")
    try:
        urllib.request.urlretrieve(url, dest)
        print("✅ Готово!")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def install_animations():
    """Устанавливает анимации из ZIP"""
    zip_path = DOCUMENTS_FOLDER / "animations.zip"
    
    if download_file(GIF_ZIP_URL, zip_path):
        print("📦 Распаковываю...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(DOCUMENTS_FOLDER)
            zip_path.unlink()
            print("✅ Анимации установлены в:", ANIMATIONS_FOLDER)
            return True
        except Exception as e:
            print(f"❌ Ошибка распаковки: {e}")
            return False
    return False

def download_main_script():
    """Скачивает основной скрипт программы"""
    script_path = DOCUMENTS_FOLDER / "fruitywidget.py"
    if download_file(MAIN_SCRIPT_URL, script_path):
        return script_path
    return None

def run_widget():
    """Запускает виджет"""
    script_path = DOCUMENTS_FOLDER / "fruitywidget.py"
    if script_path.exists():
        print("\n🚀 Запускаю FruityWidget...")
        subprocess.Popen([sys.executable, str(script_path)])
    else:
        print("❌ Основной скрипт не найден!")

def main():
    print("🎵 FruityWidget — Установка и запуск")
    print("="*50)
    
    # Создаем папки
    DOCUMENTS_FOLDER.mkdir(parents=True, exist_ok=True)
    ANIMATIONS_FOLDER.mkdir(exist_ok=True)
    
    # Проверяем, есть ли уже анимации
    has_gifs = any(ANIMATIONS_FOLDER.glob("*.gif"))
    
    if not has_gifs:
        print("\n📦 Устанавливаю анимации...")
        install_animations()
    else:
        print("\n✅ Анимации уже установлены!")
    
    # Скачиваем основной скрипт, если его нет
    script_path = DOCUMENTS_FOLDER / "fruitywidget.py"
    if not script_path.exists():
        print("\n📥 Скачиваю основной скрипт...")
        download_main_script()
    
    # Запускаем виджет
    run_widget()
    
    print("\n" + "="*50)
    print("🎯 Виджет запущен! Наслаждайся!")
    print("📂 Все файлы в:", DOCUMENTS_FOLDER)
    print("🔄 Чтобы перезапустить, просто запусти этот файл снова.")
    print("="*50)

if __name__ == "__main__":
    main()
    input("\nНажми Enter, чтобы закрыть это окно...")
