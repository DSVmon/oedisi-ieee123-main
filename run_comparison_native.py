import os
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from gym_environment import IEEE123Env
from simulation_core import SimulationCore

# --- SETTINGS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "trained_models")
CHECKPOINT_DIR = os.path.join(MODEL_DIR, "checkpoints")

TEST_DAY = 200      # Hot day
LOAD_SCALE = 2.0    # 🔥 200% Load (Crisis!)

def find_latest_checkpoint():
    if not os.path.exists(CHECKPOINT_DIR): return None
    files = [f for f in os.listdir(CHECKPOINT_DIR) if f.endswith(".zip")]
    if not files: return None
    latest = max(files, key=lambda x: int(x.split('_')[2]))
    return os.path.join(CHECKPOINT_DIR, latest)

def run_native_opendss():
    """Run with NATIVE OpenDSS automation (without Python control)."""
    print(f"▶ Starting Native OpenDSS (Day {TEST_DAY}, Load {LOAD_SCALE*100}%)")
    
    sim = SimulationCore()
    # Reset (sets ControlMode=OFF)
    sim.reset(day_of_year=TEST_DAY, load_scale=LOAD_SCALE)
    
    # !!! IMPORTANT: Enabling OpenDSS built-in logic !!!
    # ControlMode=TIME forces OpenDSS to manage regulators itself
    # based on settings in .dss files
    sim.text.Command = "Set ControlMode=TIME" 
    sim.text.Command = "Set MaxControlIter=100" # Allow many switching operations per step
    
    voltages = []
    taps = []
    
    # List of regulators to monitor
    reg_names = sim.get_regulator_list()
    
    for _ in range(96):
        # Just solve the circuit. OpenDSS will change taps if needed.
        sim.solution.Solve()
        
        # Collect data
        raw = sim.get_state()
        v_step = [raw['voltages'][node] for node in sim.sensor_nodes]
        t_step = [raw['taps'][r] for r in reg_names]
        
        voltages.append(v_step)
        taps.append(t_step)
        
    return np.array(voltages), np.array(taps), reg_names

def run_ai_agent(model_path):
    """Run with NEURAL NETWORK (ControlMode=OFF)."""
    print(f"▶ Starting AI Agent (Day {TEST_DAY}, Load {LOAD_SCALE*100}%)")
    
    env = IEEE123Env()
    obs, _ = env.reset(seed=42)
    # Configure the same day and load
    env.sim.reset(day_of_year=TEST_DAY, load_scale=LOAD_SCALE)
    
    # Load model
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
    # 1. Search for model
    model_path = find_latest_checkpoint()
    if not model_path:
        print("❌ Model not found.")
        return
    print(f"✅ AI Model: {os.path.basename(model_path)}")
    
    # 2. Run Native OpenDSS
    v_nat, t_nat, reg_names = run_native_opendss()
    
    # 3. Run AI
    v_ai, t_ai = run_ai_agent(model_path)
    
    # 4. Compare plots
    print("\n📊 Plotting Clash of Titans (OpenDSS vs AI)...")
    time_ax = np.arange(96) * 0.25
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12), sharex=True)
    
    # --- PLOT 1: Voltages ---
    # Native = Red
    ax1.plot(time_ax, v_nat, color='red', alpha=0.15, linewidth=1)
    # AI = Blue
    ax1.plot(time_ax, v_ai, color='blue', alpha=0.15, linewidth=1)
    
    # Corridor
    ax1.axhline(0.95, color='black', linestyle='--', linewidth=2)
    ax1.axhline(1.05, color='black', linestyle='--', linewidth=2)
    
    # Legend
    ax1.plot([], [], color='red', label='Native OpenDSS (Classic)')
    ax1.plot([], [], color='blue', label='AI Agent (Neural Net)')
    
    ax1.set_title(f"Quality Comparison: Standard Automation vs AI (Load {LOAD_SCALE*100}%)", fontsize=14)
    ax1.set_ylabel("Voltage (p.u.)")
    ax1.legend(loc='lower left', fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # --- PLOT 2: Regulator Operations ---
    # To avoid clutter, let's show only specific regulators (e.g. start and end)
    
    target_regs = ['creg1a', 'creg4c'] # Main and remote
    indices = [i for i, name in enumerate(reg_names) if name in target_regs]
    
    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color']
    
    for i, idx in enumerate(indices):
        r_name = reg_names[idx]
        # Native - dashed
        ax2.step(time_ax, t_nat[:, idx], where='post', linestyle='--', color=colors[i], label=f"{r_name} (Native)")
        # AI - solid
        ax2.step(time_ax, t_ai[:, idx], where='post', linestyle='-', color=colors[i], linewidth=2, label=f"{r_name} (AI)")
        
    ax2.set_title("Switching Strategy (Example of 2 regulators)", fontsize=12)
    ax2.set_ylabel("Tap Position")
    ax2.set_xlabel("Time (hours)")
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()