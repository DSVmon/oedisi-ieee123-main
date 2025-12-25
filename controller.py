import dss
import numpy as np

class GridController:
    def __init__(self, circuit):
        self.circuit = circuit
        self.min_voltage = 0.95
        self.max_voltage = 1.05
        # Список доступных регуляторов в системе (можно расширить)
        self.regulators = ['creg1a'] # Имена RegControl в OpenDSS
        
    def check_and_act(self, step_number):
        """
        Главный метод: измеряет напряжение и принимает меры.
        Возвращает список действий для лога.
        """
        actions = []
        
        # 1. Измерение: Получаем напряжения во всех узлах
        all_voltages = self.circuit.AllBusVmagPu
        all_names = self.circuit.AllNodeNames
        
        # Находим самое проблемное напряжение
        v_min = min(v for v in all_voltages if v > 0.01) # Игнорируем отключенные (0)
        v_max = max(all_voltages)
        
        # 2. Логика (Правила "Если -> То")
        
        # Сценарий А: Низкое напряжение (Просадка)
        if v_min < self.min_voltage:
            # Если напряжение упало, нужно ПОДНЯТЬ тап на регуляторе
            msg = self._change_tap(direction=+1)
            actions.append(f"Шаг {step_number} [LOW V={v_min:.3f}]: {msg}")
            
        # Сценарий Б: Высокое напряжение (Перенапряжение от Солнца)
        elif v_max > self.max_voltage:
            # Если напряжение высоко, нужно ОПУСТИТЬ тап
            msg = self._change_tap(direction=-1)
            actions.append(f"Шаг {step_number} [HIGH V={v_max:.3f}]: {msg}")
            
        return actions

    def _change_tap(self, direction):
        """
        Изменяет отпайку на первом доступном регуляторе.
        direction: +1 (поднять напряжение) или -1 (опустить напряжение)
        """
        reg_name = self.regulators[0] # Пока управляем только главным
        self.circuit.RegControls.Name = reg_name
        
        current_tap = self.circuit.RegControls.TapNumber
        max_tap = self.circuit.RegControls.MaxTapChange
        
        new_tap = current_tap + direction
        
        # Проверка физических ограничений (обычно +/- 16)
        if -16 <= new_tap <= 16:
            self.circuit.RegControls.TapNumber = new_tap
            return f"Регулятор {reg_name}: Tap {current_tap} -> {new_tap}"
        else:
            return f"Регулятор {reg_name}: Достигнут предел ({current_tap})!"