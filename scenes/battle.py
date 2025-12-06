import pygame
import math
from config import *
from assets_manager import AssetManager
from entities.pokemon import Pokemon
from ui.components import HealthBar

class BattleScene:
    def __init__(self, game, p1_data, p2_data):
        self.game = game
        self.p1 = Pokemon("Player 1", 200, 300, p1_data[0], p1_data[1])
        self.p2 = Pokemon("Player 2", 600, 300, p2_data[0], p2_data[1])
        self.p1.enemy_ref = self.p2
        self.p2.enemy_ref = self.p1
        
        self.sprites = pygame.sprite.Group(self.p1, self.p2)
        self.projectiles = pygame.sprite.Group()
        self.particles = []
        
        self.ui_p1 = HealthBar(50, 50)
        self.ui_p2 = HealthBar(SCREEN_WIDTH - 250, 50)
        
        self.hitstop = 0
        self.winner = None

    def handle_event(self, event):
        # Se pressionar ESC a qualquer momento, volta pro menu
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            print("[GAME] Batalha cancelada pelo usuário.")
            self.game.change_scene("CHAR_SELECT")
            return
        # Se houver um vencedor, pressionar ESPAÇO reinicia o jogo
        if self.winner and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.game.change_scene("CHAR_SELECT")

    def update(self):
        if self.winner: return
        if self.hitstop > 0:
            self.hitstop -= 1
            return

        self.sprites.update(1, self.projectiles, self.particles)
        self.projectiles.update(self.particles)
        for p in self.particles[:]:
            p.update()
            if p.life <= 0: self.particles.remove(p)
            
        self._collisions()
        if self.p1.hp <= 0: self.winner = "PLAYER 2"
        elif self.p2.hp <= 0: self.winner = "PLAYER 1"

    def _collisions(self):
        # Física (Distância reduzida para 50)
        dx = self.p1.pos.x - self.p2.pos.x
        dy = self.p1.pos.y - self.p2.pos.y
        dist = math.hypot(dx, dy) or 1
        if dist < 50:
            push = (50 - dist) * 0.5
            self.p1.pos += pygame.math.Vector2((dx/dist)*push, (dy/dist)*push)
            self.p1.vel, self.p2.vel = self.p2.vel, self.p1.vel

        # Dano
        hits = pygame.sprite.groupcollide(self.sprites, self.projectiles, False, False)
        for poke, projs in hits.items():
            for p in projs:
                if p.owner != poke and not p.dying:
                    hs = poke.take_damage(p.damage)
                    self.hitstop = hs
                    p.kill_sequence()

    def draw(self, screen):
        screen.fill(COLORS["BG"])
        pygame.draw.rect(screen, COLORS["BORDER"], ARENA_RECT, 4)
        
        for p in self.projectiles:
            if p.is_floor_hazard: screen.blit(p.image, p.rect)
            
        self.p1.draw_effects(screen)
        self.p2.draw_effects(screen)
        
        self.sprites.draw(screen)
        
        for p in self.projectiles:
            if not p.is_floor_hazard: screen.blit(p.image, p.rect)
        for p in self.particles: p.draw(screen)
            
        self.ui_p1.draw(screen, self.p1)
        self.ui_p2.draw(screen, self.p2)
        
        if self.winner:
            over = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            over.fill((0,0,0,180))
            screen.blit(over, (0,0))
            font = AssetManager.get_font(80)
            screen.blit(font.render(f"{self.winner} VENCEU!", True, COLORS["WHITE"]), (150, 250))
