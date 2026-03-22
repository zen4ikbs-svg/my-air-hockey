import pygame
import math
import os
import random

# --- 1. ИНИЦИАЛИЗАЦИЯ ---
pygame.init()
info = pygame.display.Info()
W, H = info.current_w, info.current_h
screen = pygame.display.set_mode((W, H))

# ЦВЕТА
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (0, 255, 120)
CYAN = (0, 255, 255)
DARK_BG = (10, 12, 16)
WALL_COLOR = (30, 35, 45)

sparks = []
skin_effects = [] 

SKINS_DATA = {
    "Электро":  {"color": CYAN, "price": 0},
    "Огонь":    {"color": (255, 80, 0), "price": 5000},
    "КОРОЛЬ":   {"color": GOLD, "price": 15000}
}

fonts = {
    "btn": pygame.font.Font(None, 65),
    "ui": pygame.font.Font(None, 35),
    "stats": pygame.font.Font(None, 28), # Шрифт для верхней панели
    "count": pygame.font.Font(None, 350),
    "score": pygame.font.Font(None, 120)
}

# --- 2. ДАННЫЕ ---
def save_data():
    try:
        with open("save.dat", "w") as f:
            f.write(f"{air_coins}|{mmr}|0|{current_skin}")
    except: pass

def load_data():
    if os.path.exists("save.dat"):
        try:
            with open("save.dat", "r") as f:
                d = f.read().split("|")
                return int(d[0]), int(d[1]), d[3]
        except: pass
    return 2500, 1575, "Электро"

air_coins, mmr, current_skin = load_data()

# --- 3. НАСТРОЙКИ ОБЪЕКТОВ ---
MENU, GAME, END, SHOP, PAUSE = 0, 1, 2, 3, 4
state = MENU
score = [0, 0]
countdown = 0

WALL_T = 30 
G_W = int(W * 0.5) 
P_R, B_R = int(W * 0.1), int(W * 0.052)
ball_pos, ball_vel = [W/2, H/2], [0, 0]
p1, p2 = [W/2, 180], [W/2, H - 180]

START_SPEED = 1450
MAX_SPEED = 3300 
curr_speed = START_SPEED

# --- 4. ФУНКЦИИ ---
def create_hit_sparks(pos, color):
    for _ in range(12):
        sparks.append({
            "pos": list(pos),
            "vel": [random.uniform(-8, 8), random.uniform(-8, 8)],
            "life": 255,
            "color": color
        })

