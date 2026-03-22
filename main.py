import pygame
import math
import os

# --- 1. ИНИЦИАЛИЗАЦИЯ ---
pygame.init()
info = pygame.display.Info()
W, H = info.current_w, info.current_h
screen = pygame.display.set_mode((W, H))

# ЦВЕТА
GOLD, WHITE, RED, GREEN, CYAN = (255, 215, 0), (255, 255, 255), (255, 50, 50), (0, 255, 120), (0, 255, 255)
GREY, CONCRETE = (130, 130, 140), (60, 60, 75)

# СЛОЖНОСТЬ (БОТ ТЕПЕРЬ СЛАБЕЕ НА МИНИМУМЕ)
DIFFICULTIES = {
    "СЛАБАК":  {"speed": 0.04, "color": GREEN},
    "НОРМ":    {"speed": 0.12, "color": CYAN},
    "СЛОЖНЫЙ": {"speed": 0.35, "color": GOLD},
    "ЖЕСТЬ":   {"speed": 0.65, "color": RED}
}

# МАГАЗИН (ЦЕНЫ ВЕРНУЛИСЬ)
SKINS_DATA = {
    "Стандарт": {"color": CYAN, "price": 0},
    "Огонь":    {"color": (255, 60, 0), "price": 5000},
    "КОРОЛЬ":   {"color": GOLD, "price": 15000}
}

fonts = {
    "btn": pygame.font.Font(None, 60),
    "ui": pygame.font.Font(None, 40),
    "count": pygame.font.Font(None, 400),
    "score": pygame.font.Font(None, 150),
    "fps": pygame.font.Font(None, 35)
}

# --- 2. ДАННЫЕ (ЗАГРУЗКА/СОХРАНЕНИЕ) ---
def save_data():
    try:
        with open("save.dat", "w") as f:
            f.write(f"{air_coins}|{mmr}|{int(show_fps)}|{current_skin}")
    except: pass

def load_data():
    if os.path.exists("save.dat"):
        try:
            with open("save.dat", "r") as f:
                d = f.read().split("|")
                return int(d[0]), int(d[1]), bool(int(d[2])), d[3]
        except: pass
    return 1000, 1000, True, "Стандарт"

air_coins, mmr, show_fps, current_skin = load_data()

# --- 3. ПАРАМЕТРЫ ОБЪЕКТОВ ---
MENU, DIFF_SEL, GAME, END, SHOP, PAUSE, REPLAY = 0, 1, 2, 3, 4, 5, 6
state = MENU
current_diff = "НОРМ"
score = [0, 0]
countdown = 0
replay_frames = []
replay_idx = 0

WALL_T = 45 # Мощный бетон
G_W = int(W * 0.48) 
P_R, B_R = int(W * 0.09), int(W * 0.05)
ball_pos, ball_vel = [W/2, H/2], [0, 0]
p1, p2 = [W/2, 180], [W/2, H - 180]

# ФИЗИКА (УСКОРЕНИЕ ВНЕДРЕНО)
START_SPEED = 1500
MAX_SPEED = 3800 
curr_speed = START_SPEED

