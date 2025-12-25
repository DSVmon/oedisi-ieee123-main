import os
import time
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback, CheckpointCallback
from stable_baselines3.common.monitor import Monitor
import config

# Импортируем нашу среду
from gym_environment import IEEE123Env

# --- НАСТРОЙКИ ПУТЕЙ ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "training_logs")
MODEL_DIR = os.path.join(BASE_DIR, "trained_models")
CHECKPOINT_DIR = os.path.join(MODEL_DIR, "checkpoints") # Папка для промежуточных сохранений

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

TIMESTEPS = 100_000

class TensorboardCallback(BaseCallback):
    def __init__(self, verbose=0):
        super(TensorboardCallback, self).__init__(verbose)

    def _on_step(self) -> bool:
        infos = self.locals.get("infos", [{}])[0]
        if "power_kw" in infos:
            self.logger.record("custom/power_kw", infos["power_kw"])
        if "switches" in infos:
            self.logger.record("custom/switches", infos["switches"])
        return True

def main():
    print(config.tr("Init Training"))
    print(config.tr("Logs Dir", LOG_DIR))
    print(config.tr("Checkpoints Dir", CHECKPOINT_DIR))

    def make_env():
        env = IEEE123Env()
        log_file = os.path.join(LOG_DIR, "monitor") 
        env = Monitor(env, log_file) 
        return env

    env = DummyVecEnv([make_env])

    model = PPO(
        "MlpPolicy", 
        env, 
        verbose=1, 
        tensorboard_log=LOG_DIR,
        learning_rate=0.0003,
        n_steps=2048,
        batch_size=64,
        gamma=0.99
    )

    print(config.tr("Start Training", TIMESTEPS))
    start_time = time.time()

    # --- СОЗДАЕМ ЧЕКПОИНТ-КОЛЛБЕК ---
    # Сохраняем модель каждые 10 000 шагов
    checkpoint_callback = CheckpointCallback(
        save_freq=10000, 
        save_path=CHECKPOINT_DIR,
        name_prefix="ppo_ieee123"
    )

    # Передаем список коллбеков (наш логгер + чекпоинтер)
    model.learn(
        total_timesteps=TIMESTEPS, 
        callback=[TensorboardCallback(), checkpoint_callback],
        progress_bar=True,
        tb_log_name="PPO_run"
    )

    end_time = time.time()
    print(config.tr("Training Done", (end_time - start_time)/60))

    # Финальное сохранение
    final_path = os.path.join(MODEL_DIR, "ppo_ieee123_final")
    model.save(final_path)
    print(config.tr("Final Model Saved", final_path))

if __name__ == "__main__":
    main()