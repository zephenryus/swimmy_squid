import math
import random
from os import path

import pygame

pygame.init()
screen = pygame.display.set_mode((360, 640))
clock = pygame.time.Clock()
running = True
game_over = True

img_dir = path.join(path.dirname(__file__), 'assets')
player_down_img = pygame.image.load(path.join(img_dir, "blooper-down.png")).convert()
player_up_img = pygame.image.load(path.join(img_dir, "blooper-up.png")).convert()
pipe_base_img = pygame.image.load(path.join(img_dir, "pipe-base.png")).convert()
pipe_cap_img = pygame.image.load(path.join(img_dir, "pipe-cap.png")).convert()
wave_img = pygame.image.load(path.join(img_dir, "wave.png")).convert()
floor_img = pygame.image.load(path.join(img_dir, "floor.png")).convert()
seaweed_1_img = pygame.image.load(path.join(img_dir, "sea-weed-1.png")).convert()
seaweed_2_img = pygame.image.load(path.join(img_dir, "sea-weed-2.png")).convert()
seaweed_3_img = pygame.image.load(path.join(img_dir, "sea-weed-3.png")).convert()
seaweed_4_img = pygame.image.load(path.join(img_dir, "sea-weed-4.png")).convert()

all_sprites = pygame.sprite.Group()
tube_sprites = pygame.sprite.Group()
score = 0
waves = []
seaweeds = []
tubes = []
floors = []

distance_between_tubes = 384

