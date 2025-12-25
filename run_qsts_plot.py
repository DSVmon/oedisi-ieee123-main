import dss
import pathlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import config # <--- Added config
from ai_controller import AIController

# --- ГЛОБАЛЬНАЯ ПАМЯТЬ СОСТОЯНИЙ РЕГУЛЯТОРОВ ---
GLOBAL_REGULATOR_STATE = {}

def clear_regulator_state():
    """Очищает память регуляторов (для кнопки Сброс)."""
    global GLOBAL_REGULATOR_STATE
    GLOBAL_REGULATOR_STATE = {}
    print(config.tr("Clear Memory"))

# =============================================================================
# КЛАСС КОНТРОЛЛЕРА
# =============================================================================
class GridController:
    def __init__(self, circuit, target_bus):
        self.circuit = circuit
        self.target_bus = target_bus
        self.min_voltage = 0.95
        self.max_voltage = 1.05
        
        self.parent_map = self._build_topology_map()
        self.xfmr_to_reg = self._map_transformers_to_regulators()
        self.reg_chain = self._get_upstream_regulators()
        
        print(config.tr("Controller Node", target_bus))
        if self.reg_chain:
            print(config.tr("Chain Help", ' -> '.join(self.reg_chain), len(self.reg_chain)))
        else:
            print(config.tr("Warn No Regs"))

    def _build_topology_map(self):
        adj = {}
        def add_edge(b1, b2, elem_full_name):
            b1, b2 = b1.split('.')[0], b2.split('.')[0]
            if b1 not in adj: adj[b1] = []
            if b2 not in adj: adj[b2] = []
            adj[b1].append((b2, elem_full_name))
            adj[b2].append((b1, elem_full_name))

        lines = self.circuit.Lines
        idx = lines.First
        while idx > 0:
            full_name = self.circuit.ActiveCktElement.Name
            add_edge(lines.Bus1, lines.Bus2, full_name)
            idx = lines.Next
            
        xfmrs = self.circuit.Transformers
        idx = xfmrs.First
        while idx > 0:
            full_name = self.circuit.ActiveCktElement.Name
            buses = self.circuit.ActiveCktElement.BusNames
            if len(buses) >= 2:
                add_edge(buses[0], buses[1], full_name)
            idx = xfmrs.Next

        q = ['150']
        visited = set(['150'])
        parent_map = {} 
        
        while q:
            curr = q.pop(0)
            if curr in adj:
                for neighbor, elem in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        parent_map[neighbor] = elem 
                        q.append(neighbor)
        return parent_map

    def _map_transformers_to_regulators(self):
        mapping = {}
        regs = self.circuit.RegControls
        idx = regs.First
        while idx > 0:
            t_name = regs.Transformer
            t_full = f"Transformer.{t_name}"
            r_name = regs.Name
            mapping[t_full] = r_name
            idx = regs.Next
        return mapping

    def _get_upstream_regulators(self):
        chain = []
        curr = self.target_bus
        
        for _ in range(1000): 
            if curr == '150': break
            if curr not in self.parent_map: break
            
            feeding_elem = self.parent_map[curr] 
            
            if feeding_elem.lower().startswith("transformer."):
                if feeding_elem in self.xfmr_to_reg:
                    reg_name = self.xfmr_to_reg[feeding_elem]
                    chain.append(reg_name)
            
            self.circuit.SetActiveElement(feeding_elem)
            buses = self.circuit.ActiveCktElement.BusNames
            
            if len(buses) < 2: break
                
            b1 = buses[0].split('.')[0]
            b2 = buses[1].split('.')[0]
            
            if b2 == curr: curr = b1
            elif b1 == curr: curr = b2
            else: break 
                
        return chain 

    def check_and_act(self, step_number):
        actions = []
        action_occurred = False
        
        all_voltages = self.circuit.AllBusVmagPu
        if len(all_voltages) == 0: return [], False
        valid_voltages = [v for v in all_voltages if v > 0.01]
        if not valid_voltages: return [], False

        v_min = min(valid_voltages)
        v_max = max(valid_voltages)
        
        direction = 0
        reason = ""

        if v_min < self.min_voltage:
            direction = 1
            reason = config.tr("Reason Low", v_min)
        elif v_max > self.max_voltage:
            direction = -1
            reason = config.tr("Reason High", v_max)
            
        if direction != 0:
            for reg_name in self.reg_chain:
                self.circuit.RegControls.Name = reg_name
                current_tap = self.circuit.RegControls.TapNumber
                new_tap = current_tap + direction
                
                if -16 <= new_tap <= 16:
                    self.circuit.RegControls.TapNumber = new_tap
                    actions.append(config.tr("Step Log", step_number, reason, reg_name, current_tap, new_tap))
                    action_occurred = True
                    break 
                else:
                    actions.append(config.tr("Limit Log", step_number, reg_name, current_tap))
                    continue
        
        return actions, action_occurred

