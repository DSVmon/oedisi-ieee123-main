import os
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from gym_environment import IEEE123Env

# --- НАСТРОЙКИ ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "trained_models")
CHECKPOINT_DIR = os.path.join(MODEL_DIR, "checkpoints")

# Выбери модель для теста:
# Вариант А: Последний чекпоинт (используй это, пока обучение еще идет!)
# Скрипт сам найдет самый свежий файл в папке checkpoints
TRY_LATEST_CHECKPOINT = True 

# Вариант Б: Финальная модель (если обучение уже закончилось)
FINAL_MODEL_NAME = "ppo_ieee123_final.zip"

def find_latest_checkpoint():
    if not os.path.exists(CHECKPOINT_DIR): return None
    files = [f for f in os.listdir(CHECKPOINT_DIR) if f.endswith(".zip")]
    if not files: return None
    # Сортируем по номеру шага (ppo_ieee123_20000_steps.zip)
    # Извлекаем число из имени файла
    def get_step(name):
        parts = name.split('_')
        for p in parts:
            if p.isdigit(): return int(p)
        return 0
    
    latest_file = max(files, key=get_step)
    return os.path.join(CHECKPOINT_DIR, latest_file)

def main():
    print("🔎 Поиск модели...")
    model_path = None
    
    if TRY_LATEST_CHECKPOINT:
        model_path = find_latest_checkpoint()
        if model_path:
            print(f"✅ Найден свежий чекпоинт: {os.path.basename(model_path)}")
    
    if not model_path:
        final_path = os.path.join(MODEL_DIR, FINAL_MODEL_NAME)
        if os.path.exists(final_path):
            model_path = final_path
            print(f"✅ Найдена финальная модель: {FINAL_MODEL_NAME}")
    
    if not model_path:
        print("❌ Модели не найдены! Сначала запусти обучение (train_agent.py).")
        return

    print("🚀 Загрузка среды и агента...")
    # Создаем среду БЕЗ монитора логов (нам тут графики не нужны)
    env = IEEE123Env(pv_enabled=True)
    
    # Загружаем нейросеть
    model = PPO.load(model_path)
    
    # --- СЦЕНАРИЙ ТЕСТА ---
    # Берем фиксированный сложный день (например, лето, жара)
    # Чтобы сравнить честно, сбросим среду принудительно
    obs, _ = env.reset(seed=42) 
    env.day = 200 # 200-й день года (Июль)
    env.sim.reset(day_of_year=200, load_scale=1.0)
    
    print(f"📅 Тестируем день: {env.day} (Лето)")
    
    # Хранилища данных для графиков
    history = {
        'voltages': [], # [step] -> [v1, v2, ...]
        'taps': [],     # [step] -> [tap1, tap2, ...]
        'power': [],    # [step] -> kw
        'rewards': []
    }
    
    # Список имен узлов для подписи легенды (берем первые 5 для чистоты графика)
    sensor_names = env.sim.sensor_nodes[:5] 
    
    print("▶ Запуск симуляции (96 шагов)...")
    
    for step in range(96):
        # 1. Спрашиваем нейросеть
        action, _ = model.predict(obs, deterministic=True)
        
        # 2. Делаем шаг
        obs, reward, done, _, info = env.step(action)
        
        # 3. Сохраняем "сырые" физические данные из симулятора
        raw_state = env.sim.get_state()
        
        # Напряжения (всех сенсоров)
        v_vals = [raw_state['voltages'][node] for node in env.sim.sensor_nodes]
        history['voltages'].append(v_vals)
        
        # Тапы (всех регуляторов)
        t_vals = [raw_state['taps'][reg] for reg in env.reg_names]
        history['taps'].append(t_vals)
        
        # Мощность
        history['power'].append(raw_state['total_power_kw'])
        history['rewards'].append(reward)

    print("✅ Симуляция завершена. Строим графики...")
    
    # --- ОТРИСОВКА ---
    time_axis = np.arange(96) * 0.25 # Часы
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 14), sharex=True)
    plt.subplots_adjust(hspace=0.3)
    
    # 1. График напряжений
    voltages_np = np.array(history['voltages']) # Shape: (96, N_sensors)
    
    # Рисуем все напряжения серым фоном
    ax1.plot(time_axis, voltages_np, color='gray', alpha=0.1)
    # Выделяем несколько цветных линий
    for i, node_name in enumerate(sensor_names):
        ax1.plot(time_axis, voltages_np[:, i], label=f"Узел {node_name}")
        
    # Коридор нормы
    ax1.axhline(0.95, color='red', linestyle='--', linewidth=2, label='Min (0.95)')
    ax1.axhline(1.05, color='red', linestyle='--', linewidth=2, label='Max (1.05)')
    ax1.axhline(1.00, color='green', linestyle=':', alpha=0.5)
    
    ax1.set_title("Напряжения в сети (Управление AI)", fontsize=12, fontweight='bold')
    ax1.set_ylabel("Напряжение (p.u.)")
    ax1.legend(loc='upper right', ncol=3, fontsize='small')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0.90, 1.10)
    
    # 2. График переключений (Тапы)
    taps_np = np.array(history['taps'])
    for i, reg_name in enumerate(env.reg_names):
        ax2.step(time_axis, taps_np[:, i], where='post', label=reg_name, linewidth=1.5)
        
    ax2.set_title("Работа регуляторов", fontsize=12, fontweight='bold')
    ax2.set_ylabel("Положение отпайки (Tap)")
    ax2.legend(loc='upper right', fontsize='small', ncol=2)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(-17, 17)
    
    # 3. График мощности и награды
    color = 'tab:blue'
    ax3.set_xlabel("Время (часы)")
    ax3.set_ylabel("Активная мощность (кВт)", color=color)
    ax3.plot(time_axis, history['power'], color=color, linewidth=2)
    ax3.tick_params(axis='y', labelcolor=color)
    ax3.grid(True, alpha=0.3)
    
    # Вторая ось для награды
    ax3_r = ax3.twinx()
    color = 'tab:purple'
    ax3_r.set_ylabel("Награда агента", color=color)
    ax3_r.plot(time_axis, history['rewards'], color=color, linestyle='--', alpha=0.6)
    ax3_r.tick_params(axis='y', labelcolor=color)
    ax3.set_title("Потребление и оценка качества", fontsize=12, fontweight='bold')

    print("📊 График открыт.")
    plt.show()

if __name__ == "__main__":
    main()