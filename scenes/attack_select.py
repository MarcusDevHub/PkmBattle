import pygame
from config import *
from assets_manager import AssetManager
from ui.components import Button

class AttackSelectScene:
    def __init__(self, game, p1_char, p2_char):
        self.game = game
        self.p1_char = p1_char
        self.p2_char = p2_char
        self.buttons = []
        self.p1_atk = None
        self.p2_atk = None
        self._init_buttons()

    def _init_buttons(self):
        w, h = 350, 70
        start_x = (SCREEN_WIDTH - (w*2 + 20)) // 2
        for i, (aid, info) in enumerate(ATTACKS_DB.items()):
            x = start_x + (i%2)*(w+20)
            y = 150 + (i//2)*(h+20)
            btn = Button(x, y, w, h, info["name"], info["color"])
            btn.payload = aid
            self.buttons.append(btn)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            for btn in self.buttons:
                if btn.rect.collidepoint(pos):
                    if self.p1_atk is None:
                        self.p1_atk = btn.payload
                    elif self.p2_atk is None:
                        self.p2_atk = btn.payload
                        self.game.change_scene("BATTLE", (self.p1_char, self.p1_atk), (self.p2_char, self.p2_atk))
                    return

    def update(self):
        pos = pygame.mouse.get_pos()
        for btn in self.buttons: btn.update(pos)

    def draw(self, screen):
        screen.fill(COLORS["BG"])
        font = AssetManager.get_font(40)
        if self.p1_atk is None:
            txt = font.render(f"P1 ({self.p1_char}): Ataque", True, COLORS["RED"])
        else:
            txt = font.render(f"P2 ({self.p2_char}): Ataque", True, COLORS["GREEN"])
        screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 50))

        for btn in self.buttons:
            btn.draw(screen)
            if self.p1_atk == btn.payload:
                pygame.draw.circle(screen, COLORS["RED"], (btn.rect.right - 20, btn.rect.centery), 8)
            if self.p2_atk == btn.payload:
                pygame.draw.circle(screen, COLORS["GREEN"], (btn.rect.right - 45, btn.rect.centery), 8)
