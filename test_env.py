from gym_environment import IEEE123Env
import numpy as np
from localization import translate as tr

env = IEEE123Env()
obs, _ = env.reset()

print(tr("checking_environment"))
print(f"1. {tr('observation_size', shape=obs.shape)}")
print(f"2. {tr('observation_example', example=obs[:5])}")
print(f"3. {tr('action_space_size', action_space=env.action_space)}")


# Делаем случайный шаг
action = env.action_space.sample()
obs, reward, done, _, info = env.step(action)

print(f"4. {tr('reward_for_step', reward=reward)}")
print(f"5. {tr('info', info=info)}")
print(tr("test_passed"))
