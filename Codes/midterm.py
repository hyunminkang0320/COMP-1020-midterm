import pygame
import sys

# Initialize
pygame.init()

# Constants
TILE_SIZE = 32
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60
MAX_GRAPPLE_DISTANCE = 750
GRAPPLE_PULL_SPEED = 24
GRAVITY = 1.1
FRICTION = 0.90
JUMP_POWER = -15
WALK_ACCEL = 0.8
DASH_SPEED = 20

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SANABI Grapple - Direction Fix & Upward Pull")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
GREY = (150, 150, 150)
BLUE = (100, 100, 255)
DARK_GREY = (30, 30, 30)
GREEN = (0, 200, 50)
RED = (255, 50, 50)

tilemap = [
    "..............................",
    "..............................",
    "........CCCCCCCCCCC...........",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............W...............",
    "..............W...............",
    "..............W...............",
    ".....W.....................W..",
    ".....W.....................W..",
    ".....W.....................W..",
    ".....W.....................W..",
    ".....W.....................W..",
    ".....W.....................W..",
    ".....W.....................W..",
    ".....W.....................W..",
    ".....W.....................W..",
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
]

def generate_walls(map_data):
    walls = []
    ceilings = []
    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if tile == 'W':
                walls.append(rect)
            elif tile == 'C':
                ceilings.append(rect)
    return walls, ceilings

def draw_map(surface, map_data, offset):
    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            color = GREY if tile == 'W' else BLUE if tile == 'C' else DARK_GREY
            rect = pygame.Rect(x * TILE_SIZE - offset.x, y * TILE_SIZE - offset.y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, color, rect)

class Player:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.size = 24
        self.color = GREEN
        self.on_ground = False
        self.grappling = False
        self.grapple_point = pygame.Vector2()
        self.pull_to_grapple = False
        self.recalling = False
        self.facing = 1
        self.original_pos = pygame.Vector2()

    def move(self, keys):
        if keys[pygame.K_a]:
            self.vel.x -= WALK_ACCEL
            self.facing = -1
        if keys[pygame.K_d]:
            self.vel.x += WALK_ACCEL
            self.facing = 1
        if keys[pygame.K_w] and self.on_ground:
            self.vel.y = JUMP_POWER
            self.on_ground = False

    def update(self, walls, ceilings):
        self.vel.y += GRAVITY

        if self.grappling and self.pull_to_grapple:
            direction = self.grapple_point - self.pos
            if direction.length() > 5:
                direction.scale_to_length(GRAPPLE_PULL_SPEED)
                self.vel = direction
                self.vel.y = -21
            else:
                self.pull_to_grapple = False
        elif self.recalling:
            direction = self.original_pos - self.pos
            if direction.length() > 5:
                direction.scale_to_length(GRAPPLE_PULL_SPEED)
                self.vel = direction
            else:
                self.recalling = False
                self.vel = pygame.Vector2(0, 0)
                self.pos.y -= 5
                self.on_ground = True

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
                elif self.vel.x != 0:
                    if self.vel.x > 0:
                        self.pos.x = wall.left - self.size / 2
                    else:
                        self.pos.x = wall.right + self.size / 2
                    self.vel.x = 0
                player_rect = self.rect()

        self.vel *= FRICTION

    def rect(self):
        return pygame.Rect(int(self.pos.x - self.size / 2), int(self.pos.y - self.size / 2), self.size, self.size)

    def start_grapple(self, point):
        self.grappling = True
        self.grapple_point = point
        self.pull_to_grapple = False
        self.recalling = False

    def release_grapple(self):
        self.grappling = False
        self.pull_to_grapple = False
        self.recalling = False

    def pull(self):
        if self.grappling:
            if self.pull_to_grapple:
                self.recalling = True
                self.pull_to_grapple = False
            else:
                self.original_pos = self.pos.copy()
                self.pull_to_grapple = True

    def draw(self, surface, offset):
        pygame.draw.rect(surface, self.color, self.rect().move(-offset.x, -offset.y))
        if self.grappling:
            pygame.draw.line(surface, RED, self.pos - offset, self.grapple_point - offset, 2)
            pygame.draw.circle(surface, RED, (int(self.grapple_point.x - offset.x), int(self.grapple_point.y - offset.y)), 5)

player = Player(64, 500)
walls, ceilings = generate_walls(tilemap)
camera = pygame.Vector2(0, 0)

running = True
while running:
    dt = clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            world_pos = pygame.Vector2(mx, my) + camera

            if any(wall.collidepoint(world_pos) for wall in walls):
                continue

            click_box = pygame.Rect(world_pos.x - 2, world_pos.y - 2, 4, 4)
            valid = False
            for wall in walls + ceilings:
                # Only attach to wall surface facing the player
                if wall.inflate(16, 16).colliderect(click_box):
                    if player.facing == 1 and world_pos.x > wall.centerx:
                        valid = True
                        break
                    elif player.facing == -1 and world_pos.x < wall.centerx:
                        valid = True
                        break

            if valid and player.pos.distance_to(world_pos) <= MAX_GRAPPLE_DISTANCE:
                player.start_grapple(world_pos)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                player.release_grapple()
            if event.key == pygame.K_f:
                player.pull()
            if event.key == pygame.K_LSHIFT:
                direction = -1 if pygame.key.get_pressed()[pygame.K_a] else 1
                player.vel = pygame.Vector2(direction * DASH_SPEED, 0)

    keys = pygame.key.get_pressed()
    player.move(keys)
    player.update(walls, ceilings)

    camera.x = player.pos.x - SCREEN_WIDTH // 2
    camera.y = player.pos.y - SCREEN_HEIGHT // 2
    camera.x = max(0, min(camera.x, TILE_SIZE * len(tilemap[0]) - SCREEN_WIDTH))
    camera.y = max(0, min(camera.y, TILE_SIZE * len(tilemap) - SCREEN_HEIGHT))

    screen.fill("black")
    draw_map(screen, tilemap, camera)
    player.draw(screen, camera)

    font = pygame.font.SysFont(None, 24)
    screen.blit(font.render("WASD / Click: Grapple / F: Pull+Recall / R: Release / Shift: Dash", True, WHITE), (10, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
