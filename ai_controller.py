import os
import numpy as np
from stable_baselines3 import PPO
import config

class AIController:
    def __init__(self, circuit):
        self.circuit = circuit
        self.model = self._load_model()

        # Получаем список регуляторов и сенсоров, чтобы формировать observation
        # Внимание: для формирования obs нам нужны те же данные, что и в IEEE123Env
        # Проблема: у нас нет экземпляра IEEE123Env здесь.
        # Решение: дублируем логику получения sensor_nodes и reg_names

        # Инициализация списка регуляторов
        self.reg_names = self.circuit.RegControls.AllNames

        # Загрузка сенсоров (нужен путь к sensors.json)
        # Предполагаем, что controller.py лежит в корне, sensors.json тоже
        import json
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            sensors_path = os.path.join(current_dir, 'sensors.json')
            with open(sensors_path, 'r') as f:
                self.sensor_nodes = json.load(f)
        except:
            self.sensor_nodes = []

        self.obs_dim = len(self.sensor_nodes) + len(self.reg_names) + 1 + 2 # V + Taps + Power + Time(2)

    def _load_model(self):
        # Логика поиска модели аналогична run_trained_model.py
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        MODEL_DIR = os.path.join(BASE_DIR, "trained_models")
        CHECKPOINT_DIR = os.path.join(MODEL_DIR, "checkpoints")

        # 1. Checkpoints
        model_path = None
        if os.path.exists(CHECKPOINT_DIR):
            files = [f for f in os.listdir(CHECKPOINT_DIR) if f.endswith(".zip")]
            if files:
                def get_step(name):
                    parts = name.split('_')
                    for p in parts:
                        if p.isdigit(): return int(p)
                    return 0
                latest = max(files, key=get_step)
                model_path = os.path.join(CHECKPOINT_DIR, latest)

        # 2. Final model
        if not model_path:
            final_path = os.path.join(MODEL_DIR, "ppo_ieee123_final.zip")
            if os.path.exists(final_path):
                model_path = final_path

        if model_path:
            print(config.tr("Loading Model", os.path.basename(model_path)))
            return PPO.load(model_path)
        else:
            print(config.tr("Model Not Found"))
            return None

    def check_and_act(self, step_number, max_steps=96):
        """
        Выполняет шаг управления с помощью ИИ.
        """
        if not self.model:
            return [], False

        # 1. Сформировать Observation (вектор состояния)
        obs = self._get_observation(step_number, max_steps)

        # 2. Получить действие от модели
        action_indices, _ = self.model.predict(obs, deterministic=True)

        # 3. Применить действие
        action_map = {0: 0, 1: 1, 2: -1}
        actions_log = []
        action_occurred = False

        for i, reg_name in enumerate(self.reg_names):
            act_idx = action_indices[i]
            direction = action_map[act_idx]

            if direction != 0:
                self.circuit.RegControls.Name = reg_name
                current_tap = self.circuit.RegControls.TapNumber
                new_tap = current_tap + direction

                if -16 <= new_tap <= 16:
                    self.circuit.RegControls.TapNumber = new_tap
                    actions_log.append(f"{reg_name}: {current_tap} -> {new_tap}")
                    action_occurred = True

        if action_occurred:
            return [config.tr("AI Action Log", step_number, ", ".join(actions_log))], True
        return [], False

    def _get_observation(self, current_step, max_steps):
        """
        Собирает вектор состояния, идентичный тому, что был при обучении (gym_environment.py).
        """
        obs = []

        # А. Напряжения
        # Получаем напряжения (p.u.) для сенсоров
        # Внимание: здесь нужно аккуратно повторить логику SimulationCore.get_state()
        # Но у нас есть доступ к self.circuit

        # Чтобы не дублировать код чтения напряжений, используем упрощенный подход,
        # но он должен совпадать с обучением.
        # В GymEnv: (v_pu - 1.0) * 10.0

        for node in self.sensor_nodes:
            self.circuit.SetActiveBus(node)
            v_mag = self.circuit.ActiveBus.VMagAngle
            if len(v_mag) >= 2:
                voltages = v_mag[0::2]
                kv_base = self.circuit.ActiveBus.kVBase * 1000
                if kv_base > 0:
                    v_pu = np.mean(voltages) / kv_base
                else:
                    v_pu = 1.0
            else:
                v_pu = 0.0

            obs.append((v_pu - 1.0) * 10.0)

        # Б. Тапы: / 16.0
        for reg in self.reg_names:
            self.circuit.RegControls.Name = reg
            tap = self.circuit.RegControls.TapNumber
            obs.append(tap / 16.0)

        # В. Мощность: / 5000.0
        try:
            p_total = abs(self.circuit.TotalPower[0])
        except:
            p_total = 0.0
        obs.append(p_total / 5000.0)

        # Г. Время
        step_angle = 2 * np.pi * (current_step / max_steps)
        obs.append(np.sin(step_angle))
        obs.append(np.cos(step_angle))

        return np.array(obs, dtype=np.float32)
