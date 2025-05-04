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
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)

# Load images
bg_img = pygame.image.load("ghosty_background.png").convert()
player_img = pygame.image.load("player.png").convert_alpha()
enemy_img = pygame.image.load("enemy.png").convert_alpha()
door_img = pygame.image.load("door.png").convert_alpha()
heart_img = pygame.image.load("heart.png").convert_alpha()
puddle_img = pygame.image.load("toxic_puddle.png").convert_alpha()

# Scale images
bg_img = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
player_img = pygame.transform.scale(player_img, (50, 50))
enemy_img = pygame.transform.scale(enemy_img, (50, 50))
door_img = pygame.transform.scale(door_img, (50, 100))
heart_img = pygame.transform.scale(heart_img, (30, 30))
puddle_img = pygame.transform.scale(puddle_img, (200, 30))

def stage1():
    player = pygame.Rect(100, 500, 50, 50)
    player_speed = 5
    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: player.x -= player_speed
        if keys[pygame.K_d]: player.x += player_speed
        if keys[pygame.K_w]: player.y -= player_speed
        if keys[pygame.K_s]: player.y += player_speed

        screen.fill((100, 100, 255))
        screen.blit(player_img, player)
        render_text = font.render("Stage 1: Disease Hell", True, (255, 255, 255))
        screen.blit(render_text, (SCREEN_WIDTH // 2 - render_text.get_width() // 2, 50))
        pygame.display.flip()

def tutorial_stage():
    player = pygame.Rect(100, 500, 50, 50)
    player_speed = 5
    player_health = 5

    hook_pos = None
    hook_dir = None
    hook_flying = False
    grappling = False
    grapple_point = pygame.Vector2()
    pull_to_grapple = False
    MAX_GRAPPLE_DISTANCE = 1000
    HOOK_SHOOT_SPEED = 25
    GRAPPLE_PULL_SPEED = 15

    toxic_puddle = pygame.Rect(300, 550, 200, 30)
    enemy = pygame.Rect(500, 500, 50, 50)
    enemy_alive = True
    enemy_speed_x = 2
    enemy_speed_y = 2
    door = pygame.Rect(800, 500, 50, 100)
    damage_cooldown = 0

    tutorial_texts = [
        (0, "Use WASD to move."),
        (200, "Left-click to shoot your chain."),
        (400, "Press SPACE to pull yourself."),
        (600, "Avoid the toxic puddle!"),
        (700, "Beware of the enemy!"),
    ]

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        mouse_vec = pygame.Vector2(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                hook_pos = pygame.Vector2(player.center)
                hook_dir = (mouse_vec - hook_pos).normalize()
                hook_flying = True
                grappling = False
                pull_to_grapple = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                hook_flying = False
                grappling = False
                pull_to_grapple = False

        keys = pygame.key.get_pressed()
        if not pull_to_grapple:
            if keys[pygame.K_a]: player.x -= player_speed
            if keys[pygame.K_d]: player.x += player_speed
            if keys[pygame.K_w]: player.y -= player_speed
            if keys[pygame.K_s]: player.y += player_speed
        if keys[pygame.K_SPACE] and grappling:
            pull_to_grapple = True

        if hook_flying and hook_pos:
            hook_pos += hook_dir * HOOK_SHOOT_SPEED
            if (hook_pos - pygame.Vector2(player.center)).length() > MAX_GRAPPLE_DISTANCE:
                hook_flying = False
            if (hook_pos - mouse_vec).length() < 10:
                grappling = True
                grapple_point = hook_pos.copy()
                hook_flying = False

        if grappling and pull_to_grapple:
            direction = grapple_point - pygame.Vector2(player.center)
            if direction.length() > 5:
                direction = direction.normalize() * GRAPPLE_PULL_SPEED
                player.x += int(direction.x)
                player.y += int(direction.y)
            else:
                pull_to_grapple = False

        if player.colliderect(toxic_puddle):
            toxic_color = (150, 0, 0)
            player_health -= 0.02
        else:
            toxic_color = (0, 255, 0)

        if player.colliderect(enemy) and enemy_alive and damage_cooldown == 0:
            player_health -= 1
            damage_cooldown = 60
        if damage_cooldown > 0:
            damage_cooldown -= 1

        if player_health <= 0:
            print("You Died!"); pygame.quit(); sys.exit()

        if enemy_alive:
            enemy.x += enemy_speed_x
            enemy.y += enemy_speed_y
            if enemy.left <= 0 or enemy.right >= SCREEN_WIDTH: enemy_speed_x *= -1
            if enemy.top <= 0 or enemy.bottom >= SCREEN_HEIGHT: enemy_speed_y *= -1

        # Draw
        screen.blit(bg_img, (0, 0))
        screen.blit(puddle_img, toxic_puddle)
        if enemy_alive: screen.blit(enemy_img, enemy)
        screen.blit(door_img, door)
        screen.blit(player_img, player)

        if grappling:
            pygame.draw.line(screen, (255, 0, 0), player.center, grapple_point, 2)
            pygame.draw.circle(screen, (255, 0, 0), (int(grapple_point.x), int(grapple_point.y)), 5)
        elif hook_flying and hook_pos:
            pygame.draw.line(screen, (255, 255, 0), player.center, hook_pos, 2)
            pygame.draw.circle(screen, (255, 255, 0), (int(hook_pos.x), int(hook_pos.y)), 4)

        if player.colliderect(door):
            door_text = font.render("Press ENTER to enter Stage 1", True, (0, 0, 0))
            screen.blit(door_text, (SCREEN_WIDTH // 2 - door_text.get_width() // 2, 100))
            if keys[pygame.K_RETURN]:
                stage1()

        if not player.colliderect(door):
            for x_pos, text in tutorial_texts:
                if x_pos <= player.x < x_pos + 300:
                    render_text = font.render(text, True, (0, 0, 0))
                    screen.blit(render_text, (SCREEN_WIDTH // 2 - render_text.get_width() // 2, 50))
                    break

        for i in range(int(player_health)):
            screen.blit(heart_img, (20 + i * 35, 20))

        pygame.display.flip()

# Start
tutorial_stage()
