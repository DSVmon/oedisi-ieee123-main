from gym_environment import IEEE123Env
import numpy as np

env = IEEE123Env()
obs, _ = env.reset()

print("Проверка среды:")
print(f"1. Размер наблюдения: {obs.shape}")
print(f"2. Пример наблюдения (первые 5): {obs[:5]}")
print(f"3. Размерность действий: {env.action_space}")

# Делаем случайный шаг
action = env.action_space.sample()
obs, reward, done, _, info = env.step(action)

print(f"4. Награда за шаг: {reward:.4f}")
print(f"5. Инфо: {info}")
print("✅ Тест пройден!")