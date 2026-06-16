import pygame
from src.settings import WIDTH, HEIGHT, COLORS

class MenuScene:
    def __init__(self, game):
        self.game = game
        self.options = ['Новая игра', 'Продолжить', 'Выход']
        self.selected_index = 0  # Текущий выбранный пункт меню
        
        # Настраиваем шрифт для меню (встроенный в pygame, пока нет своего)
        self.font = pygame.font.SysFont('Arial', 32)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # Листаем меню вниз
            if event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            
            # Листаем меню вверх
            elif event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            
            # Нажали Enter (Выбор пункта)
            elif event.key == pygame.K_RETURN:
                if self.selected_index == 0:    # Новая игра
                    print("Запуск Новой игры...")
                    # Переключаем сцену на игровой мир (пока заглушка, класс OverworldScene создадим позже)
                    # self.game.change_scene(OverworldScene(self.game, 'cave_start'))
                
                elif self.selected_index == 1:  # Продолжить
                    print("Загрузка сохранения...")
                    # Тут будет логика загрузки файла сохранения
                
                elif self.selected_index == 2:  # Выход
                    pygame.quit()
                    import sys
                    sys.exit()

    def update(self):
        # Здесь обновляется логика сцены (если есть анимации в меню)
        pass

    def draw(self, screen):
        # Заливаем экран цветом фона из настроек
        screen.fill(COLORS['bg'])
        
        # Отрисовываем пункты меню
        for i, option in enumerate(self.options):
            # Если пункт выбран — красим его в цвет UI (белый), если нет — делаем серым
            color = COLORS['ui'] if i == self.selected_index else (100, 100, 100)
            
            # Маленький маркер (стрелочка) перед выбранным пунктом в стиле Undertale
            text_str = f"> {option}" if i == self.selected_index else f"  {option}"
            
            text_surface = self.font.render(text_str, True, color)
            
            # Выводим по центру экрана с отступом друг от друга
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50 + i * 50))
            screen.blit(text_surface, text_rect)