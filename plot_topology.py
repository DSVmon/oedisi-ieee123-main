import dss
import pathlib
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Button, CheckButtons, Slider
from matplotlib.animation import FuncAnimation
import numpy as np
import datetime
from run_qsts_plot import run_simulation_for_node, analyze_voltage_violations, clear_regulator_state

# --- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ---
node_states = {}       
voltage_issues = {'over': set(), 'under': set()}
fault_markers = []     
network_tree = {}      
bus_phases = {}        
bus_to_scatter = {}    
original_colors = {}   

def build_network_tree(circuit):
    adj = {}
    lines = circuit.Lines
    count = lines.First
    while count > 0:
        b1 = lines.Bus1.split('.')[0]
        b2 = lines.Bus2.split('.')[0]
        if b1 not in adj: adj[b1] = []
        if b2 not in adj: adj[b2] = []
        adj[b1].append(b2)
        adj[b2].append(b1)
        count = lines.Next
    xfmrs = circuit.Transformers
    count = xfmrs.First
    while count > 0:
        buses = circuit.ActiveElement.BusNames
        if len(buses) >= 2:
            b1 = buses[0].split('.')[0]
            b2 = buses[1].split('.')[0]
            if b1 not in adj: adj[b1] = []
            if b2 not in adj: adj[b2] = []
            adj[b1].append(b2)
            adj[b2].append(b1)
        count = xfmrs.Next
    tree = {}
    visited = set(['150'])
    queue = ['150']
    while queue:
        parent = queue.pop(0)
        if parent in adj:
            for neighbor in adj[parent]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    if parent not in tree: tree[parent] = []
                    tree[parent].append(neighbor)
                    queue.append(neighbor)
    print(f"Дерево построено. Охвачено узлов: {len(visited)}")
    return tree

def get_downstream_nodes(start_nodes):
    result = set()
    stack = list(start_nodes)
    while stack:
        node = stack.pop()
        if node in result: continue
        result.add(node)
        if node in network_tree:
            for child in network_tree[node]:
                stack.append(child)
    return result

