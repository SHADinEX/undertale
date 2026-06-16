# src/game.py
from src.settings import COLORS
from src.scenes.overworld import OverworldScene  # 1. Обязательно добавляем этот импорт!

class Game:
    def __init__(self, screen):
        self.screen = screen
        # 2. Заменяем None на создание сцены мира с нашей картой
        self.scene = OverworldScene(self, 'cave_start') 

    def handle_event(self, event):
        if self.scene:
            self.scene.handle_event(event)

    def update(self, dt):
        if self.scene:
            self.scene.update(dt)

    def draw(self):
        # Сначала заливаем экран цветом фона (каждый кадр)
        self.screen.fill(COLORS['bg'])
        
        # Затем, если сцена есть, рисуем её поверх фона
        if self.scene:
            self.scene.draw(self.screen)