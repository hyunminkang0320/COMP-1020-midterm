#COMP_1020_Team_Potatohead

import pygame
import sys
import csv

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

# Initialize (Don't put anything on top of thiss)
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

def load_csv_layout(path):
    with open(path, newline='') as file:
        return [list(map(int, row)) for row in csv.reader(file)]

# Load CSV layers (each uses its own tileset)
csv_back = load_csv_layout("Graphics/BGLayers/CSV_Files/MAp_Back_Layer.csv")
csv_mid = load_csv_layout("Graphics/BGLayers/CSV_Files/MAp_Mid_Layer.csv")
csv_top = load_csv_layout("Graphics/BGLayers/CSV_Files/MAp_Front_Layer.csv")
csv_props = load_csv_layout("Graphics/BGLayers/CSV_Files/MAp_Top_Props.csv")
csv_water = load_csv_layout("Graphics/BGLayers/CSV_Files/MAp_Water_Front.csv")
csv_water_props = load_csv_layout("Graphics/BGLayers/CSV_Files/MAp_Water_Props.csv")

def load_tile_images(tileset_path, tile_size):
    tileset = pygame.image.load(tileset_path).convert_alpha()
    tiles_wide = tileset.get_width() // tile_size
    tiles_high = tileset.get_height() // tile_size
    tile_dict = {}

    tile_id = 0
    for y in range(tiles_high):
        for x in range(tiles_wide):
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
            tile_image = tileset.subsurface(rect)
            tile_dict[tile_id] = tile_image
            tile_id += 1
    return tile_dict

# Load individual tilesets for each CSV
tileset_back = load_tile_images("Graphics/BGLayers/Tile_Images/TIle_Reviesed.png", TILE_SIZE)
tileset_mid = load_tile_images("Graphics/BGLayers/Tile_Images/TIle_Reviesed.png", TILE_SIZE)
tileset_top = load_tile_images("Graphics/BGLayers/Tile_Images/TIle_Reviesed.png", TILE_SIZE)
tileset_props = load_tile_images("Graphics/BGLayers/Tile_Images/TIle_Reviesed.png", TILE_SIZE)
tileset_water = load_tile_images("Graphics/BGLayers/Tile_Images/Water-Front_New.png", TILE_SIZE)
tileset_water_props = load_tile_images("Graphics/BGLayers/Tile_Images/Water_Props_Real_Final.png", TILE_SIZE)

def draw_csv_tiles(surface, layout, tileset, offset, vertical_shift=0):
    for y, row in enumerate(layout):
        for x, tile_id in enumerate(row):
            if tile_id != -1 and tile_id in tileset:
                image = tileset[tile_id]
                surface.blit(
                    image,
                    (x * TILE_SIZE - offset.x,
                     y * TILE_SIZE - offset.y + vertical_shift -128)
                )

event_texts = [
    {
        "rect": pygame.Rect(50, 550, 150, 100),
        "text": "A, D to Move",
        "alpha": 0,
    },
    {
        "rect": pygame.Rect(300, 550, 150, 100),
        "text": "Shift to Dash",
        "alpha": 0,
    },
    {
        "rect": pygame.Rect(800, 550, 150, 100),
        "text": "W to Jump",
        "alpha": 0,
    },
    {
        "rect": pygame.Rect(1200, 580, 150, 100),
        "text": "Click to Attack",
        "alpha": 0,
    },
    {
        "rect": pygame.Rect(2400, 550, 150, 150),
        "text": "F for Grapple mode",
        "alpha": 0,
    },
    {
        "rect": pygame.Rect(2400, 580, 150, 150),
        "text": "aim and click to shoot,",
        "alpha": 0,
    },
    {
        "rect": pygame.Rect(2400, 610, 150, 150),
        "text": "space to pull and release",
        "alpha": 0,
    }
]

event_text_max_alpha = 255
event_fade_speed = 5
event_player_inside = False

#BG sounds
main_music = pygame.mixer.Sound("Audio/BGM/Ambient_sound.mp3")
wind_effect = pygame.mixer.Sound("Audio/BGM/Wind_effect.mp3")
boss_bgm = pygame.mixer.Sound("The Apex of Chaos.mp3")

