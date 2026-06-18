# src/systems/save_system.py
import json
from pathlib import Path

class SaveSystem:
    def __init__(self):
        # Файл сохранения будет лежать прямо в корне проекта
        self.BASE_DIR = Path(__file__).resolve().parents[2]
        self.SAVE_PATH = self.BASE_DIR / 'savegame.json'

    def save_game(self, state):
        """Сохраняет переданный словарь состояния игрока в JSON"""
        try:
            self.SAVE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
            print("[СОХРАНЕНИЕ] Игра успешно сохранена в savegame.json!")
        except Exception as e:
            print(f"[ОШИБКА СОХРАНЕНИЯ] Не удалось записать файл: {e}")

    def load_game(self):
        """Загружает данные из файла, если он существует"""
        if self.SAVE_PATH.exists():
            try:
                data = json.loads(self.SAVE_PATH.read_text(encoding='utf-8'))
                print("[ЗАГРУЗКА] Данные игрока успешно прочитаны!")
                return data
            except Exception as e:
                print(f"[ОШИБКА ЗАГРУЗКИ] Файл поврежден: {e}")
                return None
        print("[ЗАГРУЗКА] Файл сохранения не найден.")
        return None