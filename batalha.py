import pygame
import random
import math
import os

# =============================================================================
# CONFIGURAÇÕES GERAIS
# =============================================================================
LARGURA_TELA, ALTURA_TELA = 800, 600
FPS = 60
NOME_JANELA = "Batalha Pokémon - Respiração + Flash Correto"

COR_FUNDO = (20, 20, 30)
COR_ARENA_BORDA = (200, 200, 200)

BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (100, 100, 100)
CINZA_CLARO = (200, 200, 200)
VERMELHO = (255, 50, 50)
AZUL = (50, 100, 255)
VERDE_CLARO = (100, 255, 100)

C_ELETRICO = (255, 255, 0)
C_PLANTA = (0, 255, 0)
C_FANTASMA = (140, 80, 200)
C_TERRA = (210, 180, 100)
C_FOGO = (255, 100, 50)
C_AGUA = (50, 150, 255)
C_ACO = (180, 180, 200)
C_VENENO = (160, 60, 160)

LARGURA_ARENA = 600
ALTURA_ARENA = 450
ARENA_X = (LARGURA_TELA - LARGURA_ARENA) // 2
ARENA_Y = (ALTURA_TELA - ALTURA_ARENA) // 2 + 40
ARENA_RECT = pygame.Rect(ARENA_X, ARENA_Y, LARGURA_ARENA, ALTURA_ARENA)

# =============================================================================
# ATAQUES
# =============================================================================
ATAQUES_INFO = [
    {"id": 0, "nome": "Thunder Punch", "tipo": "CARGA_FISICA", "dano": 25, "hitstop": 20, "cor": C_ELETRICO, "desc": "Soco rápido c/ paralisia"},
    {"id": 1, "nome": "Solar Beam",    "tipo": "LASER",        "dano": 2,  "hitstop": 0,  "cor": C_PLANTA,   "desc": "Laser contínuo"},
    {"id": 2, "nome": "Shadow Ball",   "tipo": "GUIADO",       "dano": 15, "hitstop": 10, "cor": C_FANTASMA, "desc": "Projétil que persegue"},
    {"id": 3, "nome": "Earthquake",    "tipo": "AREA",         "dano": 20, "hitstop": 15, "cor": C_TERRA,    "desc": "Dano em área massivo"},
    {"id": 4, "nome": "Flame Wheel",   "tipo": "RASTRO",       "dano": 8,  "hitstop": 2,  "cor": C_FOGO,     "desc": "Deixa fogo no chão"},
    {"id": 5, "nome": "Water Shuriken","tipo": "TIRO_RAPIDO",  "dano": 6,  "hitstop": 5,  "cor": C_AGUA,     "desc": "3 disparos rápidos"},
    {"id": 6, "nome": "Iron Defense",  "tipo": "ESCUDO",       "dano": 0,  "hitstop": 20, "cor": C_ACO,      "desc": "Reflete dano físico"},
    {"id": 7, "nome": "Giga Drain",    "tipo": "DRENO",        "dano": 2,  "hitstop": 0,  "cor": C_VENENO,   "desc": "Suga vida do inimigo"}
]

