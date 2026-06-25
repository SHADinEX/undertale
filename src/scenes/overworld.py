import pygame
import json
import math
from src.settings import TILE_SIZE
from src.entities.player import Player
from src.entities.npc import NPC  
from src.systems.map_loader import load_map
from src.systems.dialog_system import DialogBox

class Portal:
    """Класс анимированного портала на базе Pygame-примитивов"""
    def __init__(self, rect, color=(140, 90, 190)):
        self.rect = rect
        self.center_x = rect.x + rect.width // 2
        self.center_y = rect.y + rect.height // 2
        self.animation_timer = 0.0
        self.base_color = color
        # Несколько оттенков для колец портала
        self.colors = [
            color,
            (max(0, color[0]-40), max(0, color[1]-40), max(0, color[2]-40)),
            (min(255, color[0]+40), min(255, color[1]+40), min(255, color[2]+40))
        ]

    def update(self, dt):
        # dt обычно передается в секундах, умножаем для комфортной скорости вращения
        self.animation_timer += dt * 6.0 

    def draw(self, screen):
        # 1. Черное ядро портала, которое слегка пульсирует по радиусу
        max_radius = self.rect.width // 2
        pulse = int(math.sin(self.animation_timer * 2) * 3)
        core_radius = max(5, max_radius + pulse)
        pygame.draw.circle(screen, (15, 10, 25), (self.center_x, self.center_y), core_radius)

        # 2. Рендеринг вращающихся дуг воронки
        for i, color in enumerate(self.colors):
            radius = core_radius - (i * 6)
            if radius > 4:
                # Смещаем фазу вращения для каждого кольца в противоположные стороны
                direction = 1 if i % 2 == 0 else -1
                start_angle = (self.animation_timer * direction) + (i * math.pi / 2)
                end_angle = start_angle + (math.pi * 1.3)  # Дуга занимает ~70% окружности
                
                arc_rect = pygame.Rect(
                    self.center_x - radius, 
                    self.center_y - radius, 
                    radius * 2, 
                    radius * 2
                )
                pygame.draw.arc(screen, color, arc_rect, start_angle, end_angle, 3)


