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
                
            game.handle_event(event)
            
        game.update(dt) # Передаем dt в обновление игры
        game.draw()
        pygame.display.flip()
        
    pygame.quit()

if __name__ == '__main__':
    main()