def generate_skin_particles(pos, skin):
    if skin == "Огонь":
        skin_effects.append({
            "pos": [pos[0] + random.uniform(-P_R//2, P_R//2), pos[1] + random.uniform(-P_R//2, P_R//2)],
            "vel": [random.uniform(-1, 1), random.uniform(-4, -1)],
            "rad": random.randint(5, 12),
            "color": random.choice([(255, 200, 0), (255, 100, 0), (255, 40, 0)]),
            "type": "fire"
        })
    elif skin == "Электро":
        if random.random() > 0.5:
            skin_effects.append({
                "pos": [pos[0] + random.uniform(-P_R, P_R), pos[1] + random.uniform(-P_R, P_R)],
                "life": random.randint(5, 15),
                "type": "electro"
            })

def draw_btn(text, y, color, m_pos, w=520):
    rect = pygame.Rect(W//2 - w//2, y, w, 90)
    hover = rect.collidepoint(m_pos)
    pygame.draw.rect(screen, (20, 22, 30), rect, border_radius=15)
    pygame.draw.rect(screen, color if hover else (70, 75, 90), rect, 4, border_radius=15)
    txt = fonts["btn"].render(text, True, WHITE)
    screen.blit(txt, (W//2 - txt.get_width()//2, y + 22))
    return rect

def start_round():
    global countdown, ball_pos, ball_vel, curr_speed
    ball_pos = [W/2, H/2]; ball_vel = [0, 0]; curr_speed = START_SPEED; countdown = 3
    sparks.clear(); skin_effects.clear()

# --- 5. ЦИКЛ ---
clock = pygame.time.Clock()
running = True
last_tick = pygame.time.get_ticks()

while running:
    dt = min(clock.tick() / 1000.0, 0.04) 
    m_pos = pygame.mouse.get_pos()
    screen.fill(DARK_BG)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == MENU:
                if b_play.collidepoint(m_pos): score=[0,0]; state=GAME; start_round()
                if b_shop.collidepoint(m_pos): state = SHOP
            elif state == SHOP:
                y_s = 220
                for name, info_s in SKINS_DATA.items():
                    if pygame.Rect(W//2-260, y_s, 520, 90).collidepoint(m_pos):
                        if air_coins >= info_s["price"]: current_skin = name; save_data()
                    y_s += 110
                if b_close_s.collidepoint(m_pos): state = MENU
            elif state == GAME:
                if pygame.Rect(W-80, 20, 65, 65).collidepoint(m_pos): state = PAUSE
            elif state == PAUSE:
                if b_res.collidepoint(m_pos): state = GAME
                if b_men.collidepoint(m_pos): state = MENU
            elif state == END:
                if b_retry.collidepoint(m_pos): score=[0,0]; state=GAME; start_round()
                if b_menu_e.collidepoint(m_pos): state=MENU

    if state == MENU:
        screen.blit(fonts["ui"].render(f"AC: {air_coins}  RANK: {mmr}", 1, GOLD), (W//2-140, H-60))
        b_play = draw_btn("В БОЙ", H//2 - 100, GREEN, m_pos)
        b_shop = draw_btn("МАГАЗИН", H//2 + 20, GOLD, m_pos)

    elif state == SHOP:
        # ДОБАВИЛ БАЛАНС В МАГАЗИН
        bal_txt = fonts["ui"].render(f"БАЛАНС: {air_coins} AC", 1, GOLD)
        screen.blit(bal_txt, (W//2 - bal_txt.get_width()//2, 140))
        b_close_s = draw_btn("НАЗАД", 30, RED, m_pos, w=180)
        y_s = 220
        for name, info_s in SKINS_DATA.items():
            color = GREEN if current_skin == name else GOLD
            draw_btn(f"{name} ({info_s['price']})", y_s, color, m_pos); y_s += 110

    elif state in [GAME, PAUSE, END]:
        pygame.draw.rect(screen, WALL_COLOR, (0,0,W,H), WALL_T)
        gx = W//2 - G_W//2
        pygame.draw.rect(screen, (20, 20, 25), (gx, 0, G_W, WALL_T))
        pygame.draw.rect(screen, RED, (gx, WALL_T-5, G_W, 5)) 
        pygame.draw.rect(screen, (20, 20, 25), (gx, H-WALL_T, G_W, WALL_T))
        pygame.draw.rect(screen, CYAN, (gx, H-WALL_T, G_W, 5)) 
        
        # СЧЕТ
        s_txt = fonts["score"].render(f"{score[0]} : {score[1]}", 1, (40, 45, 55))
        screen.blit(s_txt, (W//2 - s_txt.get_width()//2, H//2 - 60))

        # --- ВОЗВРАЩЕНИЕ ВЕРХНЕЙ ПАНЕЛИ СТАТИСТИКИ ---
        fps_val = int(clock.get_fps())
        top_stats = fonts["stats"].render(f"FPS: {fps_val}  MMR: {mmr}  AC: {air_coins}", 1, WHITE)
        screen.blit(top_stats, (15, 10))

        if state == GAME:
            if countdown <= 0:
                if ball_vel == [0, 0]: ball_vel = [900, 1800]
                ball_pos[0]+=ball_vel[0]*dt; ball_pos[1]+=ball_vel[1]*dt
                
                if ball_pos[0] < B_R + WALL_T or ball_pos[0] > W - B_R - WALL_T:
                    ball_vel[0] *= -1.06
                    ball_pos[0] = B_R + WALL_T + 1 if ball_pos[0] < W/2 else W - B_R - WALL_T - 1
                    create_hit_sparks(ball_pos, WHITE)

                for p in [p1, p2]:
                    if math.hypot(ball_pos[0]-p[0], ball_pos[1]-p[1]) < B_R+P_R:
                        ang = math.atan2(ball_pos[1]-p[1], ball_pos[0]-p[0])
                        curr_speed = min(curr_speed * 1.22, MAX_SPEED) 
                        ball_vel = [math.cos(ang)*curr_speed, math.sin(ang)*curr_speed]
                        ball_pos[0] = p[0] + (B_R+P_R+2)*math.cos(ang)
                        ball_pos[1] = p[1] + (B_R+P_R+2)*math.sin(ang)
                        create_hit_sparks(ball_pos, SKINS_DATA[current_skin]["color"] if p == p2 else RED)

            bot_speed = 0.06 + (mmr / 6000)
            p1[0] += (ball_pos[0] - p1[0]) * min(bot_speed, 0.8)
            p2[0], p2[1] = m_pos[0], max(H//2+P_R, min(H-P_R-WALL_T, m_pos[1]))

            generate_skin_particles(p2, current_skin)
            
            if ball_pos[1] < WALL_T or ball_pos[1] > H-WALL_T:
                if gx < ball_pos[0] < gx + G_W:
                    if ball_pos[1] < WALL_T: score[1]+=1; air_coins+=200
                    else: score[0]+=1
                    if score[0]>=10 or score[1]>=10:
                        win = score[1]>=10; mmr = max(0, mmr + (35 if win else -30)); save_data(); state = END
                    else: start_round()
                else: 
                    ball_vel[1] *= -1.06
                    ball_pos[1] = WALL_T + 2 if ball_pos[1] < WALL_T else H - WALL_T - 2

        for eff in skin_effects[:]:
            if eff["type"] == "fire":
                pygame.draw.circle(screen, eff["color"], (int(eff["pos"][0]), int(eff["pos"][1])), int(eff["rad"]))
                eff["pos"][0] += eff["vel"][0]; eff["pos"][1] += eff["vel"][1]
                eff["rad"] -= 0.5
                if eff["rad"] <= 0: skin_effects.remove(eff)
            elif eff["type"] == "electro":
                pygame.draw.rect(screen, CYAN, (eff["pos"][0], eff["pos"][1], random.randint(2,5), random.randint(2,5)))
                eff["life"] -= 1
                if eff["life"] <= 0: skin_effects.remove(eff)

        pygame.draw.circle(screen, RED, (int(p1[0]), int(p1[1])), P_R) 
        pygame.draw.circle(screen, SKINS_DATA[current_skin]["color"], (int(p2[0]), int(p2[1])), P_R) 
        
        if current_skin == "КОРОЛЬ":
            cx, cy = int(p2[0]), int(p2[1])
            crown_points = [(cx-35, cy-15), (cx-45, cy-55), (cx-15, cy-30), (cx, cy-65), (cx+15, cy-30), (cx+45, cy-55), (cx+35, cy-15)]
            pygame.draw.polygon(screen, GOLD, crown_points)
            pygame.draw.polygon(screen, WHITE, crown_points, 2) 

        pygame.draw.circle(screen, WHITE, (int(ball_pos[0]), int(ball_pos[1])), B_R) 

        for s in sparks[:]:
            s["pos"][0]+=s["vel"][0]; s["pos"][1]+=s["vel"][1]; s["life"]-=15
            if s["life"]<=0: sparks.remove(s)
            else: pygame.draw.circle(screen, s["color"], (int(s["pos"][0]), int(s["pos"][1])), 4)

        pygame.draw.rect(screen, (35, 40, 50), (W-75, 20, 60, 60), border_radius=12)
        for i in range(3): pygame.draw.line(screen, WHITE, (W-62, 32+i*12), (W-32, 32+i*12), 4)

    if state == PAUSE:
        b_res = draw_btn("ПРОДОЛЖИТЬ", H//2 - 60, GREEN, m_pos)
        b_men = draw_btn("В МЕНЮ", H//2 + 60, RED, m_pos)
    elif state == END:
        res_t = "ПОБЕДА!" if score[1]>=10 else "ПРОИГРЫШ!"
        txt = fonts["score"].render(res_t, 1, GREEN if "ПОБ" in res_t else RED)
        screen.blit(txt, (W//2 - txt.get_width()//2, H//4))
        b_retry = draw_btn("РЕВАНШ", H//2 + 80, GREEN, m_pos)
        b_menu_e = draw_btn("В МЕНЮ", H//2 + 190, WHITE, m_pos)

    if state == GAME and countdown > 0:
        if pygame.time.get_ticks() - last_tick > 1000:
            countdown -= 1; last_tick = pygame.time.get_ticks()
        c_txt = fonts["count"].render(str(countdown), 1, WHITE)
        screen.blit(c_txt, (W//2 - c_txt.get_width()//2, H//2 - c_txt.get_height()//2))

    pygame.display.flip()
pygame.quit()
