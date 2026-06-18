# src/entities/npc.py
import pygame

class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, image, dialog_id):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.dialog_id = dialog_id

    def in_range(self, player_rect):
        # Раздуваем хитбокс NPC во все стороны для проверки нажатия кнопки E
        zone = self.rect.inflate(48, 48)
        return zone.colliderect(player_rect)