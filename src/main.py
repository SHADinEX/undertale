# src/main.py
import pygame
import sys

# Позволяет Python правильно находить модули в папке src при запуске из корня
sys.path.append('.') 

from src.settings import WIDTH, HEIGHT, FPS, TITLE
from src.game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    
    game = Game(screen) # Передаем экран в класс Game
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0 # Считаем Delta Time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # --- СИСТЕМА СОХРАНЕНИЙ: Обработка клавиш F5 и F9 ---
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F5:
                    game.save_current_game()  # Вызываем сохранение
                elif event.key == pygame.K_F9:
                    game.load_current_game()  # Вызываем загрузку
            # ----------------------------------------------------
                
            game.handle_event(event)
            
        game.update(dt) # Передаем dt в обновление игры
        game.draw()
        pygame.display.flip()
        
    pygame.quit()

if __name__ == '__main__':
    main()