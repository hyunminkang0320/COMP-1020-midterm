import pygame
import sys
import math

# Initialize
pygame.init()

# Screen settings
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tutorial to Stage 1")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Font
font = pygame.font.SysFont(None, 48)

# Clock
clock = pygame.time.Clock()

# ===== Stage 1 (질병 지옥) 함수 =====
def stage1():
    player = pygame.Rect(100, 500, 50, 50)
    player_speed = 5

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            player.x -= player_speed
        if keys[pygame.K_d]:
            player.x += player_speed
        if keys[pygame.K_w]:
            player.y -= player_speed
        if keys[pygame.K_s]:
            player.y += player_speed

        screen.fill((100, 100, 255))
        pygame.draw.rect(screen, (0, 0, 0), player)
        render_text = font.render("Stage 1: Disease Hell", True, WHITE)
        screen.blit(render_text, (SCREEN_WIDTH // 2 - render_text.get_width() // 2, 50))
        pygame.display.flip()

# ===== 튜토리얼 스테이지 함수 =====
def tutorial_stage():
    player = pygame.Rect(100, 500, 50, 50)
    player_speed = 5
    player_health = 5

    # Hook & Grapple Settings (SANABI-style)
    hook_pos = None
    hook_dir = None
    hook_flying = False
    grappling = False
    grapple_point = pygame.Vector2()
    pull_to_grapple = False
    MAX_GRAPPLE_DISTANCE = 1000
    HOOK_SHOOT_SPEED = 25
    GRAPPLE_PULL_SPEED = 15

    # Toxic puddle
    toxic_puddle = pygame.Rect(300, 550, 200, 30)

    # Enemy
    enemy = pygame.Rect(500, 500, 50, 50)
    enemy_alive = True
    enemy_speed_x = 2
    enemy_speed_y = 2

    # Door
    door = pygame.Rect(800, 500, 50, 100)

    # Damage cooldown
    damage_cooldown = 0

    # Tutorial Texts
    tutorial_texts = [
        (0, "Use WASD to move."),
        (200, "Left-click to shoot your chain."),
        (400, "Press SPACE to pull yourself."),
        (600, "Avoid the toxic puddle!"),
        (700, "Beware of the enemy!"),
    ]

    running = True
    while running:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        mouse_vec = pygame.Vector2(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Hook shoot
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                hook_pos = pygame.Vector2(player.center)
                hook_dir = (mouse_vec - hook_pos).normalize()
                hook_flying = True
                grappling = False
                pull_to_grapple = False

            # Cancel grapple
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                hook_flying = False
                grappling = False
                pull_to_grapple = False

        keys = pygame.key.get_pressed()

        if not pull_to_grapple:
            if keys[pygame.K_a]:
                player.x -= player_speed
            if keys[pygame.K_d]:
                player.x += player_speed
            if keys[pygame.K_w]:
                player.y -= player_speed
            if keys[pygame.K_s]:
                player.y += player_speed

        # Start pulling
        if keys[pygame.K_SPACE] and grappling:
            pull_to_grapple = True

        # Hook flying
        if hook_flying and hook_pos:
            hook_pos += hook_dir * HOOK_SHOOT_SPEED

            # If it goes too far
            if (hook_pos - pygame.Vector2(player.center)).length() > MAX_GRAPPLE_DISTANCE:
                hook_flying = False

            # If it reaches mouse position
            if (hook_pos - mouse_vec).length() < 10:
                grappling = True
                grapple_point = hook_pos.copy()
                hook_flying = False

        # Pulling
        if grappling and pull_to_grapple:
            direction = grapple_point - pygame.Vector2(player.center)
            if direction.length() > 5:
                direction = direction.normalize() * GRAPPLE_PULL_SPEED
                player.x += int(direction.x)
                player.y += int(direction.y)
            else:
                pull_to_grapple = False

        # Toxic puddle
        if player.colliderect(toxic_puddle):
            toxic_color = (150, 0, 0)
            player_health -= 0.02
        else:
            toxic_color = GREEN

        # Enemy collision
        if player.colliderect(enemy) and enemy_alive:
            if damage_cooldown == 0:
                player_health -= 1
                damage_cooldown = 60

        if damage_cooldown > 0:
            damage_cooldown -= 1

        if player_health <= 0:
            print("You Died!")
            pygame.quit()
            sys.exit()

        # Enemy movement
        if enemy_alive:
            enemy.x += enemy_speed_x
            enemy.y += enemy_speed_y
            if enemy.left <= 0 or enemy.right >= SCREEN_WIDTH:
                enemy_speed_x = -enemy_speed_x
            if enemy.top <= 0 or enemy.bottom >= SCREEN_HEIGHT:
                enemy_speed_y = -enemy_speed_y

        # ======================== Drawing ========================
        screen.fill(WHITE)

        # Toxic puddle
        pygame.draw.rect(screen, toxic_color, toxic_puddle)

        # Enemy
        if enemy_alive:
            pygame.draw.rect(screen, RED, enemy)

        # Door
        pygame.draw.rect(screen, (0, 0, 255), door)

        # Player
        pygame.draw.rect(screen, (0, 0, 0), player)

        # Grapple visuals
        if grappling:
            pygame.draw.line(screen, RED, player.center, grapple_point, 2)
            pygame.draw.circle(screen, RED, (int(grapple_point.x), int(grapple_point.y)), 5)
        elif hook_flying and hook_pos:
            pygame.draw.line(screen, YELLOW, player.center, hook_pos, 2)
            pygame.draw.circle(screen, YELLOW, (int(hook_pos.x), int(hook_pos.y)), 4)

        # Door message
        if player.colliderect(door):
            door_text = font.render("Press ENTER to enter Stage 1", True, BLACK)
            screen.blit(door_text, (SCREEN_WIDTH // 2 - door_text.get_width() // 2, 100))
            if keys[pygame.K_RETURN]:
                running = False
                stage1()

        # Tutorial text
        if not player.colliderect(door):
            for x_pos, text in tutorial_texts:
                if x_pos <= player.x < x_pos + 300:
                    render_text = font.render(text, True, BLACK)
                    screen.blit(render_text, (SCREEN_WIDTH // 2 - render_text.get_width() // 2, 50))
                    break

        # Health
        hearts = int(player_health)
        heart_text = font.render("❤️" * hearts, True, RED)
        screen.blit(heart_text, (20, 20))

        pygame.display.flip()

# ===== 프로그램 시작 =====
tutorial_stage()
