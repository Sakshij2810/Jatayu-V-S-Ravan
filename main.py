import pygame
import random
import math
import os

pygame.init()

# --------------------------------------------------
# GAME SETTINGS
# --------------------------------------------------
W, H = 1400, 800
FPS = 60

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("JATAYU: THE FINAL FLIGHT")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("Courier New", 16, bold=True)
SMALL = pygame.font.SysFont("Courier New", 13, bold=True)
TINY = pygame.font.SysFont("Courier New", 10, bold=True)
TITLE = pygame.font.SysFont("Courier New", 27, bold=True)

BLACK = (4, 5, 12)
WHITE = (225, 230, 238)
GOLD = (255, 205, 105)
RED = (235, 83, 76)
ORANGE = (255, 145, 65)
CYAN = (115, 220, 245)
GREEN = (105, 220, 150)
PALE = (255, 232, 170)
PURPLE = (150, 110, 230)
GRAY = (100, 105, 120)


# --------------------------------------------------
# LOAD JATAYU IMAGE
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

JATAYU_IMAGE_PATH = os.path.join(
    BASE_DIR,
    "assets",
    "jatayu.png"
)

try:
    original_image = pygame.image.load(
        JATAYU_IMAGE_PATH
    ).convert_alpha()

    original_width, original_height = original_image.get_size()

    target_width = 190

    target_height = int(
        original_height * target_width / original_width
    )

    jatayu_image = pygame.transform.smoothscale(
        original_image,
        (target_width, target_height)
    )

    # Keep two frames so the existing animation code works.
    JATAYU_IMAGES = [
        jatayu_image,
        jatayu_image
    ]

    print("Jatayu image loaded:", JATAYU_IMAGES[0].get_size())

except (pygame.error, ValueError) as error:
    raise SystemExit(
        f"Could not load Jatayu image: {JATAYU_IMAGE_PATH}\n{error}"
    )
# --------------------------------------------------
# ASCII ART FOR RAVANA AND SITA GLOW
# --------------------------------------------------
RAVANA_ART = r"""
       

 (._.) (._.) (._.) (._.) (._.) 
       (._.) (._.) (._.) 
          (._.) (._.)

              /|\
             / | \
            /__|__\
              / \
             /___\
"""

SITA_ART = r"""
       .-.
      (. .)
       \_/
      /|*|\
       / \
      /___\
"""


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------
def draw_sita_glow(surface, x, y):
    glow = pygame.Surface((130, 130), pygame.SRCALPHA)

    for radius, alpha in [
        (58, 12), (50, 20), (42, 30), (34, 45), (27, 65)
    ]:
        pygame.draw.circle(
            glow, (255, 210, 100, alpha), (65, 65), radius
        )

    surface.blit(glow, (int(x - 65), int(y - 65)))

    pulse = math.sin(pygame.time.get_ticks() * 0.004) * 3

    pygame.draw.circle(
        surface, GOLD, (int(x), int(y)), int(32 + pulse), 2
    )
    pygame.draw.circle(
        surface, PALE, (int(x), int(y)), 25, 1
    )

    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        px = x + math.cos(rad) * 42
        py = y + math.sin(rad) * 42
        pygame.draw.circle(surface, PALE, (int(px), int(py)), 2)


def text_art(surface, art, x, y, color, font=FONT, gap=1):
    lines = art.strip("\n").splitlines()
    step = font.get_linesize() + gap

    for i, line in enumerate(lines):
        image = font.render(line, True, color)
        surface.blit(image, (int(x), int(y + i * step)))

    width = max((font.size(line)[0] for line in lines), default=0)
    return pygame.Rect(int(x), int(y), width, len(lines) * step)


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


# --------------------------------------------------
# BACKGROUND EFFECTS
# --------------------------------------------------
stars = [
    {
        "x": random.randrange(W),
        "y": random.randrange(H),
        "v": random.uniform(0.25, 1.2),
        "c": random.choice([".", ".", "·", "*", "+"])
    }
   for _ in range(300)
]

particles = []


def burst(x, y, color, n=20):
    for _ in range(n):
        angle = random.random() * math.tau
        speed = random.uniform(1.2, 5)
        particles.append([
            x, y,
            math.cos(angle) * speed,
            math.sin(angle) * speed,
            random.randint(18, 38),
            random.choice(["*", "+", ".", "#"]),
            color
        ])