def get_controlling_element(circuit, bus_name):
    circuit.SetActiveBus(bus_name)
    connected_elements = circuit.ActiveBus.AllPDEatBus
    target_element = None
    target_terminal = 1
    for elem in connected_elements:
        if elem.startswith("Line."):
            target_element = elem
            circuit.SetActiveElement(elem)
            buses = circuit.ActiveElement.BusNames
            if buses[0].split('.')[0] == bus_name: target_terminal = 1
            else: target_terminal = 2
            return target_element, target_terminal
    for elem in connected_elements:
        if elem.startswith("Transformer."):
            return elem, 1
    return None, None

def setup_circuit(dss_engine, node_states_dict, pv_enabled, day_of_year, temperature, test_load_kw=0.0):
    text = dss_engine.Text
    circuit = dss_engine.ActiveCircuit
    current_dir = pathlib.Path(__file__).parent.resolve()
    qsts_master_file = current_dir / "qsts" / "master.dss"
    text.Command = f'Compile "{qsts_master_file}"'

    if pv_enabled:
        text.Command = "New XYCurve.PvTempEff npts=4 xarray=[-10 25 50 75] yarray=[1.20 1.0 0.80 0.60]"
        text.Command = f"New Tshape.TempOverride npts=1 interval=1 temp=[{temperature}]"

    pvs = circuit.PVSystems
    idx = pvs.First
    while idx > 0:
        circuit.ActiveCktElement.Enabled = pv_enabled
        if pv_enabled:
            pv_name = pvs.Name
            text.Command = f"Edit PVSystem.{pv_name} TYearly=TempOverride P-TCurve=PvTempEff temperature={temperature}"
        idx = pvs.Next

    if test_load_kw > 0.0:
        text.Command = f"New Load.Test_Experiment_Load Bus1=TestNode.1.2.3 Phases=3 kV=4.16 kW={test_load_kw} PF=0.98 Model=1"
        print(config.tr("Load Connected", test_load_kw))

    for bus, state in node_states_dict.items():
        mode = state['mode']
        phases = state['phases']
        if mode == 'Normal': continue
        elem, term = get_controlling_element(circuit, bus)
        if not elem: continue
        for ph in phases:
            if mode == 'Short Circuit':
                text.Command = f"New Fault.F_{bus}_{ph} Bus1={bus}.{ph} Phases=1 R=0.005"
            elif mode == 'Open Line':
                text.Command = f"Open {elem} Term={term} Phase={ph}"
    
    start_hour = (int(day_of_year) - 1) * 24
    text.Command = f"Set Mode=Yearly StepSize=15m Hour={start_hour}"

