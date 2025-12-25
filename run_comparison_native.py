import os
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from gym_environment import IEEE123Env
from simulation_core import SimulationCore
import config # <--- Added config

# --- НАСТРОЙКИ ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "trained_models")
CHECKPOINT_DIR = os.path.join(MODEL_DIR, "checkpoints")

TEST_DAY = 200      # Жаркий день
LOAD_SCALE = 2.0    # 🔥 200% нагрузки (Кризис!)

def find_latest_checkpoint():
    if not os.path.exists(CHECKPOINT_DIR): return None
    files = [f for f in os.listdir(CHECKPOINT_DIR) if f.endswith(".zip")]
    if not files: return None
    latest = max(files, key=lambda x: int(x.split('_')[2]))
    return os.path.join(CHECKPOINT_DIR, latest)

def run_native_opendss():
    """Прогон с РОДНОЙ автоматикой OpenDSS (без Python-управления)."""
    print(config.tr("Run Native", TEST_DAY, LOAD_SCALE*100))
    
    sim = SimulationCore()
    # Сброс (он ставит ControlMode=OFF)
    sim.reset(day_of_year=TEST_DAY, load_scale=LOAD_SCALE)
    
    # !!! ВАЖНО: Включаем встроенные мозги OpenDSS !!!
    # ControlMode=TIME заставляет OpenDSS самому управлять регуляторами
    # в зависимости от настроек в .dss файлах
    sim.text.Command = "Set ControlMode=TIME" 
    sim.text.Command = "Set MaxControlIter=100" # Разрешаем много переключений за шаг
    
    voltages = []
    taps = []
    
    # Список регуляторов для мониторинга
    reg_names = sim.get_regulator_list()
    
    for _ in range(96):
        # Просто решаем схему. OpenDSS сам поменяет тапы, если нужно.
        sim.solution.Solve()
        
        # Собираем данные
        raw = sim.get_state()
        v_step = [raw['voltages'][node] for node in sim.sensor_nodes]
        t_step = [raw['taps'][r] for r in reg_names]
        
        voltages.append(v_step)
        taps.append(t_step)
        
    return np.array(voltages), np.array(taps), reg_names

def run_ai_agent(model_path):
    """Прогон с НЕЙРОСЕТЬЮ (ControlMode=OFF)."""
    print(config.tr("Run AI Agent", TEST_DAY, LOAD_SCALE*100))
    
    env = IEEE123Env()
    obs, _ = env.reset(seed=42)
    # Настраиваем тот же день и нагрузку
    env.sim.reset(day_of_year=TEST_DAY, load_scale=LOAD_SCALE)
    
    # Загружаем модель
    model = PPO.load(model_path)
    
    voltages = []
    taps = []
    
    for _ in range(96):
        action, _ = model.predict(obs, deterministic=True)
        obs, _, _, _, _ = env.step(action)
        
        raw = env.sim.get_state()
        v_step = [raw['voltages'][node] for node in env.sim.sensor_nodes]
        t_step = [raw['taps'][r] for r in env.reg_names]
        
        voltages.append(v_step)
        taps.append(t_step)
        
    return np.array(voltages), np.array(taps)

def main():
    # 1. Ищем модель
    model_path = find_latest_checkpoint()
    if not model_path:
        print(config.tr("Model Not Found"))
        return
    print(config.tr("Loading Model", os.path.basename(model_path)))
    
    # 2. Запускаем Native OpenDSS
    v_nat, t_nat, reg_names = run_native_opendss()
    
    # 3. Запускаем AI
    v_ai, t_ai = run_ai_agent(model_path)
    
    # 4. Сравниваем графики
    print(config.tr("Plotting Battle"))
    time_ax = np.arange(96) * 0.25
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12), sharex=True)
    
    # --- ГРАФИК 1: Напряжения ---
    # Native = Красный
    ax1.plot(time_ax, v_nat, color='red', alpha=0.15, linewidth=1)
    # AI = Синий
    ax1.plot(time_ax, v_ai, color='blue', alpha=0.15, linewidth=1)
    
    # Коридор
    ax1.axhline(0.95, color='black', linestyle='--', linewidth=2)
    ax1.axhline(1.05, color='black', linestyle='--', linewidth=2)
    
    # Легенда
    ax1.plot([], [], color='red', label=config.tr("Label Native"))
    ax1.plot([], [], color='blue', label=config.tr("Label AI Agent"))
    
    ax1.set_title(config.tr("Comparison Quality Title", LOAD_SCALE*100), fontsize=14)
    ax1.set_ylabel(config.tr("Voltage Axis"))
    ax1.legend(loc='lower left', fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # --- ГРАФИК 2: Работа регуляторов ---
    # Чтобы не делать кашу, покажем только один регулятор (например, самый первый - creg1a)
    # или сумму переключений. Давайте покажем creg1a и creg4a (начало и конец).
    
    target_regs = ['creg1a', 'creg4c'] # Главный и удаленный
    indices = [i for i, name in enumerate(reg_names) if name in target_regs]
    
    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color']
    
    for i, idx in enumerate(indices):
        r_name = reg_names[idx]
        # Native - пунктир
        ax2.step(time_ax, t_nat[:, idx], where='post', linestyle='--', color=colors[i], label=f"{r_name} (Native)")
        # AI - сплошная
        ax2.step(time_ax, t_ai[:, idx], where='post', linestyle='-', color=colors[i], linewidth=2, label=f"{r_name} (AI)")
        
    ax2.set_title(config.tr("Strategy Title"), fontsize=12)
    ax2.set_ylabel(config.tr("Tap Position"))
    ax2.set_xlabel(config.tr("Time Hours"))
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()