# =============================================================================
# PARTÍCULAS
# =============================================================================
class Particula:
    def __init__(self, x, y, cor, velocidade, tamanho, vida_util):
        self.x = x
        self.y = y
        self.cor = cor
        self.vx = random.uniform(-velocidade, velocidade)
        self.vy = random.uniform(-velocidade, velocidade)
        self.tamanho = tamanho
        self.vida = vida_util
        self.vida_max = vida_util

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vida -= 1
        self.tamanho *= 0.93

    def draw(self, surface):
        if self.vida > 0 and self.tamanho > 0.5:
            alpha = int((self.vida / self.vida_max) * 255)
            s = pygame.Surface((int(self.tamanho*2), int(self.tamanho*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.cor, alpha), (int(self.tamanho), int(self.tamanho)), int(self.tamanho))
            surface.blit(s, (self.x - self.tamanho, self.y - self.tamanho))

# =============================================================================
# PROJÉTEIS
# =============================================================================
class Projetil(pygame.sprite.Sprite):
    def __init__(self, x, y, dono, tipo, alvo=None, direcao=None):
        super().__init__()
        self.dono = dono
        self.tipo = tipo
        self.alvo = alvo
        self.info = ATAQUES_INFO[dono.id_ataque]
        self.vida_util = 300

        self.morrendo = False
        self.escala = 1.0
        self.alpha = 255

        if tipo == "Shadow Ball":
            self.image_base = pygame.Surface((16, 16), pygame.SRCALPHA)
            self.image_base.fill(self.info["cor"])
            self.pos = pygame.math.Vector2(x, y)
            self.vel = pygame.math.Vector2(random.choice([-4, 4]), random.choice([-4, 4]))
        elif tipo == "Shuriken":
            self.image_base = pygame.Surface((10, 10), pygame.SRCALPHA)
            self.image_base.fill(self.info["cor"])
            self.pos = pygame.math.Vector2(x, y)
            self.vel = direcao * 12
        elif tipo == "Fogo":
            self.image_base = pygame.Surface((20, 20), pygame.SRCALPHA)
            self.image_base.fill(self.info["cor"])
            self.pos = pygame.math.Vector2(x, y)
            self.vel = pygame.math.Vector2(0, 0)
            self.vida_util = 180

        self.image = self.image_base.copy()
        self.rect = self.image.get_rect(center=(x, y))

    def iniciar_morte(self):
        if not self.morrendo:
            self.morrendo = True
            self.vel *= 0.5

    def update(self, particles):
        if self.morrendo:
            self.escala -= 0.1
            self.alpha -= 20
            if self.escala <= 0 or self.alpha <= 0:
                self.kill()
                return
            novo_tam = int(self.image_base.get_width() * self.escala)
            if novo_tam > 0:
                self.image = pygame.transform.scale(self.image_base, (novo_tam, novo_tam))
                self.image.set_alpha(self.alpha)
                self.rect = self.image.get_rect(center=self.pos)
            return

        self.vida_util -= 1
        if self.vida_util <= 0:
            self.iniciar_morte()
            return

        if self.tipo == "Shadow Ball":
            if self.alvo:
                direcao = (self.alvo.pos - self.pos)
                if direcao.length() > 0:
                    self.vel = self.vel.lerp(direcao.normalize() * 7, 0.05)
            self.pos += self.vel
            if random.random() < 0.3:
                particles.append(Particula(self.rect.centerx, self.rect.centery, self.info["cor"], 1, 3, 15))
        elif self.tipo == "Shuriken":
            self.pos += self.vel
        elif self.tipo == "Fogo":
            if random.random() < 0.2:
                particles.append(Particula(self.rect.centerx, self.rect.centery, (255, 200, 0), 1, 4, 20))

        self.rect.center = self.pos
        if self.tipo != "Fogo" and not ARENA_RECT.colliderect(self.rect):
            self.kill()

# =============================================================================
# POKEMON (respiração + flash só no sprite)
# =============================================================================
class Pokemon(pygame.sprite.Sprite):
    def __init__(self, nome_dummy, x, y, cor, id_ataque, imagem_path=None):
        super().__init__()

        if imagem_path:
            nome_arquivo = os.path.basename(imagem_path)
            nome_sem_ext = os.path.splitext(nome_arquivo)[0]
            self.nome = nome_sem_ext.capitalize()
        else:
            self.nome = nome_dummy

        self.vida = 100
        self.vida_max = 100
        self.id_ataque = id_ataque
        self.info = ATAQUES_INFO[id_ataque]
        self.inimigo_ref = None

        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(random.choice([-2, 2]), random.choice([-2, 2]))
        self.angulo = 0

        self.timer_ataque = 0
        self.estado = "MOVENDO"
        self.timer_paralisia = 0
        self.soco_carregado = False
        self.defendendo = False
        self.timers_imunidade = {}

        self.dano_flash_timer = 0
        self.dano_flash_duracao = 8

        self.breathe_phase = 0.0
        self.breathe_intensidade = 0.09

        try:
            self.image_original = pygame.image.load(imagem_path).convert_alpha()
            self.image_original = pygame.transform.scale(self.image_original, (120, 120))
        except:
            self.image_original = pygame.Surface((120, 120), pygame.SRCALPHA)
            self.image_original.fill((0, 0, 0, 0))
            pygame.draw.circle(self.image_original, cor, (60, 60), 58)

        self.image = self.image_original
        self.rect = self.image.get_rect(center=(x, y))
        self.raio_colisao = max(self.image.get_width(), self.image.get_height()) // 2  # hitbox baseada no sprite

        # pré-calcula sprite vermelha usando máscara (só pixels não transparentes)
        mask = pygame.mask.from_surface(self.image_original)  # pega pixels não transparentes[web:67]

        # cria surface só com a silhueta do personagem, toda vermelha e fundo transparente
        self.image_hit = mask.to_surface(
        setsurface=None,
        unsetsurface=None,
        setcolor=(255, 0, 0, 255),   # onde tem sprite fica vermelho
        unsetcolor=(0, 0, 0, 0)      # onde é transparente continua totalmente transparente
        )  # [web:163]

    def update(self, grupo_projeteis, particles):
        remover = []
        for tipo, tempo in self.timers_imunidade.items():
            if tempo > 0:
                self.timers_imunidade[tipo] -= 1
            else:
                remover.append(tipo)
        for k in remover:
            del self.timers_imunidade[k]

        if self.timer_paralisia > 0:
            self.timer_paralisia -= 1
            self.vel *= 0.9

        tipo_atk = self.info["tipo"]

        # ---------- lógica de ataque (igual antes) ----------
        if tipo_atk == "CARGA_FISICA":
            if self.estado == "MOVENDO":
                if self.inimigo_ref and self.pos.distance_to(self.inimigo_ref.pos) < 180:
                    if random.randint(0, 50) == 0:
                        self.estado = "CARREGANDO"
                        self.timer_ataque = 40
                        self.vel *= 0.1
            elif self.estado == "CARREGANDO":
                particles.append(Particula(self.pos.x, self.pos.y, self.info["cor"], 2, 4, 10))
                self.timer_ataque -= 1
                if self.timer_ataque <= 0:
                    self.estado = "ATACANDO"
                    self.soco_carregado = True
                    self.timer_ataque = 25
                    if self.inimigo_ref:
                        self.vel = (self.inimigo_ref.pos - self.pos).normalize() * 16
            elif self.estado == "ATACANDO":
                particles.append(Particula(self.pos.x, self.pos.y, BRANCO, 0, 8, 8))
                self.timer_ataque -= 1
                if self.timer_ataque <= 0:
                    self.estado = "MOVENDO"
                    self.soco_carregado = False
                    self.vel *= 0.2

        elif tipo_atk == "LASER" or tipo_atk == "DRENO":
            if self.estado == "MOVENDO":
                if random.randint(0, 150) == 0:
                    self.estado = "CARREGANDO"
                    self.timer_ataque = 50
                    self.vel *= 0.1
            elif self.estado == "CARREGANDO":
                cor = self.info["cor"]
                particles.append(Particula(self.pos.x + random.randint(-10, 10),
                                           self.pos.y + random.randint(-10, 10),
                                           cor, -1, 3, 15))
                self.timer_ataque -= 1
                if self.timer_ataque <= 0:
                    self.estado = "ATIRANDO"
                    self.timer_ataque = 30
            elif self.estado == "ATIRANDO":
                if self.inimigo_ref:
                    self.vel += (self.pos - self.inimigo_ref.pos).normalize() * 0.5
                self.timer_ataque -= 1
                if self.timer_ataque <= 0:
                    self.estado = "MOVENDO"

        elif tipo_atk == "GUIADO":
            if random.randint(0, 180) == 0:
                grupo_projeteis.add(Projetil(self.pos.x, self.pos.y, self,
                                             "Shadow Ball", self.inimigo_ref))

        elif tipo_atk == "AREA":
            if random.randint(0, 250) == 0:
                self.estado = "ATIVO_AREA"
                self.timer_ataque = 40
                self.vel *= 0.2
                if self.inimigo_ref and self.pos.distance_to(self.inimigo_ref.pos) < 230:
                    self.inimigo_ref.vida -= self.info["dano"]
                    self.inimigo_ref.dano_flash_timer = self.inimigo_ref.dano_flash_duracao
                    emp = (self.inimigo_ref.pos - self.pos).normalize() * 25
                    self.inimigo_ref.vel += emp

        elif tipo_atk == "RASTRO":
            if random.randint(0, 10) == 0:
                grupo_projeteis.add(Projetil(self.pos.x, self.pos.y, self, "Fogo"))
            if self.vel.length() < 6:
                self.vel *= 1.05

        elif tipo_atk == "TIRO_RAPIDO":
            if self.estado == "MOVENDO":
                if random.randint(0, 100) == 0:
                    self.estado = "DISPARANDO"
                    self.timer_ataque = 3
                    self.intervalo_tiro = 0
            elif self.estado == "DISPARANDO":
                self.intervalo_tiro -= 1
                if self.intervalo_tiro <= 0:
                    if self.inimigo_ref:
                        dir_tiro = (self.inimigo_ref.pos - self.pos).normalize()
                        dir_tiro = dir_tiro.rotate(random.uniform(-10, 10))
                        grupo_projeteis.add(Projetil(self.pos.x, self.pos.y, self,
                                                     "Shuriken", direcao=dir_tiro))
                    self.timer_ataque -= 1
                    self.intervalo_tiro = 8
                    if self.timer_ataque <= 0:
                        self.estado = "MOVENDO"

        elif tipo_atk == "ESCUDO":
            if self.estado == "MOVENDO":
                if random.randint(0, 200) == 0:
                    self.estado = "DEFENDENDO"
                    self.defendendo = True
                    self.timer_ataque = 90
                    self.vel *= 0.5
            elif self.estado == "DEFENDENDO":
                self.timer_ataque -= 1
                if self.timer_ataque <= 0:
                    self.defendendo = False
                    self.estado = "MOVENDO"

        # ---------- movimento / paredes ----------
        self.pos += self.vel

        bateu = False
        if self.pos.x - self.raio_colisao < ARENA_RECT.left:
            self.pos.x = ARENA_RECT.left + self.raio_colisao
            self.vel.x *= -1
            bateu = True
        elif self.pos.x + self.raio_colisao > ARENA_RECT.right:
            self.pos.x = ARENA_RECT.right - self.raio_colisao
            self.vel.x *= -1
            bateu = True
        if self.pos.y - self.raio_colisao < ARENA_RECT.top:
            self.pos.y = ARENA_RECT.top + self.raio_colisao
            self.vel.y *= -1
            bateu = True
        elif self.pos.y + self.raio_colisao > ARENA_RECT.bottom:
            self.pos.y = ARENA_RECT.bottom - self.raio_colisao
            self.vel.y *= -1
            bateu = True

        if bateu:
            self.vel *= random.uniform(0.9, 1.2)
            v_len = self.vel.length()
            if v_len < 2:
                self.vel.scale_to_length(2)
            if v_len > 12:
                self.vel.scale_to_length(12)

        # ---------- animação (respiração + flash) ----------
        self.breathe_phase += 0.12
        fator = (math.sin(self.breathe_phase) + 1) / 2  # varia de 0 a 1
        escala_y = 1.0 + fator * self.breathe_intensidade 
        escala_x = 1.0 

        base_img = self.image_original
        larg = max(1, int(base_img.get_width() * escala_x))
        alt  = max(1, int(base_img.get_height() * escala_y))
        img_breathe = pygame.transform.smoothscale(base_img, (larg, alt))
        img_hit_breathe = pygame.transform.smoothscale(self.image_hit, (larg, alt))  # mesma respiração no hit

        rot_speed = 5 + (self.vel.length())
        self.angulo += (rot_speed * 0.5)
        img_rot = pygame.transform.rotate(img_breathe, self.angulo)
        img_hit_rot = pygame.transform.rotate(img_hit_breathe, self.angulo)

        if self.dano_flash_timer > 0:
            self.dano_flash_timer -= 1
            final_image = img_rot.copy()
            final_image.blit(img_hit_rot, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)  # vermelho só onde há sprite[web:123]
        else:
            final_image = img_rot

        self.image = final_image
        self.rect = self.image.get_rect(center=self.pos)

    def draw_special(self, surface):
        tipo = self.info["tipo"]

        if (tipo == "LASER" or tipo == "DRENO") and self.estado == "ATIRANDO":
            if self.inimigo_ref:
                cor_raio = self.info["cor"]
                start = self.pos
                end = self.inimigo_ref.pos
                largura = random.randint(8, 15)
                pygame.draw.line(surface, cor_raio, start, end, largura)
                pygame.draw.line(surface, BRANCO, start, end, 4)
                dano = self.info["dano"]
                self.inimigo_ref.vida -= dano
                self.inimigo_ref.dano_flash_timer = self.inimigo_ref.dano_flash_duracao
                if tipo == "DRENO":
                    self.vida = min(self.vida_max, self.vida + dano)

        elif tipo == "AREA" and self.estado == "ATIVO_AREA":
            raio = (40 - self.timer_ataque) * 6
            pygame.draw.circle(surface, self.info["cor"],
                               (int(self.pos.x), int(self.pos.y)), int(raio), 4)
            self.timer_ataque -= 1
            if self.timer_ataque <= 0:
                self.estado = "MOVENDO"

        elif tipo == "ESCUDO" and self.defendendo:
            pygame.draw.circle(surface, self.info["cor"],
                               (int(self.pos.x), int(self.pos.y)), 50, 3)
            pygame.draw.circle(surface, (255, 255, 255, 100),
                               (int(self.pos.x), int(self.pos.y)), 45, 1)

# =============================================================================
# MENU
# =============================================================================
class BotaoAtaque:
    def __init__(self, x, y, w, h, info):
        self.rect = pygame.Rect(x, y, w, h)
        self.info = info
        self.hover = False

    def draw(self, tela):
        cor = self.info["cor"]
        if self.hover:
            pygame.draw.rect(tela, cor, self.rect)
            pygame.draw.rect(tela, BRANCO, self.rect, 3)
            cor_texto = PRETO
        else:
            pygame.draw.rect(tela, (40, 40, 50), self.rect)
            pygame.draw.rect(tela, cor, self.rect, 2)
            cor_texto = cor

        font = pygame.font.Font(None, 26)
        font_peq = pygame.font.Font(None, 18)
        txt_nome = font.render(self.info["nome"], True, cor_texto)
        txt_desc = font_peq.render(self.info["desc"], True,
                                   BRANCO if not self.hover else PRETO)
        tela.blit(txt_nome, (self.rect.x + 10, self.rect.y + 10))
        tela.blit(txt_desc, (self.rect.x + 10, self.rect.y + 40))

    def check_hover(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)

    def check_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

def tela_menu_mouse(tela):
    botoes = []
    cols = 2
    largura_btn = 350
    altura_btn = 70
    espaco_x = 20
    espaco_y = 20
    start_x = (LARGURA_TELA - (cols * largura_btn + (cols - 1) * espaco_x)) // 2
    start_y = 150

    for i, info in enumerate(ATAQUES_INFO):
        c = i % cols
        r = i // cols
        x = start_x + c * (largura_btn + espaco_x)
        y = start_y + r * (altura_btn + espaco_y)
        botoes.append(BotaoAtaque(x, y, largura_btn, altura_btn, info))

    p1_choice = None
    p2_choice = None
    font_titulo = pygame.font.Font(None, 40)

    rodando = True
    while rodando:
        mouse_pos = pygame.mouse.get_pos()
        tela.fill(COR_FUNDO)

        if p1_choice is None:
            txt = font_titulo.render("PLAYER 1: Escolha seu Ataque", True, VERMELHO)
        elif p2_choice is None:
            txt = font_titulo.render("PLAYER 2: Escolha seu Ataque", True, AZUL)
        else:
            txt = font_titulo.render("PRONTO! Pressione qualquer tecla...", True, VERDE_CLARO)

        tela.blit(txt, (LARGURA_TELA // 2 - txt.get_width() // 2, 50))

        for btn in botoes:
            btn.check_hover(mouse_pos)
            btn.draw(tela)

        if p1_choice is not None:
            btn = botoes[p1_choice]
            pygame.draw.circle(tela, VERMELHO,
                               (btn.rect.right - 20, btn.rect.centery), 10)
        if p2_choice is not None:
            btn = botoes[p2_choice]
            pygame.draw.circle(tela, AZUL,
                               (btn.rect.right - 45, btn.rect.centery), 10)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, btn in enumerate(botoes):
                    if btn.check_click(mouse_pos):
                        if p1_choice is None:
                            p1_choice = i
                        elif p2_choice is None:
                            p2_choice = i
                            rodando = False

    return p1_choice, p2_choice

# =============================================================================
# BATALHA (vitória com ESPAÇO)
# =============================================================================
def rodar_batalha(tela, id1, id2):
    info1 = ATAQUES_INFO[id1]
    info2 = ATAQUES_INFO[id2]

    poke1 = Pokemon("P1", 200, 300, info1["cor"], id1, "assets/pokemon1.png")
    poke2 = Pokemon("P2", 600, 300, info2["cor"], id2, "assets/pokemon2.png")
    poke1.inimigo_ref = poke2
    poke2.inimigo_ref = poke1

    grupo_pokes = pygame.sprite.Group(poke1, poke2)
    grupo_projeteis = pygame.sprite.Group()
    particles = []

    clock = pygame.time.Clock()
    hitstop_timer = 0
    vencedor = None

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "SAIR"

        if vencedor:
            font_big = pygame.font.Font(None, 80)
            font_small = pygame.font.Font(None, 40)
            tela.fill(COR_FUNDO)
            txt_win = font_big.render(f"{vencedor} VENCEU!", True, BRANCO)
            txt_info = font_small.render("Pressione ESPAÇO para voltar ao menu", True, CINZA)
            tela.blit(txt_win, (LARGURA_TELA // 2 - txt_win.get_width() // 2,
                                ALTURA_TELA // 2 - 60))
            tela.blit(txt_info, (LARGURA_TELA // 2 - txt_info.get_width() // 2,
                                 ALTURA_TELA // 2 + 10))
            pygame.display.flip()

            esperando = True
            while esperando:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "SAIR"
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        return "MENU"
                pygame.time.Clock().tick(30)
            continue

        if hitstop_timer > 0:
            hitstop_timer -= 1
        else:
            grupo_pokes.update(grupo_projeteis, particles)
            grupo_projeteis.update(particles)
            for p in particles[:]:
                p.update()
                if p.vida <= 0:
                    particles.remove(p)

            # colisão física
            # colisão física com raio ajustável
            RAIO_COLISAO_POKES = 60  # experimente valores menores, ex: 60, 50

            dist = poke1.pos.distance_to(poke2.pos)
            if dist < RAIO_COLISAO_POKES:
                poke1.vel, poke2.vel = poke2.vel, poke1.vel
                dx, dy = poke1.pos.x - poke2.pos.x, poke1.pos.y - poke2.pos.y
                dist = math.hypot(dx, dy) or 1
                poke1.pos += (dx / dist) * 8, (dy / dist) * 8

                dano_p1 = 0
                dano_p2 = 0

                if poke1.info["tipo"] == "CARGA_FISICA" and poke1.soco_carregado:
                    dano_p1 = poke1.info["dano"]
                    poke2.timer_paralisia = 120
                    poke2.dano_flash_timer = poke2.dano_flash_duracao
                    poke1.soco_carregado = False
                    poke1.estado = "MOVENDO"
                    hitstop_timer = 20
                    if poke2.defendendo:
                        dano_p1 = 0
                        poke1.vel *= -2

                if poke2.info["tipo"] == "CARGA_FISICA" and poke2.soco_carregado:
                    dano_p2 = poke2.info["dano"]
                    poke1.timer_paralisia = 120
                    poke1.dano_flash_timer = poke1.dano_flash_duracao
                    poke2.soco_carregado = False
                    poke2.estado = "MOVENDO"
                    hitstop_timer = 20
                    if poke1.defendendo:
                        dano_p2 = 0
                        poke2.vel *= -2

                poke1.vida -= dano_p2
                poke2.vida -= dano_p1

                if dano_p1 > 0 or dano_p2 > 0:
                    for _ in range(15):
                        particles.append(Particula(poke1.pos.x, poke1.pos.y,
                                                   BRANCO, 4, 5, 20))

            # colisão com projéteis
            for p in grupo_pokes:
                hits = pygame.sprite.spritecollide(p, grupo_projeteis, False)
                for tiro in hits:
                    if tiro.dono != p and not tiro.morrendo:
                        tipo_dano = tiro.tipo
                        if p.timers_imunidade.get(tipo_dano, 0) > 0:
                            continue

                        dano = tiro.info["dano"]
                        if p.defendendo:
                            dano = 0
                            tiro.vel *= -1
                            tiro.dono = p
                            continue

                        p.vida -= dano
                        p.dano_flash_timer = p.dano_flash_duracao
                        hitstop_timer = tiro.info["hitstop"]

                        if tipo_dano == "Fogo":
                            p.timers_imunidade["Fogo"] = 30
                            hitstop_timer = 2

                        for _ in range(10):
                            particles.append(Particula(p.pos.x, p.pos.y,
                                                       tiro.info["cor"], 3, 5, 20))
                        tiro.iniciar_morte()

            if poke1.vida <= 0:
                vencedor = "JOGADOR 2"
            elif poke2.vida <= 0:
                vencedor = "JOGADOR 1"

        tela.fill(COR_FUNDO)
        pygame.draw.rect(tela, COR_ARENA_BORDA, ARENA_RECT, 4)

        poke1.draw_special(tela)
        poke2.draw_special(tela)

        for proj in grupo_projeteis:
            if proj.tipo == "Fogo":
                tela.blit(proj.image, proj.rect)

        grupo_pokes.draw(tela)

        for proj in grupo_projeteis:
            if proj.tipo != "Fogo":
                tela.blit(proj.image, proj.rect)

        for part in particles:
            part.draw(tela)

        def draw_bar(x, y, p):
            ratio = max(0, p.vida / p.vida_max)
            pygame.draw.rect(tela, (50, 50, 50), (x, y, 200, 25))
            pygame.draw.rect(tela,
                             (0, 255, 0) if ratio > 0.3 else (255, 0, 0),
                             (x, y, 200 * ratio, 25))
            pygame.draw.rect(tela, BRANCO, (x, y, 200, 25), 2)

            status = ""
            if p.timer_paralisia > 0:
                status += " [LENTO]"
            if p.defendendo:
                status += " [ESCUDO]"

            font_nome = pygame.font.Font(None, 28)
            font_atk = pygame.font.Font(None, 22)

            tela.blit(font_nome.render(f"{p.nome}{status}", True, BRANCO),
                      (x, y - 25))
            tela.blit(font_atk.render(f"Ataque: {p.info['nome']}", True, CINZA_CLARO),
                      (x, y + 30))

        draw_bar(50, 50, poke1)
        draw_bar(LARGURA_TELA - 250, 50, poke2)
        pygame.display.flip()

# =============================================================================
# MAIN
# =============================================================================
def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption(NOME_JANELA)

    while True:
        escolhas = tela_menu_mouse(tela)
        if escolhas[0] is None:
            break
        id1, id2 = escolhas
        res = rodar_batalha(tela, id1, id2)
        if res == "SAIR":
            break

    pygame.quit()

if __name__ == "__main__":
    main()