def update_effects():
    for star in stars:
        star["y"] += star["v"]
        if star["y"] > H:
            star["y"] = -5
            star["x"] = random.randrange(W)

    for particle in particles:
        particle[0] += particle[2]
        particle[1] += particle[3]
        particle[2] *= 0.97
        particle[3] *= 0.97
        particle[4] -= 1

    particles[:] = [p for p in particles if p[4] > 0]


def draw_effects():
    for star in stars:
        shade = random.randint(115, 205)
        screen.blit(
            TINY.render(star["c"], True, (shade, shade, min(255, shade + 25))),
            (star["x"], star["y"])
        )

    for particle in particles:
        screen.blit(
            SMALL.render(particle[5], True, particle[6]),
            (int(particle[0]), int(particle[1]))
        )


# --------------------------------------------------
# UI BAR
# --------------------------------------------------
def bar(x, y, w, h, value, maximum, color, label):
    screen.blit(SMALL.render(label, True, WHITE), (x, y - 19))

    pygame.draw.rect(
        screen, (35, 38, 50), (x, y, w, h), border_radius=4
    )

    percentage = max(0, min(1, value / maximum))
    pygame.draw.rect(
        screen, color, (x, y, int(w * percentage), h), border_radius=4
    )
    pygame.draw.rect(
        screen, (105, 110, 125), (x, y, w, h), 1, border_radius=4
    )


# --------------------------------------------------
# JATAYU
# --------------------------------------------------
class Jatayu:
    def __init__(self):
        self.x = 100
        self.y = H // 2 - 100

        self.health = 100
        self.stamina = 100

        self.frame = 0
        self.anim = 0

        self.attack_cooldown = 0
        self.invuln = 0

        self.shots = []
        self.has_sita = False

    def rect(self):
        # Collision box is slightly smaller than the visible sprite.
        return pygame.Rect(
            int(self.x + 25),
            int(self.y + 20),
            145,
            90
        )

    def update(self, keys):
        dx = (
            (keys[pygame.K_RIGHT] or keys[pygame.K_d])
            - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        )
        dy = (
            (keys[pygame.K_DOWN] or keys[pygame.K_s])
            - (keys[pygame.K_UP] or keys[pygame.K_w])
        )

        scale = 0.7071 if dx and dy else 1
        speed = 4.5

        boosting = keys[pygame.K_LSHIFT] and self.stamina > 0

        if boosting:
            speed = 8
            self.stamina = max(0, self.stamina - 1.2)

            if random.random() < 0.35:
                particles.append([
                    self.x + 25,
                    self.y + random.randint(30, 100),
                    -random.uniform(2, 5),
                    random.uniform(-1, 1),
                    15,
                    "~",
                    CYAN
                ])
        else:
            self.stamina = min(100, self.stamina + 0.35)

        # Carrying Sita makes Jatayu slower.
        if self.has_sita:
            speed *= 0.75

        self.x += dx * speed * scale
        self.y += dy * speed * scale

        sprite_w, sprite_h = JATAYU_IMAGES[0].get_size()
        self.x = max(8, min(W - sprite_w - 8, self.x))
        self.y = max(100, min(H - sprite_h - 55, self.y))

        # Alternate between the two wing poses.
        self.anim += 1
        if self.anim >= 11:
            self.frame = (self.frame + 1) % len(JATAYU_IMAGES)
            self.anim = 0

        self.attack_cooldown = max(0, self.attack_cooldown - 1)
        self.invuln = max(0, self.invuln - 1)

        for shot in self.shots:
            shot[0] += 11

        self.shots[:] = [shot for shot in self.shots if shot[0] < W + 30]

    def attack(self):
        if self.attack_cooldown == 0 and len(self.shots) < 4:
            _, sprite_h = JATAYU_IMAGES[0].get_size()
            self.shots.append([
                self.x + 165,
                self.y + sprite_h * 0.48
            ])
            self.attack_cooldown = 17

    def hit(self):
        if self.invuln:
            return

        self.health = max(0, self.health - 10)
        self.invuln = 45
        burst(self.x + 90, self.y + 65, ORANGE, 14)

    def draw(self):
        if self.invuln == 0 or self.invuln // 5 % 2 == 0:
            screen.blit(
                JATAYU_IMAGES[self.frame],
                (int(self.x), int(self.y))
            )

        # Jatayu attacks.
        for x, y in self.shots:
            screen.blit(
                FONT.render("==>*", True, ORANGE),
                (int(x), int(y))
            )

        # Sita travels with Jatayu after rescue.
        if self.has_sita:
            text_art(
                screen, SITA_ART,
                self.x + 95, self.y + 70,
                PALE, TINY, 0
            )


