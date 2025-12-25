import gymnasium as gym
import numpy as np
from gymnasium import spaces

# Импортируем наше ядро (убедись, что файл называется simulation_core.py)
from simulation_core import SimulationCore

class IEEE123Env(gym.Env):
    """
    Среда Gymnasium для управления напряжением в сети IEEE 123.
    """
    metadata = {'render_modes': ['console']}

    def __init__(self, pv_enabled=True):
        super(IEEE123Env, self).__init__()
        
        # 1. Инициализация симулятора
        self.sim = SimulationCore()
        
        # Получаем список регуляторов, чтобы знать размерность действий
        # (Запускаем холостой сброс, чтобы подгрузить схему)
        self.sim.reset() 
        self.reg_names = self.sim.get_regulator_list()
        self.n_regulators = len(self.reg_names)
        
        print(f"🤖 Среда инициализирована. Управляемых регуляторов: {self.n_regulators}")
        print(f"   {self.reg_names}")

        # 2. Пространство действий (Action Space)
        # Для каждого регулятора 3 варианта: 0=Ничего, 1=Вверх, 2=Вниз
        # Используем MultiDiscrete: [3, 3, 3, ...]
        self.action_space = spaces.MultiDiscrete([3] * self.n_regulators)

        # 3. Пространство наблюдений (Observation Space)
        # Вектор: [Напряжения (N штук) | Положения тапов (N штук) | Общая нагрузка (1) | Время (2)]
        self.n_sensors = len(self.sim.sensor_nodes)
        if self.n_sensors == 0:
            print("⚠ ВНИМАНИЕ: Нет сенсоров в sensors.json! Нейросеть будет слепой.")
        
        # Размер вектора состояния
        # V (N_sens) + Taps (N_reg) + Power (1) + Time (2: sin/cos)
        self.obs_dim = self.n_sensors + self.n_regulators + 1 + 2
        
        # Границы (примерные, для нормализации)
        self.observation_space = spaces.Box(
            low=-2.0, high=2.0, shape=(self.obs_dim,), dtype=np.float32
        )
        
        # Параметры симуляции
        self.pv_enabled = pv_enabled
        self.day = 1

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # Выбираем случайный день или по порядку (для разнообразия при обучении)
        self.day = np.random.randint(1, 365) 
        # Добавляем случайности в нагрузку (+/- 20%)
        load_scale = np.random.uniform(0.8, 1.2)
        
        raw_state = self.sim.reset(
            day_of_year=self.day, 
            pv_enabled=self.pv_enabled,
            load_scale=load_scale
        )
        
        observation = self._process_observation(raw_state)
        return observation, {}

    def step(self, action):
        """
        Основной шаг: Агент дает действие -> Среда возвращает (state, reward, done)
        """
        # 1. Преобразование действий Gym -> SimulationCore
        # Gym выдает [0, 2, 1...], а Core ждет {name: +1/-1/0}
        # Маппинг: 0 -> 0 (Stay), 1 -> +1 (Up), 2 -> -1 (Down)
        action_map = {0: 0, 1: 1, 2: -1}
        
        core_actions = {}
        switch_count = 0
        
        for i, reg_name in enumerate(self.reg_names):
            act_idx = action[i]
            val = action_map[act_idx]
            core_actions[reg_name] = val
            if val != 0:
                switch_count += 1

        # 2. Шаг симуляции
        raw_state, done = self.sim.step(core_actions)
        
        # 3. Обработка наблюдения
        observation = self._process_observation(raw_state)
        
        # 4. Расчет награды (Самое важное!)
        reward = self._calculate_reward(raw_state, switch_count)
        
        # 5. Доп. информация
        info = {
            'day': self.day,
            'power_kw': raw_state['total_power_kw'],
            'switches': switch_count
        }
        
        return observation, reward, done, False, info

    def _process_observation(self, raw_state):
        """Нормализация данных для нейросети."""
        obs = []
        
        # А. Напряжения: центрируем вокруг 1.0 p.u. (чтобы 1.0 стало 0.0)
        # Умножаем на 10, чтобы отклонение 0.05 стало 0.5 (заметнее для сети)
        v_dict = raw_state['voltages']
        for node in self.sim.sensor_nodes:
            v_pu = v_dict.get(node, 1.0)
            obs.append((v_pu - 1.0) * 10.0)
            
        # Б. Тапы: нормализуем -16..16 в -1..1
        t_dict = raw_state['taps']
        for reg in self.reg_names:
            t_val = t_dict.get(reg, 0)
            obs.append(t_val / 16.0)
            
        # В. Мощность: нормализуем (допустим макс 5000 кВт)
        p_val = raw_state['total_power_kw']
        obs.append(p_val / 5000.0)
        
        # Г. Время (цикличность)
        # Шаг 0..96 -> Угол 0..2pi
        step_angle = 2 * np.pi * (self.sim.current_step / self.sim.max_steps)
        obs.append(np.sin(step_angle))
        obs.append(np.cos(step_angle))
        
        return np.array(obs, dtype=np.float32)

    def _calculate_reward(self, raw_state, switch_count):
        """Формула успеха."""
        reward = 0.0
        
        # 1. Штраф за напряжение (Voltage Penalty)
        # Идем по всем сенсорам
        violations = 0
        total_deviation = 0.0
        
        for v in raw_state['voltages'].values():
            # Отклонение от идеала 1.0
            dev = abs(v - 1.0)
            total_deviation += dev
            
            # Жесткий штраф за выход за границы 0.95 - 1.05
            if v < 0.95 or v > 1.05:
                violations += 1
                reward -= 2.0 # Сильный удар по рукам
        
        # Мягкий штраф за любое отклонение (чтобы стремился к 1.0)
        reward -= total_deviation * 0.5
        
        # 2. Штраф за переключения (Switching Penalty)
        # Чтобы не дергал регулятор туда-сюда без нужды
        if switch_count > 0:
            reward -= 0.1 * switch_count
            
        return reward