def analyze_voltage_violations(node_states_dict, pv_enabled, day_of_year, temperature, test_load_kw=0.0):
    global GLOBAL_REGULATOR_STATE
    dss_engine = dss.DSS
    circuit = dss_engine.ActiveCircuit
    solution = circuit.Solution
    
    setup_circuit(dss_engine, node_states_dict, pv_enabled, day_of_year, temperature, test_load_kw)
    
    dss_engine.Text.Command = "Set ControlMode=OFF"
    
    if GLOBAL_REGULATOR_STATE:
        print(config.tr("Apply Reg Settings"))
        for reg_name, tap_val in GLOBAL_REGULATOR_STATE.items():
            circuit.RegControls.Name = reg_name
            circuit.RegControls.TapNumber = tap_val
            print(config.tr("Reg Set To", reg_name, tap_val))
    else:
        print(config.tr("No Settings"))
    
    dss_engine.Text.Command = "Set Number=1" 
    
    print(config.tr("Scan Net"))
    max_v = {}
    min_v = {}
    max_total_kw = 0.0
    
    for _ in range(96):
        solution.Solve()
        if not solution.Converged: continue
        
        # --- Подсчет общей мощности (ИСПРАВЛЕНО: добавлен abs) ---
        # TotalPower возвращает массив [P, Q]. Часто P отрицательное (инжекция).
        try:
            p_total = abs(circuit.TotalPower[0])
            if p_total > max_total_kw: max_total_kw = p_total
        except: pass
        # ------------------------------

        all_nodes = circuit.AllNodeNames 
        all_v = circuit.AllBusVmagPu   
        for i, node_full in enumerate(all_nodes):
            v = all_v[i]
            bus = node_full.split('.')[0]
            if bus not in max_v: max_v[bus] = 0.0; min_v[bus] = 999.0
            if v > max_v[bus]: max_v[bus] = v
            if v < min_v[bus] and v > 0.0: min_v[bus] = v

    over, under = set(), set()
    # Format the header row using the translated template
    header_fmt = config.tr("Table Header")
    # Because config.tr returns a format string like "{:<10}...", we need to format it with empty strings
    # OR we just hardcode the column names in the config.
    # Actually, let's fix the logic. The config now contains the TEXT for the columns, but with format specifiers.
    # To be safe and simple: I updated config to contain the full string with placeholders for alignment if needed,
    # but the simplest way is to format it with the column names themselves if they were dynamic,
    # but here they are static in the config value (except for alignment).
    # Let's use .format() with dummy values if the string expects arguments, or just print if it's a fixed string.
    # The updated config removes the quotes around the last column, but keeps the brace placeholders {:<10}.
    # So we must provide arguments.
    # "RU": "{:<10} | {:<15} | ЗНАЧЕНИЕ (p.u.)"
    # This expects 2 arguments.
    print(header_fmt.format(config.tr("Column Node"), config.tr("Column Status")))
    print(config.tr("Total Power Peak", max_total_kw))
    print("-" * 45)
    
    sorted_buses = sorted(max_v.keys())
    for bus in sorted_buses:
        if bus in ['150', 'sourcebus']: continue
        if min_v[bus] < 0.95 and min_v[bus] > 0.001: 
            under.add(bus); print(config.tr("Under Voltage", bus, min_v[bus]))
        elif max_v[bus] > 1.05:
            over.add(bus); print(config.tr("Over Voltage", bus, max_v[bus]))

    if not over and not under: print(config.tr("No Violations"))
    return over, under

