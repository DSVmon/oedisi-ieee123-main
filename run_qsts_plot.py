import dss
import pathlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime

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

def setup_circuit(dss_engine, node_states_dict, pv_enabled, day_of_year, temperature):
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

def analyze_voltage_violations(node_states_dict, pv_enabled, day_of_year, temperature):
    dss_engine = dss.DSS
    circuit = dss_engine.ActiveCircuit
    solution = circuit.Solution
    
    setup_circuit(dss_engine, node_states_dict, pv_enabled, day_of_year, temperature)
    dss_engine.Text.Command = "Set Number=1" 
    
    print("\n--- АНАЛИЗ НАПРЯЖЕНИЯ (Сканирование суток...) ---")
    max_v = {}
    min_v = {}
    
    for _ in range(96):
        solution.Solve()
        if not solution.Converged: continue
        all_nodes = circuit.AllNodeNames 
        all_v = circuit.AllBusVmagPu   
        for i, node_full in enumerate(all_nodes):
            v = all_v[i]
            bus = node_full.split('.')[0]
            if bus not in max_v:
                max_v[bus] = 0.0
                min_v[bus] = 999.0
            if v > max_v[bus]: max_v[bus] = v
            # Убрал порог 0.1, чтобы ловить КЗ как просадку (если V не ровно 0)
            if v < min_v[bus] and v > 0.0: min_v[bus] = v

    over, under = set(), set()
    print(f"{'УЗЕЛ':<10} | {'СТАТУС':<15} | {'ЗНАЧЕНИЕ (p.u.)'}")
    print("-" * 45)
    for bus in max_v:
        if bus in ['150', 'sourcebus']: continue
        
        # Приоритет: сначала проверяем низкое напряжение (оно критичнее при авариях)
        if min_v[bus] < 0.95 and min_v[bus] > 0.001: # 0.001 чтобы не спамить отключенными
            under.add(bus)
            print(f"{bus:<10} | ПРОСАДКА      | {min_v[bus]:.4f}")
        
        # Если просадки нет, проверяем перенапряжение
        elif max_v[bus] > 1.05:
            over.add(bus)
            print(f"{bus:<10} | ПЕРЕНАПРЯЖЕНИЕ | {max_v[bus]:.4f}")

    if not over and not under: print("✅ Нарушений не обнаружено.")
    return over, under

