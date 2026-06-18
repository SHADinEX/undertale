# src/systems/audio.py
import pygame
from pathlib import Path

class AudioManager:
    def __init__(self):
        # Инициализируем звуковой движок Pygame, если он еще не запущен
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        # За базовую директорию берем корень проекта
        self.BASE_DIR = Path(__file__).resolve().parents[2]

    def play_music(self, name, loop=True):
        """Запускает фоновую музыку (.ogg)"""
        path = self.BASE_DIR / f'assets/music/{name}.ogg'
        try:
            if path.exists():
                pygame.mixer.music.load(str(path))
                pygame.mixer.music.play(-1 if loop else 0)
            else:
                print(f"Предупреждение: Аудиофайл музыки {name}.ogg не найден по пути {path}")
        except pygame.error:
            print(f"Предупреждение: Аудиофайл музыки {name}.ogg поврежден.")

    def sfx(self, name):
        """Воспроизводит короткий звуковой эффект (.wav)"""
        path = self.BASE_DIR / f'assets/sfx/{name}.wav'
        try:
            # Проверяем, существует ли файл, чтобы предотвратить FileNotFoundError в Pygame
            if path.exists():
                sound = pygame.mixer.Sound(str(path))
                sound.play()
            else:
                print(f"Предупреждение: Звуковой эффект {name}.wav не найден по пути {path}")
        except pygame.error as e:
            print(f"Предупреждение: Не удалось воспроизвести звук {name}: {e}")