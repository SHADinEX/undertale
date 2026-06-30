import pygame
import random
import math

class BattleScene:
    def __init__(self, game, enemy_id):
        self.game = game
        self.enemy_id = enemy_id
        self.screen = game.screen
        
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        
        print(f"[BATTLE] Начат пошаговый бой против {self.enemy_id.upper()}!")
        self.game.audio.play_music("battle_theme", loop=True)
        
        # --- БАЛАНС ---
        self.player_max_hp = 12   
        self.player_hp = self.player_max_hp
        self.game_over = False  
        
        self.shield_charges = 0  
        self.enemy_hp = 5         
        self.enemy_damage_timer = 0.0
        self.enemy_sneezed = False  
        self.player_is_moving = False
        
        # --- ОБЛАЧКО РЕПЛИК КРОЛИКА ---
        self.bubble_text = ""         # Текст внутри облачка
        self.bubble_timer = 0.0       # Таймер показа (в секундах)
        
        # --- СИСТЕМА СМЕРТИ ИГРОКА (КРАСНОЕ СЕРДЦЕ) ---
        self.death_state = 'alive' # 'alive', 'frozen', 'shattered'
        self.death_timer = 0.0
        self.shards = [] # Осколки сердечка
        
        # --- СИСТЕМА ПОБЕДЫ НАД БОССОМ (БЕЛОЕ СЕРДЦЕ) ---
        self.victory_state = 'alive' # 'alive', 'fading', 'heart_shake', 'heart_shattered'
        self.victory_timer = 0.0
        self.enemy_alpha = 255       # Прозрачность кролика для эффекта испарения
        self.boss_shards = []        # Белые осколки сердца босса
        
        # --- РАМКИ БОЯ ---
        self.menu_width = 460
        self.menu_height = 140
        self.defense_width = 160   
        self.defense_height = 160  
        
        self.box_rect = pygame.Rect(0, 0, self.menu_width, self.menu_height)
        self.box_rect.center = (self.screen_width // 2, int(self.screen_height * 0.45))
        
        self.buttons = ["FIGHT", "ACT", "ITEM"]
        self.current_button_index = 0
        self.battle_state = 'main_menu' 
        
        self.act_options = ["Оценить", "Поговорить", "Угрожать"]
        self.current_act_index = 0
        self.displayed_text = f"* Появился {self.enemy_id.upper()}!\n* Пыль летит во все стороны."
        
        self.strike_bar_x = self.box_rect.x + 10  
        self.strike_speed = 400                    
        self.center_target_x = self.box_rect.centerx  
        
        # --- НАСТРОЙКИ СЕРДЦА ---
        self.heart_pos = pygame.Vector2(self.box_rect.center)
        self.heart_speed = 180    
        self.heart_size = 16 
        
        # --- ХОД БОССА ---
        self.bullets = []
        self.enemy_turn_timer = 0.0
        self.attack_wave_timer = 0.0
        self.attack_pattern = 0   
        
        button_y = int(self.screen_height * 0.82) 
        spacing = self.screen_width // 3
        start_x = (spacing - 100) // 2 
        
        self.button_positions = [
            (start_x + i * spacing, button_y) for i in range(len(self.buttons))
        ]
        
        self.font = pygame.font.SysFont("Courier New", 18, bold=True)
        self.game_over_font = pygame.font.SysFont("Courier New", 36, bold=True)

    def trigger_death(self):
        """ Запускает цепочку анимации смерти игрока """
        self.death_state = 'frozen'
        self.death_timer = 0.0
        self.game.audio.play_music(None)
        self.game.audio.sfx("blip")

    def create_shards(self):
        """ Генерирует разлетающиеся красные осколки """
        self.death_state = 'shattered'
        self.death_timer = 0.0
        self.game.audio.sfx("blip")
        hx, hy = self.heart_pos.x + self.heart_size // 2, self.heart_pos.y + self.heart_size // 2
        for _ in range(6):
            self.shards.append({
                "pos": pygame.Vector2(hx, hy),
                "vel": pygame.Vector2(random.uniform(-150, 150), random.uniform(-250, -50)),
                "gravity": 400
            })

    def trigger_boss_victory(self):
        """ Запускает катсцену уничтожения босса """
        self.victory_state = 'fading'
        self.victory_timer = 0.0
        self.game.audio.play_music(None) 

    def create_boss_shards(self):
        """ Взрыв белого сердца босса на кусочки """
        self.victory_state = 'heart_shattered'
        self.victory_timer = 0.0
        self.game.audio.sfx("blip") 
        
        bx = self.screen_width // 2
        by = self.box_rect.top - 65
        for _ in range(8):
            self.boss_shards.append({
                "pos": pygame.Vector2(bx, by),
                "vel": pygame.Vector2(random.uniform(-180, 180), random.uniform(-180, 180)),
                "gravity": 200
            })

    def reset_battle(self):
        """ Полный сброс параметров боя на начальные (Перезагрузка на R) """
        self.player_hp = self.player_max_hp
        self.enemy_hp = 5
        self.game_over = False
        self.shield_charges = 0
        self.enemy_sneezed = False
        self.enemy_damage_timer = 0.0
        
        self.bubble_text = ""
        self.bubble_timer = 0.0
        
        self.death_state = 'alive'
        self.death_timer = 0.0
        self.shards.clear()
        
        self.victory_state = 'alive'
        self.victory_timer = 0.0
        self.enemy_alpha = 255
        self.boss_shards.clear()
        
        self.bullets.clear()
        self.current_button_index = 0
        self.battle_state = 'main_menu'
        self.displayed_text = f"* Бой перезапущен!\n* Пыльный Кролик снова перед вами."
        
        self.box_rect.size = (self.menu_width, self.menu_height)
        self.box_rect.center = (self.screen_width // 2, int(self.screen_height * 0.45))
        self.heart_pos = pygame.Vector2(self.box_rect.center)
        
        # Перезапускаем музыку
        self.game.audio.play_music("battle_theme", loop=True)

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN: return

        # ХОТКЕЙ ПЕРЕЗАПУСКА: Теперь работает как при Game Over, так и в любой момент боя
        if event.key == pygame.K_r:
            self.game.audio.sfx("blip")
            self.reset_battle()
            return

        if self.game_over:
            if event.key == pygame.K_ESCAPE:
                self.game.change_scene("overworld")
            return

        if self.death_state != 'alive' or self.victory_state != 'alive':
            return

        if event.key == pygame.K_ESCAPE:
            self.game.change_scene("overworld")
            return
        
        if self.battle_state == 'main_menu':
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.current_button_index = (self.current_button_index - 1) % len(self.buttons)
                self.game.audio.sfx("blip")
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.current_button_index = (self.current_button_index + 1) % len(self.buttons)
                self.game.audio.sfx("blip")
            elif event.key in (pygame.K_z, pygame.K_RETURN):
                self.game.audio.sfx("blip")
                self.confirm_action()

        elif self.battle_state == 'act_menu':
            if event.key in (pygame.K_UP, pygame.K_w, pygame.K_LEFT, pygame.K_a):
                self.current_act_index = (self.current_act_index - 1) % len(self.act_options)
                self.game.audio.sfx("blip")
            elif event.key in (pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d):
                self.current_act_index = (self.current_act_index + 1) % len(self.act_options)
                self.game.audio.sfx("blip")
            elif event.key in (pygame.K_x, pygame.K_BACKSPACE):
                self.battle_state = 'main_menu'
                self.game.audio.sfx("blip")
            elif event.key in (pygame.K_z, pygame.K_RETURN):
                self.game.audio.sfx("blip")
                self.confirm_act_action()
                
        elif self.battle_state in ('fight_timing', 'item_timing'):
            if event.key in (pygame.K_z, pygame.K_RETURN):
                if self.battle_state == 'fight_timing': self.calculate_damage()
                else: self.calculate_item_use()

        elif self.battle_state == 'text_display':
            if event.key in (pygame.K_z, pygame.K_RETURN):
                self.game.audio.sfx("blip")
                if self.enemy_hp <= 0:
                    self.trigger_boss_victory() 
                    return
                self.start_enemy_turn()

    def confirm_action(self):
        selected = self.buttons[self.current_button_index]
        if selected == "FIGHT":
            self.strike_bar_x = self.box_rect.x + 10
            self.battle_state = 'fight_timing'
        elif selected == "ACT":
            self.battle_state = 'act_menu'
            self.current_act_index = 0
        elif selected == "ITEM":
            self.strike_bar_x = self.box_rect.x + 10
            self.battle_state = 'item_timing'

    def confirm_act_action(self):
        chosen_act = self.act_options[self.current_act_index]
        if chosen_act == "Оценить":
            self.displayed_text = f"* DUST BUNNY - АТК 3 ЗАЩ 10.\n* Готов биться до последнего."
            self.bubble_text = "Эй, не смотри на\nменя так пристально!"
            self.bubble_timer = 2.0  
        elif chosen_act == "Поговорить":
            self.enemy_sneezed = True
            self.displayed_text = f"* Вы вежливо завели беседу.\n* Он не в духе, поднялось много пыли!"
            self.bubble_text = "А-апчхи! Не заговаривай\nмне зубы!"
            self.bubble_timer = 2.0
        elif chosen_act == "Угрожать":
            self.enemy_hp = 0  
            self.displayed_text = "* Вы пригрозили пылесосом.\n* Пыльный Кролик в ужасе исчез!"
            self.bubble_text = "ТОЛЬКО НЕ ПЫЛЕСОС!!!"
            self.bubble_timer = 1.5
        self.battle_state = 'text_display'

    def calculate_damage(self):
        distance = abs(self.strike_bar_x - self.center_target_x)
        max_distance = self.box_rect.width / 2
        accuracy = max(0.0, 1.0 - (distance / max_distance))
        
        if accuracy > 0.88:
            self.enemy_hp -= 2  
            self.enemy_damage_timer = 0.6  
            self.displayed_text = f"* ОТЛИЧНЫЙ УДАР!\n* Нанесено 2 урона комку пыли!"
        elif accuracy > 0.35:
            self.enemy_hp -= 1  
            self.enemy_damage_timer = 0.6  
            self.displayed_text = f"* Хорошее попадание шваброй.\n* Снято 1 HP."
        else:
            self.displayed_text = f"* Вы махнули мимо!\n* Кролик лениво увернулся."
            
        if self.enemy_hp <= 0:
            self.displayed_text = f"* Вы полностью вымели Пыльного Кролика!\n* Победа!"

        self.battle_state = 'text_display'

    def calculate_item_use(self):
        distance = abs(self.strike_bar_x - self.center_target_x)
        max_distance = self.box_rect.width / 2
        accuracy = max(0.0, 1.0 - (distance / max_distance))
        
        if accuracy > 0.85:
            self.shield_charges = 3  
            self.displayed_text = f"* Идеальный тайминг!\n* Вы развернули липкую паутину (Защита: 3 удара)."
        else:
            self.player_hp = min(self.player_max_hp, self.player_hp + 4)
            self.displayed_text = f"* Вы съели старую конфетку из кармана.\n* Восстановлено 4 HP!"
            
        self.battle_state = 'text_display'

    def generate_bullet_type(self):
        rand = random.random()
        if rand < 0.15: return 'heal'
        elif rand < 0.35: return 'orange'
        return 'normal'

    def start_enemy_turn(self):
        self.battle_state = 'enemy_turn'
        self.enemy_turn_timer = 4.5  
        self.attack_wave_timer = 0.0
        self.bullets.clear()
        
        self.attack_pattern = random.randint(0, 2)
        
        self.box_rect.size = (self.defense_width, self.defense_height)
        self.box_rect.center = (self.screen_width // 2, int(self.screen_height * 0.45))
        self.heart_pos = pygame.Vector2(self.box_rect.center)

    def end_enemy_turn(self):
        self.battle_state = 'main_menu'
        self.box_rect.size = (self.menu_width, self.menu_height)
        self.box_rect.center = (self.screen_width // 2, int(self.screen_height * 0.45))

    def update(self, dt):
        if self.bubble_timer > 0:
            self.bubble_timer -= dt
            if self.bubble_timer < 0:
                self.bubble_timer = 0.0

        if self.death_state == 'frozen':
            self.death_timer += dt
            if self.death_timer >= 0.8:
                self.create_shards()
            return
        elif self.death_state == 'shattered':
            self.death_timer += dt
            for shard in self.shards:
                shard["pos"] += shard["vel"] * dt
                shard["vel"].y += shard["gravity"] * dt
            if self.death_timer >= 1.5:
                self.death_state = 'alive'
                self.game_over = True
            return

        if self.victory_state == 'fading':
            self.victory_timer += dt
            self.enemy_alpha = max(0, 255 - int(self.victory_timer * 180)) 
            if self.enemy_alpha <= 0:
                self.victory_state = 'heart_shake'
                self.victory_timer = 0.0
            return
            
        elif self.victory_state == 'heart_shake':
            self.victory_timer += dt
            if self.victory_timer >= 4.0: 
                self.create_boss_shards()
            return
            
        elif self.victory_state == 'heart_shattered':
            self.victory_timer += dt
            for shard in self.boss_shards:
                shard["pos"] += shard["vel"] * dt
                shard["vel"].y += shard["gravity"] * dt
            if self.victory_timer >= 1.2: 
                self.game.change_scene("overworld")
            return

        if self.game_over: return

        if self.enemy_damage_timer > 0:
            self.enemy_damage_timer -= dt

        if self.battle_state in ('fight_timing', 'item_timing'):
            self.strike_bar_x += self.strike_speed * dt
            if self.strike_bar_x >= self.box_rect.right - 10:
                self.displayed_text = f"* Слишком долго целились!\n* Кролик легко увернулся."
                self.battle_state = 'text_display'

        elif self.battle_state == 'enemy_turn':
            self.enemy_turn_timer -= dt
            if self.enemy_turn_timer <= 0:
                self.enemy_sneezed = False
                self.end_enemy_turn()
                return

            keys = pygame.key.get_pressed()
            move_vec = pygame.Vector2(0, 0)
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:  move_vec.x -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: move_vec.x += 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:    move_vec.y -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:  move_vec.y += 1
            
            self.player_is_moving = (move_vec.length_squared() > 0)
            
            if self.player_is_moving:
                self.heart_pos += move_vec.normalize() * self.heart_speed * dt

            padding = 6
            if self.heart_pos.x < self.box_rect.left + padding:  self.heart_pos.x = self.box_rect.left + padding
            if self.heart_pos.x > self.box_rect.right - padding - self.heart_size: self.heart_pos.x = self.box_rect.right - padding - self.heart_size
            if self.heart_pos.y < self.box_rect.top + padding:   self.heart_pos.y = self.box_rect.top + padding
            if self.heart_pos.y > self.box_rect.bottom - padding - self.heart_size: self.heart_pos.y = self.box_rect.bottom - padding - self.heart_size

            self.attack_wave_timer += dt
            spawn_cooldown = 0.15 if self.enemy_sneezed else 0.28

            if self.attack_pattern == 0:
                if self.attack_wave_timer >= spawn_cooldown:
                    self.attack_wave_timer = 0.0
                    for i in range(2):
                        bx = self.box_rect.left + 20 + (i * 60) + (int(self.enemy_turn_timer * 30) % 30)
                        b_type = self.generate_bullet_type()
                        speed = 160 if not self.enemy_sneezed else 240
                        if b_type == 'heal': speed *= 0.75
                        
                        self.bullets.append({
                            "pos": pygame.Vector2(bx, self.box_rect.top - 5),
                            "vel": pygame.Vector2(0, speed),
                            "type": b_type
                        })

            elif self.attack_pattern == 1:
                if self.attack_wave_timer >= spawn_cooldown * 1.8:
                    self.attack_wave_timer = 0.0
                    h = random.randint(self.box_rect.top + 20, self.box_rect.bottom - 20)
                    b_type = self.generate_bullet_type()
                    speed = 160 if not self.enemy_sneezed else 240
                    if b_type == 'heal': speed *= 0.75

                    self.bullets.append({
                        "pos": pygame.Vector2(self.box_rect.left - 5, h),
                        "vel": pygame.Vector2(speed, 0),
                        "type": b_type
                    })

            elif self.attack_pattern == 2:
                if self.attack_wave_timer >= spawn_cooldown * 2.5:
                    self.attack_wave_timer = 0.0
                    b_pos = pygame.Vector2(self.box_rect.centerx, self.box_rect.top + 5)
                    target_dir = (self.heart_pos - b_pos)
                    if target_dir.length() > 0: target_dir = target_dir.normalize()
                    else: target_dir = pygame.Vector2(0, 1)
                        
                    b_type = self.generate_bullet_type()
                    speed = 130 if not self.enemy_sneezed else 200
                    if b_type == 'heal': speed *= 0.75

                    self.bullets.append({
                        "pos": b_pos,
                        "vel": target_dir * speed,
                        "type": b_type
                    })

            heart_rect = pygame.Rect(int(self.heart_pos.x), int(self.heart_pos.y), self.heart_size, self.heart_size)
            
            for bullet in self.bullets[:]:
                bullet["pos"] += bullet["vel"] * dt  
                bullet_rect = pygame.Rect(int(bullet["pos"].x), int(bullet["pos"].y), 7, 7)
                
                if bullet_rect.colliderect(heart_rect):
                    b_type = bullet.get("type", "normal")
                    
                    if b_type == "heal":
                        self.game.audio.sfx("blip")
                        if self.shield_charges > 0: self.shield_charges += 1
                        else: self.player_hp = min(self.player_max_hp, self.player_hp + 1)
                    
                    elif b_type == "orange":
                        if not self.player_is_moving:
                            if self.shield_charges > 0: self.shield_charges -= 1
                            else: self.player_hp -= 3  
                            self.game.audio.sfx("blip")
                    else:
                        if self.shield_charges > 0: self.shield_charges -= 1
                        else: self.player_hp -= 3  
                        self.game.audio.sfx("blip")
                        
                    self.bullets.remove(bullet)
                    
                    if self.player_hp <= 0:
                        self.player_hp = 0
                        self.trigger_death()
                    continue
                
                if (bullet["pos"].y > self.box_rect.bottom + 10 or 
                    bullet["pos"].y < self.box_rect.top - 10 or
                    bullet["pos"].x < self.box_rect.left - 10 or 
                    bullet["pos"].x > self.box_rect.right + 10):
                    self.bullets.remove(bullet)

    def draw_undertale_heart(self, screen, x, y, size, broken=False, color=(255, 0, 0)):
        if not broken:
            pygame.draw.circle(screen, color, (x + size // 4, y + size // 4), size // 4)
            pygame.draw.circle(screen, color, (x + 3 * size // 4, y + size // 4), size // 4)
            points = [(x, y + size // 4), (x + size, y + size // 4), (x + size // 2, y + size)]
            pygame.draw.polygon(screen, color, points)
        else:
            pygame.draw.circle(screen, color, (x - 2 + size // 4, y + size // 4), size // 4)
            points_left = [(x - 2, y + size // 4), (x - 2 + size // 2 - 1, y + size // 4), 
                           (x - 2 + size // 2 - 3, y + size // 2), (x - 2 + size // 2 - 1, y + 3 * size // 4), 
                           (x - 2 + size // 2, y + size)]
            pygame.draw.polygon(screen, color, points_left)
            
            pygame.draw.circle(screen, color, (x + 4 + 3 * size // 4, y + size // 4), size // 4)
            points_right = [(x + 4 + size // 2 + 1, y + size // 4), (x + 4 + size, y + size // 4), 
                            (x + 4 + size // 2, y + size), (x + 4 + size // 2 + 1, y + 3 * size // 4),
                            (x + 4 + size // 2 - 1, y + size // 2)]
            pygame.draw.polygon(screen, color, points_right)

    def draw_boss(self, screen, alpha=255):
        bunny_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        offset_x = int(math.sin(pygame.time.get_ticks() * 0.01) * 12) if self.battle_state != 'enemy_turn' else int(math.sin(pygame.time.get_ticks() * 0.02) * 4)
        offset_y = random.randint(-3, 3) if self.enemy_damage_timer > 0 else 0
        
        bx, by = 60 + offset_x, 70 + offset_y
        
        body_color = (255, 0, 0, alpha) if self.enemy_damage_timer > 0 else (130, 130, 135, alpha)
        ear_color = (200, 50, 50, alpha) if self.enemy_damage_timer > 0 else (100, 100, 105, alpha)
        eye_color = (255, 255, 255, alpha) if self.enemy_damage_timer > 0 else (200, 0, 0, alpha) 
        detail_color = (255, 255, 255, alpha) if self.enemy_damage_timer > 0 else (0, 0, 0, alpha)

        pygame.draw.ellipse(bunny_surface, ear_color, (bx - 22, by - 45, 14, 40))
        pygame.draw.ellipse(bunny_surface, ear_color, (bx + 8, by - 45, 14, 40))
        pygame.draw.circle(bunny_surface, body_color, (bx, by), 32)
        
        pygame.draw.line(bunny_surface, eye_color, (bx - 14, by - 6), (bx - 4, by - 2), 3)
        pygame.draw.circle(bunny_surface, eye_color, (bx - 8, by), 2)
        pygame.draw.line(bunny_surface, eye_color, (bx + 14, by - 6), (bx + 4, by - 2), 3)
        pygame.draw.circle(bunny_surface, eye_color, (bx + 8, by), 2)
        
        mouth_rect = pygame.Rect(bx - 10, by + 6, 20, 10)
        pygame.draw.rect(bunny_surface, detail_color, mouth_rect, 2) 
        pygame.draw.line(bunny_surface, detail_color, (bx - 5, by + 6), (bx - 5, by + 14), 2)
        pygame.draw.line(bunny_surface, detail_color, (bx, by + 6), (bx, by + 14), 2)
        pygame.draw.line(bunny_surface, detail_color, (bx + 5, by + 6), (bx + 5, by + 14), 2)
        
        screen.blit(bunny_surface, (self.screen_width // 2 - 60, self.box_rect.top - 135))

    def draw(self, screen):
        if self.game_over:
            screen.fill((0, 0, 0))
            go_surface = self.game_over_font.render("ВЫ ПОГРЯЗЛИ В ПЫЛИ", True, (255, 0, 0))
            sub_surface = self.font.render("Нажмите [R] для перезапуска или [ESC] для выхода", True, (255, 255, 255))
            screen.blit(go_surface, (self.screen_width // 2 - go_surface.get_width() // 2, self.screen_height // 2 - 30))
            screen.blit(sub_surface, (self.screen_width // 2 - sub_surface.get_width() // 2, self.screen_height // 2 + 30))
            return

        if self.death_state == 'frozen':
            screen.fill((0, 0, 0))
            self.draw_undertale_heart(screen, int(self.heart_pos.x), int(self.heart_pos.y), self.heart_size, broken=True)
            return
        elif self.death_state == 'shattered':
            screen.fill((0, 0, 0))
            for shard in self.shards:
                pygame.draw.rect(screen, (255, 0, 0), (int(shard["pos"].x), int(shard["pos"].y), 5, 5))
            return

        if self.victory_state == 'fading':
            screen.fill((0, 0, 0))
            pygame.draw.rect(screen, (255, 255, 255), self.box_rect, 4)
            self.draw_boss(screen, alpha=self.enemy_alpha) 
            return
            
        elif self.victory_state == 'heart_shake':
            screen.fill((0, 0, 0))
            pygame.draw.rect(screen, (255, 255, 255), self.box_rect, 4)
            
            shake_x = random.randint(-2, 2)
            shake_y = random.randint(-2, 2)
            bx = (self.screen_width // 2) - (self.heart_size // 2) + shake_x
            by = (self.box_rect.top - 65) - (self.heart_size // 2) + shake_y
            
            self.draw_undertale_heart(screen, bx, by, self.heart_size, broken=False, color=(255, 255, 255))
            return
            
        elif self.victory_state == 'heart_shattered':
            screen.fill((0, 0, 0))
            pygame.draw.rect(screen, (255, 255, 255), self.box_rect, 4)
            for shard in self.boss_shards:
                pygame.draw.rect(screen, (255, 255, 255), (int(shard["pos"].x), int(shard["pos"].y), 5, 5))
            return

        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (255, 255, 255), self.box_rect, 4)
        
        if self.enemy_hp > 0:
            self.draw_boss(screen, alpha=255)
            if self.bubble_timer > 0 and self.bubble_text:
                bubble_x = self.screen_width // 2 + 50
                bubble_y = self.box_rect.top - 120
                
                lines = self.bubble_text.split('\n')
                bubble_font = pygame.font.SysFont("Courier New", 14, bold=True)
                
                max_line_w = max([bubble_font.size(line)[0] for line in lines])
                line_h = 18
                box_w = max_line_w + 20
                box_h = (len(lines) * line_h) + 16
                
                pygame.draw.rect(screen, (255, 255, 255), (bubble_x, bubble_y, box_w, box_h), border_radius=8)
                
                tail_points = [
                    (bubble_x, bubble_y + box_h // 2 - 5),
                    (bubble_x - 10, bubble_y + box_h // 2),
                    (bubble_x, bubble_y + box_h // 2 + 5)
                ]
                pygame.draw.polygon(screen, (255, 255, 255), tail_points)
                
                for idx, line in enumerate(lines):
                    text_surface = bubble_font.render(line, True, (0, 0, 0))
                    screen.blit(text_surface, (bubble_x + 10, bubble_y + 8 + (idx * line_h)))

        if self.battle_state in ('main_menu', 'text_display'):
            lines = self.displayed_text.split('\n')
            for idx, line in enumerate(lines):
                text_surface = self.font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (self.box_rect.x + 20, self.box_rect.y + 20 + (idx * 25)))
            
        elif self.battle_state == 'act_menu':
            for i, option in enumerate(self.act_options):
                opt_text = f"* {option}"
                is_selected_opt = (i == self.current_act_index)
                color = (255, 255, 255) if is_selected_opt else (120, 120, 120)
                text_surface = self.font.render(opt_text, True, color)
                col = i % 2
                row = i // 2
                screen.blit(text_surface, (self.box_rect.x + 40 + (col * 200), self.box_rect.y + 25 + (row * 35)))
                    
        elif self.battle_state in ('fight_timing', 'item_timing'):
            target_area = pygame.Rect(self.center_target_x - 15, self.box_rect.y + 10, 30, self.box_rect.height - 20)
            pygame.draw.rect(screen, (60, 60, 60), target_area) 
            pygame.draw.line(screen, (255, 255, 255), (self.center_target_x, self.box_rect.y + 10), (self.center_target_x, self.box_rect.bottom - 10), 2)
            pygame.draw.line(screen, (0, 255, 255), (int(self.strike_bar_x), self.box_rect.y + 6), (int(self.strike_bar_x), self.box_rect.bottom - 6), 4)

        if self.battle_state == 'enemy_turn':
            self.draw_undertale_heart(screen, int(self.heart_pos.x), int(self.heart_pos.y), self.heart_size, broken=False)
            if self.shield_charges > 0:
                pygame.draw.rect(screen, (0, 255, 255), (int(self.heart_pos.x) - 4, int(self.heart_pos.y) - 4, self.heart_size + 8, self.heart_size + 8), 1)
            
            for bullet in self.bullets:
                b_type = bullet.get("type", "normal")
                bullet_color = (0, 255, 0) if b_type == "heal" else (255, 127, 0) if b_type == "orange" else (255, 255, 255)
                pygame.draw.circle(screen, bullet_color, (int(bullet["pos"].x), int(bullet["pos"].y)), 4)
        
        status_text = f"ИГРОК   HP {self.player_hp}/{self.player_max_hp}"
        if self.shield_charges > 0: status_text += f"   [ЩИТ: {self.shield_charges}]"
        status_surface = self.font.render(status_text, True, (255, 255, 255))
        screen.blit(status_surface, (self.box_rect.x, self.box_rect.bottom + 15))
        
        bar_x = self.box_rect.x + status_surface.get_width() + 15 
        bar_y = self.box_rect.bottom + 18
        pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, 100, 14))
        pygame.draw.rect(screen, (255, 215, 0), (bar_x, bar_y, int(100 * (self.player_hp / self.player_max_hp)), 14))

        for i, button_name in enumerate(self.buttons):
            pos = self.button_positions[i]
            is_selected = (self.battle_state == 'main_menu' and i == self.current_button_index)
            color = (255, 165, 0) if is_selected else (130, 65, 0)
            btn_rect = pygame.Rect(pos[0], pos[1], 100, 35)
            pygame.draw.rect(screen, color, btn_rect, 2)
            screen.blit(self.font.render(button_name, True, color), (btn_rect.x + 12, btn_rect.y + 7))
            if is_selected:
                pygame.draw.rect(screen, (255, 0, 0), (btn_rect.x - 15, btn_rect.y + 12, 8, 8))