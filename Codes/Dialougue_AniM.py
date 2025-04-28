# SANABI Grapple Game with Parallax and Animated Player

import pygame
import sys

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
BG_WIDTH = 1000
BG_HEIGHT = 500

# Initialize
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SANABI Grapple - Parallax BG")
clock = pygame.time.Clock()

# Load Character Portrait
character_portrait = pygame.image.load("Character_Illustration.png").convert_alpha()
character_portrait = pygame.transform.scale(character_portrait, (500, 600))  # resize if needed

# Dialogue State
dialogue_active = False
font = pygame.font.SysFont(None, 36)  # You already have a font for text


# Load backgrounds
gradient = pygame.transform.scale(pygame.image.load("Gradient (z -6).png").convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT))
mountains = pygame.transform.scale(pygame.image.load("mtn (z -4).png").convert_alpha(), (BG_WIDTH, BG_HEIGHT))
sky = pygame.transform.scale(pygame.image.load("sky (z -3).png").convert_alpha(), (BG_WIDTH, BG_HEIGHT))
bg2 = pygame.transform.scale(pygame.image.load("bg_2 (z -2).png").convert_alpha(), (BG_WIDTH, BG_HEIGHT))
bg1 = pygame.transform.scale(pygame.image.load("bg_1 (z -1).png").convert_alpha(), (BG_WIDTH, BG_HEIGHT))
middleground = pygame.transform.scale(pygame.image.load("middleground (z 0).png").convert_alpha(), (BG_WIDTH, BG_HEIGHT))
middleplus = pygame.transform.scale(pygame.image.load("middleplus (z 1).png").convert_alpha(), (BG_WIDTH, BG_HEIGHT))

# Load animations
idle_frames = [
    pygame.transform.scale(pygame.image.load("AnimationSheet_Character_01.png"), (64, 64)),
    pygame.transform.scale(pygame.image.load("AnimationSheet_Character_02.png"), (64, 64)),
    pygame.transform.scale(pygame.image.load("AnimationSheet_Character_09.png"), (64, 64)),
    pygame.transform.scale(pygame.image.load("AnimationSheet_Character_10.png"), (64, 64)),
]

move_frames = [
    pygame.transform.scale(pygame.image.load(f"AnimationSheet_Character_{i:02}.png"), (64, 64))
    for i in range(25, 33)
]

jump_frames = [
    pygame.transform.scale(pygame.image.load(f"AnimationSheet_Character_{i:02}.png"), (64, 64))
    for i in range(41, 49)
]

# Load Dust Animation
dust_frames = [
    pygame.image.load(f"SmokeNDust-P03-VFX1111-3_0{i}.png").convert_alpha()
    for i in range(1, 8)
]

# Colors
WHITE = (255, 255, 255)
GREY = (150, 150, 150)
BLUE = (100, 100, 255)
DARK_GREY = (30, 30, 30)
GREEN = (0, 200, 50)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)