up_velocity = 7.5
down_velocity = 0.25

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.vertical_velocity = 0
        self.image = pygame.transform.scale(player_down_img, (32, 32))
        self.image.set_colorkey((255, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.centerx = screen.get_width() // 4
        self.rect.centery = screen.get_height() // 2
        self.radius = 16


player = Player()


def get_random_opening_pos(opening_height):
    return random.randrange(math.floor(opening_height * 1.5),
                            math.floor(screen.get_height() - opening_height * 1.5))


class Tube(pygame.sprite.Sprite):
    def __init__(self, x, opening_pos=0, is_bottom=False):
        pygame.sprite.Sprite.__init__(self)
        self.rect = None
        self.image = None
        self.width = 64
        self.opening_height = 128
        self.is_bottom = is_bottom
        self.opening_pos = opening_pos
        self.player_cleared = False
        self.update_opening_pos(x, opening_pos)

    def update_opening_pos(self, x, opening_pos):
        self.opening_pos = opening_pos
        self.image = pygame.transform.scale(pipe_base_img, self.get_rect())
        self.image.set_colorkey((255, 0, 255))
        self.pipe_cap = pygame.transform.scale(pipe_cap_img, (64, 32))
        pipe_cap_y = 0 if self.is_bottom else self.opening_pos - self.opening_height // 2 - 32
        self.image.blit(self.pipe_cap, (0, pipe_cap_y))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.top = self.opening_pos + self.opening_height // 2 if self.is_bottom else 0
        self.player_cleared = False

    def get_rect(self):
        if not self.is_bottom:
            return self.width, self.opening_pos - self.opening_height // 2
        else:
            return self.width, screen.get_height()


class Wave(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(wave_img, (32, 32))
        self.image.set_colorkey((255, 0, 255))
        self.image.set_alpha(96)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Floor(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(floor_img, (32, 32))
        self.image.set_colorkey((255, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Seaweed(pygame.sprite.Sprite):
    def __init__(self, x, y, animation_frame=0):
        pygame.sprite.Sprite.__init__(self)
        self.images = [
            seaweed_1_img,
            seaweed_2_img,
            seaweed_3_img,
            seaweed_4_img
        ]
        self.animation_frame = animation_frame
        self.image = pygame.transform.scale(seaweed_1_img, (32, 64))
        self.image.set_colorkey((255, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        now = pygame.time.get_ticks() // 500 % len(self.images)
        self.image = pygame.transform.scale(self.images[now], (32, 64))
        self.image.set_colorkey((255, 0, 255))


def show_game_over_screen():
    waiting = True
    start_waiting = pygame.time.get_ticks()
    while waiting:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP and pygame.time.get_ticks() - start_waiting >= 1000:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    waiting = False

        for wave in waves:
            wave.rect.x += 2

        if waves[len(waves) - 1].rect.left > screen.get_width():
            offset = waves[len(waves) - 1].rect.right % waves[len(waves) - 1].rect.width
            for index, wave in enumerate(waves):
                wave.rect.x = (index - 1) * 32 + offset

        screen.fill((165, 211, 247))

        all_sprites.draw(screen)

        water_surface = pygame.Surface((screen.get_width(), screen.get_height()), screen.get_height() - 64)
        water_surface.fill((0, 64, 136))
        water_surface.set_alpha(96)
        screen.blit(water_surface, (0, 64))

        font = pygame.font.Font(pygame.font.match_font("arial"), 24)
        text_surface = font.render("Score:", True, (178, 212, 244))
        text_rect = text_surface.get_rect()
        text_rect.midtop = (screen.get_width() // 2, screen.get_height() // 2 - 16)
        screen.blit(text_surface, text_rect)

        font = pygame.font.Font(pygame.font.match_font("arial"), 36)
        text_surface = font.render(str(score), True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.midtop = (screen.get_width() // 2, screen.get_height() // 2 + 16)
        screen.blit(text_surface, text_rect)

        font = pygame.font.Font(pygame.font.match_font("arial"), 14)
        text_surface = font.render("Press Space or Up to Play", True, (178, 212, 244))
        text_rect = text_surface.get_rect()
        text_rect.midtop = (screen.get_width() // 2, screen.get_height() // 2 + 64)
        screen.blit(text_surface, text_rect)

        pygame.display.flip()


def reset_game():
    global all_sprites
    global tube_sprites
    global player
    global score
    global waves
    global seaweeds
    global tubes
    global floors
    global distance_between_tubes

    all_sprites = pygame.sprite.Group()
    player = Player()
    score = 0

    tubes = []
    tube_sprites = pygame.sprite.Group()
    for index in range(2):
        opening_pos = get_random_opening_pos(128)
        tube_top = Tube(screen.get_width() + 256 + index * distance_between_tubes, opening_pos)
        tube_bottom = Tube(screen.get_width() + 256 + index * distance_between_tubes, opening_pos, True)
        tubes.append({
            "top": tube_top,
            "bottom": tube_bottom
        })
        tube_sprites.add(tube_top)
        tube_sprites.add(tube_bottom)
        all_sprites.add(tube_top)
        all_sprites.add(tube_bottom)

    floors = []

    seaweed_x = 64
    for index in range(4):
        seaweed_x += random.randrange(0, 6) * 32
        seaweed = Seaweed(seaweed_x, screen.get_height() - 96)
        all_sprites.add(seaweed)
        seaweeds.append(seaweed)

    distance_between_tubes = 384
    tubes = []
    tube_sprites = pygame.sprite.Group()
    for index in range(2):
        opening_pos = get_random_opening_pos(128)
        tube_top = Tube(screen.get_width() + 256 + index * distance_between_tubes, opening_pos)
        tube_bottom = Tube(screen.get_width() + 256 + index * distance_between_tubes, opening_pos, True)
        tubes.append({
            "top": tube_top,
            "bottom": tube_bottom
        })
        tube_sprites.add(tube_top)
        tube_sprites.add(tube_bottom)
        all_sprites.add(tube_top)
        all_sprites.add(tube_bottom)

    floors = []

    for index in range(screen.get_width() // 32 + 1):
        floor = Floor(index * 32, screen.get_height() - 32)
        all_sprites.add(floor)
        floors.append(floor)

    all_sprites.add(player)
    waves = []

    for index in range(screen.get_width() // 32 + 2):
        wave = Wave(index * 32, 32)
        all_sprites.add(wave)
        waves.append(wave)


reset_game()

while running:
    if game_over:
        show_game_over_screen()
        reset_game()
        game_over = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                player.vertical_velocity -= up_velocity

    # Update
    position_last_frame = player.rect.y
    player.vertical_velocity += down_velocity
    player.rect.y += player.vertical_velocity

    if player.rect.y < 0 + 16:
        player.rect.y = 0 + 16
        player.vertical_velocity *= -0.4
    if player.rect.y > screen.get_height():
        player.rect.y = screen.get_height()
        game_over = True

    for tube in tubes:
        for tube_pos in tube:
            tube[tube_pos].rect.x -= 3

            if tube[tube_pos].rect.centerx < player.rect.centerx:
                if not tube[tube_pos].player_cleared:
                    score += 1
                    tube["top"].player_cleared = True
                    tube["bottom"].player_cleared = True
                    break

            if tube[tube_pos].rect.x < 0 - tube[tube_pos].width:
                new_opening_pos = get_random_opening_pos(tube["top"].opening_height)
                tube["top"].update_opening_pos(
                    distance_between_tubes * 2 - tube[tube_pos].width,
                    new_opening_pos
                )
                tube["bottom"].update_opening_pos(
                    distance_between_tubes * 2 - tube[tube_pos].width,
                    new_opening_pos
                )
                break

    for wave in waves:
        wave.rect.x -= 2

    if waves[0].rect.left < -waves[0].rect.width:
        offset = waves[0].rect.width - waves[0].rect.x % waves[0].rect.width
        for index, wave in enumerate(waves):
            wave.rect.x = index * 32 + offset

    for floor in floors:
        floor.rect.x -= 3

    if floors[0].rect.left < -floors[0].rect.width:
        for index, floor in enumerate(floors):
            floor.rect.x = index * 32

    for seaweed in seaweeds:
        seaweed.rect.x -= 3
        seaweed.update()

    leftmost_seaweed = min(seaweeds, key=lambda x: x.rect.x)
    rightmost_seaweed = max(seaweeds, key=lambda x: x.rect.x)
    if leftmost_seaweed.rect.left < -leftmost_seaweed.rect.width:
        leftmost_seaweed.rect.x = max(
            screen.get_width() + random.randrange(0, 6) * leftmost_seaweed.rect.width,
            rightmost_seaweed.rect.x + random.randrange(0, 6) * leftmost_seaweed.rect.width
        )

    hits = pygame.sprite.spritecollide(player, tube_sprites, False)
    if hits:
        for hit in hits:
            game_over = True

    # Render
    screen.fill((165, 211, 247))

    if position_last_frame - player.rect.y > -0.9999:
        player.image = pygame.transform.scale(player_up_img, (32, 32))
        player.image.set_colorkey((255, 0, 255))
    else:
        player.image = pygame.transform.scale(player_down_img, (32, 32))
        player.image.set_colorkey((255, 0, 255))

    all_sprites.draw(screen)

    water_surface = pygame.Surface((screen.get_width(), screen.get_height()), screen.get_height() - 64)
    water_surface.fill((0, 64, 136))
    water_surface.set_alpha(96)
    screen.blit(water_surface, (0, 64))

    font = pygame.font.Font(pygame.font.match_font("arial"), 18)
    text_surface = font.render(str(score), True, (255, 255, 255))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (screen.get_width() // 2, 16)
    screen.blit(text_surface, text_rect)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
