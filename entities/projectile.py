import pygame
import random
from config import *
from .particle import Particle

class Projectile(pygame.sprite.Sprite):
    def __init__(self, owner, target=None, type_override=None):
        super().__init__()
        self.owner = owner
        self.stats = owner.stats
        self.damage = self.stats["dmg"]
        self.hitstop = ATTACKS_DB[owner.attack_id]["cd"]
        
        # Define tipo e override
        self.type = type_override if type_override else self.stats["type"]
        
        # Posição inicial
        self.pos = pygame.math.Vector2(owner.pos.x, owner.pos.y)
        self.vel = pygame.math.Vector2(0, 0)
        self.target = target
        self.dying = False
        self.scale = 1.0
        self.alpha = 255
        self.is_floor_hazard = False
        
        # 1. Cria a imagem base (Garante que não seja None)
        self.base_image = self._create_base_image()
        
        # 2. Define a imagem atual e o Rect (Agora é seguro)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        
        # 3. Define velocidade inicial
        self._setup_velocity()

    def _create_base_image(self):
        """Cria a superfície visual do projétil baseado no tipo."""
        color = self.stats["color"]
        
        if self.type in ["HOMING", "Shadow Ball"]:
            surf = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (8,8), 8)
            self.life = 300
            return surf
            
        elif self.type in ["RAPID", "Water Shuriken"]:
            surf = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.rect(surf, color, (0,0,12,12))
            self.life = 100
            return surf

        elif self.type == "Fogo":
            surf = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 100, 50), (12,12), 10)
            self.life = 180
            self.is_floor_hazard = True
            self.damage = 8
            return surf

        else: # Padrão / Fallback
            surf = pygame.Surface((10, 10))
            surf.fill(color)
            self.life = 60
            return surf

    def _setup_velocity(self):
        """Define a velocidade inicial."""
        if self.type in ["HOMING", "Shadow Ball"]:
            self.vel = pygame.math.Vector2(random.choice([-4, 4]), random.choice([-4, 4]))
            
        elif self.type in ["RAPID", "Water Shuriken"]:
            if self.target:
                try:
                    direction = (self.target.pos - self.pos).normalize()
                    direction = direction.rotate(random.uniform(-10, 10))
                    self.vel = direction * 12
                except ValueError: # Caso vetor seja zero
                    self.vel = pygame.math.Vector2(12, 0)
            else:
                self.vel = pygame.math.Vector2(12, 0)
                
        elif self.type == "Fogo":
            self.vel = pygame.math.Vector2(0, 0)
            
        else:
            self.vel = pygame.math.Vector2(0, 0)

    def update(self, particles_list):
        if self.dying:
            self._animate_death()
            return

        self.life -= 1
        if self.life <= 0:
            self.kill_sequence()
            return

        # Homing Logic
        if self.type == "HOMING" and self.target:
            try:
                dir_vec = (self.target.pos - self.pos)
                if dir_vec.length() > 0:
                    self.vel = self.vel.lerp(dir_vec.normalize() * 7, 0.08)
            except Exception:
                pass # Evita crash em cálculo de vetor
            
            if random.random() < 0.3:
                particles_list.append(Particle(self.pos.x, self.pos.y, self.stats["color"], 3, 15))

        # Fogo particles
        if self.type == "Fogo" and random.random() < 0.2:
             particles_list.append(Particle(self.pos.x, self.pos.y, (255, 200, 0), 4, 20))

        self.pos += self.vel
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Colisão com parede
        if not self.is_floor_hazard and not ARENA_RECT.colliderect(self.rect):
            self.kill()

    def kill_sequence(self):
        if not self.dying:
            self.dying = True
            self.vel *= 0.1

    def _animate_death(self):
        self.scale -= 0.15
        self.alpha -= 25
        
        if self.scale <= 0 or self.alpha <= 0:
            self.kill()
            return

        w = int(self.base_image.get_width() * self.scale)
        h = int(self.base_image.get_height() * self.scale)
        
        if w <= 0 or h <= 0:
            self.kill()
            return

        new_img = pygame.transform.scale(self.base_image, (w, h))
        new_img.set_alpha(max(0, self.alpha))
        self.image = new_img
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
