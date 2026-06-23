import pygame
import json
from src.settings import TILE_SIZE
from src.entities.player import Player
from src.entities.npc import NPC  
from src.systems.map_loader import load_map
from src.systems.dialog_system import DialogBox

class OverworldScene:
    def __init__(self, game, map_name):
        self.game = game
        self.map_name = map_name
        path_to_map = f"data/maps/{map_name}.json"
        
        # Предполагаем, что load_map возвращает (map_data, walls)
        self.map_data, self.walls = load_map(path_to_map)
        
        # Находим координаты спавна из JSON-файла карты
        spawn_x = self.map_data["spawn"]["x"] * TILE_SIZE
        spawn_y = self.map_data["spawn"]["y"] * TILE_SIZE
        
        # Создаем игрока (наше красное сердечко)
        self.player = Player(spawn_x, spawn_y)
        
        self.sprites = pygame.sprite.Group()
        self.sprites.add(self.player)

        # --- Инициализируем NPC и Триггеры ---
        self.npc_group = pygame.sprite.Group()
        self.triggers = []
        self._load_map_objects()

        # Настраиваем шрифт и диалоговое окно
        self.dialog_font = pygame.font.SysFont("Arial", 20)
        self.dialog = DialogBox(self.dialog_font)
        
        # Режимы игры: 'explore', 'dialog', 'battle'
        self.mode = 'explore'

        # --- ОТЛАДКА: Флаг для включения/выключения debug-режима ---
        self.debug_mode = False

        # --- АУДИО: Включаем музыку локации при старте сцены ---
        self.game.audio.play_music('cave_theme')

    def _load_map_objects(self):
        """Парсит триггеры и NPC из текущих данных self.map_data"""
        self.npc_group.empty()
        self.triggers = []

        # 1. Загрузка триггеров из JSON (переводим тайлы в пиксели)
        if "triggers" in self.map_data:
            for t_data in self.map_data["triggers"]:
                tx, ty, tw, th = t_data["rect"]
                pixel_rect = pygame.Rect(
                    tx * TILE_SIZE, 
                    ty * TILE_SIZE, 
                    tw * TILE_SIZE, 
                    th * TILE_SIZE
                )
                trigger_entry = {
                    "rect": pixel_rect,
                    "action": t_data["action"]
                }
                if "enemy" in t_data: trigger_entry["enemy"] = t_data["enemy"]
                if "map" in t_data: trigger_entry["map"] = t_data["map"]
                self.triggers.append(trigger_entry)

        # 2. Загрузка NPC из JSON (если они прописаны в карте)
        if "npcs" in self.map_data:
            for npc_data in self.map_data["npcs"]:
                nx = npc_data["x"] * TILE_SIZE
                ny = npc_data["y"] * TILE_SIZE
                
                # Создаем временный спрайт-заглушку (желтый квадрат 32x32), если нет ассета
                npc_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
                npc_surface.fill((235, 210, 50)) 
                
                npc = NPC(nx, ny, npc_surface, npc_data["dialog_id"])
                self.npc_group.add(npc)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # Если мы в режиме диалога, листаем его
            if self.mode == 'dialog':
                if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_e]:
                    self.dialog.advance()
                    
                    # --- АУДИО: Звук перелистывания/диалога ---
                    self.game.audio.sfx('talk_blip')
                    
                    # Если после перелистывания диалог закрылся — возвращаем режим исследования
                    if not self.dialog.active:
                        self.mode = 'explore'
            
            # Если мы в режиме исследования
            elif self.mode == 'explore':
                if event.key == pygame.K_e:
                    self._check_npc_interaction()
                
                # --- ОТЛАДКА: Переключение Debug-режима по кнопке F3 ---
                elif event.key == pygame.K_F3:
                    self.debug_mode = not self.debug_mode
                    print(f"[DEBUG] Режим отладки: {self.debug_mode}")

    def _check_npc_interaction(self):
        """Проверяет, стоит ли игрок рядом с каким-либо NPC для начала диалога"""
        for npc in self.npc_group:
            if npc.in_range(self.player.rect):
                try:
                    # Читаем файл диалога динамически по id, заданному у NPC
                    with open(f"data/dialogs/{npc.dialog_id}.json", "r", encoding="utf-8") as f:
                        dialog_data = json.load(f)
                    
                    self.dialog.start_dialog(dialog_data)
                    self.mode = 'dialog'
                    
                    # --- АУДИО: Звук начала разговора ---
                    self.game.audio.sfx('talk_blip')
                    break
                except FileNotFoundError:
                    print(f"Ошибка: не найден файл data/dialogs/{npc.dialog_id}.json")

    def update(self, dt):
        if self.mode == 'explore':
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
            self.player.update(self.walls)
            self._check_triggers()  # Проверяем наступание на триггеры
            
        elif self.mode == 'dialog':
            self.dialog.update()

    def _check_triggers(self):
        """Логика обработки наступания на зоны триггеров с переключением сцен"""
        for trigger in self.triggers:
            if trigger["rect"].colliderect(self.player.rect):
                
                # ⚔️ Триггер БИТВЫ
                if trigger["action"] == "battle":
                    enemy = trigger.get("enemy", "dust_bunny")
                    print(f"[СОБЫТИЕ] Начат бой с {enemy} из data/enemies.json!")
                    
                    # Передаем управление в менеджер сцен. Он сам создаст BattleScene
                    self.game.change_scene("battle", enemy_id=enemy)
                    return  # Мгновенно выходим, чтобы оверворлд заморозился
                
                # 🌀 Триггер ПЕРЕХОДА (Warp)
                elif trigger["action"] == "warp":
                    next_map = trigger.get("map")
                    if next_map:
                        self._switch_room(next_map)
                    break

    def _switch_room(self, next_map_name):
        """Меняет карту и перезагружает объекты окружения"""
        print(f"[WARP] Переход в комнату: {next_map_name}")
        path_to_map = f"data/maps/{next_map_name}.json"
        try:
            self.map_name = next_map_name
            self.map_data, self.walls = load_map(path_to_map)
            
            # Перемещаем игрока на новый спавн
            self.player.rect.x = self.map_data["spawn"]["x"] * TILE_SIZE
            self.player.rect.y = self.map_data["spawn"]["y"] * TILE_SIZE
            
            # Пересоздаем NPC и триггеры новой карты
            self._load_map_objects()
        except Exception as e:
            print(f"Не удалось загрузить карту {next_map_name}: {e}")

    def draw(self, screen):
        # Рисуем стены карты
        for wall in self.walls:
            pygame.draw.rect(screen, (40, 40, 50), wall)
            pygame.draw.rect(screen, (60, 60, 70), wall, 1)
            
        # Рисуем неигровых персонажей
        self.npc_group.draw(screen)
            
        # Рисуем игрока
        self.sprites.draw(screen)

        # --- ОТЛАДКА: Подсветка коллизий и триггеров при активном debug_mode ---
        if self.debug_mode:
            # 1. Стены (Красные прямоугольники)
            for wall in self.walls:
                s = pygame.Surface((wall.width, wall.height), pygame.SRCALPHA)
                s.fill((255, 0, 0, 90))  # Красный с прозрачностью 90
                screen.blit(s, (wall.x, wall.y))
            
            # 2. Триггеры (Зеленые прямоугольники)
            for trigger in self.triggers:
                tr_rect = trigger["rect"]
                s = pygame.Surface((tr_rect.width, tr_rect.height), pygame.SRCALPHA)
                s.fill((0, 255, 0, 100))  # Зеленый с прозрачностью 100
                screen.blit(s, (tr_rect.x, tr_rect.y))

        # Рисуем окно диалога поверх, если режим соответствующий
        if self.mode == 'dialog':
            self.dialog.draw(screen)