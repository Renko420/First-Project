import pygame
import random
import math

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Dodge")
clock = pygame.time.Clock()
font_big = pygame.font.Font(None, 72)
font_med = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 32)

# ========== כוכבי רקע ==========
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.5, 2)] for _ in range(80)]

# ========== פונקציית ציור זוהר ==========
def draw_glow(surface, color, pos, radius):
    for i in range(radius, 0, -2):
        alpha = int(100 * (1 - i / radius))
        glow_surf = pygame.Surface((i*2, i*2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*color, alpha), (i, i), i)
        surface.blit(glow_surf, (pos[0] - i, pos[1] - i))

# ========== משתני משחק ==========
def reset_game():
    return {
        "player_x": WIDTH // 2,
        "player_y": HEIGHT - 80,
        "trail": [],
        "enemies": [],
        "particles": [],
        "score": 0,
        "spawn_timer": 0,
        "difficulty": 1.0,
        "game_over": False,
        "shake": 0,
    }

state = reset_game()
best_score = 0
PLAYER_SIZE = 20
PLAYER_SPEED = 7

running = True
while running:
    dt = clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and state["game_over"]:
                state = reset_game()
    
    if not state["game_over"]:
        # ========== תנועת שחקן ==========
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            state["player_x"] -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            state["player_x"] += PLAYER_SPEED
        state["player_x"] = max(PLAYER_SIZE, min(WIDTH - PLAYER_SIZE, state["player_x"]))
        
        # ========== זנב שחקן ==========
        state["trail"].append((state["player_x"], state["player_y"]))
        if len(state["trail"]) > 15:
            state["trail"].pop(0)
        
        # ========== יצירת אויבים ==========
        state["spawn_timer"] += 1
        if state["spawn_timer"] > max(15, 45 - state["difficulty"] * 3):
            state["spawn_timer"] = 0
            state["enemies"].append({
                "x": random.randint(20, WIDTH - 20),
                "y": -20,
                "speed": random.uniform(3, 5) * state["difficulty"],
                "size": random.randint(15, 30),
                "color": random.choice([(255, 80, 80), (255, 150, 50), (255, 80, 200)])
            })
        
        # ========== תנועת אויבים ==========
        for enemy in state["enemies"][:]:
            enemy["y"] += enemy["speed"]
            if enemy["y"] > HEIGHT + 50:
                state["enemies"].remove(enemy)
                state["score"] += 10
            
            # התנגשות
            dx = enemy["x"] - state["player_x"]
            dy = enemy["y"] - state["player_y"]
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < PLAYER_SIZE + enemy["size"] / 2:
                state["game_over"] = True
                state["shake"] = 20
                # פיצוץ חלקיקים
                for _ in range(40):
                    angle = random.uniform(0, math.pi * 2)
                    speed = random.uniform(2, 8)
                    state["particles"].append({
                        "x": state["player_x"],
                        "y": state["player_y"],
                        "vx": math.cos(angle) * speed,
                        "vy": math.sin(angle) * speed,
                        "life": 60,
                        "color": (100, 255, 255)
                    })
                if state["score"] > best_score:
                    best_score = state["score"]
        
        # ========== קושי עולה עם הזמן ==========
        state["difficulty"] += 0.001
        state["score"] += 0.1
    
    # ========== עדכון חלקיקים ==========
    for p in state["particles"][:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vy"] += 0.2
        p["life"] -= 1
        if p["life"] <= 0:
            state["particles"].remove(p)
    
    # ========== עדכון כוכבי רקע ==========
    for star in stars:
        star[1] += star[2]
        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, WIDTH)
    
    # ========== ציור ==========
    shake_x = random.randint(-state["shake"], state["shake"]) if state["shake"] > 0 else 0
    shake_y = random.randint(-state["shake"], state["shake"]) if state["shake"] > 0 else 0
    if state["shake"] > 0:
        state["shake"] -= 1
    
    # רקע דינמי
    bg_hue = int(20 + state["difficulty"] * 5) % 60
    screen.fill((5, 5, 15 + bg_hue))
    
    # כוכבים
    for star in stars:
        brightness = int(100 + star[2] * 70)
        pygame.draw.circle(screen, (brightness, brightness, brightness), 
                         (int(star[0]) + shake_x, int(star[1]) + shake_y), int(star[2]))
    
    # זנב שחקן
    for i, pos in enumerate(state["trail"]):
        alpha = i / len(state["trail"])
        size = int(PLAYER_SIZE * alpha * 0.7)
        if size > 0:
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (100, 255, 255, int(alpha * 150)), (size, size), size)
            screen.blit(trail_surf, (pos[0] - size + shake_x, pos[1] - size + shake_y))
    
    # אויבים עם זוהר
    for enemy in state["enemies"]:
        draw_glow(screen, enemy["color"], 
                 (int(enemy["x"]) + shake_x, int(enemy["y"]) + shake_y), 
                 int(enemy["size"]))
        pygame.draw.circle(screen, enemy["color"], 
                         (int(enemy["x"]) + shake_x, int(enemy["y"]) + shake_y), 
                         int(enemy["size"] / 2))
        pygame.draw.circle(screen, (255, 255, 255), 
                         (int(enemy["x"]) + shake_x, int(enemy["y"]) + shake_y), 
                         int(enemy["size"] / 4))
    
    # שחקן עם זוהר
    if not state["game_over"]:
        draw_glow(screen, (100, 255, 255), 
                 (state["player_x"] + shake_x, state["player_y"] + shake_y), 
                 PLAYER_SIZE + 10)
        pygame.draw.circle(screen, (200, 255, 255), 
                         (state["player_x"] + shake_x, state["player_y"] + shake_y), 
                         PLAYER_SIZE)
        pygame.draw.circle(screen, (255, 255, 255), 
                         (state["player_x"] + shake_x, state["player_y"] + shake_y), 
                         PLAYER_SIZE - 5)
    
    # חלקיקים
    for p in state["particles"]:
        alpha = max(0, p["life"] / 60)
        size = int(4 * alpha) + 1
        pygame.draw.circle(screen, p["color"], 
                         (int(p["x"]) + shake_x, int(p["y"]) + shake_y), size)
    
    # ניקוד
    score_text = font_med.render(f"Score: {int(state['score'])}", True, (200, 255, 255))
    screen.blit(score_text, (20, 20))
    best_text = font_small.render(f"Best: {int(best_score)}", True, (150, 200, 200))
    screen.blit(best_text, (20, 70))
    
    # Game Over
    if state["game_over"]:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        go_text = font_big.render("GAME OVER", True, (255, 100, 100))
        screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 80))
        
        final_text = font_med.render(f"Score: {int(state['score'])}", True, (255, 255, 255))
        screen.blit(final_text, (WIDTH // 2 - final_text.get_width() // 2, HEIGHT // 2))
        
        restart_text = font_small.render("Press SPACE to restart", True, (200, 200, 200))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))
    
    pygame.display.flip()

pygame.quit()
