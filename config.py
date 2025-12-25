LANGUAGE = 'RU'  # Options: 'RU', 'EN'

# Translation dictionary
TRANSLATIONS = {
    # --- Main Menu (main.py) ---
    "Main Title": {
        "RU": "=== OpenDSS IEEE 123 Запуск Симуляции ===",
        "EN": "=== OpenDSS IEEE 123 Simulation Launcher ==="
    },
    "Menu 1": {
        "RU": "1. Запуск интерактивной топологии...",
        "EN": "1. Launch interactive topology..."
    },
    "Menu 2": {
        "RU": "2. Кликайте на узлы на графике для расчета режимов.",
        "EN": "2. Click nodes on the plot to calculate regimes."
    },
    "Critical Error": {
        "RU": "Критическая ошибка: {}",
        "EN": "Critical Error: {}"
    },
    "Press Enter": {
        "RU": "Нажмите Enter, чтобы выйти...",
        "EN": "Press Enter to exit..."
    },

    # --- Simulation Core (simulation_core.py) ---
    "Sensor Load Error": {
        "RU": "⚠ Ошибка загрузки сенсоров {}: {}. Используем пустой список.",
        "EN": "⚠ Error loading sensors {}: {}. Using empty list."
    },
    "Perf Test Start": {
        "RU": "🚀 Запуск теста производительности ядра симуляции...",
        "EN": "🚀 Starting simulation core performance test..."
    },
    "Simulating Days": {
        "RU": "⏳ Симуляция {} суток ({} шагов)...",
        "EN": "⏳ Simulating {} days ({} steps)..."
    },
    "Done": {
        "RU": "✅ Готово!",
        "EN": "✅ Done!"
    },
    "Execution Time": {
        "RU": "⏱ Время выполнения: {:.4f} сек",
        "EN": "⏱ Execution time: {:.4f} sec"
    },
    "Speed": {
        "RU": "⚡ Скорость: {:.1f} шагов/сек (Steps Per Second)",
        "EN": "⚡ Speed: {:.1f} steps/sec (Steps Per Second)"
    },
    "Training Time Est": {
        "RU": "ℹ️ Это значит, что 1 год обучения (35k шагов) займет ~{:.1f} минут.",
        "EN": "ℹ️ This means 1 year of training (35k steps) will take ~{:.1f} minutes."
    },

    # --- Plot Topology (plot_topology.py) ---
    "Tree Built": {
        "RU": "Дерево построено. Охвачено узлов: {}",
        "EN": "Tree built. Nodes covered: {}"
    },
    "Loading Circuit": {
        "RU": "Загрузка схемы из: {}",
        "EN": "Loading circuit from: {}"
    },
    "Error No Buscoords": {
        "RU": "Ошибка: Нет файла координат",
        "EN": "Error: No buscoords file"
    },
    "Finding PV": {
        "RU": "Поиск солнечных панелей... Найдено: {}",
        "EN": "Searching for PV panels... Found: {}"
    },
    "Plot Title": {
        "RU": "Карта IEEE 123: Тренажер и Анализ",
        "EN": "IEEE 123 Map: Simulator and Analysis"
    },
    "3 Phases": {
        "RU": "3 Фазы",
        "EN": "3 Phases"
    },
    "2 Phases": {
        "RU": "2 Фазы",
        "EN": "2 Phases"
    },
    "1 Phase": {
        "RU": "1 Фаза",
        "EN": "1 Phase"
    },
    "Legend Load": {
        "RU": "Нагрузка",
        "EN": "Load"
    },
    "Legend Regulator": {
        "RU": "Регулятор",
        "EN": "Regulator"
    },
    "Legend PV": {
        "RU": "Солнечная панель",
        "EN": "Solar Panel"
    },
    "Legend Node": {
        "RU": "Узел",
        "EN": "Node"
    },
    "Source": {
        "RU": "Источник",
        "EN": "Source"
    },
    "Normal Mode": {
        "RU": "Нормальный режим",
        "EN": "Normal Mode"
    },
    "Short Circuit": {
        "RU": "Короткое замыкание",
        "EN": "Short Circuit"
    },
    "Open Line": {
        "RU": "Обрыв линии",
        "EN": "Open Line"
    },
    "Op Mode": {
        "RU": "РЕЖИМ РАБОТЫ:",
        "EN": "OPERATION MODE:"
    },
    "Phase 1": {
        "RU": "Фаза 1",
        "EN": "Phase 1"
    },
    "Phase 2": {
        "RU": "Фаза 2",
        "EN": "Phase 2"
    },
    "Phase 3": {
        "RU": "Фаза 3",
        "EN": "Phase 3"
    },
    "Phase Selection": {
        "RU": "ВЫБОР ФАЗ:",
        "EN": "PHASE SELECTION:"
    },
    "Enable PV": {
        "RU": "Включить Солнечные Панели",
        "EN": "Enable Solar Panels"
    },
    "Reset": {
        "RU": "Сброс",
        "EN": "Reset"
    },
    "Analyze V": {
        "RU": "Анализ V",
        "EN": "Analyze V"
    },
    "Load Slider": {
        "RU": "Нагрузка TestNode (кВт)",
        "EN": "TestNode Load (kW)"
    },
    "Day Slider": {
        "RU": "День года",
        "EN": "Day of Year"
    },
    "Temp Slider": {
        "RU": "Температура (°C)",
        "EN": "Temperature (°C)"
    },
    "January 1": {
        "RU": "1 Января",
        "EN": "January 1"
    },
    "Months": {
        "RU": ["", "Января", "Февраля", "Марта", "Апреля", "Мая", "Июня", "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"],
        "EN": ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    },
    "Base Type Phase": {
        "RU": "(Фазное)",
        "EN": "(Phase)"
    },
    "Base Type LinearToPhase": {
        "RU": "(Линейное -> привели к Фазному)",
        "EN": "(Linear -> converted to Phase)"
    },
    "Warning No Phase": {
        "RU": "⚠ Внимание: Не выбрана ни одна фаза!",
        "EN": "⚠ Warning: No phase selected!"
    },
    "System Ready": {
        "RU": "Система готова.\n- ЛКМ: Инспекция узла (без изменений)\n- ПКМ: Активное управление (изменяет регуляторы)\n- Кнопка 'Анализ V' покажет зоны перенапряжения/просадки.",
        "EN": "System ready.\n- LMB: Node inspection (no changes)\n- RMB: Active control (modifies regulators)\n- 'Analyze V' button shows over/under voltage zones."
    },

    # --- Gym Environment (gym_environment.py) ---
    "Env Init": {
        "RU": "🤖 Среда инициализирована. Управляемых регуляторов: {}",
        "EN": "🤖 Environment initialized. Controlled regulators: {}"
    },
    "Warning No Sensors": {
        "RU": "⚠ ВНИМАНИЕ: Нет сенсоров в sensors.json! Нейросеть будет слепой.",
        "EN": "⚠ WARNING: No sensors in sensors.json! Neural network will be blind."
    },

    # --- Train Agent (train_agent.py) ---
    "Init Training": {
        "RU": "🚀 Инициализация процесса обучения...",
        "EN": "🚀 Initializing training process..."
    },
    "Logs Dir": {
        "RU": "📂 Логи: {}",
        "EN": "📂 Logs: {}"
    },
    "Checkpoints Dir": {
        "RU": "💾 Чекпоинты: {}",
        "EN": "💾 Checkpoints: {}"
    },
    "Start Training": {
        "RU": "🧠 Старт обучения на {} шагов...",
        "EN": "🧠 Starting training for {} steps..."
    },
    "Training Done": {
        "RU": "✅ Обучение завершено за {:.1f} минут.",
        "EN": "✅ Training completed in {:.1f} minutes."
    },
    "Final Model Saved": {
        "RU": "💾 Финальная модель сохранена: {}.zip",
        "EN": "💾 Final model saved: {}.zip"
    },

    # --- Run Comparison / Native / Trained Model ---
    "Run Scenario": {
        "RU": "▶ Запуск сценария: {} (Нагрузка {}%)",
        "EN": "▶ Running scenario: {} (Load {}%)"
    },
    "Model Not Found Train First": {
        "RU": "❌ Модель не найдена. Сначала обучи агента.",
        "EN": "❌ Model not found. Train the agent first."
    },
    "Model Not Found": {
        "RU": "❌ Модель не найдена.",
        "EN": "❌ Model not found."
    },
    "Loading Model": {
        "RU": "✅ Загружаем модель: {}",
        "EN": "✅ Loading model: {}"
    },
    "Phase 1 No AI": {
        "RU": "\n--- ЭТАП 1: Работа без AI (Baseline) ---",
        "EN": "\n--- STAGE 1: No AI (Baseline) ---"
    },
    "Phase 2 AI": {
        "RU": "\n--- ЭТАП 2: Работа с AI ---",
        "EN": "\n--- STAGE 2: With AI ---"
    },
    "Plotting Comparison": {
        "RU": "\n📊 Строим графики сравнения...",
        "EN": "\n📊 Plotting comparison..."
    },
    "Plotting Battle": {
        "RU": "\n📊 Строим Битву Титанов (OpenDSS vs AI)...",
        "EN": "\n📊 Plotting Clash of Titans (OpenDSS vs AI)..."
    },
    "Norm Range": {
        "RU": "Норма (0.95-1.05)",
        "EN": "Norm (0.95-1.05)"
    },
    "Label No AI": {
        "RU": "Без AI (Baseline)",
        "EN": "No AI (Baseline)"
    },
    "Label With AI": {
        "RU": "C AI (Agent)",
        "EN": "With AI (Agent)"
    },
    "Comparison Title": {
        "RU": "Сравнение стабильности (День {}, Нагрузка {}%)",
        "EN": "Stability Comparison (Day {}, Load {}%)"
    },
    "Voltage Axis": {
        "RU": "Напряжение (p.u.)",
        "EN": "Voltage (p.u.)"
    },
    "Actions Title": {
        "RU": "Действия нейросети (Тапы)",
        "EN": "Neural Network Actions (Taps)"
    },
    "Tap Position": {
        "RU": "Положение",
        "EN": "Position"
    },
    "Time Hours": {
        "RU": "Время (часы)",
        "EN": "Time (hours)"
    },
    "Run Native": {
        "RU": "▶ Запуск Native OpenDSS (Day {}, Load {}%)",
        "EN": "▶ Running Native OpenDSS (Day {}, Load {}%)"
    },
    "Run AI Agent": {
        "RU": "▶ Запуск AI Agent (Day {}, Load {}%)",
        "EN": "▶ Running AI Agent (Day {}, Load {}%)"
    },
    "Label Native": {
        "RU": "Native OpenDSS (Классика)",
        "EN": "Native OpenDSS (Classic)"
    },
    "Label AI Agent": {
        "RU": "AI Agent (Нейросеть)",
        "EN": "AI Agent (Neural Net)"
    },
    "Comparison Quality Title": {
        "RU": "Сравнение качества: Стандартная автоматика vs AI (Load {}%)",
        "EN": "Quality Comparison: Standard Automation vs AI (Load {}%)"
    },
    "Strategy Title": {
        "RU": "Стратегия переключений (Пример на 2 регуляторах)",
        "EN": "Switching Strategy (Example on 2 regulators)"
    },
    "Search Model": {
        "RU": "🔎 Поиск модели...",
        "EN": "🔎 Searching for model..."
    },
    "Found Checkpoint": {
        "RU": "✅ Найден свежий чекпоинт: {}",
        "EN": "✅ Found fresh checkpoint: {}"
    },
    "Found Final": {
        "RU": "✅ Найдена финальная модель: {}",
        "EN": "✅ Found final model: {}"
    },
    "Error No Model": {
        "RU": "❌ Модели не найдены! Сначала запусти обучение (train_agent.py).",
        "EN": "❌ No models found! Run training first (train_agent.py)."
    },
    "Loading Env Agent": {
        "RU": "🚀 Загрузка среды и агента...",
        "EN": "🚀 Loading environment and agent..."
    },
    "Testing Day": {
        "RU": "📅 Тестируем день: {} (Лето)",
        "EN": "📅 Testing day: {} (Summer)"
    },
    "Run Sim 96": {
        "RU": "▶ Запуск симуляции (96 шагов)...",
        "EN": "▶ Starting simulation (96 steps)..."
    },
    "Sim Done Plotting": {
        "RU": "✅ Симуляция завершена. Строим графики...",
        "EN": "✅ Simulation complete. Plotting..."
    },
    "Voltage Network AI": {
        "RU": "Напряжения в сети (Управление AI)",
        "EN": "Network Voltages (AI Control)"
    },
    "Regulator Work": {
        "RU": "Работа регуляторов",
        "EN": "Regulator Operation"
    },
    "Tap Position Full": {
        "RU": "Положение отпайки (Tap)",
        "EN": "Tap Position"
    },
    "Active Power kW": {
        "RU": "Активная мощность (кВт)",
        "EN": "Active Power (kW)"
    },
    "Agent Reward": {
        "RU": "Награда агента",
        "EN": "Agent Reward"
    },
    "Consumption Quality": {
        "RU": "Потребление и оценка качества",
        "EN": "Consumption and Quality Assessment"
    },
    "Plot Opened": {
        "RU": "📊 График открыт.",
        "EN": "📊 Plot opened."
    },

    # --- run_qsts_plot.py ---
    "Clear Memory": {
        "RU": "🧹 Память регуляторов очищена.",
        "EN": "🧹 Regulator memory cleared."
    },
    "Controller Node": {
        "RU": "🎮 Контроллер для узла {}.",
        "EN": "🎮 Controller for node {}."
    },
    "Chain Help": {
        "RU": "⛓ Цепочка помощи: {} (Всего: {})",
        "EN": "⛓ Aid chain: {} (Total: {})"
    },
    "Warn No Regs": {
        "RU": "⚠ На пути к этому узлу нет регуляторов!",
        "EN": "⚠ No regulators on the path to this node!"
    },
    "Step Low V": {
        "RU": "Шаг {} [LOW V={:.3f}]: {}",
        "EN": "Step {} [LOW V={:.3f}]: {}"
    },
    "Step High V": {
        "RU": "Шаг {} [HIGH V={:.3f}]: {}",
        "EN": "Step {} [HIGH V={:.3f}]: {}"
    },
    "Reg Tap Change": {
        "RU": "Регулятор {}: Tap {} -> {}",
        "EN": "Regulator {}: Tap {} -> {}"
    },
    "Reg Limit": {
        "RU": "Регулятор {}: Достигнут предел ({})!",
        "EN": "Regulator {}: Limit reached ({})!"
    },
    "Load Connected": {
        "RU": "🔥 ВНИМАНИЕ: Подключена экспериментальная нагрузка {} кВт на TestNode!",
        "EN": "🔥 WARNING: Experimental load {} kW connected to TestNode!"
    },
    "Apply Reg Settings": {
        "RU": "\n🔧 [АНАЛИЗ] Применяем настройки регуляторов из памяти:",
        "EN": "\n🔧 [ANALYSIS] Applying regulator settings from memory:"
    },
    "Reg Set To": {
        "RU": "   -> {} установлен на Tap {}",
        "EN": "   -> {} set to Tap {}"
    },
    "No Settings": {
        "RU": "\nℹ️ [АНАЛИЗ] Нет сохраненных настроек. Используем исходные.",
        "EN": "\nℹ️ [ANALYSIS] No saved settings. Using defaults."
    },
    "Scan Net": {
        "RU": "\n--- СКАНИРОВАНИЕ СЕТИ (ControlMode=OFF) ---",
        "EN": "\n--- NETWORK SCAN (ControlMode=OFF) ---"
    },
    "Table Header": {
        "RU": "{:<10} | {:<15} | ЗНАЧЕНИЕ (p.u.)",
        "EN": "{:<10} | {:<15} | VALUE (p.u.)"
    },
    "Column Node": {
        "RU": "УЗЕЛ",
        "EN": "NODE"
    },
    "Column Status": {
        "RU": "СТАТУС",
        "EN": "STATUS"
    },
    "Total Power Peak": {
        "RU": "⚡ Общая активная мощность в сети (пик): {:.2f} кВт",
        "EN": "⚡ Total active network power (peak): {:.2f} kW"
    },
    "Under Voltage": {
        "RU": "{:<10} | ПРОСАДКА      | {:.4f}",
        "EN": "{:<10} | UNDER VOLTAGE | {:.4f}"
    },
    "Over Voltage": {
        "RU": "{:<10} | ПЕРЕНАПРЯЖЕНИЕ | {:.4f}",
        "EN": "{:<10} | OVER VOLTAGE   | {:.4f}"
    },
    "No Violations": {
        "RU": "✅ Нарушений не обнаружено.",
        "EN": "✅ No violations detected."
    },
    "Restoring State": {
        "RU": "\n📥 [СТАРТ] Восстанавливаем состояние регуляторов из памяти:",
        "EN": "\n📥 [START] Restoring regulator state from memory:"
    },
    "Inspect Node": {
        "RU": "🧐 ИНСПЕКЦИЯ УЗЛА {}",
        "EN": "🧐 INSPECTING NODE {}"
    },
    "ConsGen": {
        "RU": "🔌 Потребители/Генераторы (PCE): {}",
        "EN": "🔌 Consumers/Generators (PCE): {}"
    },
    "LinesTrans": {
        "RU": "⚡ Линии/Трансформаторы  (PDE): {}",
        "EN": "⚡ Lines/Transformers (PDE): {}"
    },
    "Warn Load 0": {
        "RU": "⚠ ВНИМАНИЕ: На узле есть нагрузка, хотя слайдер на 0! Проверьте файлы .dss",
        "EN": "⚠ WARNING: Node has load even though slider is 0! Check .dss files"
    },
    "Current Reg State": {
        "RU": "\n🏁 [ТЕКУЩЕЕ СОСТОЯНИЕ] Положения регуляторов:",
        "EN": "\n🏁 [CURRENT STATE] Regulator positions:"
    },
    "Monitor Mode": {
        "RU": "\n👁️ [РЕЖИМ МОНИТОРИНГА] Управление регуляторами ОТКЛЮЧЕНО.",
        "EN": "\n👁️ [MONITOR MODE] Regulator control DISABLED."
    },
    "Sim Monitor": {
        "RU": "   Симуляция пройдет с текущими (восстановленными) настройками.",
        "EN": "   Simulation will run with current (restored) settings."
    },
    "Error No Monitor": {
        "RU": "❌ Ошибка: Не к чему подключить монитор для {}",
        "EN": "❌ Error: Nothing to connect monitor to for {}"
    },
    "Start Sim Node": {
        "RU": "\n🚀 Запуск симуляции (Узел {})...",
        "EN": "\n🚀 Starting simulation (Node {})..."
    },
    "Final Reg State": {
        "RU": "\n🏁 [КОНЕЦ] Итоговые положения регуляторов (сохранено в память):",
        "EN": "\n🏁 [END] Final regulator positions (saved to memory):"
    },
    "Info No Change": {
        "RU": "\nℹ️ [ИНФО] Состояние регуляторов не изменялось и не сохранялось.",
        "EN": "\nℹ️ [INFO] Regulator state was not changed or saved."
    },
    "Node Summary": {
        "RU": " СВОДКА ПО УЗЛУ: {}",
        "EN": " NODE SUMMARY: {}"
    },
    "Params Phases": {
        "RU": "Параметры:      {} фаз(ы)",
        "EN": "Parameters:     {} phase(s)"
    },
    "Base DSS": {
        "RU": "База OpenDSS:   {} кВ {}",
        "EN": "OpenDSS Base:   {} kV {}"
    },
    "Base PU": {
        "RU": "База для p.u.:  {:.1f} В (Фазная)",
        "EN": "Base for p.u.:  {:.1f} V (Phase)"
    },
    "Daily Stats": {
        "RU": "СТАТИСТИКА ЗА СУТКИ:",
        "EN": "DAILY STATISTICS:"
    },
    "Phase Log": {
        "RU": "> Фаза {}:",
        "EN": "> Phase {}:"
    },
    "Min U": {
        "RU": "  Min U: {:.1f} В ({:.3f} p.u.) @ {} {}",
        "EN": "  Min U: {:.1f} V ({:.3f} p.u.) @ {} {}"
    },
    "Max U": {
        "RU": "  Max U: {:.1f} В ({:.3f} p.u.) @ {} {}",
        "EN": "  Max U: {:.1f} V ({:.3f} p.u.) @ {} {}"
    },
    "Warning Under": {
        "RU": "[⚠️ ПРОСАДКА]",
        "EN": "[⚠️ UNDER VOLTAGE]"
    },
    "Warning Over": {
        "RU": "[⚠️ ПЕРЕНАПРЯЖЕНИЕ]",
        "EN": "[⚠️ OVER VOLTAGE]"
    },
    "Peak Load": {
        "RU": "Пиковая нагр.: {:.2f} кВт",
        "EN": "Peak Load:     {:.2f} kW"
    },
    "Max Current": {
        "RU": "Макс. ток:     {:.2f} А",
        "EN": "Max Current:   {:.2f} A"
    },
    "Total P Net": {
        "RU": "Общ. P (сеть): {:.2f} кВт",
        "EN": "Total P (Net): {:.2f} kW"
    },
    "PV On": {
        "RU": "[PV ВКЛ, {}°C]",
        "EN": "[PV ON, {}°C]"
    },
    "PV Off": {
        "RU": "[PV ВЫКЛ]",
        "EN": "[PV OFF]"
    },
    "Load Info": {
        "RU": " (+{} кВт TestNode)",
        "EN": " (+{} kW TestNode)"
    },
    "Active Control Mode": {
        "RU": "(Активное Управление)",
        "EN": "(Active Control)"
    },
    "Monitor Mode Plot": {
        "RU": "(Мониторинг / Без управления)",
        "EN": "(Monitor / No Control)"
    },
    "Node Plot Title": {
        "RU": "Узел {}: {} {}\n{}",
        "EN": "Node {}: {} {}\n{}"
    },
    "Regulating": {
        "RU": "Регулирование",
        "EN": "Regulation"
    },
    "Voltage V": {
        "RU": "Напряжение (В)",
        "EN": "Voltage (V)"
    },
    "Current A": {
        "RU": "Ток (А)",
        "EN": "Current (A)"
    },
    "Power kW": {
        "RU": "Мощность (кВт)",
        "EN": "Power (kW)"
    },
    "Plot Error": {
        "RU": "Ошибка графика: {}",
        "EN": "Plot Error: {}"
    },
    "Solution Diverged": {
        "RU": "❌ Решение не сошлось.",
        "EN": "❌ Solution diverged."
    },
    "Reason Low": {
        "RU": "Просадка (min {:.3f})",
        "EN": "Under Voltage (min {:.3f})"
    },
    "Reason High": {
        "RU": "Перенапряжение (max {:.3f})",
        "EN": "Over Voltage (max {:.3f})"
    },
    "Step Log": {
        "RU": "⏱ Шаг {}: {} -> 🎯 {} (Tap {}->{})",
        "EN": "⏱ Step {}: {} -> 🎯 {} (Tap {}->{})"
    },
    "Limit Log": {
        "RU": "⚠ Шаг {}: {} НА ПРЕДЕЛЕ ({}). Передаю управление выше...",
        "EN": "⚠ Step {}: {} LIMIT REACHED ({}). Passing control up..."
    },

    # --- Controller (controller.py) ---
    "Controller Step Low": {
        "RU": "Шаг {} [LOW V={:.3f}]: {}",
        "EN": "Step {} [LOW V={:.3f}]: {}"
    },
    "Controller Step High": {
        "RU": "Шаг {} [HIGH V={:.3f}]: {}",
        "EN": "Step {} [HIGH V={:.3f}]: {}"
    },
    "Controller Tap Change": {
        "RU": "Регулятор {}: Tap {} -> {}",
        "EN": "Regulator {}: Tap {} -> {}"
    },
    "Controller Limit": {
        "RU": "Регулятор {}: Достигнут предел ({})!",
        "EN": "Regulator {}: Limit reached ({})!"
    },

    # --- Test Env (test_env.py) ---
    "Test Env Start": {
        "RU": "Проверка среды:",
        "EN": "Environment Check:"
    },
    "Test Obs Size": {
        "RU": "1. Размер наблюдения: {}",
        "EN": "1. Observation size: {}"
    },
    "Test Obs Ex": {
        "RU": "2. Пример наблюдения (первые 5): {}",
        "EN": "2. Observation example (first 5): {}"
    },
    "Test Action Dim": {
        "RU": "3. Размерность действий: {}",
        "EN": "3. Action dimensions: {}"
    },
    "Test Reward": {
        "RU": "4. Награда за шаг: {:.4f}",
        "EN": "4. Step reward: {:.4f}"
    },
    "Test Info": {
        "RU": "5. Инфо: {}",
        "EN": "5. Info: {}"
    },
    "Test Passed": {
        "RU": "✅ Тест пройден!",
        "EN": "✅ Test passed!"
    }
}

def tr(key, *args):
    """
    Translates the text associated with 'key' based on the LANGUAGE setting.
    If *args are provided, they are formatted into the string.
    If key is not found, returns the key itself.
    """
    if key not in TRANSLATIONS:
        # Fallback: if key looks like a format string, return it as is
        return key

    text_template = TRANSLATIONS[key].get(LANGUAGE, TRANSLATIONS[key]['RU'])

    if args:
        try:
            return text_template.format(*args)
        except Exception:
            return text_template
    return text_template

# Legacy helper for direct EN/RU strings (if strictly needed, but dict is better)
def tr_direct(en_text, ru_text):
    if LANGUAGE == 'EN':
        return en_text
    return ru_text
