import sys
import os

# Добавляем текущую директорию в путь, чтобы импорты работали корректно
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from plot_topology import plot_interactive_topology
from localization import translate as tr

def main():
    print("=== OpenDSS IEEE 123 Simulation Launcher ===")
    print(tr("launching_interactive_topology"))
    print(tr("click_on_nodes"))
    
    try:
        plot_interactive_topology()
    except Exception as e:
        print(tr("critical_error", e=e))
        input(tr("press_enter_to_exit"))

if __name__ == "__main__":
    main()
