import pygame
import random
import math
import os  # Necessário para manipular nomes de arquivos e pastas

# =============================================================================
# --- CONFIGURAÇÕES GERAIS E CORES ---
# =============================================================================
LARGURA_TELA, ALTURA_TELA = 800, 600
FPS = 60
NOME_JANELA = "Batalha Pokémon - Versão Final Comentada"

# Cores RGB para desenhar elementos
COR_FUNDO = (20, 20, 30)        # Azul escuro (quase preto) para contraste
COR_ARENA_BORDA = (200, 200, 200)

BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (100, 100, 100)
CINZA_CLARO = (200, 200, 200)
VERMELHO = (255, 50, 50)
AZUL = (50, 100, 255)
VERDE_CLARO = (100, 255, 100)

# Cores Temáticas dos Tipos de Ataque
C_ELETRICO = (255, 255, 0)
C_PLANTA = (0, 255, 0)
C_FANTASMA = (140, 80, 200)
C_TERRA = (210, 180, 100)
C_FOGO = (255, 100, 50)
C_AGUA = (50, 150, 255)
C_ACO = (180, 180, 200)
C_VENENO = (160, 60, 160)

# Configuração da Arena (Onde a luta acontece)
LARGURA_ARENA = 600
ALTURA_ARENA = 450
# Centraliza matematicamente a arena na tela
ARENA_X = (LARGURA_TELA - LARGURA_ARENA) // 2
ARENA_Y = (ALTURA_TELA - ALTURA_ARENA) // 2 + 40
ARENA_RECT = pygame.Rect(ARENA_X, ARENA_Y, LARGURA_ARENA, ALTURA_ARENA)

