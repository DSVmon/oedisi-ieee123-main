import os
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from gym_environment import IEEE123Env

# --- SETTINGS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "trained_models")
CHECKPOINT_DIR = os.path.join(MODEL_DIR, "checkpoints")

# Choose model for test:
# Option A: Latest checkpoint (use this while training is still running!)
# The script will find the freshest file in the checkpoints folder
TRY_LATEST_CHECKPOINT = True 

# Option B: Final model (if training is finished)
FINAL_MODEL_NAME = "ppo_ieee123_final.zip"

def find_latest_checkpoint():
    if not os.path.exists(CHECKPOINT_DIR): return None
    files = [f for f in os.listdir(CHECKPOINT_DIR) if f.endswith(".zip")]
    if not files: return None
    # Sort by step number (ppo_ieee123_20000_steps.zip)
    # Extract number from filename
    def get_step(name):
        parts = name.split('_')
        for p in parts:
            if p.isdigit(): return int(p)
        return 0
    
    latest_file = max(files, key=get_step)
    return os.path.join(CHECKPOINT_DIR, latest_file)

def main():
    print("🔎 Searching for model...")
    model_path = None
    
    if TRY_LATEST_CHECKPOINT:
        model_path = find_latest_checkpoint()
        if model_path:
            print(f"✅ Found fresh checkpoint: {os.path.basename(model_path)}")
    
    if not model_path:
        final_path = os.path.join(MODEL_DIR, FINAL_MODEL_NAME)
        if os.path.exists(final_path):
            model_path = final_path
            print(f"✅ Found final model: {FINAL_MODEL_NAME}")
    
    if not model_path:
        print("❌ Models not found! Run training first (train_agent.py).")
        return

    print("🚀 Loading environment and agent...")
    # Create environment WITHOUT log monitor (we don't need graphs here)
    env = IEEE123Env(pv_enabled=True)
    
    # Load neural network
    model = PPO.load(model_path)
    
    # --- TEST SCENARIO ---
    # Pick a fixed difficult day (e.g., hot summer)
    # To compare fairly, reset environment forcibly
    obs, _ = env.reset(seed=42) 
    env.day = 200 # 200th day of year (July)
    env.sim.reset(day_of_year=200, load_scale=1.0)
    
    print(f"📅 Testing day: {env.day} (Summer)")
    
    # Data storage for plots
    history = {
        'voltages': [], # [step] -> [v1, v2, ...]
        'taps': [],     # [step] -> [tap1, tap2, ...]
        'power': [],    # [step] -> kw
        'rewards': []
    }
    
    # List of node names for legend (take first 5 for clean plot)
    sensor_names = env.sim.sensor_nodes[:5] 
    
    print("▶ Starting simulation (96 steps)...")
    
    for step in range(96):
        # 1. Ask Neural Network
        action, _ = model.predict(obs, deterministic=True)
        
        # 2. Take step
        obs, reward, done, _, info = env.step(action)
        
        # 3. Save "raw" physical data from simulator
        raw_state = env.sim.get_state()
        
        # Voltages (all sensors)
        v_vals = [raw_state['voltages'][node] for node in env.sim.sensor_nodes]
        history['voltages'].append(v_vals)
        
        # Taps (all regulators)
        t_vals = [raw_state['taps'][reg] for reg in env.reg_names]
        history['taps'].append(t_vals)
        
        # Power
        history['power'].append(raw_state['total_power_kw'])
        history['rewards'].append(reward)

    print("✅ Simulation complete. Plotting charts...")
    
    # --- PLOTTING ---
    time_axis = np.arange(96) * 0.25 # Hours
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 14), sharex=True)
    plt.subplots_adjust(hspace=0.3)
    
    # 1. Voltage Chart
    voltages_np = np.array(history['voltages']) # Shape: (96, N_sensors)
    
    # Draw all voltages with gray background
    ax1.plot(time_axis, voltages_np, color='gray', alpha=0.1)
    # Highlight a few colored lines
    for i, node_name in enumerate(sensor_names):
        ax1.plot(time_axis, voltages_np[:, i], label=f"Node {node_name}")
        
    # Norm corridor
    ax1.axhline(0.95, color='red', linestyle='--', linewidth=2, label='Min (0.95)')
    ax1.axhline(1.05, color='red', linestyle='--', linewidth=2, label='Max (1.05)')
    ax1.axhline(1.00, color='green', linestyle=':', alpha=0.5)
    
    ax1.set_title("Grid Voltages (AI Control)", fontsize=12, fontweight='bold')
    ax1.set_ylabel("Voltage (p.u.)")
    ax1.legend(loc='upper right', ncol=3, fontsize='small')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0.90, 1.10)
    
    # 2. Switching Chart (Taps)
    taps_np = np.array(history['taps'])
    for i, reg_name in enumerate(env.reg_names):
        ax2.step(time_axis, taps_np[:, i], where='post', label=reg_name, linewidth=1.5)
        
    ax2.set_title("Regulator Operations", fontsize=12, fontweight='bold')
    ax2.set_ylabel("Tap Position")
    ax2.legend(loc='upper right', fontsize='small', ncol=2)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(-17, 17)
    
    # 3. Power and Reward Chart
    color = 'tab:blue'
    ax3.set_xlabel("Time (hours)")
    ax3.set_ylabel("Active Power (kW)", color=color)
    ax3.plot(time_axis, history['power'], color=color, linewidth=2)
    ax3.tick_params(axis='y', labelcolor=color)
    ax3.grid(True, alpha=0.3)
    
    # Twin axis for reward
    ax3_r = ax3.twinx()
    color = 'tab:purple'
    ax3_r.set_ylabel("Agent Reward", color=color)
    ax3_r.plot(time_axis, history['rewards'], color=color, linestyle='--', alpha=0.6)
    ax3_r.tick_params(axis='y', labelcolor=color)
    ax3.set_title("Consumption & Quality Score", fontsize=12, fontweight='bold')

    print("📊 Chart opened.")
    plt.show()

if __name__ == "__main__":
    main()