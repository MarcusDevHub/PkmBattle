import pygame
import math
import random
from config import COLORS, ATTACKS_DB
from .projectile import Projectile
from .particle import Particle

class AttackBase:
    def __init__(self, owner, stats):
        self.owner = owner
        self.stats = stats
        
        # Balanceamento: Cooldown base * 3 para ficar visível na UI
        self.max_cooldown = stats.get("cd", 40) * 3
        self.cooldown_timer = 0
        
        self.is_active = False
        self.duration_timer = 0 # Quanto tempo o ataque dura acontecendo

    def can_use(self):
        # Só pode usar se não estiver em cooldown E não estiver atacando agora
        return self.cooldown_timer <= 0 and not self.is_active

    def start(self, projectiles_group):
        self.is_active = True
        self.on_start(projectiles_group)

    def update(self, projectiles_group, particles_list):
        # 1. Se o ataque acabou, recupera cooldown
        if not self.is_active:
            if self.cooldown_timer > 0:
                self.cooldown_timer -= 1
        
        # 2. Se o ataque está acontecendo, processa lógica
        else:
            self.duration_timer -= 1
            self.on_update(projectiles_group, particles_list)
            
            if self.duration_timer <= 0:
                self.finish()

    def finish(self):
        self.is_active = False
        self.cooldown_timer = self.max_cooldown # Inicia a recarga
        self.on_finish()

    # --- Hooks para as subclasses ---
    def on_start(self, projectiles): pass
    def on_update(self, projectiles, particles): pass
    def on_finish(self): pass
    def draw(self, surface): pass
    def modify_incoming_damage(self, amount): return amount


# ==============================================================================
# ARQUÉTIPO 1: TIRO GUIADO (Shadow Ball, Energy Ball)
# ==============================================================================
class HomingAttack(AttackBase):
    def on_start(self, projectiles):
        # Lança e libera o Pokémon imediatamente
        p = Projectile(self.owner, self.owner.enemy_ref)
        # Força tipo HOMING independente do config para garantir comportamento
        p.type = "HOMING" 
        p.color = self.stats["color"]
        p._setup_behavior() # Re-aplica comportamento
        p.base_image = p._create_image()
        p.image = p.base_image.copy()
        
        projectiles.add(p)
        self.duration_timer = 5 # Animação muito breve

# ==============================================================================
# ARQUÉTIPO 2: METRALHADORA (Water Shuriken, Bullet Seed)
# ==============================================================================
class RapidFireAttack(AttackBase):
    def on_start(self, projectiles):
        self.shots_to_fire = 3
        self.fire_interval = 8
        self.current_interval = 0
        self.duration_timer = 100 # Tempo de segurança

    def on_update(self, projectiles, particles):
        # Diminui velocidade do dono enquanto atira
        self.owner.vel *= 0.8
        
        if self.shots_to_fire > 0:
            if self.current_interval <= 0:
                # Dispara
                p = Projectile(self.owner, self.owner.enemy_ref)
                p.type = "RAPID"
                p.color = self.stats["color"]
                p._setup_behavior()
                p.base_image = p._create_image()
                p.image = p.base_image.copy()
                projectiles.add(p)
                
                self.shots_to_fire -= 1
                self.current_interval = self.fire_interval
            else:
                self.current_interval -= 1
        else:
            self.finish() # Acabou munição

# ==============================================================================
# ARQUÉTIPO 3: RAIO LASER (Solar Beam, Hyper Beam)
# ==============================================================================
class LaserAttack(AttackBase):
    def on_start(self, projectiles):
        self.duration_timer = 45 # 0.75 segundos travado atirando
        # Cria um projétil "falso" que é apenas visual/hitbox
        # Na verdade, vamos criar vários projéteis rápidos em linha
        self.fire_rate = 3

    def on_update(self, projectiles, particles):
        # TRAVA o Pokémon totalmente
        self.owner.vel *= 0
        
        # Gera partículas de carga
        if self.duration_timer > 30:
            particles.append(Particle(
                self.owner.pos.x + random.randint(-20, 20),
                self.owner.pos.y + random.randint(-20, 20),
                self.stats["color"], 2, 10
            ))
        else:
            # DISPARA (fase de dano)
            if self.duration_timer % self.fire_rate == 0:
                # Cria projétil de altíssima velocidade
                p = Projectile(self.owner, self.owner.enemy_ref)
                p.type = "RAPID" # Usa lógica simples de tiro
                p.life = 20 # Vida curta (range limitado pelo tempo)
                p.vel = (self.owner.enemy_ref.pos - self.owner.pos).normalize() * 25
                p.color = self.stats["color"]
                p.base_image = pygame.Surface((20, 20))
                p.base_image.fill(p.color)
                p.image = p.base_image.copy()
                p.rect = p.image.get_rect(center=(int(self.owner.pos.x), int(self.owner.pos.y)))
                projectiles.add(p)