# --------------------------------------------------
# RAVANA + CHARIOT
# --------------------------------------------------
class RavanaChariot:
    def __init__(self):
        self.x = 1250
        self.y = H // 2 - 100

        self.shield = 100
        self.phase = 0
        self.direction_timer = 0
        self.attack_clock = 80

        self.shots = []
        self.flash = 0
        self.sita_rescued = False

    def rect(self):
        return pygame.Rect(self.x, self.y, 340, 260)

    def update(self, player):
        self.phase += 0.018
        self.x += math.sin(self.phase) * 0.7
        self.y += math.sin(self.phase * 1.8) * 1.3

        self.x = max(W * 0.65, min(W - 380, self.x))
        self.y = max(130, min(H - 260, self.y))

        self.direction_timer += 1
        if self.direction_timer > 180:
            self.y += random.randint(-80, 80)
            self.direction_timer = 0

        self.attack_clock -= 1
        attack_speed = 35 if self.sita_rescued else 70

        if self.attack_clock <= 0:
            self.fire(player)
            self.attack_clock = attack_speed

        self.flash = max(0, self.flash - 1)

        for shot in self.shots:
            shot[0] += shot[2]
            shot[1] += shot[3]

        self.shots[:] = [
            shot for shot in self.shots
            if -30 < shot[0] < W + 30 and -30 < shot[1] < H + 30
        ]

    def fire(self, player):
        sx = self.x + 100
        sy = self.y + 110

        tx, ty = player.rect().center
        dx = tx - sx
        dy = ty - sy
        length = max(1, math.hypot(dx, dy))

        speed = 6 if self.sita_rescued else 4.5

        self.shots.append([
            sx, sy,
            dx / length * speed,
            dy / length * speed
        ])

        if self.sita_rescued:
            for offset in [-1.2, 1.2]:
                self.shots.append([
                    sx, sy,
                    dx / length * speed,
                    dy / length * speed + offset
                ])

    def take_hit(self):
        if self.shield <= 0:
            return

        self.shield = max(0, self.shield - 10)
        self.flash = 8
        burst(self.x + 150, self.y + 110, PURPLE, 16)

    def draw(self):
        # Chariot shield.
        if self.shield > 0:
            shield_surface = pygame.Surface((360, 280), pygame.SRCALPHA)
            pygame.draw.ellipse(
                shield_surface,
                (130, 100, 255, 30),
                (10, 10, 330, 250),
                3
            )
            screen.blit(shield_surface, (self.x - 10, self.y - 15))

        # Ravana.
        text_art(
            screen,
            RAVANA_ART,
            self.x + 65,
            self.y + 15,
            RED if not self.flash else GOLD,
            SMALL,
            0
        )

        # Sita's glowing magical sphere.
        if not self.sita_rescued:
            draw_sita_glow(screen, self.x + 265, self.y + 155)

        # Ravana's arrows.
        for x, y, _, _ in self.shots:
            screen.blit(
                SMALL.render("<##>", True, RED),
                (int(x), int(y))
            )


# --------------------------------------------------
# COLLISIONS
# --------------------------------------------------
def collisions(jatayu, chariot):
    # Jatayu attacks the chariot.
    for shot in jatayu.shots[:]:
        shot_rect = pygame.Rect(int(shot[0]), int(shot[1]), 55, 22)

        if chariot.rect().colliderect(shot_rect) and chariot.shield > 0:
            jatayu.shots.remove(shot)
            chariot.take_hit()

    # Ravana's arrows hit Jatayu.
    for shot in chariot.shots[:]:
        shot_rect = pygame.Rect(int(shot[0]), int(shot[1]), 38, 18)

        if jatayu.rect().colliderect(shot_rect):
            chariot.shots.remove(shot)
            jatayu.hit()


# --------------------------------------------------
# GAME OBJECTIVE
# --------------------------------------------------
def get_mission(jatayu, chariot):
    if chariot.shield > 0:
        return "MISSION: BREAK THE CHARIOT SHIELD"
    if not jatayu.has_sita:
        return "MISSION: GET CLOSE TO SITA MA AND PRESS E"
    return "MISSION: ESCAPE TO THE SAFE ZONE"


def try_rescue(jatayu, chariot):
    if chariot.shield > 0:
        return

    sita_position = (chariot.x + 265, chariot.y + 155)
    jatayu_position = jatayu.rect().center

    if distance(sita_position, jatayu_position) < 120:
        jatayu.has_sita = True
        chariot.sita_rescued = True
        burst(sita_position[0], sita_position[1], GOLD, 50)