class OverworldScene:
    def __init__(self, game, map_name):
        self.game = game
        self.map_name = map_name
        path_to_map = f"data/maps/{map_name}.json"
        
        self.map_data, self.walls = load_map(path_to_map)
        
        spawn_x = self.map_data["spawn"]["x"] * TILE_SIZE
        spawn_y = self.map_data["spawn"]["y"] * TILE_SIZE
        
        self.player = Player(spawn_x, spawn_y)
        
        self.sprites = pygame.sprite.Group()
        self.sprites.add(self.player)

        # --- Инициализируем NPC, Триггеры и Порталы ---
        self.npc_group = pygame.sprite.Group()
        self.triggers = []
        self.portals = [] # Список визуальных объектов для порталов
        self._load_map_objects()

        self.dialog_font = pygame.font.SysFont("Arial", 20)
        self.dialog = DialogBox(self.dialog_font)
        
        self.mode = 'explore'
        self.debug_mode = False

        self.game.audio.play_music('cave_theme')

    def _load_map_objects(self):
        """Парсит триггеры, порталы и NPC из текущих данных self.map_data"""
        self.npc_group.empty()
        self.triggers = []
        self.portals = [] # Сбрасываем порталы при обновлении карты

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
                
                # Сохраняем тип ("portal" или стандартный невидимый)
                trigger_type = t_data.get("type", "default")
                trigger_entry["type"] = trigger_type
                
                self.triggers.append(trigger_entry)

                # Если тип триггера — портал, создаем для него визуальный объект
                if trigger_type == "portal":
                    # Можно кастомизировать цвет в зависимости от врага
                    portal_color = (130, 110, 160) if t_data.get("enemy") == "dust_bunny" else (140, 90, 190)
                    self.portals.append(Portal(pixel_rect, portal_color))

        # 2. Загрузка NPC из JSON
        if "npcs" in self.map_data:
            for npc_data in self.map_data["npcs"]:
                nx = npc_data["x"] * TILE_SIZE
                ny = npc_data["y"] * TILE_SIZE
                
                npc_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
                npc_surface.fill((235, 210, 50)) 
                
                npc = NPC(nx, ny, npc_surface, npc_data["dialog_id"])
                self.npc_group.add(npc)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.mode == 'dialog':
                if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_e]:
                    self.dialog.advance()
                    self.game.audio.sfx('talk_blip')
                    if not self.dialog.active:
                        self.mode = 'explore'
            
            elif self.mode == 'explore':
                if event.key == pygame.K_e:
                    self._check_npc_interaction()
                elif event.key == pygame.K_F3:
                    self.debug_mode = not self.debug_mode
                    print(f"[DEBUG] Режим отладки: {self.debug_mode}")

    def _check_npc_interaction(self):
        for npc in self.npc_group:
            if npc.in_range(self.player.rect):
                try:
                    with open(f"data/dialogs/{npc.dialog_id}.json", "r", encoding="utf-8") as f:
                        dialog_data = json.load(f)
                    
                    self.dialog.start_dialog(dialog_data)
                    self.mode = 'dialog'
                    self.game.audio.sfx('talk_blip')
                    break
                except FileNotFoundError:
                    print(f"Ошибка: не найден файл data/dialogs/{npc.dialog_id}.json")

    def update(self, dt):
        if self.mode == 'explore':
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
            self.player.update(self.walls)
            
            # Обновляем внутреннюю анимацию каждого портала
            for portal in self.portals:
                portal.update(dt)

            self._check_triggers()  
            
        elif self.mode == 'dialog':
            self.dialog.update()

    def _check_triggers(self):
        for trigger in self.triggers:
            if trigger["rect"].colliderect(self.player.rect):
                if trigger["action"] == "battle":
                    enemy = trigger.get("enemy", "dust_bunny")
                    print(f"[💥 ПОРТАЛ] Игрока затянуло в аномалию! Начат бой с {enemy}...")
                    
                    self.game.change_scene("battle", enemy_id=enemy)
                    return  
                
                elif trigger["action"] == "warp":
                    next_map = trigger.get("map")
                    if next_map:
                        self._switch_room(next_map)
                    break

    def _switch_room(self, next_map_name):
        print(f"[WARP] Переход в комнату: {next_map_name}")
        path_to_map = f"data/maps/{next_map_name}.json"
        try:
            self.map_name = next_map_name
            self.map_data, self.walls = load_map(path_to_map)
            
            self.player.rect.x = self.map_data["spawn"]["x"] * TILE_SIZE
            self.player.rect.y = self.map_data["spawn"]["y"] * TILE_SIZE
            
            self._load_map_objects()
        except Exception as e:
            print(f"Не удалось загрузить карту {next_map_name}: {e}")

    def draw(self, screen):
        # Рисуем стены карты
        for wall in self.walls:
            pygame.draw.rect(screen, (40, 40, 50), wall)
            pygame.draw.rect(screen, (60, 60, 70), wall, 1)
            
        # 🌀 Рисуем анимированные порталы ПЕРЕД игроком и NPC, чтобы они были частью локации
        for portal in self.portals:
            portal.draw(screen)

        # Рисуем неигровых персонажей
        self.npc_group.draw(screen)
            
        # Рисуем игрока
        self.sprites.draw(screen)

        # --- ОТЛАДКА ---
        if self.debug_mode:
            for wall in self.walls:
                s = pygame.Surface((wall.width, wall.height), pygame.SRCALPHA)
                s.fill((255, 0, 0, 90))  
                screen.blit(s, (wall.x, wall.y))
            
            for trigger in self.triggers:
                tr_rect = trigger["rect"]
                s = pygame.Surface((tr_rect.width, tr_rect.height), pygame.SRCALPHA)
                # Порталы подсвечиваем сине-зеленым в дебаге, обычные — зеленым
                fill_color = (0, 180, 255, 120) if trigger.get("type") == "portal" else (0, 255, 0, 100)
                s.fill(fill_color)  
                screen.blit(s, (tr_rect.x, tr_rect.y))

        if self.mode == 'dialog':
            self.dialog.draw(screen)