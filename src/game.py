# src/game.py
from src.settings import COLORS
from src.scenes.overworld import OverworldScene
from src.systems.audio import AudioManager
from src.systems.save_system import SaveSystem

class Game:
    def __init__(self, screen):
        self.screen = screen
        
        # Инициализируем глобальные системы
        self.audio = AudioManager()
        self.save_system = SaveSystem()
        
        # Сцена инициализируется через специальный метод с логированием
        self.scene = None
        self.change_scene(OverworldScene(self, 'cave_start'))

    def change_scene(self, new_scene):
        """Меняет текущую сцену и логирует переход в консоль для отладки"""
        self.scene = new_scene
        if self.scene:
            print(f"-> {self.scene.__class__.__name__}")

    def save_current_game(self):
        """Собирает данные из игры и отправляет их в файл savegame.json"""
        if not self.scene: 
            return

        state = {
            "current_map": self.scene.map_name,
            "player_pos": {
                "x": self.scene.player.rect.x,
                "y": self.scene.player.rect.y
            },
            "stats": {
                "hp": 20,
                "max_hp": 20,
                "lv": 1
            },
            "inventory": [],
            "plot_flags": {}
        }
        self.save_system.save_game(state)

    def load_current_game(self):
        """Читает файл сохранения и полностью восстанавливает игровой мир"""
        data = self.save_system.load_game()
        if not data:
            print("[ЗАГРУЗКА] Файл не найден или пуст, продолжаем текущую игру.")
            return False

        # 1. Восстанавливаем карту, используя метод с логированием сцены
        map_name = data.get("current_map", "cave_start")
        self.change_scene(OverworldScene(self, map_name))

        # 2. Восстанавливаем точную позицию игрока (сердечка)
        pos = data.get("player_pos", {"x": 100, "y": 100})
        self.scene.player.rect.x = pos["x"]
        self.scene.player.rect.y = pos["y"]
        
        print("[ЗАГРУЗКА] Игра успешно восстановлена с сохранения!")
        return True

    def handle_event(self, event):
        if self.scene:
            self.scene.handle_event(event)

    def update(self, dt):
        if self.scene:
            self.scene.update(dt)

    def draw(self):
        self.screen.fill(COLORS['bg'])
        if self.scene:
            self.scene.draw(self.screen)