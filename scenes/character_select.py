import pygame
from config import *
from assets_manager import AssetManager
from ui.components import Button

class CharacterSelectScene:
    def __init__(self, game):
        self.game = game
        self.buttons = []
        self.p1_char = None
        self.p2_char = None
        
        self.available = [k for k in POKEMON_DB.keys() if k != "dummy"]
        if not self.available: self.available = ["dummy"]
        
        self._init_ui()

    def _init_ui(self):
        w, h = 300, 60
        start_y = 150
        for i, name in enumerate(self.available):
            btn = Button((SCREEN_WIDTH - w)//2, start_y + i*(h+15), w, h, name.capitalize(), COLORS["BLUE"])
            btn.payload = name
            self.buttons.append(btn)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            for btn in self.buttons:
                if btn.rect.collidepoint(pos):
                    if not self.p1_char:
                        self.p1_char = btn.payload
                    elif not self.p2_char:
                        self.p2_char = btn.payload
                        self.game.change_scene("ATTACK_SELECT", self.p1_char, self.p2_char)
                    return

    def update(self):
        pos = pygame.mouse.get_pos()
        for btn in self.buttons: btn.update(pos)

    def draw(self, screen):
        screen.fill(COLORS["BG"])
        font = AssetManager.get_font(50)
        title = "PLAYER 1: Escolha" if not self.p1_char else "PLAYER 2: Escolha"
        color = COLORS["RED"] if not self.p1_char else COLORS["GREEN"]
        
        txt = font.render(title, True, color)
        screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 50))
        
        for btn in self.buttons:
            btn.draw(screen)
            if self.p1_char == btn.payload:
                pygame.draw.circle(screen, COLORS["RED"], (btn.rect.left - 20, btn.rect.centery), 10)
            if self.p2_char == btn.payload:
                pygame.draw.circle(screen, COLORS["GREEN"], (btn.rect.right + 20, btn.rect.centery), 10)
