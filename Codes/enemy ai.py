import pygame
import sys
import math

# Initialize
pygame.init()

# Constants
TILE_SIZE = 32
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60
MAX_GRAPPLE_DISTANCE = 750
HOOK_SHOOT_SPEED = 25
GRAPPLE_PULL_SPEED = 15
GRAVITY = 1.1
FRICTION = 0.90
JUMP_POWER = -15
WALK_ACCEL = 0.6
DASH_SPEED = 20

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SANABI Grapple - Tutorial Stage")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
GREY = (150, 150, 150)
BLUE = (100, 100, 255)
DARK_GREY = (30, 30, 30)
GREEN = (0, 200, 50)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)

tilemap = [
    "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
    "C............................C",
    "C.......CCCCCCCCCCC..........C",
    "C............................C",
    "C............................C",
    "C............................C",
    "CCCCCC.......................C",
    "C............................C",
    "C............................C",
    "C.................CCCCC......C",
    "C............................C",
    "C.......CCC..................C",
    "C............................C",
    "C................CCC.........C",
    "C............................C",
    "C.............CCC............C",
    "C............................C",
    "C............................C",
    "C............................C",
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
]

def generate_walls(map_data):
    walls, ceilings = [], []
    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if tile == 'W': walls.append(rect)
            elif tile == 'C': ceilings.append(rect)
    return walls, ceilings

def draw_map(surface, map_data, offset):
    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            color = GREY if tile == 'W' else BLUE if tile == 'C' else DARK_GREY
            rect = pygame.Rect(x * TILE_SIZE - offset.x, y * TILE_SIZE - offset.y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, color, rect)

def draw_dotted_line(surface, color, start, end, width=2, dash_length=10):
    direction = end - start
    length = direction.length()
    if length == 0:
        return
    direction.normalize_ip()
    for i in range(0, int(length), dash_length * 2):
        pygame.draw.line(surface, color, start + direction * i, start + direction * (i + dash_length), width)

class Player:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.size = 24
        self.color = GREEN
        self.on_ground = False
        self.facing = 1
        self.hp = 5
        self.grappling_enabled = True
        self.grappling = False
        self.grapple_point = pygame.Vector2()
        self.pull_to_grapple = False
        self.hook_pos = None
        self.hook_dir = None
        self.hook_flying = False

    def move(self, keys):
        if keys[pygame.K_a]: self.vel.x -= WALK_ACCEL; self.facing = -1
        if keys[pygame.K_d]: self.vel.x += WALK_ACCEL; self.facing = 1
        if keys[pygame.K_w] and self.on_ground:
            self.vel.y = JUMP_POWER
            self.on_ground = False

    def update(self, walls, ceilings):
        self.vel.y += GRAVITY

        if self.grappling_enabled:
            if self.hook_flying and self.hook_pos:
                self.hook_pos += self.hook_dir * HOOK_SHOOT_SPEED
                for wall in walls + ceilings:
                    if wall.collidepoint(self.hook_pos):
                        self.grappling = True
                        self.grapple_point = self.hook_pos
                        self.hook_flying = False
                        break
                if self.pos.distance_to(self.hook_pos) > MAX_GRAPPLE_DISTANCE:
                    self.hook_flying = False

            if self.grappling and self.pull_to_grapple:
                direction = self.grapple_point - self.pos
                if direction.length() > 5:
                    direction.scale_to_length(GRAPPLE_PULL_SPEED)
                    self.vel = direction
                    self.vel.y -= 5
                else:
                    self.pull_to_grapple = False

        self.pos += self.vel
        self.on_ground = False
        player_rect = self.rect()
        for wall in walls + ceilings:
            if player_rect.colliderect(wall):
                if self.vel.y > 0 and self.pos.y < wall.centery:
                    self.pos.y = wall.top - self.size / 2
                    self.vel.y = 0
                    self.on_ground = True
                elif self.vel.y < 0:
                    self.pos.y = wall.bottom + self.size / 2
                    self.vel.y = 0
                else:
                    if self.vel.x > 0:
                        self.pos.x = wall.left - self.size / 2
                    else:
                        self.pos.x = wall.right + self.size / 2
                    self.vel.x = 0
                player_rect = self.rect()
        self.vel *= FRICTION

    def rect(self):
        return pygame.Rect(int(self.pos.x - self.size / 2), int(self.pos.y - self.size / 2), self.size, self.size)

    def shoot_grapple(self, target):
        if not self.grappling_enabled:
            return
        self.hook_pos = self.pos.copy()
        self.hook_dir = (target - self.pos).normalize()
        self.hook_flying = True
        self.grappling = False
        self.pull_to_grapple = False

    def release_grapple(self):
        self.grappling = False
        self.pull_to_grapple = False
        self.hook_flying = False

    def toggle_pull(self):
        if not self.grappling_enabled:
            return
        if self.grappling:
            if self.pull_to_grapple:
                self.release_grapple()
            else:
                self.pull_to_grapple = True

    def toggle_grappling_mode(self):
        self.grappling_enabled = not self.grappling_enabled
        self.release_grapple()

    def draw(self, surface, offset, mouse_pos_world):
        pygame.draw.rect(surface, self.color, self.rect().move(-offset.x, -offset.y))
        if self.grappling:
            pygame.draw.line(surface, RED, self.pos - offset, self.grapple_point - offset, 2)
            pygame.draw.circle(surface, RED, (int(self.grapple_point.x - offset.x), int(self.grapple_point.y - offset.y)), 5)
        if self.hook_flying:
            pygame.draw.line(surface, YELLOW, self.pos - offset, self.hook_pos - offset, 2)
            pygame.draw.circle(surface, YELLOW, (int(self.hook_pos.x - offset.x), int(self.hook_pos.y - offset.y)), 4)
        elif not self.grappling and self.grappling_enabled:
            draw_dotted_line(surface, WHITE, self.pos - offset, mouse_pos_world - offset, 1, 6)

