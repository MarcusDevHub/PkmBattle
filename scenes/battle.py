import pygame
import math
from config import *
from assets_manager import AssetManager
from entities.pokemon import Pokemon
from ui.components import HealthBar

class BattleScene:
    def __init__(self, game, p1_id, p2_id):
        self.game = game
        
        # Cria Pokémons (nomes de arquivo devem estar na pasta assets)
        self.p1 = Pokemon("Player 1", 200, 300, p1_id, "pokemon1.png")
        self.p2 = Pokemon("Player 2", 600, 300, p2_id, "pokemon2.png")
        
        # Referência cruzada para IA
        self.p1.enemy_ref = self.p2
        self.p2.enemy_ref = self.p1
        
        # Grupos de Sprites
        self.sprites = pygame.sprite.Group(self.p1, self.p2)
        self.projectiles = pygame.sprite.Group()
        self.particles = [] # Lista simples para partículas (mais rápido que Group)
        
        # UI
        self.ui_p1 = HealthBar(50, 50)
        self.ui_p2 = HealthBar(SCREEN_WIDTH - 250, 50)
        
        self.hitstop = 0
        self.winner = None

    def handle_event(self, event):
        # Se tiver vencedor, ESPAÇO volta pro menu
        if self.winner and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.game.change_scene("MENU")

    def update(self):
        # Pausa lógica se houver vencedor
        if self.winner: 
            return 
            
        # Hitstop (congelamento breve ao acertar)
        if self.hitstop > 0:
            self.hitstop -= 1
            return

        # Atualiza tudo
        # Passa dt=1 e as referências de grupos
        self.sprites.update(1, self.projectiles, self.particles)
        self.projectiles.update(self.particles)
        
        # Atualiza partículas
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)
            
        self._check_collisions()
        self._check_win()

    def _check_collisions(self):
        # Colisão Física (Empurrão)
        if pygame.sprite.collide_rect(self.p1, self.p2):
            dx = self.p1.pos.x - self.p2.pos.x
            dy = self.p1.pos.y - self.p2.pos.y
            dist = math.hypot(dx, dy) or 1
            
            push = 8
            self.p1.pos += pygame.math.Vector2(dx/dist*push, dy/dist*push)
            self.p1.vel, self.p2.vel = self.p2.vel, self.p1.vel

        # Colisão Projéteis -> Pokémons
        hits = pygame.sprite.groupcollide(self.sprites, self.projectiles, False, False)
        for poke, projs in hits.items():
            for p in projs:
                # Ignora se for o próprio dono ou se projétil já está morrendo
                if p.owner != poke and not p.dying:
                    hit_time = poke.take_damage(p.damage)
                    self.hitstop = hit_time
                    p.kill_sequence()

    def _check_win(self):
        if self.p1.hp <= 0: self.winner = "PLAYER 2"
        elif self.p2.hp <= 0: self.winner = "PLAYER 1"

    def draw(self, screen):
        screen.fill(COLORS["BG"])
        pygame.draw.rect(screen, COLORS["BORDER"], ARENA_RECT, 4)
        
        # 1. Desenha perigos de chão (Fogo)
        for p in self.projectiles:
            if getattr(p, 'is_floor_hazard', False): 
                screen.blit(p.image, p.rect)
            
        # 2. Desenha Pokémons
        self.sprites.draw(screen)
        
        # 3. Desenha Projéteis (Voadores)
        for p in self.projectiles:
            if not getattr(p, 'is_floor_hazard', False): 
                screen.blit(p.image, p.rect)
            
        # 4. Desenha Partículas
        for part in self.particles:
            part.draw(screen)
            
        # 5. UI
        self.ui_p1.draw(screen, self.p1)
        self.ui_p2.draw(screen, self.p2)
        
        # Tela de Vitória
        if self.winner:
            self._draw_win(screen)

    def _draw_win(self, screen):
        # Overlay escuro
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0,0))
        
        # Texto Vencedor
        fb = AssetManager.get_font(80)
        txt = fb.render(f"{self.winner} VENCEU!", True, COLORS["WHITE"])
        screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        # Instrução
        fs = AssetManager.get_font(40)
        inf = fs.render("Pressione ESPAÇO para Menu", True, COLORS["GREY"])
        screen.blit(inf, (SCREEN_WIDTH//2 - inf.get_width()//2, SCREEN_HEIGHT//2 + 50))
