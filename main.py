import sys
import os

# Добавляем текущую директорию в путь, чтобы импорты работали корректно
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from plot_topology import plot_interactive_topology

def main():
    print("=== OpenDSS IEEE 123 Simulation Launcher ===")
    print("1. Запуск интерактивной топологии...")
    print("2. Кликайте на узлы на графике для расчета режимов.")
    
    try:
        plot_interactive_topology()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        input("Нажмите Enter, чтобы выйти...")

if __name__ == "__main__":
    main()