class Enemy:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.size = 28
        self.color = RED
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)

    def update(self, player):
        direction = player.pos - self.pos
        if direction.length() != 0:
            direction = direction.normalize() * 1.2
            self.pos += direction
        self.rect = pygame.Rect(int(self.pos.x - self.size / 2), int(self.pos.y - self.size / 2), self.size, self.size)

    def draw(self, surface, offset):
        pygame.draw.rect(surface, self.color, self.rect.move(-offset.x, -offset.y))

    def attack(self):
        self.attacking = True
        self.attack_time = pygame.time.get_ticks()

    def attack_rect(self):
        if not self.attacking:
            return None
        offset = pygame.Vector2(30 * self.facing, 0)
        return pygame.Rect(self.pos.x + offset.x - self.size / 2, self.pos.y - self.size / 2)

# Game setup
player = Player(64, 500)
walls, ceilings = generate_walls(tilemap)
camera = pygame.Vector2(0, 0)
space_pressed_last_frame = False

# 여러 적 생성
enemies = [
    Enemy(300, 500),
    Enemy(500, 300),
    Enemy(700, 550),
]
last_hit_time = 0

# Main loop
running = True
while running:
    dt = clock.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()
    world_mouse = pygame.Vector2(mouse_pos) + camera
    click_box = pygame.Rect(world_mouse.x - 4, world_mouse.y - 4, 8, 8)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            player.shoot_grapple(world_mouse)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                player.release_grapple()
            if event.key == pygame.K_f:
                player.toggle_grappling_mode()
            if event.key == pygame.K_LSHIFT:
                direction = -1 if pygame.key.get_pressed()[pygame.K_a] else 1
                player.vel = pygame.Vector2(direction * DASH_SPEED, 0)

    keys = pygame.key.get_pressed()
    player.move(keys)
    player.update(walls, ceilings)

    space_pressed = keys[pygame.K_SPACE]
    if space_pressed and not space_pressed_last_frame:
        player.toggle_pull()
    space_pressed_last_frame = space_pressed

    # 적 업데이트
    for enemy in enemies:
        enemy.update(player)
        if player.rect().colliderect(enemy.rect):
            current_time = pygame.time.get_ticks()
            if current_time - last_hit_time > 1000:
                player.hp -= 1
                print("Player hit! HP:", player.hp)
                last_hit_time = current_time

    # 카메라
    camera.x = player.pos.x - SCREEN_WIDTH // 2
    camera.y = player.pos.y - SCREEN_HEIGHT // 2
    camera.x = max(0, min(camera.x, TILE_SIZE * len(tilemap[0]) - SCREEN_WIDTH))
    camera.y = max(0, min(camera.y, TILE_SIZE * len(tilemap) - SCREEN_HEIGHT))

    # 그리기
    screen.fill("black")
    draw_map(screen, tilemap, camera)
    player.draw(screen, camera, world_mouse)
    for enemy in enemies:
        enemy.draw(screen, camera)
    pygame.draw.rect(screen, RED, click_box.move(-camera.x, -camera.y), 1)

    font = pygame.font.SysFont(None, 24)
    screen.blit(font.render(f"HP: {player.hp}", True, RED), (10, 30))
    mode_text = "ON" if player.grappling_enabled else "OFF"
    screen.blit(font.render(f"WASD / Click: Hook / SPACE: Pull / F: Grapple ({mode_text}) / R: Cancel / Shift: Dash", True, WHITE), (10, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()