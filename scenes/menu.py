import pygame
from config import *
from assets_manager import AssetManager
from ui.components import Button

class MenuScene:
    def __init__(self, game):
        self.game = game
        self.buttons = []
        self.p1_sel = None
        self.p2_sel = None
        self._init_buttons()

    def _init_buttons(self):
        btn_w, btn_h = 350, 70
        spacing = 20
        start_y = 150
        
        # Centraliza grid
        total_w = (btn_w * 2) + spacing
        start_x = (SCREEN_WIDTH - total_w) // 2

        for i, (atk_id, info) in enumerate(ATTACKS_DB.items()):
            col = i % 2
            row = i // 2
            x = start_x + col * (btn_w + spacing)
            y = start_y + row * (btn_h + spacing)
            
            # Cria botão
            btn = Button(x, y, btn_w, btn_h, info["name"], info["color"])
            btn.attack_id = atk_id # Armazena ID no objeto botão
            self.buttons.append(btn)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for btn in self.buttons:
                if btn.rect.collidepoint(mouse_pos):
                    if self.p1_sel is None:
                        self.p1_sel = btn.attack_id
                    elif self.p2_sel is None:
                        self.p2_sel = btn.attack_id
                        # Inicia o jogo imediatamente ao selecionar o segundo
                        self.game.change_scene("BATTLE", self.p1_sel, self.p2_sel)
                    return # Evita cliques duplos acidentais no mesmo frame

    def update(self):
        pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(pos)

    def draw(self, screen):
        screen.fill(COLORS["BG"])
        
        font = AssetManager.get_font(40)
        if self.p1_sel is None:
            txt = font.render("PLAYER 1: Escolha o Ataque", True, COLORS["RED"])
        else:
            txt = font.render("PLAYER 2: Escolha o Ataque", True, COLORS["GREEN"])
        
        screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 50))

        for btn in self.buttons:
            btn.draw(screen)
            
            # Desenha indicadores de seleção
            if self.p1_sel == btn.attack_id:
                pygame.draw.circle(screen, COLORS["RED"], (btn.rect.right - 20, btn.rect.centery), 8)
            if self.p2_sel == btn.attack_id:
                pygame.draw.circle(screen, COLORS["GREEN"], (btn.rect.right - 45, btn.rect.centery), 8)