# =============================================================================
# --- DICIONÁRIO DE ATAQUES ---
# Aqui configuramos o comportamento de cada habilidade.
# 'hitstop': Quantos frames o jogo congela ao acertar (impacto).
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
# --- CLASSE PARTÍCULA (Efeitos Visuais) ---
# Pequenos círculos que surgem em explosões e somem com o tempo.
# =============================================================================
class Particula:
    def __init__(self, x, y, cor, velocidade, tamanho, vida_util):
        self.x = x
        self.y = y
        self.cor = cor
        # Velocidade aleatória para criar efeito de explosão
        self.vx = random.uniform(-velocidade, velocidade)
        self.vy = random.uniform(-velocidade, velocidade)
        self.tamanho = tamanho
        self.vida = vida_util     # Tempo em frames que ela existe
        self.vida_max = vida_util

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vida -= 1            # Envelhece
        self.tamanho *= 0.93      # Encolhe um pouco a cada frame

    def draw(self, surface):
        if self.vida > 0 and self.tamanho > 0.5:
            # Calcula transparência baseada na vida restante
            alpha = int((self.vida / self.vida_max) * 255)
            # Cria superfície temporária para suportar transparência (Alpha)
            s = pygame.Surface((int(self.tamanho*2), int(self.tamanho*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.cor, alpha), (int(self.tamanho), int(self.tamanho)), int(self.tamanho))
            surface.blit(s, (self.x - self.tamanho, self.y - self.tamanho))

# =============================================================================
# --- CLASSE PROJÉTIL (Tiros e Poderes) ---
# Gerencia tudo que é atirado: Shadow Ball, Shuriken, Fogo no chão.
# =============================================================================
class Projetil(pygame.sprite.Sprite):
    def __init__(self, x, y, dono, tipo, alvo=None, direcao=None):
        super().__init__()
        self.dono = dono
        self.tipo = tipo
        self.alvo = alvo
        self.info = ATAQUES_INFO[dono.id_ataque]
        self.vida_util = 300 # Frames de vida antes de sumir sozinho
        
        # Variáveis para animação de desaparecimento suave
        self.morrendo = False
        self.escala = 1.0
        self.alpha = 255

        # Configuração Visual baseada no Tipo
        if tipo == "Shadow Ball":
            self.image_base = pygame.Surface((16, 16))
            self.image_base.fill(self.info["cor"])
            self.pos = pygame.math.Vector2(x, y)
            # Começa com direção aleatória, mas depois persegue
            self.vel = pygame.math.Vector2(random.choice([-4, 4]), random.choice([-4, 4]))
            
        elif tipo == "Shuriken":
            self.image_base = pygame.Surface((10, 10))
            self.image_base.fill(self.info["cor"])
            self.pos = pygame.math.Vector2(x, y)
            self.vel = direcao * 12 # Alta velocidade linear
            
        elif tipo == "Fogo":
            self.image_base = pygame.Surface((20, 20))
            self.image_base.fill(self.info["cor"])
            self.pos = pygame.math.Vector2(x, y)
            self.vel = pygame.math.Vector2(0, 0) # Fica parado no chão (Trap)
            self.vida_util = 180 # Dura 3 segundos

        self.image = self.image_base.copy()
        self.rect = self.image.get_rect(center=(x, y))

    def iniciar_morte(self):
        """Chamado quando o projétil acerta algo ou expira"""
        if not self.morrendo:
            self.morrendo = True
            self.vel *= 0.5 # Freia para sumir no local

    def update(self, particles):
        # Animação de Morte (Diminui e fica transparente)
        if self.morrendo:
            self.escala -= 0.1
            self.alpha -= 20
            if self.escala <= 0 or self.alpha <= 0:
                self.kill() # Remove do jogo
                return
            
            novo_tam = int(self.image_base.get_width() * self.escala)
            if novo_tam > 0:
                self.image = pygame.transform.scale(self.image_base, (novo_tam, novo_tam))
                self.image.set_alpha(self.alpha)
                self.rect = self.image.get_rect(center=self.pos)
            return

        # Contagem de vida normal
        self.vida_util -= 1
        if self.vida_util <= 0:
            self.iniciar_morte()
            return

        # Lógica de Movimento Específica
        if self.tipo == "Shadow Ball":
            # Perseguição (Homing): Ajusta vetor velocidade na direção do alvo
            if self.alvo:
                direcao = (self.alvo.pos - self.pos)
                if direcao.length() > 0:
                    # Lerp faz uma curva suave (0.05 = 5% de ajuste por frame)
                    self.vel = self.vel.lerp(direcao.normalize() * 7, 0.05)
            self.pos += self.vel
            # Rastro de partículas
            if random.random() < 0.3:
                particles.append(Particula(self.rect.centerx, self.rect.centery, self.info["cor"], 1, 3, 15))
                
        elif self.tipo == "Shuriken":
            self.pos += self.vel
            
        elif self.tipo == "Fogo":
            # Gera partículas de fogo enquanto parado
            if random.random() < 0.2:
                particles.append(Particula(self.rect.centerx, self.rect.centery, (255, 200, 0), 1, 4, 20))

        self.rect.center = self.pos
        
        # Remove projéteis (exceto fogo) que saem da arena
        if self.tipo != "Fogo" and not ARENA_RECT.colliderect(self.rect):
            self.kill()

# =============================================================================
# --- CLASSE POKEMON (O Personagem) ---
# Gerencia física, estados (atacando/movendo) e renderização.
# =============================================================================
class Pokemon(pygame.sprite.Sprite):
    def __init__(self, nome_dummy, x, y, cor, id_ataque, imagem_path=None):
        super().__init__()
        
        # --- LÓGICA DE NOME DE ARQUIVO ---
        # Transforma "assets/pikachu.png" em "Pikachu"
        if imagem_path:
            nome_arquivo = os.path.basename(imagem_path) # Pega só "pikachu.png"
            nome_sem_ext = os.path.splitext(nome_arquivo)[0] # Tira o ".png"
            self.nome = nome_sem_ext.capitalize() # Primeira letra maiúscula
        else:
            self.nome = nome_dummy

        # Atributos de RPG
        self.vida = 100
        self.vida_max = 100
        self.id_ataque = id_ataque
        self.info = ATAQUES_INFO[id_ataque]
        self.inimigo_ref = None # Referência ao oponente para saber onde mirar
        
        # Física (Vetores)
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(random.choice([-2, 2]), random.choice([-2, 2]))
        self.angulo = 0
        self.raio_colisao = 30
        
        # Máquina de Estados
        self.timer_ataque = 0
        self.estado = "MOVENDO" # Estados: MOVENDO, CARREGANDO, ATACANDO, ATIRANDO...
        self.timer_paralisia = 0
        self.soco_carregado = False
        self.defendendo = False
        self.timers_imunidade = {} # Evita dano infinito de fogo (i-frames)
        
        # Carregamento da Imagem
        try:
            self.image_original = pygame.image.load(imagem_path)
            self.image_original = pygame.transform.scale(self.image_original, (60, 60))
        except:
            # Fallback se não achar a imagem: Cria quadrado colorido
            self.image_original = pygame.Surface((60, 60))
            self.image_original.fill(cor)
            pygame.draw.circle(self.image_original, PRETO, (30,30), 28, 3)

        self.image = self.image_original
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, grupo_projeteis, particles):
        # --- Gerenciamento de Buffs/Debuffs ---
        
        # Reduz timers de imunidade
        chaves_para_remover = []
        for tipo, tempo in self.timers_imunidade.items():
            if tempo > 0:
                self.timers_imunidade[tipo] -= 1
            else:
                chaves_para_remover.append(tipo)
        for k in chaves_para_remover:
            del self.timers_imunidade[k]

        # Efeito de lentidão (Paralisia)
        if self.timer_paralisia > 0:
            self.timer_paralisia -= 1
            self.vel *= 0.9

        # --- MÁQUINA DE ESTADOS (IA DE ATAQUE) ---
        tipo_atk = self.info["tipo"]

        if tipo_atk == "CARGA_FISICA": # Ex: Thunder Punch
            if self.estado == "MOVENDO":
                # Se estiver perto, chance de começar a carregar o soco
                if self.inimigo_ref and self.pos.distance_to(self.inimigo_ref.pos) < 180:
                    if random.randint(0, 50) == 0:
                        self.estado = "CARREGANDO"
                        self.timer_ataque = 40
                        self.vel *= 0.1 # Para para concentrar
            elif self.estado == "CARREGANDO":
                # Efeito visual de carga
                particles.append(Particula(self.pos.x, self.pos.y, self.info["cor"], 2, 4, 10))
                self.timer_ataque -= 1
                if self.timer_ataque <= 0:
                    self.estado = "ATACANDO"
                    self.soco_carregado = True
                    self.timer_ataque = 25
                    # Dash na direção do inimigo
                    if self.inimigo_ref:
                        self.vel = (self.inimigo_ref.pos - self.pos).normalize() * 16
            elif self.estado == "ATACANDO":
                particles.append(Particula(self.pos.x, self.pos.y, BRANCO, 0, 8, 8))
                self.timer_ataque -= 1
                if self.timer_ataque <= 0:
                    self.estado = "MOVENDO"
                    self.soco_carregado = False
                    self.vel *= 0.2

        elif tipo_atk == "LASER" or tipo_atk == "DRENO": # Ex: Solar Beam
            if self.estado == "MOVENDO":
                if random.randint(0, 150) == 0:
                    self.estado = "CARREGANDO"
                    self.timer_ataque = 50
                    self.vel *= 0.1
            elif self.estado == "CARREGANDO":
                cor = self.info["cor"]
                particles.append(Particula(self.pos.x+random.randint(-10,10), self.pos.y+random.randint(-10,10), cor, -1, 3, 15))
                self.timer_ataque -= 1
                if self.timer_ataque <= 0:
                    self.estado = "ATIRANDO"
                    self.timer_ataque = 30
            elif self.estado == "ATIRANDO":
                # Pequeno recuo ao atirar
                if self.inimigo_ref:
                    self.vel += (self.pos - self.inimigo_ref.pos).normalize() * 0.5
                self.timer_ataque -= 1
                if self.timer_ataque <= 0: self.estado = "MOVENDO"

        elif tipo_atk == "GUIADO": # Ex: Shadow Ball
            if random.randint(0, 180) == 0:
                grupo_projeteis.add(Projetil(self.pos.x, self.pos.y, self, "Shadow Ball", self.inimigo_ref))

        elif tipo_atk == "AREA": # Ex: Earthquake
            if random.randint(0, 250) == 0:
                self.estado = "ATIVO_AREA"
                self.timer_ataque = 40
                self.vel *= 0.2
                # Aplica dano se estiver no raio
                if self.inimigo_ref and self.pos.distance_to(self.inimigo_ref.pos) < 230:
                    self.inimigo_ref.vida -= self.info["dano"]
                    # Empurrão forte
                    push = (self.inimigo_ref.pos - self.pos).normalize() * 25
                    self.inimigo_ref.vel += push

        elif tipo_atk == "RASTRO": # Ex: Flame Wheel
            if random.randint(0, 10) == 0:
                grupo_projeteis.add(Projetil(self.pos.x, self.pos.y, self, "Fogo"))
            if self.vel.length() < 6: self.vel *= 1.05 # Corre mais rápido

        elif tipo_atk == "TIRO_RAPIDO": # Ex: Water Shuriken
            if self.estado == "MOVENDO":
                if random.randint(0, 100) == 0:
                    self.estado = "DISPARANDO"
                    self.timer_ataque = 3 # Número de disparos
                    self.intervalo_tiro = 0
            elif self.estado == "DISPARANDO":
                self.intervalo_tiro -= 1
                if self.intervalo_tiro <= 0:
                    if self.inimigo_ref:
                        dir_tiro = (self.inimigo_ref.pos - self.pos).normalize()
                        # Adiciona imprecisão aleatória no tiro
                        dir_tiro = dir_tiro.rotate(random.uniform(-10, 10))
                        grupo_projeteis.add(Projetil(self.pos.x, self.pos.y, self, "Shuriken", direcao=dir_tiro))
                    self.timer_ataque -= 1
                    self.intervalo_tiro = 8 # Delay entre tiros
                    if self.timer_ataque <= 0:
                        self.estado = "MOVENDO"

        elif tipo_atk == "ESCUDO": # Ex: Iron Defense
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

        # --- FÍSICA DE MOVIMENTO ---
        self.pos += self.vel
        
        # --- COLISÃO COM PAREDES (Com Rebote) ---
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
            # Adiciona caos: velocidade muda levemente ao bater
            self.vel *= random.uniform(0.9, 1.2)
            # Clamp (Limita a velocidade mínima e máxima)
            v_len = self.vel.length()
            if v_len < 2: self.vel.scale_to_length(2)
            if v_len > 12: self.vel.scale_to_length(12)

        # Rotação Visual (Gira conforme velocidade)
        rot_speed = 5 + (self.vel.length())
        self.angulo += (rot_speed * 0.5)
        self.image = pygame.transform.rotate(self.image_original, self.angulo)
        self.rect = self.image.get_rect(center=self.pos)

    def draw_special(self, surface):
        # Desenha efeitos que não são objetos físicos (Laser, Escudo, Onda)
        tipo = self.info["tipo"]
        
        if (tipo == "LASER" or tipo == "DRENO") and self.estado == "ATIRANDO":
            if self.inimigo_ref:
                cor_raio = self.info["cor"]
                start = self.pos
                end = self.inimigo_ref.pos
                largura = random.randint(8, 15)
                pygame.draw.line(surface, cor_raio, start, end, largura)
                pygame.draw.line(surface, BRANCO, start, end, 4)
                # Aplica dano direto (Hitscan)
                dano = self.info["dano"]
                self.inimigo_ref.vida -= dano
                if tipo == "DRENO":
                    self.vida = min(self.vida_max, self.vida + dano)
                    
        elif tipo == "AREA" and self.estado == "ATIVO_AREA":
            raio = (40 - self.timer_ataque) * 6
            pygame.draw.circle(surface, self.info["cor"], (int(self.pos.x), int(self.pos.y)), int(raio), 4)
            self.timer_ataque -= 1
            if self.timer_ataque <= 0: self.estado = "MOVENDO"
            
        elif tipo == "ESCUDO" and self.defendendo:
            pygame.draw.circle(surface, self.info["cor"], (int(self.pos.x), int(self.pos.y)), 50, 3)
            pygame.draw.circle(surface, (255,255,255, 100), (int(self.pos.x), int(self.pos.y)), 45, 1)

