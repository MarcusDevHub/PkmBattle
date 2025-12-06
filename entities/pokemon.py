import pygame
import math
import random
from config import *
from assets_manager import AssetManager
from .projectile import Projectile
from .particle import Particle

class Pokemon(pygame.sprite.Sprite):
    def __init__(self, name, x, y, attack_id, img_filename):
        super().__init__()
        self.name = name
        self.attack_id = attack_id
        self.stats = ATTACKS_DB[attack_id]
        
        self.hp = self.max_hp = 100
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(random.choice([-2, 2]), random.choice([-2, 2]))
        
        self.timers = {"attack": 0, "stun": 0, "flash": 0}
        self.immunity_timers = {}
        self.enemy_ref = None
        
        # Animação
        self.angle = 0
        self.breathe_phase = 0.0
        self.breathe_intensity = 0.18 # Intenso
        
        self._init_graphics(img_filename)

    def _init_graphics(self, filename):
        # 120x120 pixels
        self.original_image = AssetManager.get_image(filename, (120, 120))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=self.pos)
        self.radius = max(self.image.get_width(), self.image.get_height()) // 2
        
        # Máscara para Flash Vermelho (Preenchida)
        mask = pygame.mask.from_surface(self.original_image)
        self.hit_image = mask.to_surface(setcolor=(255, 0, 0, 255), unsetcolor=(0, 0, 0, 0))

    def update(self, dt, projectiles_group, particles_list):
        self._update_timers()
        self._handle_ai(projectiles_group, particles_list)
        self._handle_movement()
        self._handle_animation()

    def _update_timers(self):
        for k in self.timers:
            if self.timers[k] > 0: self.timers[k] -= 1
        
        for k in list(self.immunity_timers.keys()):
            if self.immunity_timers[k] > 0: self.immunity_timers[k] -= 1
            else: del self.immunity_timers[k]

    def _handle_movement(self):
        if self.timers["stun"] > 0:
            self.vel *= 0.9
            
        self.pos += self.vel
        
        # Paredes
        r = self.radius
        if self.pos.x - r < ARENA_RECT.left:   self.pos.x = ARENA_RECT.left + r; self.vel.x *= -1
        elif self.pos.x + r > ARENA_RECT.right: self.pos.x = ARENA_RECT.right - r; self.vel.x *= -1
        if self.pos.y - r < ARENA_RECT.top:    self.pos.y = ARENA_RECT.top + r; self.vel.y *= -1
        elif self.pos.y + r > ARENA_RECT.bottom:self.pos.y = ARENA_RECT.bottom - r; self.vel.y *= -1

        if self.timers["stun"] <= 0:
            s = self.vel.length()
            if s < 2: self.vel.scale_to_length(2)
            if s > 12: self.vel.scale_to_length(12)

    def _handle_animation(self):
        # Respiração Intensa e Clara
        self.breathe_phase += 0.12
        # Senoide mapeada para 0 a 1
        factor = (math.sin(self.breathe_phase) + 1) / 2
        scale_y = 1.0 + factor * self.breathe_intensity
        
        w, h = self.original_image.get_size()
        new_h = int(h * scale_y)
        
        img_anim = pygame.transform.smoothscale(self.original_image, (w, new_h))
        hit_anim = pygame.transform.smoothscale(self.hit_image, (w, new_h))

        # Rotação Suave
        rot_speed = 3 + (self.vel.length() * 0.4)
        self.angle += rot_speed
        
        img_rot = pygame.transform.rotate(img_anim, self.angle)
        hit_rot = pygame.transform.rotate(hit_anim, self.angle)

        if self.timers["flash"] > 0:
            final = img_rot.copy()
            # Aplica o vermelho PREENCHIDO sobre o sprite
            final.blit(hit_rot, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            self.image = final
        else:
            self.image = img_rot
            
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def _handle_ai(self, projectiles, particles):
        atk_type = self.stats["type"]
        
        # Exemplo de alguns tipos (expandir conforme necessário)
        if atk_type == "HOMING" and random.randint(0, 180) == 0:
            projectiles.add(Projectile(self, self.enemy_ref))
        
        elif atk_type == "TRAIL":
             if random.randint(0, 10) == 0:
                projectiles.add(Projectile(self, type_override="Fogo"))
             if self.vel.length() < 6: self.vel *= 1.05
             
        elif atk_type == "RAPID" and random.randint(0, 100) == 0:
             # Dispara 3 vezes rápido (lógica simplificada)
             projectiles.add(Projectile(self, self.enemy_ref))

    def take_damage(self, amount):
        self.hp -= amount
        self.timers["flash"] = 8
        return ATTACKS_DB[self.attack_id]["cd"] # Retorna hitstop time
