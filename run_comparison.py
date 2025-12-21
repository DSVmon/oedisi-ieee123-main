import os
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from gym_environment import IEEE123Env

# --- SETTINGS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "trained_models")
CHECKPOINT_DIR = os.path.join(MODEL_DIR, "checkpoints")

# Choose day and load for crash test
TEST_DAY = 200      # Hot summer day
LOAD_SCALE = 1.5    # 🔥 150% Load on the entire grid!

def find_latest_checkpoint():
    if not os.path.exists(CHECKPOINT_DIR): return None
    files = [f for f in os.listdir(CHECKPOINT_DIR) if f.endswith(".zip")]
    if not files: return None
    latest = max(files, key=lambda x: int(x.split('_')[2]))
    return os.path.join(CHECKPOINT_DIR, latest)

def run_episode(env, model=None, label=""):
    """Runs one day. If model=None, then no control."""
    print(f"▶ Starting scenario: {label} (Load {LOAD_SCALE*100}%)")
    
    # Reset with fixed overload
    obs, _ = env.reset(seed=42)
    env.sim.reset(day_of_year=TEST_DAY, load_scale=LOAD_SCALE)
    
    voltages = []
    taps = []
    
    for step in range(96):
        if model:
            # Ask Neural Network
            action, _ = model.predict(obs, deterministic=True)
        else:
            # NO ACTION (Simulating old dumb grid)
            # 0 = "Do nothing" for all regulators
            action = np.zeros(env.n_regulators, dtype=int) 
            
        obs, reward, done, _, info = env.step(action)
        
        # Save data
        raw = env.sim.get_state()
        v_step = [raw['voltages'][node] for node in env.sim.sensor_nodes]
        voltages.append(v_step)
        taps.append([raw['taps'][r] for r in env.reg_names])
        
    return np.array(voltages), np.array(taps)

def main():
    # 1. Find model
    model_path = find_latest_checkpoint()
    if not model_path:
        print("❌ Model not found. Train the agent first.")
        return
    print(f"✅ Loading model: {os.path.basename(model_path)}")
    model = PPO.load(model_path)
    
    env = IEEE123Env()
    
    # 2. Run WITHOUT NEURAL NETWORK (Baseline)
    print("\n--- PHASE 1: No AI (Baseline) ---")
    v_base, t_base = run_episode(env, model=None, label="No AI")
    
    # 3. Run WITH NEURAL NETWORK (AI Agent)
    print("\n--- PHASE 2: With AI ---")
    v_ai, t_ai = run_episode(env, model=model, label="With AI")
    
    # 4. Visualization: Before vs After
    print("\n📊 Plotting comparison charts...")
    time_ax = np.arange(96) * 0.25
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # VOLTAGE PLOT
    # Draw "cloud" of voltages for Baseline (red semi-transparent)
    ax1.plot(time_ax, v_base, color='red', alpha=0.1, linewidth=1)
    # Draw "cloud" for AI (blue semi-transparent)
    ax1.plot(time_ax, v_ai, color='blue', alpha=0.1, linewidth=1)
    
    # Corridor lines
    ax1.axhline(0.95, color='black', linestyle='--', linewidth=2, label='Norm (0.95-1.05)')
    ax1.axhline(1.05, color='black', linestyle='--', linewidth=2)
    
    # Fake lines for legend
    ax1.plot([], [], color='red', alpha=0.5, label='No AI (Baseline)')
    ax1.plot([], [], color='blue', alpha=0.5, label='With AI (Agent)')
    
    ax1.set_title(f"Stability Comparison (Day {TEST_DAY}, Load {LOAD_SCALE*100}%)", fontsize=14)
    ax1.set_ylabel("Voltage (p.u.)")
    ax1.legend(loc='lower left')
    ax1.grid(True, alpha=0.3)
    
    # SWITCHING PLOT (only for AI, since baseline is static)
    for i, name in enumerate(env.reg_names):
        ax2.step(time_ax, t_ai[:, i], where='post', label=name)
        
    ax2.set_title("Neural Network Actions (Taps)", fontsize=12)
    ax2.set_ylabel("Position")
    ax2.set_xlabel("Time (hours)")
    ax2.legend(loc='upper right', ncol=3, fontsize='small')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()