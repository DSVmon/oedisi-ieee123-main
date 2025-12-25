import os
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from gym_environment import IEEE123Env

# --- НАСТРОЙКИ ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "trained_models")
CHECKPOINT_DIR = os.path.join(MODEL_DIR, "checkpoints")

# Выбираем день и нагрузку для краш-теста
TEST_DAY = 200      # Жаркий летний день
LOAD_SCALE = 1.5    # 🔥 150% нагрузки на всю сеть!

def find_latest_checkpoint():
    if not os.path.exists(CHECKPOINT_DIR): return None
    files = [f for f in os.listdir(CHECKPOINT_DIR) if f.endswith(".zip")]
    if not files: return None
    latest = max(files, key=lambda x: int(x.split('_')[2]))
    return os.path.join(CHECKPOINT_DIR, latest)

def run_episode(env, model=None, label=""):
    """Прогоняет один день. Если model=None, то без управления."""
    print(f"▶ Запуск сценария: {label} (Нагрузка {LOAD_SCALE*100}%)")
    
    # Сброс с фиксированной перегрузкой
    obs, _ = env.reset(seed=42)
    env.sim.reset(day_of_year=TEST_DAY, load_scale=LOAD_SCALE)
    
    voltages = []
    taps = []
    
    for step in range(96):
        if model:
            # Спрашиваем нейросеть
            action, _ = model.predict(obs, deterministic=True)
        else:
            # БЕЗ ДЕЙСТВИЙ (Имитация старой глупой сети)
            # 0 = "Ничего не менять" для всех регуляторов
            action = np.zeros(env.n_regulators, dtype=int) 
            
        obs, reward, done, _, info = env.step(action)
        
        # Сохраняем данные
        raw = env.sim.get_state()
        v_step = [raw['voltages'][node] for node in env.sim.sensor_nodes]
        voltages.append(v_step)
        taps.append([raw['taps'][r] for r in env.reg_names])
        
    return np.array(voltages), np.array(taps)

def main():
    # 1. Ищем модель
    model_path = find_latest_checkpoint()
    if not model_path:
        print("❌ Модель не найдена. Сначала обучи агента.")
        return
    print(f"✅ Загружаем модель: {os.path.basename(model_path)}")
    model = PPO.load(model_path)
    
    env = IEEE123Env()
    
    # 2. Прогон БЕЗ НЕЙРОСЕТИ (Baseline)
    print("\n--- ЭТАП 1: Работа без AI (Baseline) ---")
    v_base, t_base = run_episode(env, model=None, label="Без AI")
    
    # 3. Прогон С НЕЙРОСЕТЬЮ (AI Agent)
    print("\n--- ЭТАП 2: Работа с AI ---")
    v_ai, t_ai = run_episode(env, model=model, label="С AI")
    
    # 4. Визуализация: Было vs Стало
    print("\n📊 Строим графики сравнения...")
    time_ax = np.arange(96) * 0.25
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # ГРАФИК НАПРЯЖЕНИЙ
    # Рисуем "облако" напряжений для Baseline (красным полупрозрачным)
    ax1.plot(time_ax, v_base, color='red', alpha=0.1, linewidth=1)
    # Рисуем "облако" для AI (синим полупрозрачным)
    ax1.plot(time_ax, v_ai, color='blue', alpha=0.1, linewidth=1)
    
    # Линии коридора
    ax1.axhline(0.95, color='black', linestyle='--', linewidth=2, label='Норма (0.95-1.05)')
    ax1.axhline(1.05, color='black', linestyle='--', linewidth=2)
    
    # Фейковые линии для легенды
    ax1.plot([], [], color='red', alpha=0.5, label='Без AI (Baseline)')
    ax1.plot([], [], color='blue', alpha=0.5, label='C AI (Agent)')
    
    ax1.set_title(f"Сравнение стабильности (День {TEST_DAY}, Нагрузка {LOAD_SCALE*100}%)", fontsize=14)
    ax1.set_ylabel("Напряжение (p.u.)")
    ax1.legend(loc='lower left')
    ax1.grid(True, alpha=0.3)
    
    # ГРАФИК ПЕРЕКЛЮЧЕНИЙ (только для AI, т.к. baseline стоит на месте)
    for i, name in enumerate(env.reg_names):
        ax2.step(time_ax, t_ai[:, i], where='post', label=name)
        
    ax2.set_title("Действия нейросети (Тапы)", fontsize=12)
    ax2.set_ylabel("Положение")
    ax2.set_xlabel("Время (часы)")
    ax2.legend(loc='upper right', ncol=3, fontsize='small')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()