# ==============================================================================
# ARQUÉTIPO 4: CORPO A CORPO / DASH (Thunder Punch, Tackle)
# ==============================================================================
class MeleeAttack(AttackBase):
    def on_start(self, projectiles):
        self.duration_timer = 15
        # Impulso na direção do inimigo
        direction = (self.owner.enemy_ref.pos - self.owner.pos).normalize()
        self.dash_vel = direction * 15 # Dash rápido

        # Cria hitbox de dano (projétil invisível na frente)
        p = Projectile(self.owner, self.owner.enemy_ref)
        p.life = 10
        p.vel = direction * 18
        p.base_image = pygame.Surface((40, 40), pygame.SRCALPHA) # Hitbox grande invisivel
        # p.base_image.fill((255, 0, 0, 100)) # Descomente para ver a hitbox (debug)
        p.image = p.base_image.copy()
        p.rect = p.image.get_rect(center=(int(self.owner.pos.x), int(self.owner.pos.y)))
        projectiles.add(p)

    def on_update(self, projectiles, particles):
        # Força movimento manual (Dash)
        self.owner.pos += self.dash_vel
        # Partículas de rastro
        particles.append(Particle(
            self.owner.pos.x, self.owner.pos.y,
            self.stats["color"], 4, 15
        ))

# ==============================================================================
# ARQUÉTIPO 5: ÁREA / DEFESA (Earthquake, Iron Defense)
# ==============================================================================
class ZoneAttack(AttackBase):
    def on_start(self, projectiles):
        self.duration_timer = 60 # 1 segundo ativo
        self.radius = 0
        self.is_shield = (self.stats["type"] == "SHIELD")

    def on_update(self, projectiles, particles):
        # Se for escudo, trava movimento. Se for terremoto, só desacelera.
        if self.is_shield:
            self.owner.vel *= 0
        else:
            self.owner.vel *= 0.5
            
        # Expande raio visual
        self.radius = 120 + math.sin(pygame.time.get_ticks() * 0.05) * 10

        # Lógica de Dano de Área (Earthquake)
        if not self.is_shield:
            enemy = self.owner.enemy_ref
            if self.owner.pos.distance_to(enemy.pos) < 140:
                # Dano por tick
                if self.duration_timer % 10 == 0:
                    enemy.take_damage(5)
                    # Empurrão para fora da área
                    vec = (enemy.pos - self.owner.pos).normalize() * 15
                    enemy.pos += vec
        
        # Partículas
        if random.random() < 0.2:
            particles.append(Particle(
                self.owner.pos.x + random.randint(-60, 60),
                self.owner.pos.y + random.randint(-60, 60),
                self.stats["color"], 2, 20
            ))

    def modify_incoming_damage(self, amount):
        if self.is_shield:
            return 0 # Imune
        return amount

    def draw(self, surface):
        # Desenha o círculo no chão
        pygame.draw.circle(surface, self.stats["color"], 
                           (int(self.owner.pos.x), int(self.owner.pos.y)), 
                           int(self.radius), 4)


# ==============================================================================
# FÁBRICA (Factory)
# ==============================================================================
def create_attack(owner, attack_id):
    stats = ATTACKS_DB.get(attack_id, ATTACKS_DB[0])
    t = stats["type"]
    
    if t == "HOMING": return HomingAttack(owner, stats)
    if t == "RAPID": return RapidFireAttack(owner, stats)
    if t == "LASER": return LaserAttack(owner, stats)
    if t == "PHYSICAL": return MeleeAttack(owner, stats)
    if t == "AREA" or t == "SHIELD": return ZoneAttack(owner, stats)
    if t == "TRAIL": return HomingAttack(owner, stats) # Trail vira Homing simples por enquanto
    
    # Fallback
    return HomingAttack(owner, stats)
