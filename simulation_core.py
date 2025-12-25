import dss
import pathlib
import numpy as np
import time

class SimulationCore:
    def __init__(self, sensors_file='sensors.json'):
        self.dss = dss.DSS
        self.text = self.dss.Text
        self.circuit = self.dss.ActiveCircuit
        self.solution = self.circuit.Solution
        
        # Пути к файлам
        self.current_dir = pathlib.Path(__file__).parent.resolve()
        self.master_file = self.current_dir / "qsts" / "master.dss"
        
        # Список регуляторов (наши "руки" для нейросети)
        self.regulator_names = []
        # Список сенсоров (наши "глаза")
        self.sensor_nodes = self._load_sensors(sensors_file)
        
        # Состояние симуляции
        self.current_step = 0
        self.max_steps = 96  # 24 часа * 4 (15 мин)
        self.base_voltages = {} # Кэш базовых напряжений

    def _load_sensors(self, filename):
        """Загружает список узлов для мониторинга."""
        import json
        try:
            path = self.current_dir / filename
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠ Ошибка загрузки сенсоров {filename}: {e}. Используем пустой список.")
            return []

    def reset(self, day_of_year=1, pv_enabled=True, temperature=25.0, load_scale=1.0):
        """
        Сброс среды в начальное состояние (00:00).
        Подготовка схемы, профилей и погоды.
        """
        # 1. Компиляция схемы
        self.text.Command = f'Compile "{self.master_file}"'
        
        # 2. Настройка PV и погоды
        if pv_enabled:
            self.text.Command = "New XYCurve.PvTempEff npts=4 xarray=[-10 25 50 75] yarray=[1.20 1.0 0.80 0.60]"
            self.text.Command = f"New Tshape.TempOverride npts=1 interval=1 temp=[{temperature}]"
            
            # Применяем температурный профиль ко всем PV
            pvs = self.circuit.PVSystems
            idx = pvs.First
            while idx > 0:
                self.circuit.ActiveCktElement.Enabled = True
                name = pvs.Name
                self.text.Command = f"Edit PVSystem.{name} TYearly=TempOverride P-TCurve=PvTempEff temperature={temperature}"
                idx = pvs.Next
        else:
            # Отключаем PV если нужно
            pvs = self.circuit.PVSystems
            idx = pvs.First
            while idx > 0:
                self.circuit.ActiveCktElement.Enabled = False
                idx = pvs.Next

        # 3. Масштабирование нагрузки (для создания стресс-тестов)
        if load_scale != 1.0:
            self.text.Command = f"Set LoadMult={load_scale}"

        # 4. Инициализация времени
        start_hour = (int(day_of_year) - 1) * 24
        self.text.Command = f"Set Mode=Yearly StepSize=15m Hour={start_hour} Number=1"
        self.text.Command = "Set ControlMode=OFF" # Мы сами будем управлять регуляторами!

        # 5. Кэширование списка регуляторов (если схема изменилась)
        self.regulator_names = self.circuit.RegControls.AllNames

        # 6. Расчет начального состояния (без шага времени, просто Snapshot для инициализации)
        self.solution.SolveNoControl()
        self.current_step = 0
        
        return self.get_state()

    def step(self, action_dict):
        """
        Выполняет один шаг симуляции (15 минут).
        
        Args:
            action_dict (dict): Словарь { 'RegulatorName': direction }, 
                                где direction = +1 (up), -1 (down), 0 (none)
        Returns:
            observation (dict): Текущие измерения
            done (bool): Конец ли суток
        """
        # 1. Применяем действия Агента
        for reg_name, direction in action_dict.items():
            if direction == 0: continue
            
            # Устанавливаем активный регулятор
            self.circuit.RegControls.Name = reg_name
            
            # Получаем текущий тап
            current_tap = self.circuit.RegControls.TapNumber
            new_tap = current_tap + direction
            
            # Физические ограничения (-16..+16)
            if -16 <= new_tap <= 16:
                self.circuit.RegControls.TapNumber = new_tap

        # 2. Шаг физики (Power Flow)
        self.solution.Solve()
        
        self.current_step += 1
        done = (self.current_step >= self.max_steps)
        
        return self.get_state(), done

    def get_state(self):
        """
        Собирает 'сырые' данные для нейросети.
        Возвращает:
            - Напряжения на сенсорах (p.u.)
            - Общую мощность сети
            - Положения регуляторов
        """
        state = {}
        
        # А. Напряжения (Sensor Voltages)
        # Оптимизация: читаем весь вектор один раз, потом фильтруем
        # (В Python перебор всех узлов медленный, но в DSS доступ быстрый)
        # Для скорости лучше заранее закешировать индексы узлов, но пока сделаем надежно:
        
        voltage_map = {}
        # Получаем напряжения
        for node in self.sensor_nodes:
            self.circuit.SetActiveBus(node)
            # Берем среднее напряжение по фазам узла (упрощение для вектора состояния)
            v_mag = self.circuit.ActiveBus.VMagAngle
            if len(v_mag) >= 2:
                # VMagAngle возвращает [v1, a1, v2, a2...], берем только v
                voltages = v_mag[0::2] 
                kv_base = self.circuit.ActiveBus.kVBase * 1000
                if kv_base > 0:
                    v_pu = np.mean(voltages) / kv_base
                    voltage_map[node] = v_pu
                else:
                    voltage_map[node] = 1.0 # Fallback
            else:
                voltage_map[node] = 0.0

        state['voltages'] = voltage_map

        # Б. Общая мощность (Total Power)
        try:
            # Берем модуль активной мощности (P)
            p_total_kw = abs(self.circuit.TotalPower[0])
            state['total_power_kw'] = p_total_kw
            state['total_loss_kw'] = self.circuit.Losses[0] / 1000.0
        except:
            state['total_power_kw'] = 0.0
            state['total_loss_kw'] = 0.0

        # В. Состояние регуляторов (Tap positions)
        tap_state = {}
        regs = self.circuit.RegControls
        idx = regs.First
        while idx > 0:
            tap_state[regs.Name] = regs.TapNumber
            idx = regs.Next
        state['taps'] = tap_state

        return state

    def get_regulator_list(self):
        """Возвращает список доступных для управления регуляторов."""
        return self.circuit.RegControls.AllNames

