import pygame
from config import *
from assets_manager import AssetManager

class HealthBar:
    def __init__(self, x, y, width=200, height=25):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = (50, 50, 50)
        
    def draw(self, surface, pokemon):
        ratio = max(0, pokemon.hp / pokemon.max_hp)
        fill_w = int(self.rect.width * ratio)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_w, self.rect.height)
        
        color = COLORS["GREEN"] if ratio > 0.3 else COLORS["RED"]
        
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, color, fill_rect)
        pygame.draw.rect(surface, COLORS["WHITE"], self.rect, 2)
        
        font = AssetManager.get_font(28)
        txt = font.render(f"{pokemon.name}", True, COLORS["WHITE"])
        surface.blit(txt, (self.rect.x, self.rect.y - 25))

class Button:
    def __init__(self, x, y, w, h, text, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.base_color = color
        self.hover = False
        self.attack_id = None # Para armazenar metadados
        
    def update(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)
        
    def draw(self, surface):
        # Efeito de brilho no hover
        c = self.base_color
        if self.hover:
            c = (min(c[0]+40, 255), min(c[1]+40, 255), min(c[2]+40, 255))
        
        border = COLORS["WHITE"] if self.hover else self.base_color
        
        pygame.draw.rect(surface, (40,40,50), self.rect)
        pygame.draw.rect(surface, border, self.rect, 3)
        
        font = AssetManager.get_font(26)
        txt = font.render(self.text, True, c)
        surface.blit(txt, (self.rect.x + 10, self.rect.y + 25))
