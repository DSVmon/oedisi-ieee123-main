from gym_environment import IEEE123Env
import numpy as np
from config import tr

env = IEEE123Env()
obs, _ = env.reset()

print(tr("Checking the environment:", "Проверка среды:"))
print(tr(f"1. Observation size: {obs.shape}", f"1. Размер наблюдения: {obs.shape}"))
print(tr(f"2. Observation example (first 5): {obs[:5]}", f"2. Пример наблюдения (первые 5): {obs[:5]}"))
print(tr(f"3. Action space: {env.action_space}", f"3. Размерность действий: {env.action_space}"))

# Делаем случайный шаг
action = env.action_space.sample()
obs, reward, done, _, info = env.step(action)

print(tr(f"4. Reward per step: {reward:.4f}", f"4. Награда за шаг: {reward:.4f}"))
print(tr(f"5. Info: {info}", f"5. Инфо: {info}"))
print(tr("✅ Test passed!", "✅ Тест пройден!"))