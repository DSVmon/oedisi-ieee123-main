# localization.py
from config import LANGUAGE

translations = {
    'ru': {
        # main.py
        "launching_interactive_topology": "1. Запуск интерактивной топологии...",
        "click_on_nodes": "2. Кликайте на узлы на графике для расчета режимов.",
        "critical_error": "Критическая ошибка: {e}",
        "press_enter_to_exit": "Нажмите Enter, чтобы выйти...",

        # plot_topology.py
        "tree_built": "Дерево построено. Охвачено узлов: {count}",
        "loading_circuit": "Загрузка схемы из: {file}",
        "no_coordinates_file": "Ошибка: Нет файла координат",
        "searching_pv": "Поиск солнечных панелей... Найдено: {count}",
        "map_title": "Карта IEEE 123: Тренажер и Анализ",
        'phases_3': '3 Фазы',
        'phases_2': '2 Фазы',
        'phase_1': '1 Фаза',
        'load': 'Нагрузка',
        'regulator': 'Регулятор',
        'pv_panel': 'Солнечная панель',
        'node': 'Узел',
        'source': 'Источник',
        'normal_mode': 'Нормальный режим',
        'short_circuit': 'Короткое замыкание',
        'open_line': 'Обрыв линии',
        "operation_mode": "РЕЖИМ РАБОТЫ:",
        'phase_1_select': 'Фаза 1',
        'phase_2_select': 'Фаза 2',
        'phase_3_select': 'Фаза 3',
        "phase_selection": "ВЫБОР ФАЗ:",
        'enable_pv': 'Включить Солнечные Панели',
        'reset': 'Сброс',
        'analyze_v': 'Анализ V',
        'testnode_load': 'Нагрузка TestNode (кВт)',
        'day_of_year': 'День года',
        'temperature': 'Температура (°C)',
        "january_1": "1 Января",
        "no_phase_selected": "⚠ Внимание: Не выбрана ни одна фаза!",
        "system_ready_prompt": "Система готова.\n- ЛКМ: Инспекция узла (без изменений)\n- ПКМ: Активное управление (изменяет регуляторы)\n- Кнопка 'Анализ V' покажет зоны перенапряжения/просадки.",

        # simulation_core.py
        "error_loading_sensors": "⚠ Ошибка загрузки сенсоров {filename}: {e}. Используем пустой список.",
        "start_perf_test": "🚀 Запуск теста производительности ядра симуляции...",
        "simulating_days": "⏳ Симуляция {days} суток ({steps} шагов)...",
        "done": "✅ Готово!",
        "execution_time": "⏱ Время выполнения: {duration:.4f} сек",
        "speed": "⚡ Скорость: {fps:.1f} шагов/сек (Steps Per Second)",
        "training_time_estimate": "ℹ️ Это значит, что 1 год обучения (35k шагов) займет ~{minutes:.1f} минут.",

        # gym_environment.py
        "env_initialized": "🤖 Среда инициализирована. Управляемых регуляторов: {count}",
        "no_sensors_warning": "⚠ ВНИМАНИЕ: Нет сенсоров в sensors.json! Нейросеть будет слепой.",

        # controller.py
        "step_low_v": "Шаг {step} [LOW V={v:.3f}]: {msg}",
        "step_high_v": "Шаг {step} [HIGH V={v:.3f}]: {msg}",
        "regulator_tap_change": "Регулятор {name}: Tap {current} -> {new}",
        "regulator_limit_reached": "Регулятор {name}: Достигнут предел ({tap})!",

        # test_env.py
        "checking_environment": "Проверка среды:",
        "observation_size": "Размер наблюдения: {shape}",
        "observation_example": "Пример наблюдения (первые 5): {example}",
        "action_space_size": "Размерность действий: {action_space}",
        "reward_for_step": "Награда за шаг: {reward:.4f}",
        "info": "Инфо: {info}",
        "test_passed": "✅ Тест пройден!",
    },
    'en': {
        # main.py
        "launching_interactive_topology": "1. Launching interactive topology...",
        "click_on_nodes": "2. Click on nodes on the graph to calculate modes.",
        "critical_error": "Critical error: {e}",
        "press_enter_to_exit": "Press Enter to exit...",

        # plot_topology.py
        "tree_built": "Tree built. Nodes covered: {count}",
        "loading_circuit": "Loading circuit from: {file}",
        "no_coordinates_file": "Error: No coordinates file",
        "searching_pv": "Searching for PV panels... Found: {count}",
        "map_title": "IEEE 123 Map: Simulator & Analysis",
        'phases_3': '3 Phases',
        'phases_2': '2 Phases',
        'phase_1': '1 Phase',
        'load': 'Load',
        'regulator': 'Regulator',
        'pv_panel': 'PV Panel',
        'node': 'Node',
        'source': 'Source',
        'normal_mode': 'Normal Mode',
        'short_circuit': 'Short Circuit',
        'open_line': 'Open Line',
        "operation_mode": "OPERATION MODE:",
        'phase_1_select': 'Phase 1',
        'phase_2_select': 'Phase 2',
        'phase_3_select': 'Phase 3',
        "phase_selection": "PHASE SELECTION:",
        'enable_pv': 'Enable PV Panels',
        'reset': 'Reset',
        'analyze_v': 'Analyze V',
        'testnode_load': 'TestNode Load (kW)',
        'day_of_year': 'Day of Year',
        'temperature': 'Temperature (°C)',
        "january_1": "January 1",
        "no_phase_selected": "⚠ Warning: No phase selected!",
        "system_ready_prompt": "System ready...\n- Left Click: Inspect node\n- Right Click: Active control\n- 'Analyze V' button: Show voltage violations.",

        # simulation_core.py
        "error_loading_sensors": "⚠ Error loading sensors {filename}: {e}. Using an empty list.",
        "start_perf_test": "🚀 Starting simulation core performance test...",
        "simulating_days": "⏳ Simulating {days} days ({steps} steps)...",
        "done": "✅ Done!",
        "execution_time": "⏱ Execution time: {duration:.4f} sec",
        "speed": "⚡ Speed: {fps:.1f} steps/sec (Steps Per Second)",
        "training_time_estimate": "ℹ️ This means that 1 year of training (35k steps) will take ~{minutes:.1f} minutes.",

        # gym_environment.py
        "env_initialized": "🤖 Environment initialized. Controllable regulators: {count}",
        "no_sensors_warning": "⚠ WARNING: No sensors in sensors.json! The neural network will be blind.",

        # controller.py
        "step_low_v": "Step {step} [LOW V={v:.3f}]: {msg}",
        "step_high_v": "Step {step} [HIGH V={v:.3f}]: {msg}",
        "regulator_tap_change": "Regulator {name}: Tap {current} -> {new}",
        "regulator_limit_reached": "Regulator {name}: Limit reached ({tap})!",

        # test_env.py
        "checking_environment": "Checking environment:",
        "observation_size": "Observation size: {shape}",
        "observation_example": "Observation example (first 5): {example}",
        "action_space_size": "Action space size: {action_space}",
        "reward_for_step": "Reward for step: {reward:.4f}",
        "info": "Info: {info}",
        "test_passed": "✅ Test passed!",
    }
}


def translate(key, **kwargs):
    lang = LANGUAGE.lower()
    if lang in translations and key in translations[lang]:
        return translations[lang][key].format(**kwargs)
    # Fallback to English if the key is not found in the target language
    if 'en' in translations and key in translations['en']:
        return translations['en'][key].format(**kwargs)
    return key # return key as is if not found anywhere