# --- 4. ФУНКЦИИ ИНТЕРФЕЙСА ---
def draw_btn(text, y, color, m_pos, w=550, h=95):
    rect = pygame.Rect(W//2 - w//2, y, w, h)
    hover = rect.collidepoint(m_pos)
    pygame.draw.rect(screen, (25, 25, 45), rect, border_radius=20)
    pygame.draw.rect(screen, color if hover else (80, 80, 100), rect, 4, border_radius=20)
    txt = fonts["btn"].render(text, True, WHITE)
    screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
    return rect

def start_round():
    global countdown, ball_pos, ball_vel, curr_speed, replay_frames
    ball_pos = [W/2, H/2]; ball_vel = [0, 0]; curr_speed = START_SPEED; countdown = 3
    replay_frames = []

# --- 5. ЦИКЛ ---
clock = pygame.time.Clock()
running = True
last_tick = pygame.time.get_ticks()

while running:
    dt = min(clock.tick() / 1000.0, 0.03) 
    m_pos = pygame.mouse.get_pos()
    screen.fill((10, 5, 20))

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == MENU:
                if b_play.collidepoint(m_pos): state = DIFF_SEL
                if b_shop.collidepoint(m_pos): state = SHOP
            elif state == DIFF_SEL:
                y_d = 200
                for d in DIFFICULTIES:
                    if pygame.Rect(W//2-275, y_d, 550, 95).collidepoint(m_pos):
                        current_diff = d; score=[0,0]; state=GAME; start_round()
                    y_d += 115
                if b_back_d.collidepoint(m_pos): state = MENU
            elif state == SHOP:
                y_s = 200
                for name, info_s in SKINS_DATA.items():
                    if pygame.Rect(W//2-275, y_s, 550, 95).collidepoint(m_pos):
                        if air_coins >= info_s["price"]: current_skin = name; save_data()
                    y_s += 115
                if b_back_s.collidepoint(m_pos): state = MENU
            elif state == GAME:
                if b_pause_zone.collidepoint(m_pos): state = PAUSE
            elif state == PAUSE:
                if b_resume.collidepoint(m_pos): state = GAME
                if b_restart.collidepoint(m_pos): start_round(); state = GAME
                if b_exit.collidepoint(m_pos): state = MENU
            elif state == END:
                if b_retry.collidepoint(m_pos): score=[0,0]; state=GAME; start_round()
                if b_replay_btn.collidepoint(m_pos): state=REPLAY; replay_idx=0
                if b_menu_end.collidepoint(m_pos): state=MENU

    # --- ЛОГИКА И ОТРИСОВКА ---
    if state == MENU:
        screen.blit(fonts["ui"].render(f"AC: {air_coins}  MMR: {mmr}", 1, GOLD), (30, H-60))
        b_play = draw_btn("ИГРАТЬ", H//2 - 120, GREEN, m_pos)
        b_shop = draw_btn("МАГАЗИН", H//2 + 20, GOLD, m_pos)

    elif state == DIFF_SEL:
        b_back_d = draw_btn("НАЗАД", 50, RED, m_pos, w=220)
        y_v = 200
        for name in DIFFICULTIES:
            draw_btn(name, y_v, DIFFICULTIES[name]["color"], m_pos); y_v += 115

    elif state == SHOP:
        screen.blit(fonts["ui"].render(f"БАЛАНС: {air_coins} AC", 1, GOLD), (W//2-130, 140))
        b_back_s = draw_btn("НАЗАД", 50, RED, m_pos, w=220)
        y_s = 200
        for name, info_s in SKINS_DATA.items():
            btn_txt = f"{name} ({info_s['price']})" if current_skin != name else f"{name} [ВЫБРАНО]"
            btn_col = GREEN if current_skin == name else (GOLD if air_coins >= info_s["price"] else RED)
            draw_btn(btn_txt, y_s, btn_col, m_pos); y_s += 115

    elif state in [GAME, PAUSE, REPLAY]:
        # Поле (БЕТОН)
        pygame.draw.rect(screen, CONCRETE, (0,0,W,H), WALL_T)
        gx = W//2 - G_W//2
        pygame.draw.rect(screen, WHITE, (gx, 0, G_W, WALL_T))
        pygame.draw.rect(screen, WHITE, (gx, H-WALL_T, G_W, WALL_T))
        
        # Счет
        stxt = fonts["score"].render(f"{score[0]} : {score[1]}", 1, (50, 50, 70))
        screen.blit(stxt, (W//2 - stxt.get_width()//2, H//2 - 75))

        # Кнопка ПАУЗЫ (ВНЕДРЕНА)
        b_pause_zone = pygame.Rect(W-120, 25, 95, 95)
        if state == GAME:
            pygame.draw.rect(screen, (50, 50, 80), b_pause_zone, border_radius=15)
            for i in range(3): pygame.draw.line(screen, WHITE, (W-100, 45+i*22), (W-45, 45+i*22), 10)

        if state == GAME:
            if countdown <= 0:
                replay_frames.append((list(ball_pos), list(p1), list(p2)))
                if ball_vel == [0, 0]: ball_vel = [800, 1600]
                ball_pos[0]+=ball_vel[0]*dt; ball_pos[1]+=ball_vel[1]*dt
                
                # Коллизии стен
                if ball_pos[0] < B_R+WALL_T or ball_pos[0] > W-B_R-WALL_T:
                    ball_vel[0]*=-1; ball_pos[0] = max(B_R+WALL_T+2, min(W-B_R-WALL_T-2, ball_pos[0]))

                # СТОЛКНОВЕНИЕ С УСКОРЕНИЕМ 1.25
                for p in [p1, p2]:
                    if math.hypot(ball_pos[0]-p[0], ball_pos[1]-p[1]) < B_R+P_R:
                        ang = math.atan2(ball_pos[1]-p[1], ball_pos[0]-p[0])
                        curr_speed = min(curr_speed * 1.25, MAX_SPEED)
                        ball_vel = [math.cos(ang)*curr_speed, math.sin(ang)*curr_speed]
                        ball_pos[0] = p[0] + (B_R+P_R+3)*math.cos(ang)
                        ball_pos[1] = p[1] + (B_R+P_R+3)*math.sin(ang)

                p1[0] += (ball_pos[0] - p1[0]) * DIFFICULTIES[current_diff]["speed"]
                p2[0], p2[1] = m_pos[0], max(H//2+P_R, min(H-P_R-WALL_T, m_pos[1]))
                
                if ball_pos[1] < WALL_T or ball_pos[1] > H-WALL_T:
                    if gx < ball_pos[0] < gx + G_W:
                        if ball_pos[1] < WALL_T: score[1]+=1; air_coins+=100
                        else: score[0]+=1
                        if score[0]>=10 or score[1]>=10:
                            mmr = max(0, mmr + (25 if score[1]>=10 else -20)); save_data(); state = END
                        else: start_round()
                    else: ball_vel[1] *= -1

        elif state == REPLAY:
            if replay_idx < len(replay_frames):
                ball_pos, p1, p2 = replay_frames[replay_idx]; replay_idx += 1
            else: state = END

        # Отрисовка ЗАКРАШЕННЫХ объектов
        pygame.draw.circle(screen, RED, (int(p1[0]), int(p1[1])), P_R)
        pygame.draw.circle(screen, WHITE, (int(p1[0]), int(p1[1])), P_R, 5) # Контур
        pygame.draw.circle(screen, SKINS_DATA[current_skin]["color"], (int(p2[0]), int(p2[1])), P_R)
        pygame.draw.circle(screen, WHITE, (int(p2[0]), int(p2[1])), P_R, 5) # Контур
        pygame.draw.circle(screen, GREY, (int(ball_pos[0]), int(ball_pos[1])), B_R)
        pygame.draw.circle(screen, WHITE, (int(ball_pos[0]), int(ball_pos[1])), B_R, 3)

    if state == PAUSE:
        overlay = pygame.Surface((W, H), pygame.SRCALPHA); overlay.fill((0,0,0,180))
        screen.blit(overlay, (0,0))
        b_resume = draw_btn("ПРОДОЛЖИТЬ", H//2 - 160, GREEN, m_pos)
        b_restart = draw_btn("РЕСТАРТ РАУНДА", H//2 - 45, CYAN, m_pos)
        b_exit = draw_btn("В МЕНЮ", H//2 + 70, RED, m_pos)

    elif state == END:
        screen.blit(fonts["score"].render("ФИНАЛ", 1, WHITE), (W//2-180, H//6))
        b_retry = draw_btn("ЕЩЕ РАЗ", H//2 - 60, GREEN, m_pos)
        b_replay_btn = draw_btn("ПОВТОР ГОЛА", H//2 + 55, GOLD, m_pos)
        b_menu_end = draw_btn("В МЕНЮ", H//2 + 170, WHITE, m_pos)

    # --- САМЫЙ ВЕРХНИЙ СЛОЙ (ОТСЧЕТ И FPS) ---
    if state == GAME and countdown > 0:
        if pygame.time.get_ticks() - last_tick > 1000:
            countdown -= 1; last_tick = pygame.time.get_ticks()
        c_txt = fonts["count"].render(str(countdown), 1, WHITE)
        screen.blit(c_txt, (W//2 - c_txt.get_width()//2, H//2 - c_txt.get_height()//2))

    if show_fps:
        fps_text = fonts["fps"].render(f"FPS: {int(clock.get_fps())}", 1, GREEN)
        pygame.draw.rect(screen, (0,0,0), (10, 10, 140, 45), border_radius=10)
        screen.blit(fps_text, (25, 15))

    pygame.display.flip()
pygame.quit()
