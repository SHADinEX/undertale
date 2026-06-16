# src/systems/dialog_system.py
import pygame

class DialogBox:
    def __init__(self, font):
        self.font = font
        self.lines = []
        self.index = 0
        self.visible_chars = 0
        self.waiting_advance = False
        self.active = False  # Флаг: открыт ли диалог сейчас

    def start_dialog(self, dialog_data):
        self.lines = dialog_data["lines"]
        self.index = 0
        self.visible_chars = 0
        self.waiting_advance = False
        self.active = True

    def current_text(self):
        # Метод, которого не хватало в методичке. 
        # Возвращает текст текущей реплики (если это не выбор)
        if self.index < len(self.lines) and "text" in self.lines[self.index]:
            return self.lines[self.index]["text"]
        return ""

    def update(self):
        if not self.active or self.index >= len(self.lines):
            self.active = False
            return

        # Проверяем, идет ли сейчас обычный текст или развилка (choices)
        current_line = self.lines[self.index]
        if "choices" in current_line:
            self.waiting_advance = True
            return

        text = self.current_text()
        if self.visible_chars < len(text):
            self.visible_chars += 1
        else:
            self.waiting_advance = True

    def advance(self):
        if not self.waiting_advance:
            # Скип анимации: если текст ещё печатается, показываем его весь
            self.visible_chars = 9999
            return
            
        # Если это были выборы — пока просто закрываем диалог (логику маршрутов сделаем позже)
        if "choices" in self.lines[self.index]:
            self.active = False
            return

        self.index += 1
        self.visible_chars = 0
        self.waiting_advance = False
        
        # Если реплики кончились — закрываем окно
        if self.index >= len(self.lines):
            self.active = False

    def draw(self, screen):
        if not self.active:
            return

        # Практика 1: Рисуем рамку внизу экрана (черный прямоугольник с белой обводкой)
        # Координаты: x=40, y=320, ширина=560, высота=130 (для экрана 640x480)
        box_rect = pygame.Rect(40, 320, 560, 130)
        pygame.draw.rect(screen, (0, 0, 0), box_rect)          # Чёрная заливка
        pygame.draw.rect(screen, (255, 255, 255), box_rect, 3) # Белая обводка (толщина 3)

        current_line = self.lines[self.index]

        # Отрисовка обычного текста
        if "text" in current_line:
            speaker = current_line["speaker"]
            full_text = current_line["text"]
            # Обрезаем строку до количества видимых символов
            printed_text = full_text[:self.visible_chars]

            # Рисуем имя говорящего
            speaker_surf = self.font.render(f"{speaker}:", True, (255, 255, 255))
            screen.blit(speaker_surf, (60, 335))

            # Рисуем сам печатающийся текст
            text_surf = self.font.render(printed_text, True, (255, 255, 255))
            screen.blit(text_surf, (60, 370))

            # Практика 2: Индикатор ▼ когда строка допечатана
            if self.waiting_advance:
                indicator_surf = self.font.render("▼", True, (255, 255, 255))
                screen.blit(indicator_surf, (560, 410))

        # Отрисовка вариантов выбора (choices)
        elif "choices" in current_line:
            choices = current_line["choices"]
            for i, choice in enumerate(choices):
                choice_surf = self.font.render(f"[ {choice} ]", True, (255, 255, 255))
                screen.blit(choice_surf, (60 + (i * 200), 370))