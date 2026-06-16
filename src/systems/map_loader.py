# src/systems/map_loader.py
import json
from pathlib import Path
import pygame
from src.settings import TILE_SIZE

def load_map(path):
    # __file__ — это путь к этому файлу (map_loader.py)
    # .parents[2] поднимает нас на 2 уровня вверх: из systems -> в src -> в корень my_undertale_game
    BASE_DIR = Path(__file__).resolve().parents[2]
    
    # Склеиваем точный абсолютный путь до файла JSON
    full_path = BASE_DIR / path
    
    # Читаем файл по железному абсолютному пути
    data = json.loads(full_path.read_text(encoding='utf-8'))
    walls = []
    w, h = data['width'], data['height']
    col = data['layers']['collision']
    
    for y in range(h):
        for x in range(w):
            if col[y * w + x]:
                walls.append(pygame.Rect(
                    x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    return data, walls