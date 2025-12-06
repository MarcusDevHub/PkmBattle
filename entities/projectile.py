import pygame
import random
from config import ARENA_RECT
from .particle import Particle

class Projectile(pygame.sprite.Sprite):
    def __init__(self, owner, target, type_override=None):
        super().__init__()
        self.owner = owner
        # Pega stats do owner (que pega do attack_controller)
        self.stats = owner.stats 
        self.damage = self.stats["dmg"]
        
        # Define tipo
        self.type = type_override if type_override else self.stats["type"]
        self.color = (255, 100, 50) if self.type == "Fogo" else self.stats["color"]
        
        # Posição e Movimento
        self.pos = pygame.math.Vector2(owner.pos.x, owner.pos.y)
        self.target = target
        self.dying = False
        self.scale = 1.0
        self.alpha = 255
        self.is_floor_hazard = (self.type == "Fogo")
        self.life = 300
        
        # Configuração Visual/Física
        self._setup_behavior()
        
        # Gera Imagem
        self.base_image = self._create_image()
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def _create_image(self):
        if self.type in ["HOMING", "Shadow Ball"]:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(s, self.color, (8,8), 8)
            return s
        elif self.type == "Fogo":
            s = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(s, self.color, (12,12), 10)
            return s
        else:
            s = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.rect(s, self.color, (0,0,12,12))
            return s

    def _setup_behavior(self):
        if self.type == "HOMING":
            self.vel = pygame.math.Vector2(random.choice([-4, 4]), random.choice([-4, 4]))
        elif self.type == "Fogo":
            self.vel = pygame.math.Vector2(0, 0)
            self.life = 180
        else:
            # Tenta mirar no alvo
            try:
                direction = (self.target.pos - self.pos).normalize()
                if self.type == "RAPID": 
                    direction = direction.rotate(random.uniform(-10, 10))
                self.vel = direction * 12
            except:
                self.vel = pygame.math.Vector2(12, 0)

    def update(self, particles_list):
        if self.dying:
            self._animate_death()
            return

        self.life -= 1
        if self.life <= 0:
            self.kill_sequence()
            return

        # Comportamento Homing
        if self.type == "HOMING" and self.target:
            try:
                desired = (self.target.pos - self.pos).normalize() * 7
                self.vel = self.vel.lerp(desired, 0.08)
                if random.random() < 0.3:
                    particles_list.append(Particle(self.pos.x, self.pos.y, self.color, 3, 15))
            except: pass

        if self.type == "Fogo" and random.random() < 0.2:
             particles_list.append(Particle(self.pos.x, self.pos.y, (255, 200, 0), 4, 20))

        self.pos += self.vel
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        if not self.is_floor_hazard and not ARENA_RECT.colliderect(self.rect):
            self.kill()

    def kill_sequence(self):
        if not self.dying:
            self.dying = True
            self.vel *= 0.1

    def _animate_death(self):
        self.scale -= 0.15
        self.alpha -= 25
        if self.scale <= 0:
            self.kill()
            return
        w = max(1, int(self.base_image.get_width() * self.scale))
        h = max(1, int(self.base_image.get_height() * self.scale))
        self.image = pygame.transform.scale(self.base_image, (w, h))
        self.image.set_alpha(max(0, self.alpha))
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
