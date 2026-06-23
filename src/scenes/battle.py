import pygame
import random

class BattleScene:
    def __init__(self, game, enemy_id):
        self.game = game
        self.enemy_id = enemy_id
        self.screen = game.screen
        
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        
        print(f"[BATTLE] Инициализация боя. Размер окна: {self.screen_width}x{self.screen_height}")
        self.game.audio.play_music("battle_theme", loop=True)
        
        # --- СИСТЕМА ЖИЗНЕЙ И ПРОИГРЫША ---
        self.player_max_hp = 2
        self.player_hp = self.player_max_hp
        self.game_over = False  # Флаг, блокирующий игру при смерти
        
        # --- СИСТЕМА ЩИТА (ИММУНИТЕТ К ПЫЛИ) ---
        self.shield_charges = 0  # Сколько попаданий пыли может заблокировать паутина
        
        # --- СИСТЕМА ДЛЯ ПОБЕДЫ НАД ВРАГОМ ---
        self.enemy_hp = 3  # По умолчанию нужно попасть 3 раза
        
        # --- МОДИФИКАТОРЫ ВРАГА ---
        self.enemy_sneezed = False  # Стал ли кролик чихать (удваивает спавн пыли)
        
        # 1. Настройки размеров боевой рамки
        self.normal_width = int(self.screen_width * 0.8)
        self.normal_height = int(self.screen_height * 0.4)
        self.defense_width = 160  # Размер коробки для уклонения
        self.defense_height = 160
        
        # Текущий Rect рамки (начинаем с нормального размера)
        self.box_rect = pygame.Rect(0, 0, self.normal_width, self.normal_height)
        self.box_rect.center = (self.screen_width // 2, int(self.screen_height * 0.35))
        
        # 2. Настройки главных кнопок
        self.buttons = ["FIGHT", "ACT", "ITEM"]
        self.current_button_index = 0
        
        # --- СОСТОЯНИЯ БОЯ ---
        self.battle_state = 'main_menu'
        
        # Подменю ACT
        self.act_options = ["Оценить", "Поговорить", "Угрожать"]
        self.current_act_index = 0
        self.displayed_text = ""
        
        # Настройки для МИНИ-ИГРЫ FIGHT / ITEM (Тайминг-полоска)
        self.strike_bar_x = self.box_rect.x + 10  
        self.strike_speed = 450                    
        self.center_target_x = self.box_rect.centerx  
        
        # --- НАСТРОЙКИ ДЛЯ ХОДА ВРАГА (DEFENSE) ---
        self.heart_pos = pygame.Vector2(self.box_rect.center)
        self.heart_speed = 180  # Скорость движения души
        self.heart_size = 10
        
        # Снаряды и таймер хода
        self.bullets = []  # Список словарей: [{"pos": Vector2, "speed": float}]
        self.enemy_turn_timer = 0.0
        self.bullet_spawn_timer = 0.0
        
        # Равномерное распределение на 3 кнопки по ширине экрана
        button_y = int(self.screen_height * 0.75) 
        spacing = self.screen_width // 3
        start_x = (spacing - 100) // 2 
        
        self.button_positions = [
            (start_x + i * spacing, button_y) for i in range(len(self.buttons))
        ]
        
        self.font = pygame.font.SysFont("Courier New", 18, bold=True)
        self.game_over_font = pygame.font.SysFont("Courier New", 36, bold=True)

    def start_enemy_turn(self):
        """Запуск фазы защиты"""
        if self.game_over: return
        self.battle_state = 'enemy_turn'
        self.enemy_turn_timer = 5.0  # Ход врага длится 5 секунд
        self.bullet_spawn_timer = 0.0
        self.bullets.clear()
        
        # Сужаем рамку до размеров коробки защиты
        self.box_rect.width = self.defense_width
        self.box_rect.height = self.defense_height
        self.box_rect.center = (self.screen_width // 2, int(self.screen_height * 0.35))
        
        # Спавним сердечко ровно по центру новой сжатой коробки
        self.heart_pos = pygame.Vector2(self.box_rect.center)

    def end_enemy_turn(self):
        """Возврат в главное меню"""
        if self.game_over: return
        self.battle_state = 'main_menu'
        
        # Возвращаем рамку в нормальное состояние
        self.box_rect.width = self.normal_width
        self.box_rect.height = self.normal_height
        self.box_rect.center = (self.screen_width // 2, int(self.screen_height * 0.35))

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if self.game_over:
            if event.key == pygame.K_r:
                print("[GAME OVER] Перезапуск! Загружаем сохранение...")
                if hasattr(self.game, 'save_system'):
                    self.game.save_system.load_game() 
                self.game.change_scene("overworld")
            elif event.key == pygame.K_ESCAPE:
                self.game.change_scene("overworld")
            return

        if event.key == pygame.K_ESCAPE:
            self.game.change_scene("overworld")
            return
        
        # --- 1. ЛОГИКА В ГЛАВНОМ МЕНЮ ---
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

        # --- 2. ЛОГИКА В МЕНЮ ACT ---
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
                
        # --- 3. ЛОГИКА МИНИ-ИГРЫ (FIGHT ИЛИ ITEM) ---
        elif self.battle_state in ('fight_timing', 'item_timing'):
            if event.key in (pygame.K_z, pygame.K_RETURN):
                if self.battle_state == 'fight_timing':
                    self.calculate_damage()
                else:
                    self.calculate_item_use()

        # --- 4. ЛОГИКА ПРИ ЧТЕНИИ ТЕКСТА РЕЗУЛЬТАТА ---
        elif self.battle_state == 'text_display':
            if event.key in (pygame.K_z, pygame.K_RETURN):
                self.game.audio.sfx("blip")
                
                # ПРОВЕРКА НА ПОБЕДУ
                if self.enemy_hp <= 0:
                    print(f"[ПОБЕДА] Враг {self.enemy_id} побежден!")
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
            # Вместо пустого текста запускаем мини-игру для использования предмета!
            self.strike_bar_x = self.box_rect.x + 10
            self.battle_state = 'item_timing'

    def confirm_act_action(self):
        chosen_act = self.act_options[self.current_act_index]
        if chosen_act == "Оценить":
            self.enemy_hp = 5
            self.displayed_text = (
                f"* DUST BUNNY - АТК 4 ЗАЩ 99.\n"
                f"* Кролик заметил вашу оценку и\n"
                f"  сильно навострил уши!\n"
                f"* Теперь по нему нужно попасть 5 раз!"
            )
        elif chosen_act == "Поговорить":
            self.enemy_sneezed = True
            self.displayed_text = (
                f"* Вы сказали привет.\n"
                f"* Пыльный Кролик громко чихнул в ответ!\n"
                f"* Кажется, поднялось много пыли..."
            )
        elif chosen_act == "Угрожать":
            self.enemy_hp = 0  
            self.displayed_text = (
                "* Вы пообещали принести пылесос.\n"
                "* Пыльный Кролик в панике сжался\n"
                "  в комок и улетел под диван!\n"
                "* Вы победили!"
            )
        self.battle_state = 'text_display'

    def calculate_damage(self):
        distance = abs(self.strike_bar_x - self.center_target_x)
        max_distance = self.box_rect.width / 2
        accuracy = max(0.0, 1.0 - (distance / max_distance))
        
        base_damage = 15
        final_damage = int(base_damage * accuracy * 1.5)  
        
        if accuracy > 0.92:
            self.enemy_hp -= 1  
            self.displayed_text = f"* КРИТИЧЕСКИЙ УДАР!\n* Нанесено {final_damage} урона врагу {self.enemy_id.upper()}!"
        elif final_damage > 0:
            self.enemy_hp -= 1  
            self.displayed_text = f"* Вы атаковали!\n* Нанесено {final_damage} урона врагу {self.enemy_id.upper()}."
        else:
            self.displayed_text = f"* Промах!\n* Враг {self.enemy_id.upper()} увернулся."
            
        if self.enemy_hp <= 0:
            self.displayed_text += f"\n* Враг {self.enemy_id.upper()} развеялся по ветру! Вы победили!"

        self.battle_state = 'text_display'

    def calculate_item_use(self):
        """Логика использования Карманных Пауков через мини-игру"""
        distance = abs(self.strike_bar_x - self.center_target_x)
        max_distance = self.box_rect.width / 2
        accuracy = max(0.0, 1.0 - (distance / max_distance))
        
        # Проверяем, попал ли игрок с 1 раза точно в центр (критический хит)
        if accuracy > 0.92:
            self.shield_charges = 2  # Даем иммунитет на 2 комочка пыли
            self.displayed_text = (
                f"* Вы идеально выпустили Карманных Пауков!\n"
                f"* Они быстро сплели липкую паутину вокруг души.\n"
                f"* Получен иммунитет к 2 комочкам пыли!"
            )
            print("[ITEM] Идеальный тайминг! Активирован щит на 2 удара.")
        else:
            self.displayed_text = (
                f"* Вы неудачно открыли карман...\n"
                f"* Пауки испугались шума и просто разбежались.\n"
                f"* Ничего не произошло."
            )
            print("[ITEM] Промах по таймингу предмета. Щит не получен.")
            
        self.battle_state = 'text_display'

    def update(self, dt):
        if self.game_over:
            return

        # 1. Если идет мини-игра (атака или предмет)
        if self.battle_state in ('fight_timing', 'item_timing'):
            self.strike_bar_x += self.strike_speed * dt
            if self.strike_bar_x >= self.box_rect.right - 10:
                if self.battle_state == 'fight_timing':
                    self.displayed_text = f"* Слишком медленно!\n* Вы промахнулись по {self.enemy_id.upper()}."
                else:
                    self.displayed_text = f"* Слишком медленно!\n* Пауки уползли, пока вы думали."
                self.battle_state = 'text_display'

        # 2. Если идет ФАЗА ЗАЩИТЫ (Ход врага)
        elif self.battle_state == 'enemy_turn':
            self.enemy_turn_timer -= dt
            if self.enemy_turn_timer <= 0:
                self.enemy_sneezed = False
                self.end_enemy_turn()
                return

            # --- УПРАВЛЕНИЕ СЕРДЕЧКОМ ---
            keys = pygame.key.get_pressed()
            move_vec = pygame.Vector2(0, 0)
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:  move_vec.x -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: move_vec.x += 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:    move_vec.y -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:  move_vec.y += 1
            
            if move_vec.length_squared() > 0:
                move_vec = move_vec.normalize()
                self.heart_pos += move_vec * self.heart_speed * dt

            # Ограничения движения сердечка
            padding = 6
            if self.heart_pos.x < self.box_rect.left + padding:  self.heart_pos.x = self.box_rect.left + padding
            if self.heart_pos.x > self.box_rect.right - padding - self.heart_size: self.heart_pos.x = self.box_rect.right - padding - self.heart_size
            if self.heart_pos.y < self.box_rect.top + padding:   self.heart_pos.y = self.box_rect.top + padding
            if self.heart_pos.y > self.box_rect.bottom - padding - self.heart_size: self.heart_pos.y = self.box_rect.bottom - padding - self.heart_size

            # --- СПАВН СНАРЯДОВ ---
            self.bullet_spawn_timer += dt
            spawn_cooldown = 0.15 if self.enemy_sneezed else 0.3
            
            if self.bullet_spawn_timer >= spawn_cooldown:  
                self.bullet_spawn_timer = 0.0
                bullet_x = random.randint(self.box_rect.left + 10, self.box_rect.right - 15)
                bullet_y = self.box_rect.top - 10
                self.bullets.append({
                    "pos": pygame.Vector2(bullet_x, bullet_y),
                    "speed": random.randint(120, 200)
                })

            # --- ДВИЖЕНИЕ И КОЛЛИЗИЯ СНАРЯДОВ ---
            heart_rect = pygame.Rect(int(self.heart_pos.x), int(self.heart_pos.y), self.heart_size, self.heart_size)
            
            for bullet in self.bullets[:]:
                bullet["pos"].y += bullet["speed"] * dt  
                bullet_rect = pygame.Rect(int(bullet["pos"].x), int(bullet["pos"].y), 6, 6)
                
                if bullet_rect.colliderect(heart_rect):
                    # --- ПРОВЕРКА ЩИТА ОТ ПАУКОВ ---
                    if self.shield_charges > 0:
                        self.shield_charges -= 1
                        print(f"[ЩИТ] Паутина поглотила удар! Зарядов осталось: {self.shield_charges}")
                    else:
                        # Если щита нет, игрок получает урон
                        self.player_hp -= 1  
                        print(f"[УРОН] Попадание! Текущее HP: {self.player_hp}/{self.player_max_hp}")
                        
                    self.game.audio.sfx("blip")  
                    self.bullets.remove(bullet)
                    
                    if self.player_hp <= 0:
                        self.game_over = True
                        self.game.audio.play_music(None)  
                        print("[GAME OVER] У вас закончились жизни.")
                    continue
                
                if bullet["pos"].y > self.box_rect.bottom:
                    self.bullets.remove(bullet)

    def draw(self, screen):
        if self.game_over:
            screen.fill((0, 0, 0))
            go_surface = self.game_over_font.render("ИГРА ОКОНЧЕНА", True, (255, 0, 0))
            sub_surface = self.font.render("Нажмите [R] для загрузки или [ESC] для выхода", True, (255, 255, 255))
            screen.blit(go_surface, (self.screen_width // 2 - go_surface.get_width() // 2, self.screen_height // 2 - 30))
            screen.blit(sub_surface, (self.screen_width // 2 - sub_surface.get_width() // 2, self.screen_height // 2 + 30))
            return

        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (255, 255, 255), self.box_rect, 4)
        
        if self.battle_state == 'main_menu':
            flavor_text = f"* {self.enemy_id.upper()} преграждает путь!"
            text_surface = self.font.render(flavor_text, True, (255, 255, 255))
            screen.blit(text_surface, (self.box_rect.x + 20, self.box_rect.y + 20))
            
        elif self.battle_state == 'act_menu':
            for i, option in enumerate(self.act_options):
                opt_text = f"* {option}"
                is_selected_opt = (i == self.current_act_index)
                color = (255, 255, 255) if is_selected_opt else (130, 130, 130)
                text_surface = self.font.render(opt_text, True, color)
                text_y = self.box_rect.y + 25 + (i * 35)
                screen.blit(text_surface, (self.box_rect.x + 60, text_y))
                if is_selected_opt:
                    heart_rect = pygame.Rect(self.box_rect.x + 35, text_y + 6, 10, 10)
                    pygame.draw.rect(screen, (255, 0, 0), heart_rect)
                    
        # Отрисовка шкалы тайминга работает и для FIGHT, и для ITEM
        elif self.battle_state in ('fight_timing', 'item_timing'):
            target_area = pygame.Rect(self.center_target_x - 15, self.box_rect.y + 10, 30, self.box_rect.height - 20)
            pygame.draw.rect(screen, (60, 60, 60), target_area) 
            pygame.draw.line(screen, (150, 150, 150), (self.center_target_x, self.box_rect.y + 10), (self.center_target_x, self.box_rect.bottom - 10), 2)
            
            hint_str = "ВЫПУСТИ ПАУКОВ [Z]!" if self.battle_state == 'item_timing' else "ЖМИ [Z] В ЦЕНТРЕ!"
            hint_surface = self.font.render(hint_str, True, (100, 100, 100))
            screen.blit(hint_surface, (self.box_rect.x + 20, self.box_rect.bottom - 30))
            pygame.draw.line(screen, (0, 255, 255), (int(self.strike_bar_x), self.box_rect.y + 8), (int(self.strike_bar_x), self.box_rect.bottom - 8), 5)
                    
        elif self.battle_state == 'text_display':
            lines = self.displayed_text.split('\n')
            for idx, line in enumerate(lines):
                text_surface = self.font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (self.box_rect.x + 20, self.box_rect.y + 20 + (idx * 30)))

        elif self.battle_state == 'enemy_turn':
            # Отрендерим обычное сердечко души
            pygame.draw.rect(screen, (255, 0, 0), (int(self.heart_pos.x), int(self.heart_pos.y), self.heart_size, self.heart_size))
            
            # ВИЗУАЛЬНЫЙ ЭФФЕКТ: Если активен щит пауков, рисуем защитный белый контур (паутинку) вокруг сердечка
            if self.shield_charges > 0:
                shield_rect = pygame.Rect(int(self.heart_pos.x) - 4, int(self.heart_pos.y) - 4, self.heart_size + 8, self.heart_size + 8)
                pygame.draw.rect(screen, (255, 255, 255), shield_rect, 1)
                
            for bullet in self.bullets:
                pygame.draw.rect(screen, (255, 255, 255), (int(bullet["pos"].x), int(bullet["pos"].y), 6, 6))
        
        # --- HP BAR И ИНДИКАТОР ЩИТА ---
        status_text = f"ИГРОК  HP {self.player_hp}/{self.player_max_hp}"
        if self.shield_charges > 0:
            status_text += f"  [ЩИТ ПАУКОВ: {self.shield_charges}]"
            
        hp_text_surface = self.font.render(status_text, True, (255, 255, 255))
        screen.blit(hp_text_surface, (self.box_rect.x, self.box_rect.bottom + 15))
        
        bar_x = self.box_rect.x + 150
        bar_y = self.box_rect.bottom + 18
        bar_max_width = 60
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_max_width, 14))
        current_bar_width = int(bar_max_width * (self.player_hp / self.player_max_hp))
        pygame.draw.rect(screen, (255, 255, 0), (bar_x, bar_y, current_bar_width, 14))

        # --- ОТРИСОВКА 3 КНОПОК ---
        for i, button_name in enumerate(self.buttons):
            pos = self.button_positions[i]
            is_selected = (self.battle_state == 'main_menu' and i == self.current_button_index)
            color = (255, 200, 0) if is_selected else (120, 90, 0)
            
            btn_rect = pygame.Rect(pos[0], pos[1], 100, 35)
            pygame.draw.rect(screen, color, btn_rect, 2)
            
            btn_text = self.font.render(button_name, True, color)
            screen.blit(btn_text, (btn_rect.x + 10, btn_rect.y + 7))
            
            if is_selected:
                heart_rect = pygame.Rect(btn_rect.x - 15, btn_rect.y + 12, 10, 10)
                pygame.draw.rect(screen, (255, 0, 0), heart_rect)