main_music.set_volume(0.2)
wind_effect.set_volume(0.08)
boss_bgm.set_volume(0.0)

# Play on separate channel
main_channel = pygame.mixer.Channel(0)
wind_channel = pygame.mixer.Channel(1)
boss_channel = pygame.mixer.Channel(2)

main_channel.play(main_music, loops=-1)
wind_channel.play(wind_effect, loops=-1)
boss_channel.play(boss_bgm, loops=-1)

'''
Boss music will play when the boss appears
Will set the volume to 0.4 when collided with event collider
'''

jump_sound = pygame.mixer.Sound("Audio/Player_Sounds/ClothesSyntheticfabric3.wav")
jump_sound.set_volume(0.3)

grapple_line_sound = pygame.mixer.Sound("Audio/Player_Sounds/Lineeffect.mp3")
grapple_line_sound.set_volume(0.3)

attack_sound = pygame.mixer.Sound("Audio/Player_Sounds/Attack_Swing.mp3")
attack_sound.set_volume(0.3)

footstep_sounds = [
    pygame.mixer.Sound("Audio/Player_Sounds/FootstepsConcrete3.wav"),
    pygame.mixer.Sound("Audio/Player_Sounds/FootstepsConcrete4.wav")
]
for s in footstep_sounds:
    s.set_volume(0.25)

grapple_toggle_sound = pygame.mixer.Sound("Audio/Player_Sounds/Grappletoggle.wav")
grapple_toggle_sound.set_volume(0.3)

dialogue_start_sound = pygame.mixer.Sound("Audio/Dialogue_Sounds/SkywardHero_UI (27).wav")
dialogue_start_sound.set_volume(0.4)

dialogue_end_sound = pygame.mixer.Sound("Audio/Dialogue_Sounds/SkywardHero_UI (30).wav")
dialogue_end_sound.set_volume(0.33)

character_portrait = pygame.image.load("Graphics/Player_Illustration/Character_Illustration.png").convert_alpha()
character_portrait = pygame.transform.scale(character_portrait, (400, 550))  # resize if needed
agiss_portrait = pygame.image.load("Graphics/NPC/NPC_Illustration/Agiss_Illustration.png").convert_alpha()
agiss_portrait = pygame.transform.scale(agiss_portrait, (600, 700))

cursor_image = pygame.image.load("Graphics/Cursor_Sprite/cursor_fairy.png").convert_alpha()

dialogue_active = False
dialogue_start_time = 0
illustration_alpha = 0
FADE_DURATION = 200
font = pygame.font.Font("Graphics/Font/BlockBlueprint.ttf", 36)

bg_0 = pygame.transform.scale(pygame.image.load("Graphics/BGLayers/BG_Sprites/BG-0.png").convert_alpha(), (960, 700))
bg_1 = pygame.transform.scale(pygame.image.load("Graphics/BGLayers/BG_Sprites/BG-1.png").convert_alpha(), (960, 700))
bg_2 = pygame.transform.scale(pygame.image.load("Graphics/BGLayers/BG_Sprites/BG-2.png").convert_alpha(), (960, 700))
bg_3 = pygame.transform.scale(pygame.image.load("Graphics/BGLayers/BG_Sprites/Agony.png").convert_alpha(), (680, 120))
bg_4 = pygame.transform.scale(pygame.image.load("Graphics/BGLayers/BG_Sprites/Water-Back.png").convert_alpha(), (960,150))
bg_5 = pygame.transform.scale(pygame.image.load("Graphics/BGLayers/BG_Sprites/BG-3.png").convert_alpha(), (960, 700))

idle_frames = [
    pygame.transform.scale(pygame.image.load(f"Graphics/Player_Anim/Player_Idle_Blink/AnimationSheet_Character_01.png"), (64, 64)),
    pygame.transform.scale(pygame.image.load("Graphics/Player_Anim/Player_Idle_Blink/AnimationSheet_Character_02.png"), (64, 64)),
    pygame.transform.scale(pygame.image.load("Graphics/Player_Anim/Player_Idle_Blink/AnimationSheet_Character_09.png"), (64, 64)),
    pygame.transform.scale(pygame.image.load("Graphics/Player_Anim/Player_Idle_Blink/AnimationSheet_Character_10.png"), (64, 64)),
]

