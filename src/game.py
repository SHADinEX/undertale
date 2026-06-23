# src/game.py
from src.settings import COLORS
from src.scenes.overworld import OverworldScene
from src.scenes.battle import BattleScene
from src.systems.audio import AudioManager
from src.systems.save_system import SaveSystem

class Game:
    def __init__(self, screen):
        self.screen = screen
        
        # Инициализируем глобальные системы
        self.audio = AudioManager()
        self.save_system = SaveSystem()
        
        self.scene = None
        # Стартуем с оверворлда
        self.change_scene(OverworldScene(self, 'cave_start'))

    def change_scene(self, new_scene, **kwargs):
        """Меняет текущую сцену. Принимает как объекты сцен, так и текстовые ID."""
        
        if isinstance(new_scene, str) and new_scene == "battle":
            enemy_id = kwargs.get("enemy_id", "dust_bunny")
            self.scene = BattleScene(self, enemy_id)
            
        elif isinstance(new_scene, str) and new_scene == "overworld":
            self.scene = OverworldScene(self, 'cave_start')
            
        else:
            self.scene = new_scene
            
        if self.scene:
            print(f"-> {self.scene.__class__.__name__}")

    def save_current_game(self):
        """Собирает данные из игры и отправляет их в SaveSystem (F5)"""
        # Сохраняться можно только в оверворлде (как в оригинале)
        if not isinstance(self.scene, OverworldScene):
            print("[SAVE] Сохранение невозможно во время боя или диалога!")
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
        print(f"[SAVE] Игра сохранена! Карта: {self.scene.map_name}")

    def load_current_game(self):
        """Читает файл сохранения и восстанавливает мир (F9)"""
        data = self.save_system.load_game()
        if not data:
            print("[LOAD] Файл сохранения не найден.")
            return

        # 1. Восстанавливаем сцену мира на нужной карте
        map_name = data.get("current_map", "cave_start")
        self.change_scene(OverworldScene(self, map_name))

        # 2. Восстанавливаем позицию игрока
        pos = data.get("player_pos", {"x": 100, "y": 100})
        if self.scene and hasattr(self.scene, 'player'):
            self.scene.player.rect.x = pos["x"]
            self.scene.player.rect.y = pos["y"]
        
        print(f"[LOAD] Игра загружена! Карта: {map_name}")

    def handle_event(self, event):
        if self.scene:
            if hasattr(self.scene, 'handle_event'):
                self.scene.handle_event(event)
            elif hasattr(self.scene, 'handle_events'):
                self.scene.handle_events([event])

    def update(self, dt):
        if self.scene:
            self.scene.update(dt)

    def draw(self):
        # Заливаем фон
        self.screen.fill(COLORS.get('bg', (0, 0, 0)))
        
        if self.scene:
            try:
                # Рисуем сцену (передаем экран)
                self.scene.draw(self.screen)
            except TypeError:
                # Если в сцене метод draw не принимает аргументов
                self.scene.draw()