# --- Блок тестирования производительности ---
if __name__ == "__main__":
    print("🚀 Запуск теста производительности ядра симуляции...")
    
    sim = SimulationCore()
    # Тестовый прогон: 10 дней
    days_to_simulate = 10
    total_steps = 96 * days_to_simulate
    
    start_time = time.time()
    
    print(f"⏳ Симуляция {days_to_simulate} суток ({total_steps} шагов)...")
    
    for day in range(1, days_to_simulate + 1):
        # Сброс дня
        obs = sim.reset(day_of_year=day, load_scale=1.1) # +10% перегрузки для теста
        
        # Получаем список регуляторов
        regs = sim.get_regulator_list()
        
        done = False
        while not done:
            # Эмуляция "глупого" агента: случайные действия
            # Шанс 10% переключить тап
            actions = {}
            for r in regs:
                if np.random.rand() < 0.1:
                    actions[r] = np.random.choice([-1, 1])
                else:
                    actions[r] = 0
            
            obs, done = sim.step(actions)
            
            # Просто чтение данных (проверка, что не падает)
            p_curr = obs['total_power_kw']
    
    end_time = time.time()
    duration = end_time - start_time
    fps = total_steps / duration
    
    print(f"✅ Готово!")
    print(f"⏱ Время выполнения: {duration:.4f} сек")
    print(f"⚡ Скорость: {fps:.1f} шагов/сек (Steps Per Second)")
    print(f"ℹ️ Это значит, что 1 год обучения (35k шагов) займет ~{35040/fps/60:.1f} минут.")