def plot_interactive_topology():
    global network_tree, bus_phases, bus_to_scatter, original_colors, voltage_issues
    
    dss_engine = dss.DSS
    text = dss_engine.Text
    circuit = dss_engine.ActiveCircuit

    current_dir = pathlib.Path(__file__).parent.resolve()
    master_file = current_dir / "qsts" / "master.dss"
    buscoords_file = current_dir / "qsts" / "Buscoords.dss"

    print(f"Загрузка схемы из: {master_file}")
    text.Command = f'Compile "{master_file}"'
    if not buscoords_file.exists():
        print("Ошибка: Нет файла координат")
        return
    text.Command = f'Buscoords "{buscoords_file}"'
    text.Command = "UpdateStorage"

    network_tree = build_network_tree(circuit)

    pickable_data = {} 
    node_coords = {} 
    loaded_buses = set()
    loads = circuit.Loads
    ae = circuit.ActiveCktElement
    i = loads.First
    while i > 0:
        loaded_buses.add(ae.BusNames[0].split('.')[0])
        i = loads.Next

    pv_buses = set()
    pvs = circuit.PVSystems
    i = pvs.First
    print(f"Поиск солнечных панелей... Найдено: {pvs.Count}")
    while i > 0:
        bus_name = ae.BusNames[0].split('.')[0]
        pv_buses.add(bus_name)
        i = pvs.Next

    bus_to_reg_names = {} 
    regs = circuit.RegControls
    idx = regs.First
    while idx > 0:
        reg_name = regs.Name
        transformer_name = regs.Transformer
        if transformer_name:
            circuit.SetActiveElement(f"Transformer.{transformer_name}")
            buses = circuit.ActiveCktElement.BusNames
            for b in buses:
                clean_b = b.split('.')[0]
                if clean_b not in bus_to_reg_names:
                    bus_to_reg_names[clean_b] = []
                if reg_name not in bus_to_reg_names[clean_b]:
                    bus_to_reg_names[clean_b].append(reg_name)
        idx = regs.Next

    groups = {
        'load':   {'x': [], 'y': [], 'names': [], 'base_color': 'red'},
        'reg':    {'x': [], 'y': [], 'names': [], 'base_color': 'orange'},
        'pv':     {'x': [], 'y': [], 'names': [], 'base_color': 'gold'}, 
        'normal': {'x': [], 'y': [], 'names': [], 'base_color': 'dodgerblue'}
    }

    all_bus_names = circuit.AllBusNames
    for bus in all_bus_names:
        if bus == "150" or (bus.startswith("s") and not bus.endswith("r") and bus not in ['s1a']):
            continue
        circuit.SetActiveBus(bus)
        x, y = circuit.ActiveBus.x, circuit.ActiveBus.y
        if x != 0 or y != 0:
            node_coords[bus] = (x, y)
            current_phases = set(circuit.ActiveBus.Nodes)
            bus_phases[bus] = current_phases
            
            if bus in pv_buses: g = 'pv'
            elif bus in loaded_buses: g = 'load'
            elif bus.endswith('r') or bus in ['61s', '610'] or 'open' in bus: g = 'reg'
            else: g = 'normal'
            
            idx = len(groups[g]['names'])
            bus_to_scatter[bus] = (g, idx)
            groups[g]['x'].append(x)
            groups[g]['y'].append(y)
            groups[g]['names'].append(bus)

    fig, ax = plt.subplots(figsize=(16, 14))
    plt.subplots_adjust(left=0.25, bottom=0.25) 
    ax.set_title("Карта IEEE 123: Тренажер и Анализ", fontsize=16)

    lines = circuit.Lines
    lc = lines.First
    while lc > 0:
        b1, b2 = lines.Bus1.split('.')[0], lines.Bus2.split('.')[0]
        circuit.SetActiveBus(b1); x1, y1 = circuit.ActiveBus.x, circuit.ActiveBus.y
        circuit.SetActiveBus(b2); x2, y2 = circuit.ActiveBus.x, circuit.ActiveBus.y
        ph = lines.Phases
        if (x1!=0 or y1!=0) and (x2!=0 or y2!=0):
            c, w, z = ('black', 2.0, 2) if ph>=3 else (('teal', 1.5, 2) if ph==2 else ('darkgray', 1.0, 1))
            ax.plot([x1, x2], [y1, y2], c=c, lw=w, zorder=z)
        lc = lines.Next

    ax.plot([],[], c='black', lw=2, label='3 Фазы')
    ax.plot([],[], c='teal', lw=1.5, label='2 Фазы')
    ax.plot([],[], c='darkgray', lw=1, label='1 Фаза')

    scatter_objects = {}
    lbl_map = {'load': 'Нагрузка', 'reg': 'Регулятор', 'pv': 'Солнечная панель', 'normal': 'Узел'}

    for g_name, g in groups.items():
        marker = 'o'
        if g_name == 'load': marker = '^'
        elif g_name == 'reg': marker = 's'
        elif g_name == 'pv': marker = (12, 1) 
        
        size = 250 if g_name == 'pv' else (80 if g_name in ['load', 'reg'] else 30)
        edge = 'orange' if g_name == 'pv' else ('black' if g_name!='normal' else None)
        
        sc = ax.scatter(g['x'], g['y'], s=size, c=g['base_color'], marker=marker, 
                        label=lbl_map[g_name], zorder=3, edgecolors=edge, picker=5)
        
        scatter_objects[g_name] = sc
        pickable_data[sc] = g['names']
        
        colors = sc.get_facecolors()
        if len(colors) == 1 and len(g['x']) > 1: colors = np.repeat(colors, len(g['x']), axis=0)
        elif len(colors) == 0: colors = np.empty((0, 4))
        original_colors[g_name] = colors

    for g_name, g in groups.items():
        for i, txt in enumerate(g['names']):
            fw = 'bold' if g_name in ['load', 'pv', 'reg'] else 'normal'
            display_text = f"  {txt}"
            if g_name == 'reg' and txt in bus_to_reg_names:
                reg_list = bus_to_reg_names[txt]
                reg_str = ",".join(reg_list)
                display_text = f"  {txt}\n  ({reg_str})" 
            ax.text(g['x'][i], g['y'][i], display_text, fontsize=10, fontweight=fw, ha='left', va='center')

    circuit.SetActiveBus("150")
    if circuit.ActiveBus.x != 0:
        ax.scatter(circuit.ActiveBus.x, circuit.ActiveBus.y, s=300, c='gold', marker='*', label='Источник', zorder=6, edgecolors='black')

    ax.legend(loc='upper right', shadow=True)
    ax.axis('equal')
    ax.grid(True, alpha=0.3)

    rax_mode = plt.axes([0.02, 0.70, 0.20, 0.12], facecolor='#f0f0f0')
    radio_mode = RadioButtons(rax_mode, ('Нормальный режим', 'Короткое замыкание', 'Обрыв линии'))
    translation_map = {'Нормальный режим': 'Normal', 'Короткое замыкание': 'Short Circuit', 'Обрыв линии': 'Open Line'}
    
    try:
        circles = getattr(radio_mode, 'circles', [])
        if not circles: circles = [p for p in rax_mode.patches if hasattr(p, 'center')]
        for i, circle in enumerate(circles):
            if i >= 3: break
            if hasattr(circle, 'set_visible'): circle.set_visible(False)
            if hasattr(circle, 'center'):
                cx, cy = circle.center
                if i == 0: rax_mode.scatter(cx, cy, s=100, c='dodgerblue', marker='o')
                elif i == 1: rax_mode.scatter(cx, cy, s=120, c='yellow', marker='X', edgecolors='red')
                elif i == 2: rax_mode.scatter(cx, cy, s=100, c='black', marker='s', edgecolors='white')
    except: pass

    plt.axes([0.02, 0.83, 0.20, 0.04], frameon=False)
    plt.text(0, 0, "РЕЖИМ РАБОТЫ:", fontsize=11, fontweight='bold')
    plt.axis('off')

    rax_phase = plt.axes([0.02, 0.52, 0.20, 0.12], facecolor='#f0f0f0')
    check_phase = CheckButtons(rax_phase, ('Фаза 1', 'Фаза 2', 'Фаза 3'), (True, False, False))
    plt.axes([0.02, 0.65, 0.20, 0.04], frameon=False)
    plt.text(0, 0, "ВЫБОР ФАЗ:", fontsize=11, fontweight='bold')
    plt.axis('off')

    rax_pv = plt.axes([0.02, 0.42, 0.20, 0.05], facecolor='#fffde7')
    check_pv = CheckButtons(rax_pv, ['Включить Солнечные Панели'], [True])

    btn_reset_ax = plt.axes([0.02, 0.35, 0.09, 0.05])
    btn_reset = Button(btn_reset_ax, 'Сброс', color='lightblue', hovercolor='0.9')
    
    btn_anal_ax = plt.axes([0.12, 0.35, 0.10, 0.05])
    btn_analyze = Button(btn_anal_ax, 'Анализ V', color='violet', hovercolor='magenta')

    slider_load_ax = plt.axes([0.25, 0.18, 0.65, 0.03], facecolor='#ffcccc') 
    slider_load = Slider(slider_load_ax, 'Нагрузка TestNode (кВт)', 0, 5000, valinit=0, valstep=100, color='red')

    slider_day_ax = plt.axes([0.25, 0.14, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    slider_day = Slider(slider_day_ax, 'День года', 1, 365, valinit=1, valstep=1, color='orange')
    
    date_text_ax = plt.axes([0.25, 0.10, 0.65, 0.03], frameon=False)
    date_text = date_text_ax.text(0.5, 0.5, "1 Января", ha='center', va='center', fontsize=12, fontweight='bold')
    date_text_ax.axis('off')

    slider_temp_ax = plt.axes([0.25, 0.06, 0.65, 0.03], facecolor='lightblue')
    slider_temp = Slider(slider_temp_ax, 'Температура (°C)', -10, 50, valinit=25.0, valstep=1, color='blue')

    def update_slider(val):
        day = int(val)
        sim_date = datetime.date(2020, 1, 1) + datetime.timedelta(days=day - 1)
        date_text.set_text(sim_date.strftime("%d %B"))
    slider_day.on_changed(update_slider)
    
    plot_interactive_topology.slider_day = slider_day
    plot_interactive_topology.slider_temp = slider_temp
    plot_interactive_topology.slider_load = slider_load

    blink_state = False
    def animate(frame):
        nonlocal blink_state
        blink_state = not blink_state
        
        faults = [bus for bus, state in node_states.items() if state['mode'] != 'Normal']
        nodes_blink_black = set()
        
        if faults:
            sc_faults = [n for n, s in node_states.items() if s['mode'] == 'Short Circuit']
            open_faults = [n for n, s in node_states.items() if s['mode'] == 'Open Line']
            
            affected = set()
            if open_faults: affected.update(get_downstream_nodes(open_faults))
            if sc_faults:
                affected.update(network_tree.keys())
                for ch in network_tree.values(): affected.update(ch)
            
            for f_node in faults:
                f_phases = node_states[f_node]['phases']
                for aff_node in affected:
                    node_ph = bus_phases.get(aff_node, set())
                    if not set(f_phases).isdisjoint(node_ph):
                        nodes_blink_black.add(aff_node)

        for g_name, sc in scatter_objects.items():
            new_colors = original_colors[g_name].copy()
            names = groups[g_name]['names']
            
            for i, name in enumerate(names):
                if name in nodes_blink_black:
                    if blink_state: new_colors[i] = [0.1, 0.1, 0.1, 1]
                
                elif name in voltage_issues['over']:
                    new_colors[i] = [1, 0.5, 0, 1] 
                elif name in voltage_issues['under']:
                    new_colors[i] = [0, 0.8, 1, 1] 

            sc.set_facecolors(new_colors)
        return scatter_objects.values()

    anim = FuncAnimation(fig, animate, interval=500, blit=False, cache_frame_data=False)
    plot_interactive_topology.anim = anim 

    def update_markers():
        global fault_markers
        for m in fault_markers: m.remove()
        fault_markers.clear()
        for bus, state in node_states.items():
            mode = state['mode']
            if bus not in node_coords: continue
            x, y = node_coords[bus]
            c, m = ('yellow', 'X') if mode=='Short Circuit' else ('black', 's')
            ec = 'red' if mode=='Short Circuit' else 'white'
            fault_markers.append(ax.scatter(x, y, s=180, c=c, marker=m, zorder=10, edgecolors=ec, linewidth=1.5))

    def on_plot_click(event):
        if event.inaxes != ax: return 
        
        click_x, click_y = event.x, event.y
        closest_bus = None
        min_dist = float('inf')
        for bus, (nx, ny) in node_coords.items():
            screen_pos = ax.transData.transform([(nx, ny)])[0]
            dist = np.sqrt((screen_pos[0] - click_x)**2 + (screen_pos[1] - click_y)**2)
            if dist < min_dist:
                min_dist = dist
                closest_bus = bus
        
        if closest_bus and min_dist < 15:
            # --- ЛОГИКА КЛИКОВ (ЛКМ vs ПКМ) ---
            active_mode = False
            if event.button == 1:   # ЛКМ (Левая) - Инспекция
                active_mode = False
            elif event.button == 3: # ПКМ (Правая) - Управление
                active_mode = True
            else:
                return # Игнорируем колесико и прочее
            # ----------------------------------

            mode_ru = radio_mode.value_selected
            mode_eng = translation_map[mode_ru]
            status = check_phase.get_status()
            selected_phases_list = [i+1 for i, s in enumerate(status) if s]
            pv_on = check_pv.get_status()[0]
            day = slider_day.val
            temp = slider_temp.val
            load_kw = slider_load.val
            
            if mode_eng == 'Normal':
                if closest_bus in node_states: del node_states[closest_bus]
            else:
                if not selected_phases_list:
                    print("⚠ Внимание: Не выбрана ни одна фаза!")
                    return
                node_states[closest_bus] = {'mode': mode_eng, 'phases': selected_phases_list}
            
            update_markers()
            
            # Запускаем симуляцию с нужным флагом active_control
            run_simulation_for_node(closest_bus, node_states, pv_enabled=pv_on, day_of_year=day, temperature=temp, test_load_kw=load_kw, active_control=active_mode)

    def on_reset(event):
        node_states.clear()
        voltage_issues['over'].clear()
        voltage_issues['under'].clear()
        clear_regulator_state()
        update_markers()

    def on_analyze(event):
        pv_on = check_pv.get_status()[0]
        day = slider_day.val
        temp = slider_temp.val
        load_kw = slider_load.val
        
        over, under = analyze_voltage_violations(node_states, pv_on, day, temp, test_load_kw=load_kw)
        voltage_issues['over'] = over
        voltage_issues['under'] = under

    fig.canvas.mpl_connect('button_press_event', on_plot_click)
    btn_reset.on_clicked(on_reset)
    btn_analyze.on_clicked(on_analyze)

    manager = plt.get_current_fig_manager()
    try: manager.window.state('zoomed')
    except:
        try: manager.window.showMaximized()
        except: pass

    print("Система готова.\n- ЛКМ: Инспекция узла (без изменений)\n- ПКМ: Активное управление (изменяет регуляторы)\n- Кнопка 'Анализ V' покажет зоны перенапряжения/просадки.")
    plt.show()

if __name__ == "__main__":
    plot_interactive_topology()