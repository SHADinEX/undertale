import pygame
import math

class Portal:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.center_x = x + width // 2
        self.center_y = y + height // 2
        self.animation_timer = 0
        
        # Цвета в стиле Undertale / Пыльного Кролика (фиолетово-серые, загадочные)
        self.colors = [(80, 50, 100), (120, 80, 150), (200, 180, 220)]

    def update(self, dt):
        # Увеличиваем таймер для анимации вращения и пульсации
        self.animation_timer += dt * 5  # скорость анимации

    def draw(self, surface):
        # 1. Рисуем темное ядро портала
        pulse_radius = (self.rect.width // 2) + int(math.sin(self.animation_timer) * 4)
        pygame.draw.circle(surface, (20, 10, 30), (self.center_x, self.center_y), pulse_radius)

        # 2. Рисуем закручивающиеся орбиты/частицы
        for i, color in enumerate(self.colors):
            # Каждое кольцо имеет свой радиус и смещение по фазе
            radius = pulse_radius - (i * 8)
            if radius > 0:
                # Рисуем пунктирный или сегментированный круг через дуги для эффекта вращения
                start_angle = self.animation_timer + (i * math.pi / 3)
                end_angle = start_angle + (math.pi * 1.5)
                
                # Ограничиваем rect для дуги
                arc_rect = pygame.Rect(
                    self.center_x - radius, 
                    self.center_y - radius, 
                    radius * 2, 
                    radius * 2
                )
                pygame.draw.arc(surface, color, arc_rect, start_angle, end_angle, 3)