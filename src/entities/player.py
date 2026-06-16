# src/entities/player.py
import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, surface=None):
        super().__init__()
        # Создаем прозрачную поверхность для игрока размером 24x24
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 200

        # Рисуем КРАСНОЕ СЕРДЕЧКО внутри нашей поверхности
        # Нам понадобятся два круга сверху и треугольник снизу
        red = (255, 0, 0)
        # Левое ушко сердца
        pygame.draw.circle(self.image, red, (7, 8), 6)
        # Правое ушко сердца
        pygame.draw.circle(self.image, red, (17, 8), 6)
        # Нижняя часть сердца (треугольник)
        points = [(1, 10), (23, 10), (12, 23)]
        pygame.draw.polygon(self.image, red, points)

    def handle_input(self, keys):
        self.velocity_x = 0
        self.velocity_y = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.velocity_y = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.velocity_y = self.speed

    def update(self, walls):
        # Движение по X
        self.rect.x += self.velocity_x * 0.016
        self._resolve_collision(walls, 'x')
        
        # Движение по Y
        self.rect.y += self.velocity_y * 0.016
        self._resolve_collision(walls, 'y')

    def _resolve_collision(self, walls, direction):
        for wall in walls:
            if self.rect.colliderect(wall):
                if direction == 'x':
                    if self.velocity_x > 0:
                        self.rect.right = wall.left
                    if self.velocity_x < 0:
                        self.rect.left = wall.right
                if direction == 'y':
                    if self.velocity_y > 0:
                        self.rect.bottom = wall.top
                    if self.velocity_y < 0:
                        self.rect.top = wall.bottom