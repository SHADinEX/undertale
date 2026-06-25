# src/entities/npc.py
import pygame

class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, image, dialog_id):
        super().__init__()
        
        # Если вместо картинки передано что-то стандартное, генерируем дедулю кодом
        if image is None or (hasattr(image, 'get_width') and image.get_width() <= 50): 
            self.image = pygame.Surface((48, 48), pygame.SRCALPHA)
            self.rect = self.image.get_rect(topleft=(x, y))
            self.generate_art() # Запекаем дедушку прямо на текстуру
        else:
            self.image = image
            self.rect = self.image.get_rect(topleft=(x, y))
            
        self.dialog_id = dialog_id

    def generate_art(self):
        """Рисует милого дедулю с серой бородкой прямо на поверхности self.image"""
        self.image.fill((0, 0, 0, 0))  # Прозрачный фон
        
        w, h = self.image.get_width(), self.image.get_height()
        center_x = w // 2
        center_y = h // 2 - 2  # Смещаем чуть вверх, чтобы влезла борода
        head_radius = 14

        # Цвета
        skin_color = (240, 195, 150)   # Цвет кожи (теплый бежевый)
        beard_color = (180, 180, 185)  # Серая борода
        shadow_beard = (150, 150, 155) # Тень на бороде
        shirt_color = (85, 107, 47)    # Домашняя зеленая рубаха/жилетка

        # 1. ТЕНЬ ПОД ДЕДУЛЕЙ
        pygame.draw.ellipse(self.image, (30, 30, 30, 140), (4, h - 8, w - 8, 6))

        # 2. ТЕЛО / ПЛЕЧИ (Зелёная рубашка)
        pygame.draw.ellipse(self.image, shirt_color, (center_x - 16, center_y + 8, 32, 16))

        # 3. БОЛЬШАЯ СЕРАЯ БОРОДА (рисуем её чуть ниже подбородка, чтобы она ложилась на тело)
        # Основа бороды
        pygame.draw.circle(self.image, beard_color, (center_x, center_y + 12), 11)
        pygame.draw.circle(self.image, beard_color, (center_x - 6, center_y + 10), 8)
        pygame.draw.circle(self.image, beard_color, (center_x + 6, center_y + 10), 8)
        # Сужение бороды к низу (клинышек)
        pygame.draw.polygon(self.image, beard_color, [
            (center_x - 10, center_y + 12),
            (center_x + 10, center_y + 12),
            (center_x, center_y + 24)
        ])

        # 4. ГОЛОВА / ЛИЦО
        pygame.draw.circle(self.image, skin_color, (center_x, center_y), head_radius)

        # 5. СЕДЫЕ ВОЛОСЫ ПО БОКАМ (Лысина дедули)
        # Левый пучок волос
        pygame.draw.circle(self.image, beard_color, (center_x - head_radius + 2, center_y - 2), 5)
        # Правый пучок волос
        pygame.draw.circle(self.image, beard_color, (center_x + head_radius - 2, center_y - 2), 5)

        # 6. ГЛАЗА-ЩЁЛОЧКИ (Добрые, прищуренные глаза дедушки)
        # Левый глаз (дуга или линия)
        pygame.draw.line(self.image, (40, 40, 40), (center_x - 8, center_y - 2), (center_x - 3, center_y - 2), 2)
        # Правый глаз
        pygame.draw.line(self.image, (40, 40, 40), (center_x + 3, center_y - 2), (center_x + 8, center_y - 2), 2)

        # 7. ГУСТЫЕ БРОВИ (Нависают над глазами)
        pygame.draw.line(self.image, (220, 220, 225), (center_x - 10, center_y - 6), (center_x - 2, center_y - 5), 3)
        pygame.draw.line(self.image, (220, 220, 225), (center_x + 2, center_y - 5), (center_x + 10, center_y - 6), 3)

        # 8. КРУГЛЫЙ НОС КАРТОШКОЙ
        pygame.draw.circle(self.image, (225, 165, 120), (center_x, center_y + 2), 4)

        # 9. УСЫ (Поверх бороды, под носом)
        pygame.draw.ellipse(self.image, (200, 200, 205), (center_x - 10, center_y + 4, 20, 5))

    def in_range(self, player_rect):
        # Раздуваем хитбокс NPC во все стороны для проверки нажатия кнопки E
        zone = self.rect.inflate(48, 48)
        return zone.colliderect(player_rect)
        
    def draw(self, screen):
        """Отрисовка дедули на экран"""
        screen.blit(self.image, self.rect)