move_frames = [
    pygame.transform.scale(pygame.image.load(f"Graphics/Player_Anim/Player_Run/AnimationSheet_Character_{i:02}.png"), (64, 64))
    for i in range(25, 33)
]

attack_frames = [
    pygame.transform.scale(pygame.image.load(f"Graphics/Player_Anim/Player_Attack/AnimationSheet_Character_{i}.png"), (64, 64))
    for i in range(65, 73)
]

jump_frames = [
    pygame.transform.scale(pygame.image.load(f"Graphics/Player_Anim/Player_Jump/AnimationSheet_Character_{i:02}.png"), (64, 64))
    for i in range(41, 49)
]

dust_frames = [
    pygame.image.load(f"Graphics/Player_Effects/Dust_effect/SmokeNDust-P03-VFX00_0{i}.png").convert_alpha()
    for i in range(1, 10)
]

torch_frames = [
    pygame.transform.scale(pygame.image.load(f"Graphics/BGLayers/BG_Sprites/Torches/Torch_0{i}.png"), (23, 100))
    for i in range(1, 6)
]
torch_anim_index = 0
torch_anim_timer = 0
torch_anim_speed = 100

# Colors
WHITE = (255, 255, 255)
GREY = (150, 150, 150)
BLUE = (100, 100, 255)
DARK_GREY = (30, 30, 30)
GREEN = (0, 200, 50)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)

'''
Adjust the tilemap after applying new CSV file.
'''

tilemap = [
    "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
    "......................................................................................................................................................................................................................C",
    "......................................................................................................................................................................................................................C",
    "......................................................................................................................................................................................................................C",
    "......................................................................................................................................................................................................................C",
    "......................................................................................................................................................................................................................C",
    "......................................................................................................................................................................................................................C",
    "........................................................................................................................................CCCCCC........................................................................C",
    "C.......................................................................................................................................CCCCCC........................................................................C",
    "C....................................................................................................................CCCCCCC..........................................................................................C",
    "C.....................................................................................................................................................................................................................C",
    "C.....................................................................................................................................................................................................................C",
    "C..............CCCCCC.................................................................................................................................................................................................C",
    "C....CCC.................................................................................................CCC............CCCCCC....CCC.................................................................................C",
    "C........................................................................................................CCC....CCC.....CCCCCC....C.C.................................................................................C",
    "C.......................................................................................................................CCCCCC....C.C.................................................................................C",
    "C..........................................................................................C...............................CCC....C.C.................................................................................C",
    "C..........................................................................................C.......................CCC.....CCC....C.C....CCCCCCCCCC...................................................................C",
    "C..........................................................................................C...............................CCC....C.C.................................................................................C",
    "C.............................................................................................................CCC..........CCC....C.C.................................................................................C",
    "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC....................CCCCCCCCCCCC............................................................CCC....C.CCC.........CCCCCCCCCC............................................................C",
    "..............................C.... CCCCCCCCCCC....C..........C...................................................................C.C.C.....................CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
    "..............................C.....C.........C....C..........CCCCCCCCCCCCCCCCC..........CCCCCCCCCCCCC.........................CCCC.C.C...............................................................................C",
    "..............................C.....C.........C....C..........................C..........C...........C......CCCCCCCCCCCCCC.....C..C.C.C.CCCCCCCCCC....................................................................C",
    "..............................C.....C.........C....C..........................C..........C...........C......C............C.....C..C.C.C.C.............................................................................C",
    "..............................C.....C.........C....C..........................C..........C...........C......C............C.....C..C.C.C.C.............................................................................C",
]

def generate_walls(map_data):
    walls, ceilings = [], []
    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if tile == 'W': walls.append(rect)
            elif tile == 'C': ceilings.append(rect)
    return walls, ceilings

'''
Uncomment the "elif tile == 'C': color = RED" below to
modify the colliders for the map
(It will show red boxes)
'''

def draw_map(surface, map_data, offset):
    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            if tile == 'W': color = GREY
            # elif tile == 'C': color = RED
            else: continue
            rect = pygame.Rect(x * TILE_SIZE - offset.x, y * TILE_SIZE - offset.y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, color, rect)

