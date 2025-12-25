import dss
import pathlib
import os

def run_test():
    dss_engine = dss.DSS
    text = dss_engine.Text
    circuit = dss_engine.ActiveCircuit
    solution = circuit.Solution

    current_dir = pathlib.Path(__file__).parent.resolve()
    master_file = current_dir / "qsts" / "master.dss"

    results = []

    scenarios = [
        {"name": "1. База (0%, 0kW)", "mult": 1.0, "add_kw": 0.0},
        {"name": "2. Конфиг (+20%, 0kW)", "mult": 1.2, "add_kw": 0.0},
        {"name": "3. Слайдер (0%, 1000kW)", "mult": 1.0, "add_kw": 1000.0},
        {"name": "4. Комбо (+20%, 1000kW)", "mult": 1.2, "add_kw": 1000.0},
    ]

    print(f"{'Сценарий':<25} | {'Множитель':<10} | {'Доп. кВт':<10} | {'Total Power (kW)':<15} | {'Delta (от Базы)'}")
    print("-" * 80)

    base_power = 0

    for sc in scenarios:
        # 1. Compile
        text.Command = f'Compile "{master_file}"'

        # 2. Add custom load (Slider simulation)
        if sc["add_kw"] > 0:
            # Создаем нагрузку
            text.Command = f"New Load.Test_Experiment_Load Bus1=TestNode.1.2.3 Phases=3 kV=4.16 kW={sc['add_kw']} PF=1.0 Model=1"

        # 3. Set LoadMult (Config simulation)
        text.Command = f"Set LoadMult={sc['mult']}"

        # 4. Solve (Snapshot)
        solution.Solve()

        # 5. Measure
        try:
            p_total = abs(circuit.TotalPower[0])
        except:
            p_total = 0.0

        if sc["name"].startswith("1."):
            base_power = p_total

        delta = p_total - base_power
        results.append((sc['name'], p_total))

        print(f"{sc['name']:<25} | {sc['mult']:<10} | {sc['add_kw']:<10} | {p_total:<16.2f} | {delta:+.2f}")

    # Анализ
    p_base = results[0][1]
    p_config = results[1][1]
    p_slider = results[2][1]
    p_combo = results[3][1]

    print("\n--- АНАЛИЗ ---")

    diff_config = p_config - p_base
    expected_config = p_base * 0.2
    print(f"Эффект конфига (+20%): +{diff_config:.2f} кВт (Ожидалось ~{expected_config:.2f})")

    diff_slider = p_slider - p_base
    print(f"Эффект слайдера (1000кВт): +{diff_slider:.2f} кВт (Ожидалось ~1000 + потери)")

    diff_combo = p_combo - p_base
    print(f"Эффект комбо: +{diff_combo:.2f} кВт")

    # Проверка гипотезы:
    # Если LoadMult действует на ВСЕ нагрузки (включая новую), то прирост от слайдера тоже должен умножиться на 1.2
    # То есть ожидаем: (Base * 1.2) + (1000 * 1.2) = p_config + 1200

    theory_A = p_config + (1000 * 1.2) # Если множитель действует на слайдер
    theory_B = p_config + 1000         # Если множитель НЕ действует на слайдер

    print(f"\nГипотеза А (Множитель умножает и слайдер): {theory_A:.2f} кВт")
    print(f"Гипотеза Б (Множитель только на базу):     {theory_B:.2f} кВт")
    print(f"ФАКТ:                                      {p_combo:.2f} кВт")

    if abs(p_combo - theory_A) < abs(p_combo - theory_B):
        print("\n✅ ВЫВОД: LoadMult умножает ВСЕ нагрузки, включая добавленную слайдером.")
    else:
        print("\n✅ ВЫВОД: LoadMult НЕ влияет на нагрузку слайдера (она добавляется абсолютно).")

if __name__ == "__main__":
    run_test()