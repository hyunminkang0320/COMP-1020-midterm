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

# Font
font = pygame.font.SysFont(None, 48)

# Clock
clock = pygame.time.Clock()

# ===== 튜토리얼 스테이지 함수 =====
def tutorial_stage():
    # Player settings
    player = pygame.Rect(100, 500, 50, 50)
    player_speed = 5
    player_health = 5

    # Whip settings
    whip_active = False
    whip_start_pos = (0, 0)
    whip_end_pos = (0, 0)
    whip_timer = 0

    # Grapple settings
    grapple_active = False
    grapple_target = (0, 0)
    grapple_speed = 15

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
        (200, "Left-click to use your chain."),
        (400, "Press R to grapple."),
        (600, "Avoid the toxic puddle!"),
        (700, "Beware of the enemy!"),
    ]

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                whip_active = True
                whip_start_pos = (player.centerx, player.centery)
                whip_end_pos = pygame.mouse.get_pos()
                whip_timer = 10
                grapple_target = whip_end_pos

        keys = pygame.key.get_pressed()

        if not grapple_active:
            if keys[pygame.K_a]:
                player.x -= player_speed
            if keys[pygame.K_d]:
                player.x += player_speed
            if keys[pygame.K_w]:
                player.y -= player_speed
            if keys[pygame.K_s]:
                player.y += player_speed

        if keys[pygame.K_r]:
            grapple_active = True

        if grapple_active:
            dx = grapple_target[0] - player.centerx
            dy = grapple_target[1] - player.centery
            dist = math.hypot(dx, dy)
            if dist > 5:
                player.x += int(grapple_speed * dx / dist)
                player.y += int(grapple_speed * dy / dist)
            else:
                grapple_active = False

        # Toxic puddle 충돌
        if player.colliderect(toxic_puddle):
            toxic_color = (150, 0, 0)
            player_health -= 0.02
        else:
            toxic_color = GREEN

        # Enemy 충돌 + 쿨타임 적용
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

        # Enemy 움직이기 (대각선 이동)
        if enemy_alive:
            enemy.x += enemy_speed_x
            enemy.y += enemy_speed_y

            if enemy.left <= 0 or enemy.right >= SCREEN_WIDTH:
                enemy_speed_x = -enemy_speed_x
            if enemy.top <= 0 or enemy.bottom >= SCREEN_HEIGHT:
                enemy_speed_y = -enemy_speed_y

        # ======================== Drawing ========================
        screen.fill(WHITE)  # 배경을 전체 하얀색으로 채움

        # Toxic puddle
        pygame.draw.rect(screen, toxic_color, toxic_puddle)

        # Enemy
        if enemy_alive:
            pygame.draw.rect(screen, RED, enemy)

        # Door
        pygame.draw.rect(screen, (0, 0, 255), door)

        # Player
        pygame.draw.rect(screen, (0, 0, 0), player)

        # Whip
        if whip_active:
            pygame.draw.line(screen, (0, 0, 0), whip_start_pos, whip_end_pos, 5)
            whip_timer -= 1
            if whip_timer <= 0:
                whip_active = False

        # 문 안내 문구
        if player.colliderect(door):
            door_text = font.render("Press ENTER to enter Stage 1", True, BLACK)
            screen.blit(door_text, (SCREEN_WIDTH // 2 - door_text.get_width() // 2, 100))

            if keys[pygame.K_RETURN]:
                running = False
                stage1()

        # Tutorial text (문에 닿아있지 않을 때만)
        if not player.colliderect(door):
            for x_pos, text in tutorial_texts:
                if x_pos <= player.x < x_pos + 300:
                    render_text = font.render(text, True, BLACK)
                    screen.blit(render_text, (SCREEN_WIDTH // 2 - render_text.get_width() // 2, 50))
                    break

        # 체력 하트 표시
        hearts = int(player_health)
        heart_text = font.render("❤️" * hearts, True, RED)
        screen.blit(heart_text, (20, 20))

        pygame.display.flip()

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

# ===== 프로그램 시작 =====
tutorial_stage()
