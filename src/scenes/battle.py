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
        
        print(f"[BATTLE] Инициализация эпичного боя против {self.enemy_id.upper()}!")
        self.game.audio.play_music("battle_theme", loop=True)
        
        # --- БАЛАНС ДЛЯ ДИНАМИЧНОГО И ПОТНОГО БОЯ (НЕ ЗАТЯНУТО) ---
        self.player_max_hp = 12   # Достаточно, чтобы выдержать 4 удара
        self.player_hp = self.player_max_hp
        self.game_over = False  
        
        self.shield_charges = 0  
        self.enemy_hp = 4         # Всего 4 точных удара — бой не будет долгим!
        self.enemy_damage_timer = 0.0
        self.enemy_sneezed = False  
        
        # --- МАСШТАБНЫЕ РАЗМЕРЫ РАМКИ (БОЛЬШЕ МЕСТА ДЛЯ МАНЕВРОВ) ---
        self.normal_width = int(self.screen_width * 0.8)
        self.normal_height = int(self.screen_height * 0.4)
        self.defense_width = 220   
        self.defense_height = 220  
        
        self.box_rect = pygame.Rect(0, 0, self.normal_width, self.normal_height)
        self.box_rect.center = (self.screen_width // 2, int(self.screen_height * 0.42)) 
        
        self.buttons = ["FIGHT", "ACT", "ITEM"]
        self.current_button_index = 0
        self.battle_state = 'main_menu'
        
        self.act_options = ["Оценить", "Поговорить", "Угрожать"]
        self.current_act_index = 0
        self.displayed_text = ""
        
        self.strike_bar_x = self.box_rect.x + 10  
        self.strike_speed = 500                    
        self.center_target_x = self.box_rect.centerx  
        
        # --- НАСТРОЙКИ СЕРДЦА ---
        self.heart_pos = pygame.Vector2(self.box_rect.center)
        self.heart_speed = 220    
        self.heart_size = 12
        
        # --- АТАКУЮЩИЕ ПЕРЕМЕННЫЕ ---
        self.bullets = []  
        self.enemy_turn_timer = 0.0
        self.attack_pattern = 0   
        self.attack_wave_timer = 0.0 
        
        button_y = int(self.screen_height * 0.85) 
        spacing = self.screen_width // 3
        start_x = (spacing - 100) // 2 
        
        self.button_positions = [
            (start_x + i * spacing, button_y) for i in range(len(self.buttons))
        ]
        
        self.font = pygame.font.SysFont("Courier New", 18, bold=True)
        self.game_over_font = pygame.font.SysFont("Courier New", 36, bold=True)

    def start_enemy_turn(self):
        if self.game_over: return
        self.battle_state = 'enemy_turn'
        self.enemy_turn_timer = 4.5  
        self.attack_wave_timer = 0.0
        self.bullets.clear()
        
        self.attack_pattern = random.randint(0, 2)
        
        self.box_rect.width = self.defense_width
        self.box_rect.height = self.defense_height
        self.box_rect.center = (self.screen_width // 2, int(self.screen_height * 0.42))
        
        self.heart_pos = pygame.Vector2(self.box_rect.center)

    def end_enemy_turn(self):
        if self.game_over: return
        self.battle_state = 'main_menu'
        self.box_rect.width = self.normal_width
        self.box_rect.height = self.normal_height
        self.box_rect.center = (self.screen_width // 2, int(self.screen_height * 0.42))

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN: return

        if self.game_over:
            if event.key == pygame.K_r:
                if hasattr(self.game, 'save_system'): self.game.save_system.load_game() 
                self.game.change_scene("overworld")
            elif event.key == pygame.K_ESCAPE:
                self.game.change_scene("overworld")
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
                    self.game.change_scene("overworld")
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
            self.enemy_hp = 5
            self.displayed_text = (
                f"* DUST BUNNY - АТК 3 ЗАЩ 10.\n"
                f"* Разозлился и навострил уши!\n"
                f"* Теперь у него 5 HP вместо 4!"
            )
        elif chosen_act == "Поговорить":
            self.enemy_sneezed = True
            self.displayed_text = (
                f"* Вы поздоровались.\n"
                f"* Кролик в ярости чихнул огромным облаком!\n"
                f"* В следующем ходу атаки ускорятся!"
            )
        elif chosen_act == "Угрожать":
            self.enemy_hp = 0  
            self.displayed_text = (
                "* Вы грозно замахнулись веником.\n"
                "* Пыльный Кролик в панике сжался\n"
                "  и улетел прямо в вентиляцию!\n"
                "* Вы победили!"
            )
        self.battle_state = 'text_display'

    def calculate_damage(self):
        distance = abs(self.strike_bar_x - self.center_target_x)
        max_distance = self.box_rect.width / 2
        accuracy = max(0.0, 1.0 - (distance / max_distance))
        
        if accuracy > 0.88:
            self.enemy_hp -= 1  
            self.enemy_damage_timer = 1.0  
            self.displayed_text = f"* КРИТИЧЕСКИЙ УДАР ШВАБРОЙ!\n* Кролик разлетается на куски! (Осталось {self.enemy_hp} HP)"
        elif accuracy > 0.35:
            self.enemy_hp -= 1  
            self.enemy_damage_timer = 1.0  
            self.displayed_text = f"* Точное попадание!\n* Пыльный Кролик теряет форму. (Осталось {self.enemy_hp} HP)"
        else:
            self.displayed_text = f"* Промах!\n* Вы ударили мимо комка пыли."
            
        if self.enemy_hp <= 0:
            self.displayed_text += f"\n* Враг повержен и окончательно выметен!"

        self.battle_state = 'text_display'

    def calculate_item_use(self):
        distance = abs(self.strike_bar_x - self.center_target_x)
        max_distance = self.box_rect.width / 2
        accuracy = max(0.0, 1.0 - (distance / max_distance))
        
        if accuracy > 0.88:
            self.shield_charges = 3  
            self.displayed_text = (
                f"* Идеально! Пауки сплели липкую сеть.\n"
                f"* Она полностью заблокирует 3 удара пыли!"
            )
        else:
            self.player_hp = min(self.player_max_hp, self.player_hp + 5)
            self.displayed_text = f"* Вы съели старую конфетку из кармана.\n* Восстановлено 5 HP!"
            
        self.battle_state = 'text_display'

    def update(self, dt):
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
            
            if move_vec.length_squared() > 0:
                self.heart_pos += move_vec.normalize() * self.heart_speed * dt

            padding = 6
            if self.heart_pos.x < self.box_rect.left + padding:  self.heart_pos.x = self.box_rect.left + padding
            if self.heart_pos.x > self.box_rect.right - padding - self.heart_size: self.heart_pos.x = self.box_rect.right - padding - self.heart_size
            if self.heart_pos.y < self.box_rect.top + padding:   self.heart_pos.y = self.box_rect.top + padding
            if self.heart_pos.y > self.box_rect.bottom - padding - self.heart_size: self.heart_pos.y = self.box_rect.bottom - padding - self.heart_size

            self.attack_wave_timer += dt
            spawn_cooldown = 0.12 if self.enemy_sneezed else 0.24

            if self.attack_pattern == 0:
                if self.attack_wave_timer >= spawn_cooldown:
                    self.attack_wave_timer = 0.0
                    for i in range(2):
                        bx = self.box_rect.left + 30 + (i * 90) + (int(self.enemy_turn_timer * 40) % 40)
                        self.bullets.append({
                            "pos": pygame.Vector2(bx, self.box_rect.top - 5),
                            "vel": pygame.Vector2(0, 160 if not self.enemy_sneezed else 240)
                        })

            elif self.attack_pattern == 1:
                if self.attack_wave_timer >= spawn_cooldown * 2.0:
                    self.attack_wave_timer = 0.0
                    h1 = random.randint(self.box_rect.top + 25, self.box_rect.bottom - 25)
                    h2 = random.randint(self.box_rect.top + 25, self.box_rect.bottom - 25)
                    self.bullets.append({
                        "pos": pygame.Vector2(self.box_rect.left - 5, h1),
                        "vel": pygame.Vector2(160, 0)
                    })
                    self.bullets.append({
                        "pos": pygame.Vector2(self.box_rect.right + 5, h2),
                        "vel": pygame.Vector2(-160, 0)
                    })

            elif self.attack_pattern == 2:
                if self.attack_wave_timer >= spawn_cooldown * 3.0:
                    self.attack_wave_timer = 0.0
                    spawn_x = random.choice([self.box_rect.left + 40, self.box_rect.right - 40, self.box_rect.centerx])
                    b_pos = pygame.Vector2(spawn_x, self.box_rect.top + 5)
                    
                    target_dir = (self.heart_pos - b_pos)
                    if target_dir.length() > 0: target_dir = target_dir.normalize()
                    else: target_dir = pygame.Vector2(0, 1)
                        
                    speed = 130 if not self.enemy_sneezed else 200
                    self.bullets.append({
                        "pos": b_pos,
                        "vel": target_dir * speed
                    })

            heart_rect = pygame.Rect(int(self.heart_pos.x), int(self.heart_pos.y), self.heart_size, self.heart_size)
            
            for bullet in self.bullets[:]:
                bullet["pos"] += bullet["vel"] * dt  
                bullet_rect = pygame.Rect(int(bullet["pos"].x), int(bullet["pos"].y), 7, 7)
                
                if bullet_rect.colliderect(heart_rect):
                    if self.shield_charges > 0:
                        self.shield_charges -= 1
                    else:
                        self.player_hp -= 3  
                        
                    self.game.audio.sfx("blip")  
                    self.bullets.remove(bullet)
                    
                    if self.player_hp <= 0:
                        self.player_hp = 0
                        self.game_over = True
                        self.game.audio.play_music(None)  
                    continue
                
                if (bullet["pos"].y > self.box_rect.bottom + 10 or 
                    bullet["pos"].y < self.box_rect.top - 10 or
                    bullet["pos"].x < self.box_rect.left - 10 or 
                    bullet["pos"].x > self.box_rect.right + 10):
                    self.bullets.remove(bullet)

    def draw(self, screen):
        if self.game_over:
            screen.fill((0, 0, 0))
            go_surface = self.game_over_font.render("ВЫ ПОГРЯЗЛИ В ПЫЛИ", True, (255, 0, 0))
            sub_surface = self.font.render("Нажмите [R] для очистки сейва или [ESC] для сдачи", True, (255, 255, 255))
            screen.blit(go_surface, (self.screen_width // 2 - go_surface.get_width() // 2, self.screen_height // 2 - 30))
            screen.blit(sub_surface, (self.screen_width // 2 - sub_surface.get_width() // 2, self.screen_height // 2 + 30))
            return

        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (255, 255, 255), self.box_rect, 4)
        
        if self.enemy_hp > 0:
            offset_x, offset_y = 0, 0
            if self.battle_state == 'enemy_turn':
                offset_x = int(math.sin(pygame.time.get_ticks() * 0.01) * 8)
                offset_y = random.randint(-1, 1)
                
            bunny_center_x = self.screen_width // 2 + offset_x
            bunny_center_y = self.box_rect.top - 70 + offset_y
            
            body_color = (200, 30, 30) if self.enemy_damage_timer > 0 else (140, 140, 145)
            ear_color = (230, 50, 50) if self.enemy_damage_timer > 0 else (110, 110, 115)
            face_color = (255, 255, 255) if self.enemy_damage_timer > 0 else (0, 0, 0)

            pygame.draw.ellipse(screen, ear_color, (bunny_center_x - 24, bunny_center_y - 50, 15, 45))
            pygame.draw.ellipse(screen, ear_color, (bunny_center_x + 9, bunny_center_y - 50, 15, 45))
            pygame.draw.circle(screen, body_color, (bunny_center_x, bunny_center_y), 36)
            
            pygame.draw.line(screen, face_color, (bunny_center_x - 14, bunny_center_y - 8), (bunny_center_x - 4, bunny_center_y - 4), 3)
            pygame.draw.line(screen, face_color, (bunny_center_x + 14, bunny_center_y - 8), (bunny_center_x + 4, bunny_center_y - 4), 3)
            pygame.draw.circle(screen, face_color, (bunny_center_x - 8, bunny_center_y), 3)
            pygame.draw.circle(screen, face_color, (bunny_center_x + 8, bunny_center_y), 3)
            pygame.draw.arc(screen, face_color, (bunny_center_x - 10, bunny_center_y + 4, 20, 12), 0, 3.14, 2)

        if self.battle_state == 'main_menu':
            flavor_text = f"* Даст Банни окружил вас стеной плотной грязи!\n* Воздух становится тяжелым."
            lines = flavor_text.split('\n')
            for idx, line in enumerate(lines):
                text_surface = self.font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (self.box_rect.x + 20, self.box_rect.y + 20 + (idx * 30)))
            
        elif self.battle_state == 'act_menu':
            for i, option in enumerate(self.act_options):
                opt_text = f"* {option}"
                is_selected_opt = (i == self.current_act_index)
                color = (255, 255, 255) if is_selected_opt else (130, 130, 130)
                text_surface = self.font.render(opt_text, True, color)
                screen.blit(text_surface, (self.box_rect.x + 60, self.box_rect.y + 25 + (i * 35)))
                if is_selected_opt:
                    pygame.draw.rect(screen, (255, 0, 0), (self.box_rect.x + 35, self.box_rect.y + 31 + (i * 35), 10, 10))
                    
        elif self.battle_state in ('fight_timing', 'item_timing'):
            target_area = pygame.Rect(self.center_target_x - 15, self.box_rect.y + 10, 30, self.box_rect.height - 20)
            pygame.draw.rect(screen, (50, 50, 50), target_area) 
            pygame.draw.line(screen, (200, 200, 200), (self.center_target_x, self.box_rect.y + 10), (self.center_target_x, self.box_rect.bottom - 10), 2)
            pygame.draw.line(screen, (0, 255, 255), (int(self.strike_bar_x), self.box_rect.y + 8), (int(self.strike_bar_x), self.box_rect.bottom - 8), 5)
                    
        elif self.battle_state == 'text_display':
            lines = self.displayed_text.split('\n')
            for idx, line in enumerate(lines):
                text_surface = self.font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (self.box_rect.x + 20, self.box_rect.y + 20 + (idx * 30)))

        elif self.battle_state == 'enemy_turn':
            pygame.draw.rect(screen, (255, 0, 0), (int(self.heart_pos.x), int(self.heart_pos.y), self.heart_size, self.heart_size))
            if self.shield_charges > 0:
                pygame.draw.rect(screen, (0, 255, 255), (int(self.heart_pos.x) - 4, int(self.heart_pos.y) - 4, self.heart_size + 8, self.heart_size + 8), 1)
            
            for bullet in self.bullets:
                pygame.draw.circle(screen, (230, 230, 230), (int(bullet["pos"].x), int(bullet["pos"].y)), 4)
        
        # --- СТАТУС БАР ---
        status_text = f"ИГРОК  HP {self.player_hp}/{self.player_max_hp}"
        if self.shield_charges > 0: status_text += f"   [ЩИТ: {self.shield_charges}]"
        screen.blit(self.font.render(status_text, True, (255, 255, 255)), (self.box_rect.x, self.box_rect.bottom + 15))
        
        # Сдвинуто на +220 пикселей, чтобы текст HP и полоска идеально разделялись!
        bar_x = self.box_rect.x + 220 
        bar_y = self.box_rect.bottom + 18
        bar_max_width = 100
        pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_max_width, 14))
        current_bar_width = int(bar_max_width * (self.player_hp / self.player_max_hp))
        pygame.draw.rect(screen, (255, 215, 0), (bar_x, bar_y, current_bar_width, 14))

        # --- ОТРИСОВКА КНОПОК ---
        for i, button_name in enumerate(self.buttons):
            pos = self.button_positions[i]
            is_selected = (self.battle_state == 'main_menu' and i == self.current_button_index)
            color = (255, 165, 0) if is_selected else (140, 70, 0)
            
            btn_rect = pygame.Rect(pos[0], pos[1], 100, 35)
            pygame.draw.rect(screen, color, btn_rect, 2)
            screen.blit(self.font.render(button_name, True, color), (btn_rect.x + 10, btn_rect.y + 7))
            
            if is_selected:
                pygame.draw.rect(screen, (255, 0, 0), (btn_rect.x - 15, btn_rect.y + 12, 10, 10))