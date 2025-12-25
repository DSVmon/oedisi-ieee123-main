from gym_environment import IEEE123Env
import numpy as np
import config # <--- Added config

env = IEEE123Env()
obs, _ = env.reset()

print(config.tr("Test Env Start"))
print(config.tr("Test Obs Size", obs.shape))
print(config.tr("Test Obs Ex", obs[:5]))
print(config.tr("Test Action Dim", env.action_space))

# Делаем случайный шаг
action = env.action_space.sample()
obs, reward, done, _, info = env.step(action)

print(config.tr("Test Reward", reward))
print(config.tr("Test Info", info))
print(config.tr("Test Passed"))