import pygame as pg
import math
from settings import *


class ObjectRenderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.font = pg.font.SysFont('consolas', 22, bold=True)
        self.small_font = pg.font.SysFont('consolas', 16, bold=True)
        self.title_font = pg.font.SysFont('consolas', 28, bold=True)
        self.wall_textures = self.load_wall_textures()
        self.sky_image = self.get_texture('resources/textures/sky.png', (WIDTH, HALF_HEIGHT))
        self.sky_offset = 0
        self.blood_screen = self.get_texture('resources/textures/blood_screen.png', RES)
        self.digit_size = 90
        self.digit_images = [self.get_texture(f'resources/textures/digits/{i}.png', [self.digit_size] * 2)
                             for i in range(11)]
        self.digits = dict(zip(map(str, range(11)), self.digit_images))
        self.game_over_image = self.get_texture('resources/textures/game_over.png', RES)
        self.win_image = self.get_texture('resources/textures/win.png', RES)
        self.vignette = self.build_vignette()
        self.damage_until = 0
        self.hit_until = 0
        self.damage_numbers = []
        self.messages = []
        self.replay_button = pg.Rect(HALF_WIDTH - 145, HALF_HEIGHT + 90, 290, 58)
        
    def draw(self):
        shake = int(self.game.camera_shake)
        if shake:
            self.screen.scroll((shake % 3) - 1, shake % 3 - 1)
        self.draw_background()
        self.draw_pickups()
        self.render_game_objects()
        self.draw_player_health()
        self.draw_crosshair()
        self.draw_damage_feedback()
        self.draw_vignette()
        self.draw_world_feedback()

    def show_message(self, text):
        self.messages.append((text, pg.time.get_ticks() + 1200))

    def draw_world_feedback(self):
        now = pg.time.get_ticks()
        self.messages = [(text, expires) for text, expires in self.messages if expires > now]
        for index, (text, expires) in enumerate(self.messages):
            surface = self.font.render(text, True, (239, 193, 82))
            self.screen.blit(surface, surface.get_rect(center=(HALF_WIDTH, 90 + index * 30)))
        for pos, expires in self.game.object_handler.explosions:
            progress = 1 - max(0, expires - now) / 250
            radius = round(18 + progress * 42)
            pg.draw.circle(self.screen, (255, 165, 40), (HALF_WIDTH, HALF_HEIGHT), radius, 3)

    def draw_pickups(self):
        for pickup in self.game.object_handler.pickups:
            dx = pickup['pos'][0] - self.game.player.x
            dy = pickup['pos'][1] - self.game.player.y
            distance = math.hypot(dx, dy)
            angle = math.atan2(dy, dx) - self.game.player.angle
            angle = (angle + math.pi) % (math.tau) - math.pi
            if distance > 0.4 and abs(angle) < HALF_FOV:
                screen_x = HALF_WIDTH + math.tan(angle) * SCREEN_DIST
                radius = max(4, min(18, int(22 / distance)))
                color = {'health': (205, 48, 35), 'armor': (105, 183, 210), 'ammo': (239, 193, 82)}[pickup['kind']]
                pg.draw.circle(self.screen, color, (round(screen_x), HALF_HEIGHT + 55), radius)

    def draw_pause(self):
        overlay = pg.Surface(RES, pg.SRCALPHA)
        overlay.fill((3, 5, 7, 190))
        self.screen.blit(overlay, (0, 0))
        title = self.title_font.render('MISSION PAUSED', True, (232, 238, 231))
        hint = self.small_font.render('P: RESUME    F1/F2/F3: DIFFICULTY', True, (206, 151, 45))
        self.screen.blit(title, title.get_rect(center=(HALF_WIDTH, HALF_HEIGHT - 35)))
        self.screen.blit(hint, hint.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 20)))

    def win(self):
        self.draw_end_screen('win')

    def game_over(self):
        self.draw_end_screen('game_over')

    def draw_end_screen(self, state):
        self.draw_background()
        self.render_game_objects()
        self.draw_vignette()

        overlay = pg.Surface(RES, pg.SRCALPHA)
        overlay.fill((4, 6, 8, 190))
        self.screen.blit(overlay, (0, 0))

        panel = pg.Rect(HALF_WIDTH - 330, HALF_HEIGHT - 190, 660, 330)
        pg.draw.rect(self.screen, (12, 16, 20), panel)
        pg.draw.rect(self.screen, (121, 137, 140), panel, 2)
        pg.draw.line(self.screen, (206, 151, 45), panel.topleft, (panel.left + 120, panel.top), 4)
        pg.draw.line(self.screen, (206, 151, 45), (panel.right - 120, panel.bottom), panel.bottomright, 4)

        if state == 'win':
            title = 'SECTOR CLEARED'
            subtitle = 'ALL HOSTILES NEUTRALIZED'
            accent = (206, 151, 45)
        else:
            title = 'SIGNAL LOST'
            subtitle = 'VITAL SIGNS CRITICAL'
            accent = (205, 48, 35)
        title_surface = self.title_font.render(title, True, accent)
        subtitle_surface = self.small_font.render(subtitle, True, (174, 185, 184))
        self.screen.blit(title_surface, title_surface.get_rect(center=(HALF_WIDTH, HALF_HEIGHT - 120)))
        self.screen.blit(subtitle_surface, subtitle_surface.get_rect(center=(HALF_WIDTH, HALF_HEIGHT - 82)))

        self.replay_button = pg.Rect(HALF_WIDTH - 145, HALF_HEIGHT + 35, 290, 58)
        pg.draw.rect(self.screen, (174, 125, 39), self.replay_button)
        pg.draw.rect(self.screen, (239, 193, 82), self.replay_button, 2)
        button_text = self.font.render('REPLAY MISSION', True, (15, 17, 18))
        self.screen.blit(button_text, button_text.get_rect(center=self.replay_button.center))
        hint = self.small_font.render('PRESS R OR ENTER', True, (132, 144, 145))
        self.screen.blit(hint, hint.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 120)))

    def draw_intro(self):
        overlay = pg.Surface(RES, pg.SRCALPHA)
        overlay.fill((3, 5, 7, 165))
        self.screen.blit(overlay, (0, 0))

        panel = pg.Rect(HALF_WIDTH - 390, HALF_HEIGHT - 170, 780, 340)
        pg.draw.rect(self.screen, (9, 13, 16), panel)
        pg.draw.rect(self.screen, (126, 139, 139), panel, 2)
        pg.draw.line(self.screen, (206, 151, 45), panel.topleft, (panel.left + 170, panel.top), 4)
        pg.draw.line(self.screen, (205, 48, 35), (panel.right - 170, panel.bottom), panel.bottomright, 4)

        title = self.title_font.render('OPERATION: NIGHTFALL', True, (232, 238, 231))
        subtitle = self.small_font.render('SECTOR 07  /  HOSTILE SIGNALS DETECTED', True, (206, 151, 45))
        controls = self.small_font.render('WASD MOVE     MOUSE AIM     LEFT CLICK FIRE', True, (174, 185, 184))
        prompt = self.font.render('PRESS ENTER TO DEPLOY', True, (239, 193, 82))
        self.screen.blit(title, title.get_rect(center=(HALF_WIDTH, HALF_HEIGHT - 100)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(HALF_WIDTH, HALF_HEIGHT - 52)))
        self.screen.blit(controls, controls.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 8)))
        self.screen.blit(prompt, prompt.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 92)))

    def draw_player_health(self):
        health = max(0, int(self.game.player.health))
        panel = pg.Rect(28, HEIGHT - 92, 310, 64)
        pg.draw.rect(self.screen, (10, 12, 16), panel)
        pg.draw.rect(self.screen, (112, 125, 132), panel, 2)
        pg.draw.line(self.screen, (208, 52, 38), (panel.left, panel.top), (panel.left + 52, panel.top), 3)
        label = self.small_font.render('VITAL SIGNS', True, (155, 168, 172))
        value = self.title_font.render(f'{health:03d}', True, (232, 238, 231))
        self.screen.blit(label, (panel.left + 14, panel.top + 8))
        self.screen.blit(value, (panel.left + 132, panel.top + 4))
        bar = pg.Rect(panel.left + 14, panel.bottom - 14, panel.width - 28, 5)
        pg.draw.rect(self.screen, (51, 58, 61), bar)
        fill = int(bar.width * min(health, PLAYER_MAX_HEALTH) / PLAYER_MAX_HEALTH)
        pg.draw.rect(self.screen, (205, 48, 35) if health < 35 else (206, 151, 45), (bar.left, bar.top, fill, bar.height))

        ammo = self.font.render(f'{self.game.player.shells:02d}', True, (232, 238, 231))
        ammo_label = self.small_font.render('SHELLS', True, (155, 168, 172))
        self.screen.blit(ammo_label, (WIDTH - 125, HEIGHT - 76))
        self.screen.blit(ammo, (WIDTH - 58, HEIGHT - 85))
        armor = self.small_font.render(f'ARMOR {self.game.player.armor:03d}', True, (105, 183, 210))
        self.screen.blit(armor, (panel.left + 14, panel.top - 24))

    def draw_crosshair(self):
        center = (HALF_WIDTH, HALF_HEIGHT)
        color = (218, 224, 211)
        gap = 8
        length = 7
        pg.draw.line(self.screen, color, (center[0] - gap - length, center[1]), (center[0] - gap, center[1]), 2)
        pg.draw.line(self.screen, color, (center[0] + gap, center[1]), (center[0] + gap + length, center[1]), 2)
        pg.draw.line(self.screen, color, (center[0], center[1] - gap - length), (center[0], center[1] - gap), 2)
        pg.draw.line(self.screen, color, (center[0], center[1] + gap), (center[0], center[1] + gap + length), 2)

    def draw_damage_feedback(self):
        now = pg.time.get_ticks()
        active_numbers = []
        for amount, x, y, expires in self.damage_numbers:
            if expires <= now:
                continue
            progress = 1 - (expires - now) / 850
            surface = self.font.render(f'-{amount}', True, (255, 216, 78))
            surface.set_alpha(max(0, int(255 * (1 - progress))))
            self.screen.blit(surface, (x - surface.get_width() // 2, y - int(progress * 55)))
            active_numbers.append((amount, x, y, expires))
        self.damage_numbers = active_numbers
        if self.hit_until > now:
            center = (HALF_WIDTH, HALF_HEIGHT)
            pg.draw.circle(self.screen, (255, 231, 128), center, 18, 2)
            pg.draw.line(self.screen, (255, 231, 128), (center[0] - 28, center[1]), (center[0] - 20, center[1]), 2)
            pg.draw.line(self.screen, (255, 231, 128), (center[0] + 20, center[1]), (center[0] + 28, center[1]), 2)

    def show_damage(self, amount, x, y):
        self.damage_numbers.append((amount, int(x), int(y), pg.time.get_ticks() + 850))
        self.hit_until = pg.time.get_ticks() + 120

    def draw_vignette(self):
        self.screen.blit(self.vignette, (0, 0))
        now = pg.time.get_ticks()
        if self.damage_until > now:
            overlay = pg.Surface(RES, pg.SRCALPHA)
            remaining = self.damage_until - now
            alpha = max(0, min(105, remaining // 2))
            overlay.fill((170, 20, 12, alpha))
            self.screen.blit(overlay, (0, 0))

    @staticmethod
    def build_vignette():
        surface = pg.Surface(RES, pg.SRCALPHA)
        for border in range(220):
            alpha = int(115 * (1 - border / 220) ** 2)
            pg.draw.rect(surface, (0, 0, 0, alpha), (border, border, WIDTH - border * 2, HEIGHT - border * 2), 2)
        return surface

    def player_damage(self):
        self.damage_until = pg.time.get_ticks() + 220

    def draw_background(self):
        self.sky_offset = (self.sky_offset + 4.5 * self.game.player.rel) % WIDTH
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + WIDTH, 0))
        #floor
        pg.draw.rect(self.screen, (22, 25, 27), (0, HALF_HEIGHT, WIDTH, HEIGHT))
        for y in range(HALF_HEIGHT, HEIGHT, 22):
            shade = min(48, 20 + (y - HALF_HEIGHT) // 16)
            pg.draw.line(self.screen, (shade, shade + 2, shade + 3), (0, y), (WIDTH, y), 1)

    def render_game_objects(self):
        list_objects = sorted(self.game.raycasting.objects_to_render, key=lambda t: t[0], reverse=True)
        for depth, image, pos in list_objects:
            self.screen.blit(image, pos)

    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        texture = pg.image.load(resource_path(path)).convert_alpha()
        return pg.transform.smoothscale(texture, res)

    def load_wall_textures(self):
        return {
            1: self.get_texture('resources/textures/1.png'),
            2: self.get_texture('resources/textures/2.png'),
            3: self.get_texture('resources/textures/3.png'),
            4: self.get_texture('resources/textures/4.png'),
            5: self.get_texture('resources/textures/5.png'),
        }