# =============================================================================
# --- INTERFACE DO MENU (Mouse) ---
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
        txt_desc = font_peq.render(self.info["desc"], True, BRANCO if not self.hover else PRETO)
        tela.blit(txt_nome, (self.rect.x + 10, self.rect.y + 10))
        tela.blit(txt_desc, (self.rect.x + 10, self.rect.y + 40))

    def check_hover(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)

    def check_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

def tela_menu_mouse(tela):
    # Gera botões dinamicamente baseado na lista de ataques
    botoes = []
    cols = 2
    largura_btn = 350
    altura_btn = 70
    espaco_x = 20
    espaco_y = 20
    start_x = (LARGURA_TELA - (cols * largura_btn + (cols-1)*espaco_x)) // 2
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

        tela.blit(txt, (LARGURA_TELA//2 - txt.get_width()//2, 50))
        
        for btn in botoes:
            btn.check_hover(mouse_pos)
            btn.draw(tela)
            
        # Indicadores visuais de seleção
        if p1_choice is not None:
            btn = botoes[p1_choice]
            pygame.draw.circle(tela, VERMELHO, (btn.rect.right - 20, btn.rect.centery), 10)
        if p2_choice is not None:
            btn = botoes[p2_choice]
            pygame.draw.circle(tela, AZUL, (btn.rect.right - 45, btn.rect.centery), 10)

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None, None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, btn in enumerate(botoes):
                        if btn.check_click(mouse_pos):
                            if p1_choice is None: p1_choice = i
                            elif p2_choice is None:
                                p2_choice = i
                                rodando = False # Sai do loop
    return p1_choice, p2_choice

# =============================================================================
# --- FUNÇÃO PRINCIPAL DE BATALHA ---
# =============================================================================
def rodar_batalha(tela, id1, id2):
    info1 = ATAQUES_INFO[id1]
    info2 = ATAQUES_INFO[id2]
    
    # Aqui define-se as imagens. Se existirem na pasta assets/, elas serão usadas.
    poke1 = Pokemon("P1", 200, 300, info1["cor"], id1, "assets/pokemon1.png")
    poke2 = Pokemon("P2", 600, 300, info2["cor"], id2, "assets/pokemon2.png")
    poke1.inimigo_ref = poke2
    poke2.inimigo_ref = poke1
    
    grupo_pokes = pygame.sprite.Group(poke1, poke2)
    grupo_projeteis = pygame.sprite.Group()
    particles = []
    
    clock = pygame.time.Clock()
    hitstop_timer = 0 # Controla o "congelamento" de impacto
    vencedor = None
    tempo_vitoria = 0

    while True:
        clock.tick(FPS)
        agora = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "SAIR"

        # Tela de Vitória
        if vencedor:
            tela.fill(COR_FUNDO)
            txt_win = pygame.font.Font(None, 80).render(f"{vencedor} VENCEU!", True, BRANCO)
            tela.blit(txt_win, (LARGURA_TELA//2 - txt_win.get_width()//2, ALTURA_TELA//2 - 50))
            segundos = 10 - ((agora - tempo_vitoria) // 1000)
            txt_time = pygame.font.Font(None, 40).render(f"Menu em {segundos}...", True, CINZA)
            tela.blit(txt_time, (LARGURA_TELA//2 - txt_time.get_width()//2, ALTURA_TELA//2 + 50))
            pygame.display.flip()
            if agora - tempo_vitoria > 10000: return "MENU"
            continue

        # Lógica de Hitstop (Se timer > 0, o jogo pausa lógica e só desenha)
        if hitstop_timer > 0:
            hitstop_timer -= 1
        else:
            grupo_pokes.update(grupo_projeteis, particles)
            grupo_projeteis.update(particles)
            for p in particles[:]:
                p.update()
                if p.vida <= 0: particles.remove(p)

            # --- COLISÃO FÍSICA ENTRE POKÉMONS ---
            if pygame.sprite.collide_rect(poke1, poke2):
                # Troca momento linear (Física de Bilhar)
                poke1.vel, poke2.vel = poke2.vel, poke1.vel
                # Separação para evitar "grude"
                dx, dy = poke1.pos.x - poke2.pos.x, poke1.pos.y - poke2.pos.y
                dist = math.hypot(dx, dy) or 1
                poke1.pos += (dx/dist)*8, (dy/dist)*8 
                
                dano_p1 = 0 
                dano_p2 = 0
                
                # Verifica ataques de carga (Thunder Punch)
                if poke1.info["tipo"] == "CARGA_FISICA" and poke1.soco_carregado:
                    dano_p1 = poke1.info["dano"]
                    poke2.timer_paralisia = 120
                    poke1.soco_carregado = False
                    poke1.estado = "MOVENDO"
                    hitstop_timer = 20
                    # Counter do Escudo
                    if poke2.defendendo:
                        dano_p1 = 0
                        poke1.vel *= -2

                if poke2.info["tipo"] == "CARGA_FISICA" and poke2.soco_carregado:
                    dano_p2 = poke2.info["dano"]
                    poke1.timer_paralisia = 120
                    poke2.soco_carregado = False
                    poke2.estado = "MOVENDO"
                    hitstop_timer = 20
                    if poke1.defendendo:
                        dano_p2 = 0
                        poke2.vel *= -2

                poke1.vida -= dano_p2
                poke2.vida -= dano_p1
                
                # Gera partículas de impacto
                if dano_p1 > 0 or dano_p2 > 0:
                    for _ in range(15):
                        particles.append(Particula(poke1.pos.x, poke1.pos.y, BRANCO, 4, 5, 20))

            # --- COLISÃO DE PROJÉTEIS ---
            for p in grupo_pokes:
                hits = pygame.sprite.spritecollide(p, grupo_projeteis, False)
                for tiro in hits:
                    if tiro.dono != p and not tiro.morrendo:
                        # Verifica imunidade (ex: Fogo contínuo)
                        tipo_dano = tiro.tipo
                        if p.timers_imunidade.get(tipo_dano, 0) > 0:
                            continue 

                        dano = tiro.info["dano"]
                        # Reflete se estiver defendendo
                        if p.defendendo:
                            dano = 0
                            tiro.vel *= -1 
                            tiro.dono = p 
                            continue 
                        
                        p.vida -= dano
                        hitstop_timer = tiro.info["hitstop"]
                        
                        if tipo_dano == "Fogo":
                            p.timers_imunidade["Fogo"] = 30 # I-Frames para fogo
                            hitstop_timer = 2
                        
                        for _ in range(10):
                            particles.append(Particula(p.pos.x, p.pos.y, tiro.info["cor"], 3, 5, 20))
                        
                        tiro.iniciar_morte()

            if poke1.vida <= 0: 
                vencedor = "JOGADOR 2"
                tempo_vitoria = agora
            elif poke2.vida <= 0: 
                vencedor = "JOGADOR 1"
                tempo_vitoria = agora

        # --- DESENHO DA TELA ---
        tela.fill(COR_FUNDO)
        pygame.draw.rect(tela, COR_ARENA_BORDA, ARENA_RECT, 4)
        
        poke1.draw_special(tela)
        poke2.draw_special(tela)
        
        # Desenha camada de chão (Fogo)
        for proj in grupo_projeteis:
            if proj.tipo == "Fogo": tela.blit(proj.image, proj.rect)
        
        grupo_pokes.draw(tela)
        
        # Desenha projéteis aéreos
        for proj in grupo_projeteis:
            if proj.tipo != "Fogo": tela.blit(proj.image, proj.rect)
            
        for part in particles: part.draw(tela)
        
        # Interface (Barras de Vida e Nomes)
        def draw_bar(x, y, p):
            ratio = max(0, p.vida / p.vida_max)
            # Fundo da barra
            pygame.draw.rect(tela, (50,50,50), (x, y, 200, 25))
            # Vida (Verde ou Vermelha)
            pygame.draw.rect(tela, (0, 255, 0) if ratio > 0.3 else (255, 0, 0), (x, y, 200*ratio, 25))
            # Borda
            pygame.draw.rect(tela, BRANCO, (x, y, 200, 25), 2)
            
            status = ""
            if p.timer_paralisia > 0: status += " [LENTO]"
            if p.defendendo: status += " [ESCUDO]"
            
            font_nome = pygame.font.Font(None, 28)
            font_atk = pygame.font.Font(None, 22)
            
            # Nome em cima
            tela.blit(font_nome.render(f"{p.nome}{status}", True, BRANCO), (x, y-25))
            # Ataque embaixo
            tela.blit(font_atk.render(f"Ataque: {p.info['nome']}", True, CINZA_CLARO), (x, y+30))
        
        draw_bar(50, 50, poke1)
        draw_bar(LARGURA_TELA-250, 50, poke2)
        pygame.display.flip()

def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption(NOME_JANELA)
    while True:
        escolhas = tela_menu_mouse(tela)
        if escolhas[0] is None: break
        id1, id2 = escolhas
        res = rodar_batalha(tela, id1, id2)
        if res == "SAIR": break
    pygame.quit()

if __name__ == "__main__":
    main()