def run_simulation_for_node(target_bus_name, node_states_dict, pv_enabled=True, day_of_year=1, temperature=25.0, test_load_kw=0.0, active_control=True, ai_mode=False):
    global GLOBAL_REGULATOR_STATE
    dss_engine = dss.DSS
    text = dss_engine.Text
    circuit = dss_engine.ActiveCircuit
    solution = circuit.Solution

    setup_circuit(dss_engine, node_states_dict, pv_enabled, day_of_year, temperature, test_load_kw)
    
    # Apply global load increase (from config) for ALL modes
    if config.AI_LOAD_INCREASE_PERCENT > 0:
        load_mult = 1.0 + (config.AI_LOAD_INCREASE_PERCENT / 100.0)
        text.Command = f"Set LoadMult={load_mult}"
        print(config.tr("AI Load Increase", config.AI_LOAD_INCREASE_PERCENT))

    if GLOBAL_REGULATOR_STATE:
        print(config.tr("Restoring State"))
        for reg_name, tap_val in GLOBAL_REGULATOR_STATE.items():
            circuit.RegControls.Name = reg_name
            circuit.RegControls.TapNumber = tap_val

    # --- ИНСПЕКЦИЯ СОСТАВА УЗЛА ---
    circuit.SetActiveBus(target_bus_name)
    print(f"\n{'='*40}")
    print(config.tr("Inspect Node", target_bus_name))
    pce = circuit.ActiveBus.AllPCEatBus 
    pde = circuit.ActiveBus.AllPDEatBus 
    print(config.tr("ConsGen", pce))
    print(config.tr("LinesTrans", pde))
    if len(pce) > 0 and test_load_kw == 0 and "TestNode" in target_bus_name:
        print(config.tr("Warn Load 0"))
    print(f"{'='*40}")
    # ------------------------------

    # --- ВЫВОД СОСТОЯНИЯ РЕГУЛЯТОРОВ (ТЕПЕРЬ ДЛЯ ВСЕХ РЕЖИМОВ) ---
    print(config.tr("Current Reg State"))
    regs = circuit.RegControls
    idx = regs.First
    while idx > 0:
        print(f"   - {regs.Name}: {regs.TapNumber}")
        idx = regs.Next
    # -------------------------------------------------------------

    controller = None
    if ai_mode:
        controller = AIController(circuit)
    elif active_control:
        controller = GridController(circuit, target_bus_name)
    else:
        print(config.tr("Monitor Mode"))
        print(config.tr("Sim Monitor"))
    
    text.Command = "Set ControlMode=OFF" 
    text.Command = "Set Number=1"

    elem, term = get_controlling_element(circuit, target_bus_name)
    if not elem:
        print(config.tr("Error No Monitor", target_bus_name))
        return

    monitor_vi = f"Mon_Target_{target_bus_name}_VI"
    monitor_pq = f"Mon_Target_{target_bus_name}_PQ"
    text.Command = f"New Monitor.{monitor_vi} element={elem} terminal={term} mode=0"
    text.Command = f"New Monitor.{monitor_pq} element={elem} terminal={term} mode=1 ppolar=no"
    
    print(config.tr("Start Sim Node", target_bus_name))
    
    regulation_steps = []
    max_total_kw = 0.0

    for step in range(96):
        solution.Solve()
        
        # --- Подсчет общей мощности (ИСПРАВЛЕНО: добавлен abs) ---
        try:
            p_total = abs(circuit.TotalPower[0])
            if p_total > max_total_kw: max_total_kw = p_total
        except: pass
        # ------------------------------
        
        if active_control and controller:
            logs, acts = controller.check_and_act(step)
            if acts:
                regulation_steps.append(step)
                for msg in logs: print(msg)

    if active_control:
        print(config.tr("Final Reg State"))
        regs = circuit.RegControls
        idx = regs.First
        while idx > 0:
            tap_now = regs.TapNumber
            GLOBAL_REGULATOR_STATE[regs.Name] = tap_now
            print(f"   - {regs.Name}: {tap_now}")
            idx = regs.Next
    else:
        print(config.tr("Info No Change"))

    if solution.Converged:
        text.Command = f"Export Monitor {monitor_vi}"
        file_vi = text.Result
        text.Command = f"Export Monitor {monitor_pq}"
        file_pq = text.Result
        try:
            df_vi = pd.read_csv(file_vi)
            df_pq = pd.read_csv(file_pq)
            df = pd.concat([df_vi, df_pq], axis=1)

            p_cols = [c for c in df.columns if c.strip().startswith('P')]
            q_cols = [c for c in df.columns if c.strip().startswith('Q')]
            if term == 2:
                for col in p_cols + q_cols: df[col] = df[col] * -1.0

            circuit.SetActiveElement(elem)
            bus_def = circuit.ActiveElement.BusNames[term - 1]
            parts = bus_def.split('.')
            con_phases = parts[1:] if len(parts)>1 else [str(i) for i in range(1, circuit.ActiveElement.NumPhases + 1)]
            v_cols = [c for c in df_vi.columns if 'V' in c and 'Angle' not in c]
            i_cols = [c for c in df_vi.columns if 'I' in c and 'Angle' not in c]
            
            target_state = node_states_dict.get(target_bus_name, {'mode': 'Normal', 'phases': []})
            t_mode, t_phases = target_state['mode'], target_state['phases']
            sim_date = datetime.date(2020, 1, 1) + datetime.timedelta(days=int(day_of_year) - 1)

            # Localized month name
            month_idx = sim_date.month
            month_names = config.tr("Months")
            if isinstance(month_names, list) and len(month_names) > month_idx:
                 m_name = month_names[month_idx]
                 date_str = f"{sim_date.day} {m_name}"
            else:
                 date_str = sim_date.strftime("%d %B")

            circuit.SetActiveBus(target_bus_name)
            kv_base_dss = circuit.ActiveBus.kVBase 
            
            print(f"\n{'='*40}")
            print(config.tr("Node Summary", target_bus_name))
            print(f"{'='*40}")
            
            v_meas_mean = 0
            cnt = 0
            for col in v_cols:
                v_meas_mean += df[col].mean()
                cnt += 1
            if cnt > 0: v_meas_mean /= cnt
            
            v_base_candidate = kv_base_dss * 1000
            v_base_phase = v_base_candidate
            base_type_str = config.tr("Base Type Phase")
            if v_base_candidate > 0 and (v_meas_mean / v_base_candidate) < 0.8 and v_meas_mean > 10:
                 v_base_phase = v_base_candidate / np.sqrt(3)
                 base_type_str = config.tr("Base Type LinearToPhase")
            
            print(config.tr("Params Phases", circuit.ActiveBus.NumNodes))
            print(config.tr("Base DSS", kv_base_dss, base_type_str))
            print(config.tr("Base PU", v_base_phase))
            print(f"-"*40)
            print(config.tr("Daily Stats"))
            
            for i, col in enumerate(v_cols):
                if i >= len(con_phases): continue
                ph = con_phases[i]
                v_min = df[col].min()
                v_max = df[col].max()
                t_min_idx = df[col].idxmin()
                t_max_idx = df[col].idxmax()
                
                def idx_to_time(idx):
                    total_min = int(idx * 15)
                    h = (total_min // 60) % 24
                    m = total_min % 60
                    return f"{h:02d}:{m:02d}"

                v_pu_min = v_min / v_base_phase if v_base_phase > 0 else 0
                v_pu_max = v_max / v_base_phase if v_base_phase > 0 else 0
                
                status_min = config.tr("Warning Under") if v_pu_min < 0.95 else ""
                status_max = config.tr("Warning Over") if v_pu_max > 1.05 else ""

                print(config.tr("Phase Log", ph))
                print(config.tr("Min U", v_min, v_pu_min, idx_to_time(t_min_idx), status_min))
                print(config.tr("Max U", v_max, v_pu_max, idx_to_time(t_max_idx), status_max))

            p_max = 0
            for col in p_cols:
                curr_max = df[col].max()
                if abs(curr_max) > abs(p_max): p_max = curr_max
            
            i_max = 0
            for col in i_cols:
                curr_max = df[col].max()
                if curr_max > i_max: i_max = curr_max

            print(f"-"*40)
            print(config.tr("Peak Load", p_max))
            print(config.tr("Max Current", i_max))
            print(config.tr("Total P Net", max_total_kw))
            print(f"{'='*40}\n")

            time_hours = df.index * 0.25
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
            plt.subplots_adjust(bottom=0.08, hspace=0.25)
            
            pv_st = config.tr("PV On", temperature) if pv_enabled else config.tr("PV Off")
            fig.canvas.manager.set_window_title(f"Узел {target_bus_name} | {date_str}")
            
            load_info = config.tr("Load Info", test_load_kw) if test_load_kw > 0 else ""

            if ai_mode:
                mode_str = config.tr("AI Control Mode")
            elif active_control:
                mode_str = config.tr("Active Control Mode")
            else:
                mode_str = config.tr("Monitor Mode Plot")

            # Append load info to title if applicable
            if config.AI_LOAD_INCREASE_PERCENT > 0:
                mode_str += " | " + config.tr("AI Load Increase", config.AI_LOAD_INCREASE_PERCENT)

            ax1.set_title(config.tr("Node Plot Title", target_bus_name, date_str, pv_st, load_info, mode_str), fontsize=14, fontweight='bold')

            max_v_plot = 0
            for idx, col in enumerate(v_cols):
                if idx >= len(con_phases): continue
                if df[col].max() > max_v_plot: max_v_plot = df[col].max()
                ph = con_phases[idx]
                ax1.plot(time_hours, df[col], label=f"V ph{ph}")

            for step in regulation_steps:
                t = step * 0.25
                ax1.axvline(x=t, color='green', linestyle='-', alpha=0.3, linewidth=2)
            
            if regulation_steps:
                ax1.plot([], [], color='green', linestyle='-', alpha=0.5, label=config.tr("Regulating"))

            ax1.set_ylabel(config.tr("Voltage V"))
            ax1.grid(True, linestyle=':', alpha=0.6)
            ax1.legend(loc='upper right', fontsize='small')
            if max_v_plot < 1000: ax1.set_ylim(0, 3000)
            else: ax1.autoscale(enable=True, axis='y'); ax1.margins(y=0.1)

            for idx, col in enumerate(i_cols):
                if idx >= len(con_phases): continue
                ph = con_phases[idx]
                ax2.plot(time_hours, df[col], label=f"I ph{ph}")
            ax2.set_ylabel(config.tr("Current A"))
            ax2.grid(True, linestyle=':', alpha=0.6)
            ax2.legend(loc='upper right')

            for idx, col in enumerate(p_cols):
                if idx >= len(con_phases): continue
                ph = con_phases[idx]
                ax3.plot(time_hours, df[col], label=f"P ph{ph}")
            ax3.set_ylabel(config.tr("Power kW"))
            ax3.set_xlabel(config.tr("Time Hours"))
            ax3.set_xlim(0, 24); ax3.set_xticks(range(0, 25, 2))
            ax3.grid(True, linestyle=':', alpha=0.6)
            ax3.legend(loc='upper right')
            
            for step in regulation_steps:
                t = step * 0.25
                ax3.axvline(x=t, color='green', linestyle='-', alpha=0.15)

            lv = ax1.axvline(0, c='gray', ls='--', alpha=0.8)
            li = ax2.axvline(0, c='gray', ls='--', alpha=0.8)
            lp = ax3.axvline(0, c='gray', ls='--', alpha=0.8)
            
            txt = ax1.text(0.02, 0.95, '', transform=ax1.transAxes, va='top', bbox=dict(facecolor='white', alpha=0.9))

            def on_move(event):
                if not event.inaxes: return
                x = event.xdata
                lv.set_xdata([x, x]); li.set_xdata([x, x]); lp.set_xdata([x, x])
                idx = (np.abs(time_hours - x)).argmin()
                tm = int(round(time_hours[idx]*60))
                info = f"Время: {tm//60:02d}:{tm%60:02d}\n" + "-"*20 + "\n"
                
                for i, c in enumerate(v_cols):
                     if i >= len(con_phases): continue
                     val = df[c].iloc[idx]
                     p = con_phases[i]
                     info += f"V{p}: {val:.1f} V\n"
                info += "-"*20 + "\n"
                for i, c in enumerate(i_cols):
                     if i >= len(con_phases): continue
                     val = df[c].iloc[idx]
                     p = con_phases[i]
                     info += f"I{p}: {val:.1f} A\n"
                info += "-"*20 + "\n"
                for i, c in enumerate(p_cols):
                     if i >= len(con_phases): continue
                     val = df[c].iloc[idx]
                     p = con_phases[i]
                     info += f"P{p}: {val:.1f} kW\n"

                txt.set_text(info)
                fig.canvas.draw_idle()

            fig.canvas.mpl_connect('motion_notify_event', on_move)
            plt.show()
        except Exception as e: print(config.tr("Plot Error", e))
    else: print(config.tr("Solution Diverged"))