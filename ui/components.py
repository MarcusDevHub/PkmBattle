import pygame
from config import COLORS
from assets_manager import AssetManager

class HealthBar:
    def __init__(self, x, y, width=200, height=25):
        self.rect = pygame.Rect(x, y, width, height)
        self.cd_rect = pygame.Rect(x, y + height + 5, width, 8)
    
    def draw(self, surface, pokemon):
        # HP
        ratio_hp = max(0, pokemon.hp / pokemon.max_hp)
        fill_hp = pygame.Rect(self.rect.x, self.rect.y, int(self.rect.width * ratio_hp), self.rect.height)
        c_hp = COLORS["GREEN"] if ratio_hp > 0.3 else COLORS["RED"]
        
        pygame.draw.rect(surface, (50, 50, 50), self.rect)
        pygame.draw.rect(surface, c_hp, fill_hp)
        pygame.draw.rect(surface, COLORS["WHITE"], self.rect, 2)
        
        # CD
        if pokemon.max_cooldown > 0:
            ratio_cd = 1.0 - (pokemon.current_cooldown / pokemon.max_cooldown)
        else: ratio_cd = 1.0
        
        ratio_cd = max(0.0, min(1.0, ratio_cd))
        fill_cd = pygame.Rect(self.cd_rect.x, self.cd_rect.y, int(self.cd_rect.width * ratio_cd), self.cd_rect.height)
        c_cd = (255, 255, 0) if ratio_cd >= 0.99 else (0, 200, 255)
        
        pygame.draw.rect(surface, (30, 30, 30), self.cd_rect)
        pygame.draw.rect(surface, c_cd, fill_cd)
        pygame.draw.rect(surface, (100, 100, 100), self.cd_rect, 1)
        
        # Text
        font = AssetManager.get_font(28)
        surface.blit(font.render(pokemon.name, True, COLORS["WHITE"]), (self.rect.x, self.rect.y - 25))

class Button:
    def __init__(self, x, y, w, h, text, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover = False
        self.payload = None # Guarda ID do ataque ou nome do char
        
    def update(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)
        
    def draw(self, surface):
        c = self.color
        if self.hover: c = (min(c[0]+40, 255), min(c[1]+40, 255), min(c[2]+40, 255))
        border = COLORS["WHITE"] if self.hover else self.color
        
        pygame.draw.rect(surface, (40,40,50), self.rect)
        pygame.draw.rect(surface, border, self.rect, 3)
        
        font = AssetManager.get_font(26)
        txt = font.render(self.text, True, c)
        surface.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.centery - txt.get_height()//2))