def draw_parallax(surface, camera):
    surface.blit(bg_0, (0, 0))

    bg1 = (-camera.x * 0.1) % bg_1.get_width()
    surface.blit(bg_1, (bg1 - bg_1.get_width(), -50))
    surface.blit(bg_1, (bg1, -50))

    bg2 = (-camera.x * 0.2) % bg_2.get_width()
    surface.blit(bg_2, (bg2 - bg_2.get_width(), -50))
    surface.blit(bg_2, (bg2, -50))

    bg3 = (-camera.x * 0.3) % bg_3.get_width()
    surface.blit(bg_3, (bg3 - bg_3.get_width(), +420))
    surface.blit(bg_3, (bg3, +420))

    bg4 = (-camera.x * 0.4) % bg_4.get_width()
    surface.blit(bg_4, (bg4 - bg_4.get_width(), + 500))
    surface.blit(bg_4, (bg4, + 500))

    bg5 = (-camera.x * 0.4) % bg_5.get_width()
    surface.blit(bg_5, (bg5 - bg_5.get_width(), -50))
    surface.blit(bg_5, (bg5, -50))

    torch_relative_x_positions = [140, 490, 830]

    for tx in torch_relative_x_positions:
        torch_world_x1 = (bg4 - bg_4.get_width()) + tx
        torch_world_x2 = bg4 + tx
        surface.blit(torch_frames[torch_anim_index], (torch_world_x1, 200))
        surface.blit(torch_frames[torch_anim_index], (torch_world_x2, 200))

