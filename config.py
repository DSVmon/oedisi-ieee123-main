# -*- coding: utf-8 -*-

# --- LANGUAGE SETTINGS ---
# Установите 'EN' для английского или 'RU' для русского
LANGUAGE = 'EN'

def tr(en_text, ru_text):
    """
    Возвращает строку на выбранном языке.
    :param en_text: Текст на английском.
    :param ru_text: Текст на русском.
    :return: Строка на языке, указанном в переменной LANGUAGE.
    """
    if LANGUAGE == 'RU':
        return ru_text
    else:
        return en_text
