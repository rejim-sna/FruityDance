import subprocess
import sys
import os

def install_package(package):
    """Устанавливает пакет через pip"""
    print(f"📦 Устанавливаю: {package}")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", package
        ])
        print(f"✅ {package} установлен!")
        return True
    except Exception as e:
        print(f"❌ Ошибка установки {package}: {e}")
        return False

def install_all():
    """Устанавливает все необходимые библиотеки"""
    print("🎵 FruityWidget — Установка зависимостей")
    print("="*50)
    
    # Список необходимых библиотек
    packages = [
        "pygame",
        "pyaudio",
        "numpy",
        "pillow"
    ]
    
    print("\n📋 Будет установлено:")
    for pkg in packages:
        print(f"  - {pkg}")
    print()
    
    success = True
    for package in packages:
        if not install_package(package):
            success = False
    
    print("\n" + "="*50)
    if success:
        print("✅ Все зависимости установлены успешно!")
        print("🚀 Теперь можно запускать FruityWidget!")
    else:
        print("⚠️ Некоторые пакеты не установились.")
        print("   Попробуй установить их вручную:")
        print("   pip install pygame pyaudio numpy pillow")
    print("="*50)

if __name__ == "__main__":
    install_all()
    input("\nНажми Enter, чтобы закрыть...")