class Player:

    def __init__(self, x, y, toggle_sound, grapple_line_sound):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.size = 32
        self.on_ground = False
        self.grappling_enabled = False
        self.grappling = False
        self.grapple_toggle_sound = toggle_sound
        self.grapple_line_sound = grapple_line_sound
        self.grapple_point = pygame.Vector2()
        self.grapple_status_text = ""
        self.grapple_status_timer = 0
        self.pull_to_grapple = False
        self.hook_pos = None
        self.hook_dir = None
        self.hook_flying = False
        self.touching_wall_left = False
        self.touching_wall_right = False
        self.wall_jump_cooldown = 0
        self.attacking = False
        self.attack_frames = attack_frames
        self.attack_frame = 0
        self.attack_timer = 0
        self.attack_speed = 50
        self.dust_frames = dust_frames
        self.dust_playing = False
        self.dust_timer = 0
        self.dust_frame = 0
        self.can_dash = True
        self.last_dash_time = 0
        self.dash_cooldown = 800
        self.last_step_time = 0
        self.footstep_interval = 400
        self.step_sound_index = 0

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
        self.holding_jump = keys[pygame.K_w]

        if self.holding_left:
            self.vel.x -= WALK_ACCEL
            self.facing = -1
            self.moving = True
        if self.holding_right:
            self.vel.x += WALK_ACCEL
            self.facing = 1
            self.moving = True

        if self.holding_jump:
            if self.on_ground:
                self.vel.y = JUMP_POWER
                self.on_ground = False
                jump_sound.play()
        elif self.wall_jump_cooldown <= 0:
            if self.touching_wall_left and self.holding_right:
                self.pos.x += 1
                self.vel.y = JUMP_POWER
                self.vel.x = 10
                self.wall_jump_cooldown = 300
            elif self.touching_wall_right and self.holding_left:
                self.pos.x -= 1
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

    def try_dash(self):
        now = pygame.time.get_ticks()
        if self.can_dash and now - self.last_dash_time >= self.dash_cooldown:
            direction = -1 if self.holding_left else 1
            self.vel = pygame.Vector2(direction * DASH_SPEED, 0)

            if self.on_ground:
                self.play_dust()

            jump_sound.play()
            self.last_dash_time = now

    def update(self, walls, ceilings):
        self.vel.y += GRAVITY

        self.on_ground = False
        self.touching_wall_left = False
        self.touching_wall_right = False

        # Handle grapple hook flying
        if self.hook_flying and self.hook_pos:
            self.hook_pos += self.hook_dir * HOOK_SHOOT_SPEED
            for wall in walls + ceilings:
                if wall.collidepoint(self.hook_pos):
                    self.grappling = True
                    self.grapple_point = self.hook_pos
                    self.hook_flying = False
                    if self.grapple_line_sound:
                        self.grapple_line_sound.stop()
                    break
            if self.pos.distance_to(self.hook_pos) > MAX_GRAPPLE_DISTANCE:
                self.hook_flying = False
                if self.grapple_line_sound:
                    self.grapple_line_sound.stop()

        # Update attack animation
        if self.attacking:
            now = pygame.time.get_ticks()
            if now - self.attack_timer > self.attack_speed:
                self.attack_timer = now
                self.attack_frame += 1
                if self.attack_frame >= len(self.attack_frames):
                    self.attacking = False
                    self.attack_frame = 0
                    self.current_frame = 0

        # Handle pulling toward grapple
        if self.grappling and self.pull_to_grapple:
            direction = self.grapple_point - self.pos
            if direction.length() > 5:
                direction.scale_to_length(GRAPPLE_PULL_SPEED)
                self.vel = direction
                self.vel.y -= 5
            else:
                self.pull_to_grapple = False

        # Move the player
        self.pos += self.vel

        # Collision detection
        player_rect = self.rect()
        for wall in walls + ceilings:
            if player_rect.colliderect(wall):
                if self.vel.y > 0 and self.pos.y < wall.centery:
                    self.pos.y = wall.top - self.size / 2
                    self.vel.y = 0
                    self.on_ground = True

                    if self.moving:
                        now = pygame.time.get_ticks()
                        if now - self.last_step_time > self.footstep_interval:
                            footstep_sounds[self.step_sound_index].play()
                            self.step_sound_index = (self.step_sound_index + 1) % len(footstep_sounds)
                            self.last_step_time = now
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

        if self.dust_playing:
            self.dust_timer += clock.get_time()
            if self.dust_timer > 20:
                self.dust_timer = 0
                self.dust_frame += 1
                if self.dust_frame >= len(self.dust_frames):
                    self.dust_playing = False

        if not self.on_ground:
            if (self.touching_wall_left and self.holding_left) or (self.touching_wall_right and self.holding_right):
                if self.vel.y > 2:
                    self.vel.y = 1

        if self.wall_jump_cooldown > 0:
            self.wall_jump_cooldown -= clock.get_time()

        self.vel.x *= FRICTION

    def rect(self):
        return pygame.Rect(int(self.pos.x - self.size / 2), int(self.pos.y - self.size / 2), self.size, self.size)

    def shoot_grapple(self, target):
        if not self.grappling_enabled:
            return
        self.hook_pos = self.pos.copy()
        self.hook_dir = (target - self.pos).normalize()
        self.hook_flying = True
        if self.grapple_line_sound:
            self.grapple_line_sound.play(-1)
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

        self.grapple_status_text = "Grapple ON" if self.grappling_enabled else "Grapple OFF"
        self.grapple_status_timer = pygame.time.get_ticks()

        if self.grapple_toggle_sound:
            self.grapple_toggle_sound.play()

    def draw(self, surface, offset, mouse_pos_world):
        now = pygame.time.get_ticks()

        '''
        
        UNCOMMENT the code below to see player debug collider.
        
        '''
        #pygame.draw.rect(surface, (255, 0, 0), self.rect().move(-offset.x, -offset.y), 1)

        if self.dust_playing and self.dust_frame < len(self.dust_frames):
            dust_img = self.dust_frames[self.dust_frame]

            scale_factor = 1.3
            dust_img = pygame.transform.scale(
                dust_img,
                (int(dust_img.get_width() * scale_factor), int(dust_img.get_height() * scale_factor))
            )

            if self.facing == -1:
                dust_img = pygame.transform.flip(dust_img, True, False)
                dust_offset_x = 45
            else:
                dust_offset_x = -45

            dust_pos = (int(self.pos.x - offset.x - dust_img.get_width() // 2 + dust_offset_x),
                        int(self.pos.y - offset.y - 50))

            surface.blit(dust_img, dust_pos)

        if self.attacking:
            frames = self.attack_frames
            image = frames[self.attack_frame]
            anim_speed = self.attack_speed
        else:
            if not self.on_ground:
                frames = jump_frames
                anim_speed = 120
            elif abs(self.vel.x) > 0.2:
                frames = self.move_frames
                anim_speed = 100
            else:
                frames = self.idle_frames
                anim_speed = 300

        if self.current_frame >= len(frames):
            self.current_frame = 0

        if now - self.animation_timer > anim_speed:
            self.animation_timer = now
            self.current_frame = (self.current_frame + 1) % len(frames)

        image = frames[self.current_frame]

        if self.facing == -1:
            image = pygame.transform.flip(image, True, False)

        draw_pos = (int(self.pos.x - offset.x - 32), int(self.pos.y - offset.y - 47))
        surface.blit(image, draw_pos)

        # Grapple visuals
        if self.grappling:
            pygame.draw.line(surface, RED, self.pos - offset, self.grapple_point - offset, 2)
            pygame.draw.circle(surface, RED,
                               (int(self.grapple_point.x - offset.x), int(self.grapple_point.y - offset.y)), 5)
        elif self.hook_flying:
            pygame.draw.line(surface, YELLOW, self.pos - offset, self.hook_pos - offset, 2)
            pygame.draw.circle(surface, YELLOW, (int(self.hook_pos.x - offset.x), int(self.hook_pos.y - offset.y)), 4)
        elif self.grappling_enabled:
            # Show dotted line only when grapple mode is on
            self.draw_dotted_line(surface, WHITE, self.pos - offset, mouse_pos_world - offset, width=1, dash_length=6)

        if self.grapple_status_text:
            now = pygame.time.get_ticks()
            if now - self.grapple_status_timer < 500:
                status_font = pygame.font.Font("Graphics/Font/BlockBlueprint.ttf", 20)
                text_surface = status_font.render(self.grapple_status_text, True, YELLOW)
                text_rect = text_surface.get_rect(center=(self.pos.x - offset.x, self.pos.y - offset.y - 50))
                surface.blit(text_surface, text_rect)
            else:
                self.grapple_status_text = ""

class Agisss:
    def __init__(self):
        self.frames = [
            pygame.image.load(f"Graphics/NPC/NPC_Anim/Agisss_{i:02}.png").convert_alpha()
            for i in range(1, 16)
        ]
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 100
        self.pos = pygame.Vector2(2100, 600)

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

        '''
        
        UNCOMMENT the code below to see debug collider for Agiss
        
        '''
        # debug_rect = self.collider.move(-camera.x, -camera.y)
        # pygame.draw.rect(surface, (255, 0, 0), debug_rect, 2)

# Game loop
player = Player(64, 600, grapple_toggle_sound, grapple_line_sound)
agisss = Agisss()
walls, ceilings = generate_walls(tilemap)
camera = pygame.Vector2(0, 0)
space_pressed_last_frame = False
running = True

while running:
    dt = clock.tick(FPS)
    torch_anim_timer += dt
    if torch_anim_timer > torch_anim_speed:
        torch_anim_timer = 0
        torch_anim_index = (torch_anim_index + 1) % len(torch_frames)
    mouse_pos = pygame.mouse.get_pos()
    world_mouse = pygame.Vector2(mouse_pos) + camera
    click_box = pygame.Rect(world_mouse.x - 4, world_mouse.y - 4, 8, 8)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not player.attacking and not player.grappling_enabled:
                player.attacking = True
                player.attack_frame = 0
                player.attack_timer = pygame.time.get_ticks()
                attack_sound.play()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            player.shoot_grapple(world_mouse)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: player.release_grapple()
            if event.key == pygame.K_f: player.toggle_grappling_mode()
            if event.key == pygame.K_LSHIFT:
                player.try_dash()
            if event.key == pygame.K_e:
                if dialogue_active:
                    dialogue_index += 1
                    if dialogue_index >= len(dialogue_pages):
                        dialogue_active = False
                        dialogue_index = 0
                        dialogue_end_sound.play()
                    else:
                        dialogue_start_sound.play()
                else:
                    if agisss.collider.colliderect(player.rect()):
                        dialogue_active = True
                        dialogue_start_sound.play()
                        dialogue_start_time = pygame.time.get_ticks()
                        illustration_alpha = 0
                        dialogue_index = 0

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

        for evt in event_texts:
            player_inside = evt["rect"].colliderect(player.rect())
            if player_inside and evt["alpha"] < event_text_max_alpha:
                evt["alpha"] += event_fade_speed
            elif not player_inside and evt["alpha"] > 0:
                evt["alpha"] -= event_fade_speed
    else:
        pass

    screen.fill("black")
    draw_parallax(screen, camera)
    draw_csv_tiles(screen, csv_back, tileset_back, camera)
    draw_csv_tiles(screen, csv_mid, tileset_mid, camera)
    draw_csv_tiles(screen, csv_top, tileset_top, camera)
    draw_csv_tiles(screen, csv_props, tileset_props, camera)
    draw_csv_tiles(screen, csv_water, tileset_water, camera)
    draw_csv_tiles(screen, csv_water_props, tileset_water_props, camera)
    for evt in event_texts:
        if evt["alpha"] > 0:
            text_surface = font.render(evt["text"], True, (255,0, 100))
            text_surface.set_alpha(evt["alpha"])
            text_rect = text_surface.get_rect(midbottom=evt["rect"].move(-camera.x, -camera.y).midtop)
            text_rect.y -= 10  # optional upward offset
            screen.blit(text_surface, text_rect)

            '''
            
            UNCOMMENT the code below to see debug collider for 
            instruction text box
            
            '''
        # Debug red box Debug Box
        # pygame.draw.rect(screen, (255, 0, 0), evt["rect"].move(-camera.x, -camera.y), 2)

    draw_map(screen, tilemap, camera, )
    draw_map(screen, tilemap, camera)

    agisss.update()
    agisss.draw(screen, camera)
    if agisss.collider.colliderect(player.rect()) and not dialogue_active:
        e_text = font.render("E to interact", True, (255, 0, 100))

        e_pos_x = agisss.pos.x - camera.x - e_text.get_width() // 2
        e_pos_y = agisss.pos.y - camera.y - agisss.collider.height // 2 - 60

        screen.blit(e_text, (e_pos_x, e_pos_y))
    player.draw(screen, camera, world_mouse)

    mouse_pos = pygame.mouse.get_pos()
    offset = (-15, -20)
    screen.blit(cursor_image, (mouse_pos[0] + offset[0], mouse_pos[1] + offset[1]))

    if dialogue_active:
        if dialogue_active:
            elapsed = pygame.time.get_ticks() - dialogue_start_time
            progress = min(elapsed / FADE_DURATION, 1)
            illustration_alpha = int(255 * progress)

        dialogue_rect = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT * 2 // 5), pygame.SRCALPHA)
        dialogue_rect.fill((0, 0, 0, 180))
        screen.blit(dialogue_rect, (0, SCREEN_HEIGHT - SCREEN_HEIGHT * 2 // 5))

        # Sceen darken
        dialogue_rect = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dialogue_rect.fill((0, 0, 0, 100))
        screen.blit(dialogue_rect, (0, SCREEN_HEIGHT - SCREEN_HEIGHT))

        if dialogue_index % 2 == 0:

            portrait = character_portrait
            portrait_x = 550
            text_x = 50
        else:
            portrait = agiss_portrait
            portrait_x = -100
            text_x = 380

        portrait.set_alpha(illustration_alpha)
        screen.blit(portrait, (portrait_x, SCREEN_HEIGHT - portrait.get_height()))

        dialogue_pages = [
            ["Where...Where am I?", "This doesn't feel real..."],
            ["Welcome, lost soul,", "to the Passage of Tourment", "the road that leads to hell.."],
            ["...Hell? You mean this is hell?"],
            ["Not yet. But you're close.", "This the space between...", "Where the unworthy are broken,", "and some may earn a second chance."],
            ["Then How do I get out of here?"],
            ["There is only one door back", "to the living...and it lies", "beyond the lair of the Warden.."],
            ["...The boss?"],
            ["Call it what you will.", "But know this..only by defeating it", "can you reclaim your soul...", "or be devoured by the fire you brought..."]
        ]

        dialogue_lines = dialogue_pages[dialogue_index]
        for i, line in enumerate(dialogue_lines):
            text_surface = font.render(line, True, WHITE)
            screen.blit(text_surface, (text_x, SCREEN_HEIGHT - SCREEN_HEIGHT * 2 // 5 + 50 + i * 30))

    pygame.display.flip()

pygame.quit()
sys.exit()