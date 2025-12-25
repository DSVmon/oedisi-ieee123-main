import sys
import os

# Добавляем текущую директорию в путь, чтобы импорты работали корректно
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from plot_topology import plot_interactive_topology
from config import tr

def main():
    print(tr("=== OpenDSS IEEE 123 Simulation Launcher ===", "=== Запуск Симулятора OpenDSS IEEE 123 ==="))
    print(tr("1. Launching interactive topology...", "1. Запуск интерактивной топологии..."))
    print(tr("2. Click on nodes on the graph to calculate modes.", "2. Кликайте на узлы на графике для расчета режимов."))
    
    try:
        plot_interactive_topology()
    except Exception as e:
        print(f"{tr('Critical error', 'Критическая ошибка')}: {e}")
        input(tr("Press Enter to exit...", "Нажмите Enter, чтобы выйти..."))

if __name__ == "__main__":
    main()