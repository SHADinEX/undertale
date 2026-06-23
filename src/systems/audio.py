import os
import pygame
from pathlib import Path

class AudioManager:
    def __init__(self):
        # За базовую директорию берем корень проекта
        self.BASE_DIR = Path(__file__).resolve().parents[2]
        self.sound_enabled = True

        # Инициализируем звуковой движок Pygame с защитой от ошибок WASAPI
        if not pygame.mixer.get_init():
            try:
                # Стандартная инициализация (Pygame по умолчанию дергает WASAPI на Windows)
                pygame.mixer.init()
                print("[AUDIO] Звуковая система успешно инициализирована через WASAPI.")
            except pygame.error as e:
                print(f"[AUDIO] WASAPI не доступен ({e}). Пробуем переключиться на DirectSound...")
                try:
                    # Фоллбек: принудительно выставляем аудиодрайвер DirectSound для SDL
                    os.environ['SDL_AUDIODRIVER'] = 'dsound'
                    pygame.mixer.init()
                    print("[AUDIO] Звуковая система запущена через DirectSound.")
                except pygame.error as e_fallback:
                    # Если звуковых устройств вообще нет (или заблокированы), уходим в safe-режим
                    print(f"[AUDIO] КРИТИЧЕСКАЯ ОШИБКА: Аудиоустройства не найдены ({e_fallback}).")
                    print("[AUDIO] Игра запущена в беззвучном режиме. Вылетов не будет.")
                    self.sound_enabled = False

    def play_music(self, name, loop=True):
        """Запускает фоновую музыку (.ogg)"""
        if not self.sound_enabled:
            return

        path = self.BASE_DIR / f'assets/music/{name}.ogg'
        try:
            if path.exists():
                pygame.mixer.music.load(str(path))
                pygame.mixer.music.play(-1 if loop else 0)
            else:
                print(f"Предупреждение: Аудиофайл музыки {name}.ogg не найден по пути {path}")
        except pygame.error:
            print(f"Предупреждение: Аудиофайл музыки {name}.ogg поврежден или не может быть воспроизведен.")

    def sfx(self, name):
        """Воспроизводит короткий звуковой эффект (.wav)"""
        if not self.sound_enabled:
            return

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