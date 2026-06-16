# src/scenes/overworld.py
import pygame
import json
from src.settings import TILE_SIZE
from src.entities.player import Player
from src.systems.map_loader import load_map
from src.systems.dialog_system import DialogBox

class OverworldScene:
    def __init__(self, game, map_name):
        self.game = game
        path_to_map = f"data/maps/{map_name}.json"
        self.map_data, self.walls = load_map(path_to_map)
        
        # Находим координаты спавна из JSON-файла карты
        spawn_x = self.map_data["spawn"]["x"] * TILE_SIZE
        spawn_y = self.map_data["spawn"]["y"] * TILE_SIZE
        
        # Создаем игрока (наше красное сердечко)
        self.player = Player(spawn_x, spawn_y)
        
        self.sprites = pygame.sprite.Group()
        self.sprites.add(self.player)

        # Настраиваем шрифт и диалоговое окно
        self.dialog_font = pygame.font.SysFont("Arial", 20)
        self.dialog = DialogBox(self.dialog_font)
        
        # Стр. 12: Вводим официальный режим игры
        self.mode = 'explore'

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # Если мы в режиме диалога, листаем его
            if self.mode == 'dialog':
                if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_e]:
                    self.dialog.advance()
                    # Если после перелистывания диалог закрылся — возвращаем режим исследования
                    if not self.dialog.active:
                        self.mode = 'explore'
            
            # Если мы в режиме исследования, по клавише E можем начать диалог
            elif self.mode == 'explore':
                if event.key == pygame.K_e:
                    try:
                        with open("data/dialogs/hermit.json", "r", encoding="utf-8") as f:
                            dialog_data = json.load(f)
                        self.dialog.start_dialog(dialog_data)
                        # Переключаем режим на диалог!
                        self.mode = 'dialog'
                    except FileNotFoundError:
                        print("Ошибка: не найден файл data/dialogs/hermit.json")

    def update(self, dt):
        # Стр. 12: Что делает Overworld каждый кадр в зависимости от режима
        if self.mode == 'explore':
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
            self.player.update(self.walls)
            self._check_triggers() # Проверяем триггеры (бой, переходы)
            
        elif self.mode == 'dialog':
            self.dialog.update()

    def _check_triggers(self):
        # Стр. 12: Заготовка под проверку триггеров (будем программировать на следующих страницах)
        pass

    def draw(self, screen):
        # Рисуем стены карты
        for wall in self.walls:
            pygame.draw.rect(screen, (40, 40, 50), wall)
            pygame.draw.rect(screen, (60, 60, 70), wall, 1)
            
        # Рисуем игрока
        self.sprites.draw(screen)

        # Стр. 12: Рисуем окно диалога поверх, если режим соответствующий
        if self.mode == 'dialog':
            self.dialog.draw(screen)