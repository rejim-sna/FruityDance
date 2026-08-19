import os
import urllib.request
import zipfile
import subprocess
import sys
from pathlib import Path

# ============ НАСТРОЙКИ ============
DOCUMENTS_FOLDER = Path(os.path.expanduser("~/Documents/FruityWidget"))
ANIMATIONS_FOLDER = DOCUMENTS_FOLDER / "Animations"
CONFIG_FOLDER = DOCUMENTS_FOLDER / "Config"

GIF_ZIP_URL = "https://github.com/rejim-sna/FruityDance/raw/main/animations.zip"
MAIN_SCRIPT_URL = "https://raw.githubusercontent.com/rejim-sna/FruityDance/main/fruitywidget.py"

def download_file(url, dest):
    print(f"📥 Скачиваю: {url}")
    try:
        urllib.request.urlretrieve(url, dest)
        print("✅ Готово!")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def install():
    print("🎵 FruityWidget — Установка")
    print("="*50)
    
    DOCUMENTS_FOLDER.mkdir(parents=True, exist_ok=True)
    ANIMATIONS_FOLDER.mkdir(exist_ok=True)
    CONFIG_FOLDER.mkdir(exist_ok=True)
    print("📁 Папки созданы")
    
    zip_path = DOCUMENTS_FOLDER / "animations.zip"
    if download_file(GIF_ZIP_URL, zip_path):
        print("📦 Распаковываю...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(DOCUMENTS_FOLDER)
        zip_path.unlink()
        print("✅ Анимации установлены!")
    
    script_path = DOCUMENTS_FOLDER / "fruitywidget.py"
    if download_file(MAIN_SCRIPT_URL, script_path):
        print("✅ Основной скрипт установлен!")
    
    print("\n" + "="*50)
    print("✅ Установка завершена!")
    print(f"📂 Папка: {DOCUMENTS_FOLDER}")
    print("🚀 Запускаю FruityWidget...")
    print("="*50)
    
    if script_path.exists():
        subprocess.Popen([sys.executable, str(script_path)])

if __name__ == "__main__":
    install()
    input("\nНажми Enter, чтобы закрыть...")