def run_simulation_for_node(target_bus_name, node_states_dict, pv_enabled=True, day_of_year=1, temperature=25.0):
    dss_engine = dss.DSS
    text = dss_engine.Text
    circuit = dss_engine.ActiveCircuit
    solution = circuit.Solution

    setup_circuit(dss_engine, node_states_dict, pv_enabled, day_of_year, temperature)
    text.Command = "Set Number=96"

    elem, term = get_controlling_element(circuit, target_bus_name)
    if not elem:
        print(f"❌ Ошибка: Не к чему подключить монитор для {target_bus_name}")
        return

    monitor_name = f"Mon_Target_{target_bus_name}"
    text.Command = f"New Monitor.{monitor_name} element={elem} terminal={term} mode=0"
    solution.Solve()

    target_state = node_states_dict.get(target_bus_name, {'mode': 'Normal', 'phases': []})
    t_mode, t_phases = target_state['mode'], target_state['phases']
    ph_str = ",".join(map(str, t_phases)) if t_phases else "-"
    sim_date = datetime.date(2020, 1, 1) + datetime.timedelta(days=int(day_of_year) - 1)
    date_str = sim_date.strftime("%d %B")

    print(f"\n--- Расчет: {target_bus_name} ---")
    print(f"Дата: {date_str}, T={temperature}°C, PV={pv_enabled}")
    print(f"Режим: {t_mode}" + (f" (Ph {ph_str})" if t_mode!='Normal' else ""))

    if solution.Converged:
        text.Command = f"Export Monitor {monitor_name}"
        try:
            df = pd.read_csv(text.Result)
            circuit.SetActiveElement(elem)
            bus_def = circuit.ActiveElement.BusNames[term - 1]
            parts = bus_def.split('.')
            con_phases = parts[1:] if len(parts)>1 else [str(i) for i in range(1, circuit.ActiveElement.NumPhases + 1)]
            
            v_cols = [c for c in df.columns if 'V' in c and 'Angle' not in c]
            i_cols = [c for c in df.columns if 'I' in c and 'Angle' not in c]
            time_hours = df.index * 0.25

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
            plt.subplots_adjust(bottom=0.1)
            
            pv_st = f"[PV ВКЛ, {temperature}°C]" if pv_enabled else "[PV ВЫКЛ]"
            fig.canvas.manager.set_window_title(f"Узел {target_bus_name} | {date_str}")
            title_c = 'red' if t_mode == 'Short Circuit' else ('orange' if t_mode == 'Open Line' else 'black')
            
            ax1.set_title(f'Узел {target_bus_name}: {t_mode}\n{date_str} {pv_st}', fontsize=14, color=title_c, fontweight='bold')

            max_v = 0
            for idx, col in enumerate(v_cols):
                if df[col].max() > max_v: max_v = df[col].max()
                ph = con_phases[idx] if idx < len(con_phases) else "?"
                lbl_suff = f" (Ph {ph})"
                legend = f"{col.strip().split()[0]}{lbl_suff}"
                is_bad = False
                if t_mode!='Normal':
                    try: 
                        if int(ph) in t_phases: is_bad = True
                    except: pass
                ax1.plot(time_hours, df[col], label=legend, linewidth=3.0 if is_bad else 1.0)

            ax1.set_ylabel('Напряжение (В)')
            ax1.grid(True, linestyle=':', alpha=0.6)
            ax1.legend(loc='upper right', fontsize='small')
            if max_v < 1000: ax1.set_ylim(0, 3000)
            else: ax1.autoscale(enable=True, axis='y'); ax1.margins(y=0.1)

            for idx, col in enumerate(i_cols):
                ph = con_phases[idx] if idx < len(con_phases) else "?"
                lbl_suff = f" (Ph {ph})"
                legend = f"{col.strip().split()[0]}{lbl_suff}"
                is_bad = False
                if t_mode!='Normal':
                    try: 
                        if int(ph) in t_phases: is_bad = True
                    except: pass
                ax2.plot(time_hours, df[col], label=legend, linewidth=3.0 if is_bad else 1.0)

            ax2.set_ylabel('Ток (А)')
            ax2.set_xlabel('Время (часы)')
            ax2.set_xlim(0, 24); ax2.set_xticks(range(0, 25, 2))
            ax2.grid(True, linestyle=':', alpha=0.6)
            ax2.legend(loc='upper right', fontsize='small')

            lv = ax1.axvline(0, c='gray', ls='--', alpha=0.8)
            li = ax2.axvline(0, c='gray', ls='--', alpha=0.8)
            txt = ax1.text(0.02, 0.95, '', transform=ax1.transAxes, va='top', bbox=dict(facecolor='white', alpha=0.9))

            def on_move(event):
                if not event.inaxes: return
                x = event.xdata
                lv.set_xdata([x, x]); li.set_xdata([x, x])
                idx = (np.abs(time_hours - x)).argmin()
                tm = int(round(time_hours[idx]*60))
                info = f"Время: {tm//60:02d}:{tm%60:02d}\n" + "-"*20 + "\n"
                for i, c in enumerate(v_cols):
                     val = df[c][idx]
                     p = con_phases[i] if i<len(con_phases) else '?'
                     info += f"V{p}: {val:.1f} V\n"
                info += "-"*20 + "\n"
                for i, c in enumerate(i_cols):
                     val = df[c][idx]
                     p = con_phases[i] if i<len(con_phases) else '?'
                     info += f"I{p}: {val:.1f} A\n"
                txt.set_text(info)
                fig.canvas.draw_idle()

            fig.canvas.mpl_connect('motion_notify_event', on_move)
            plt.show()
        except Exception as e: print(f"Ошибка графика: {e}")
    else: print("❌ Решение не сошлось.")