# Tilemap
tilemap = [
    "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
    "C........................................................C",
    "C.......CCCCCCCCCCC......................................C",
    "C........................................................C",
    "C........................................................C",
    "C........................................................C",
    "CCCCCC...................................................C",
    "C........................................................C",
    "C........................................................C",
    "C.................CCCCC..................................C",
    "C........................................................C",
    "C.......CCC..............................................C",
    "C........................................................C",
    "C................CCC.....................................C",
    "C........................................................C",
    "C.............CCC........................................C",
    "C........................................................C",
    "C........................................................C",
    "C........................................................C",
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
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
            if tile == 'W': color = GREY
            elif tile == 'C': color = BLUE
            else: continue
            rect = pygame.Rect(x * TILE_SIZE - offset.x, y * TILE_SIZE - offset.y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, color, rect)

def draw_parallax(surface, camera):
    # Gradient (fixed)
    surface.blit(gradient, (0, 0))

    # Mountains (slowest)
    mount_x = (-camera.x * 0.1) % BG_WIDTH
    surface.blit(mountains, (mount_x - BG_WIDTH, 200))
    surface.blit(mountains, (mount_x, 200))

    # Sky trees
    sky_x = (-camera.x * 0.2) % BG_WIDTH
    surface.blit(sky, (sky_x - BG_WIDTH, 200))
    surface.blit(sky, (sky_x, 200))

    # Mid backgrounds
    bg2_x = (-camera.x * 0.4) % BG_WIDTH
    surface.blit(bg2, (bg2_x - BG_WIDTH, 140))
    surface.blit(bg2, (bg2_x, 140))

    bg1_x = (-camera.x * 0.6) % BG_WIDTH
    surface.blit(bg1, (bg1_x - BG_WIDTH, 150))
    surface.blit(bg1, (bg1_x, 150))

    middleground_x = (-camera.x * 0.8) % BG_WIDTH
    surface.blit(middleground, (middleground_x - BG_WIDTH, 200))
    surface.blit(middleground, (middleground_x, 200))

    middleplus_x = (-camera.x * 1.0) % BG_WIDTH
    surface.blit(middleplus, (middleplus_x - BG_WIDTH, 150))
    surface.blit(middleplus, (middleplus_x, 150))

class Player:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.size = 32
        self.on_ground = False
        self.grappling_enabled = True
        self.grappling = False
        self.grapple_point = pygame.Vector2()
        self.pull_to_grapple = False
        self.hook_pos = None
        self.hook_dir = None
        self.hook_flying = False
        self.touching_wall_left = False
        self.touching_wall_right = False
        self.wall_jump_cooldown = 0  # milliseconds
        self.dust_frames = dust_frames
        self.dust_playing = False
        self.dust_timer = 0
        self.dust_frame = 0

        self.idle_frames = idle_frames
        self.move_frames = move_frames
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 300
        self.facing = 1
        self.moving = False

    def move(self, keys):
        self.moving = False
        self.holding_left = keys[pygame.K_a]
        self.holding_right = keys[pygame.K_d]
        self.holding_jump = keys[pygame.K_SPACE]

        if self.holding_left:
            self.vel.x -= WALK_ACCEL
            self.facing = -1
            self.moving = True
        if self.holding_right:
            self.vel.x += WALK_ACCEL
            self.facing = 1
            self.moving = True

        # Dashing triggers dust!
        if keys[pygame.K_LSHIFT] and not self.dust_playing:
            direction = -1 if self.holding_left else 1
            self.vel = pygame.Vector2(direction * DASH_SPEED, 0)
            self.play_dust()

        # Jump
        if self.holding_jump:
            if self.on_ground:
                self.vel.y = JUMP_POWER
                self.on_ground = False
            elif self.wall_jump_cooldown <= 0:
                if self.touching_wall_left and self.holding_right:
                    self.vel.y = JUMP_POWER
                    self.vel.x = 10
                    self.wall_jump_cooldown = 300
                elif self.touching_wall_right and self.holding_left:
                    self.vel.y = JUMP_POWER
                    self.vel.x = -10
                    self.wall_jump_cooldown = 300

    def draw_dotted_line(self, surface, color, start, end, width=2, dash_length=10):
        direction = end - start
        length = direction.length()
        if length == 0:
            return
        direction.normalize_ip()
        for i in range(0, int(length), dash_length * 2):
            pygame.draw.line(surface, color, start + direction * i, start + direction * (i + dash_length), width)

    def play_dust(self):
        self.dust_playing = True
        self.dust_timer = 0
        self.dust_frame = 0

    def update(self, walls, ceilings):
        self.vel.y += GRAVITY

        self.on_ground = False
        self.touching_wall_left = False
        self.touching_wall_right = False

        # 🪝 Handle grapple hook flying
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

        # 🧲 Handle pulling toward grapple
        if self.grappling and self.pull_to_grapple:
            direction = self.grapple_point - self.pos
            if direction.length() > 5:
                direction.scale_to_length(GRAPPLE_PULL_SPEED)
                self.vel = direction
                self.vel.y -= 5
            else:
                self.pull_to_grapple = False

        # ✨ Move the player
        self.pos += self.vel

        # 🎯 Collision detection
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
                        self.vel.x = 0
                        self.touching_wall_right = True
                    elif self.vel.x < 0:
                        self.pos.x = wall.right + self.size / 2
                        self.vel.x = 0
                        self.touching_wall_left = True
                player_rect = self.rect()

            # Dust Animation Update
        if self.dust_playing:
            self.dust_timer += clock.get_time()
            if self.dust_timer > 50:  # 50ms per frame
                self.dust_timer = 0
                self.dust_frame += 1
                if self.dust_frame >= len(self.dust_frames):
                    self.dust_playing = False

        # 🧗 Wall slide
        if not self.on_ground:
            if (self.touching_wall_left and self.holding_left) or (self.touching_wall_right and self.holding_right):
                if self.vel.y > 2:
                    self.vel.y = 1  # Slow down fall when sliding against wall

        # ⏳ Cooldown timer
        if self.wall_jump_cooldown > 0:
            self.wall_jump_cooldown -= clock.get_time()

        # ⚡ Friction
        self.vel.x *= FRICTION

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
        now = pygame.time.get_ticks()

        # pygame.draw.rect(surface, (255, 0, 0), self.rect().move(-offset.x, -offset.y), 1)

        # Draw Dust under player
        if self.dust_playing and self.dust_frame < len(self.dust_frames):
            dust_img = self.dust_frames[self.dust_frame]

            # Scale dust bigger
            scale_factor = 2  # 2x size (you can tweak this to 1.5, 2.5, etc.)
            dust_img = pygame.transform.scale(
                dust_img,
                (int(dust_img.get_width() * scale_factor), int(dust_img.get_height() * scale_factor))
            )

            # Flip dust if player is dashing left
            if self.facing == -1:
                dust_img = pygame.transform.flip(dust_img, True, False)
                dust_offset_x = 40
            else:
                dust_offset_x = -40

            dust_pos = (int(self.pos.x - offset.x - dust_img.get_width() // 2 + dust_offset_x),
                        int(self.pos.y - offset.y - 70))

            surface.blit(dust_img, dust_pos)

        # Pick frames based on movement state
        if not self.on_ground:
            frames = jump_frames
            anim_speed = 120
        elif abs(self.vel.x) > 0.2:
            frames = self.move_frames
            anim_speed = 100
        else:
            frames = self.idle_frames
            anim_speed = 300

        # Reset current_frame if it exceeds new frames length
        if self.current_frame >= len(frames):
            self.current_frame = 0

        # Update animation timer
        if now - self.animation_timer > anim_speed:
            self.animation_timer = now
            self.current_frame = (self.current_frame + 1) % len(frames)

        image = frames[self.current_frame]

        if self.facing == -1:
            image = pygame.transform.flip(image, True, False)

        draw_pos = (int(self.pos.x - offset.x - 32), int(self.pos.y - offset.y - 36))
        surface.blit(image, draw_pos)

        # Grapple visuals
        if self.grappling:
            pygame.draw.line(surface, RED, self.pos - offset, self.grapple_point - offset, 2)
            pygame.draw.circle(surface, RED,
                               (int(self.grapple_point.x - offset.x), int(self.grapple_point.y - offset.y)), 5)
        elif self.hook_flying:
            pygame.draw.line(surface, YELLOW, self.pos - offset, self.hook_pos - offset, 2)
            pygame.draw.circle(surface, YELLOW, (int(self.hook_pos.x - offset.x), int(self.hook_pos.y - offset.y)), 4)
        else:
            # <-- NEW: Draw dotted line only if not grappling or hook flying
            self.draw_dotted_line(surface, WHITE, self.pos - offset, mouse_pos_world - offset, width=1, dash_length=6)

class Agisss:
    def __init__(self):
        self.frames = [
            pygame.image.load(f"Agisss_{i:02}.png").convert_alpha()
            for i in range(1, 16)
        ]
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 100  # ms per frame (10 FPS)
        self.pos = pygame.Vector2(1000, 500)  # center-right side (adjust!)

        self.collider = pygame.Rect(self.pos.x - 65, self.pos.y - 50, 130, 160)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.animation_timer > self.animation_speed:
            self.animation_timer = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def draw(self, surface, camera):
        frame = self.frames[self.current_frame]
        draw_pos = self.pos - camera
        surface.blit(frame, (draw_pos.x - frame.get_width() // 2, draw_pos.y - frame.get_height() // 2))

        # Draw red debug collider
        debug_rect = self.collider.move(-camera.x, -camera.y)
        pygame.draw.rect(surface, (255, 0, 0), debug_rect, 2)

# Game loop
player = Player(64, 500)
agisss = Agisss()
walls, ceilings = generate_walls(tilemap)
camera = pygame.Vector2(0, 0)
space_pressed_last_frame = False
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
            if event.key == pygame.K_r: player.release_grapple()
            if event.key == pygame.K_f: player.toggle_grappling_mode()
            if event.key == pygame.K_LSHIFT:
                direction = -1 if pygame.key.get_pressed()[pygame.K_a] else 1
                player.vel = pygame.Vector2(direction * DASH_SPEED, 0)
            if event.key == pygame.K_e:
                if dialogue_active:
                    dialogue_active = False  # Close dialogue
                else:
                    if agisss.collider.colliderect(player.rect()):
                        dialogue_active = True  # Open dialogue if close enough

    keys = pygame.key.get_pressed()
    if not dialogue_active:
        player.move(keys)
        player.update(walls, ceilings)

        if keys[pygame.K_SPACE] and not space_pressed_last_frame:
            player.toggle_pull()
        space_pressed_last_frame = keys[pygame.K_SPACE]

        camera.x = player.pos.x - SCREEN_WIDTH // 2
        camera.y = player.pos.y - SCREEN_HEIGHT // 2
        camera.x = max(0, min(camera.x, TILE_SIZE * len(tilemap[0]) - SCREEN_WIDTH))
        camera.y = max(0, min(camera.y, TILE_SIZE * len(tilemap) - SCREEN_HEIGHT))
    else:
        # While dialogue is active, do not update player or camera
        pass

    screen.fill("black")
    draw_parallax(screen, camera)
    draw_map(screen, tilemap, camera)
    agisss.update()
    agisss.draw(screen, camera)
    player.draw(screen, camera, world_mouse)
    if dialogue_active:
        # Semi-transparent black rectangle
        dialogue_rect = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT * 2 // 5), pygame.SRCALPHA)
        dialogue_rect.fill((0, 0, 0, 180))  # black with some transparency
        screen.blit(dialogue_rect, (0, SCREEN_HEIGHT - SCREEN_HEIGHT * 2 // 5))

        # Character portraitad
        screen.blit(character_portrait, (500, SCREEN_HEIGHT - character_portrait.get_height()))

        # Text
        text_surface = font.render("I am HyunMin Kang, and I love Berny", True, WHITE)
        screen.blit(text_surface, (100, SCREEN_HEIGHT - SCREEN_HEIGHT * 2 // 5 + 50))
    pygame.draw.rect(screen, RED, click_box.move(-camera.x, -camera.y), 1)

    font = pygame.font.SysFont(None, 32)
    mode_text = "ON" if player.grappling_enabled else "OFF"
    screen.blit(font.render(f"WASD / Click: Hook / SPACE: Pull+Release / F: Grapple Mode ({mode_text}) / R: Cancel / Shift: Dash", True, WHITE), (10, 10))
    pygame.display.flip()

pygame.quit()
sys.exit()