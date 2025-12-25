import sys
import os
import config  # <--- Added config

# Добавляем текущую директорию в путь, чтобы импорты работали корректно
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from plot_topology import plot_interactive_topology

def main():
    print(config.tr("Main Title"))
    print(config.tr("Menu 1"))
    print(config.tr("Menu 2"))
    
    try:
        plot_interactive_topology()
    except Exception as e:
        print(config.tr("Critical Error", e))
        input(config.tr("Press Enter"))

if __name__ == "__main__":
    main()