# --------------------------------------------------
# UI
# --------------------------------------------------
def draw_ui(jatayu, chariot):
    title = TITLE.render("JATAYU: THE FINAL FLIGHT", True, GOLD)
    screen.blit(title, (W // 2 - title.get_width() // 2, 15))

    bar(28, 65, 280, 14, jatayu.health, 100, GREEN, "JATAYU HEALTH")
    bar(28, 105, 280, 12, jatayu.stamina, 100, CYAN, "WING STAMINA")
    bar(W - 310, 65, 280, 14, chariot.shield, 100, PURPLE, "CHARIOT SHIELD")

    sita_status = "SAFE WITH JATAYU" if jatayu.has_sita else "NOT RESCUED"
    status_color = GREEN if jatayu.has_sita else RED

    screen.blit(
        SMALL.render(f"SITA MA: {sita_status}", True, status_color),
        (W - 310, 105)
    )

    mission_img = SMALL.render(get_mission(jatayu, chariot), True, PALE)
    screen.blit(
        mission_img,
        (W // 2 - mission_img.get_width() // 2, 100)
    )

    controls = (
        "ARROWS/WASD: FLY   SHIFT: BOOST   "
        "SPACE: ATTACK   E: RESCUE   ESC: QUIT"
    )
    controls_img = SMALL.render(controls, True, CYAN)
    screen.blit(
        controls_img,
        (W // 2 - controls_img.get_width() // 2, H - 27)
    )


# --------------------------------------------------
# SAFE ZONE
# --------------------------------------------------
def draw_safe_zone():
    pygame.draw.rect(screen, (40, 100, 70), (0, 150, 35, H - 220))
    screen.blit(TINY.render("SAFE", True, GREEN), (2, 130))


def reached_safe_zone(jatayu):
    return jatayu.has_sita and jatayu.x < 45


# --------------------------------------------------
# END SCREEN
# --------------------------------------------------
def end_screen(won):
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 215))
    screen.blit(overlay, (0, 0))

    if won:
        lines = [
            "MISSION ACCOMPLISHED!",
            "JATAYU SAVED SITA MA",
            "THE FINAL FLIGHT BECOMES LEGEND"
        ]
        colors = [GOLD, GREEN, WHITE]
    else:
        lines = [
            "JATAYU'S FLIGHT HAS ENDED",
            "RAVANA ESCAPES WITH SITA MA",
            "THE RESCUE MISSION FAILED"
        ]
        colors = [RED, WHITE, RED]

    for i, line in enumerate(lines):
        image = (
            TITLE.render(line, True, colors[i])
            if i == 0
            else SMALL.render(line, True, colors[i])
        )
        screen.blit(
            image,
            (W // 2 - image.get_width() // 2, H // 2 - 55 + i * 42)
        )

    restart = SMALL.render(
        "PRESS R TO FLY AGAIN  |  ESC TO QUIT",
        True,
        CYAN
    )
    screen.blit(
        restart,
        (W // 2 - restart.get_width() // 2, H // 2 + 100)
    )


# --------------------------------------------------
# NEW GAME
# --------------------------------------------------
def new_game():
    global jatayu, chariot, particles
    jatayu = Jatayu()
    chariot = RavanaChariot()
    particles = []


# --------------------------------------------------
# MAIN GAME LOOP
# --------------------------------------------------
new_game()

running = True
game_over = False
won = False

while running:
    clock.tick(FPS)
    update_effects()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_SPACE and not game_over:
                jatayu.attack()

            if event.key == pygame.K_e and not game_over:
                try_rescue(jatayu, chariot)

            if event.key == pygame.K_r and game_over:
                new_game()
                game_over = False
                won = False

    if not game_over:
        keys = pygame.key.get_pressed()
        jatayu.update(keys)
        chariot.update(jatayu)
        collisions(jatayu, chariot)

        if jatayu.health <= 0:
            game_over = True
            won = False
        elif reached_safe_zone(jatayu):
            game_over = True
            won = True

    screen.fill(BLACK)
    draw_effects()

    for i in range(5):
        y = 145 + i * 105
        pygame.draw.line(screen, (17, 21, 34), (0, y), (W, y), 1)

    draw_safe_zone()
    chariot.draw()
    jatayu.draw()
    draw_ui(jatayu, chariot)

    if game_over:
        end_screen(won)

    pygame.display.flip()

pygame.quit()
