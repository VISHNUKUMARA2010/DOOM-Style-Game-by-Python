from sprite_object import *


class Weapon(AnimatedSprite):
    def __init__(self, game, path='resources/sprites/weapon/shotgun/0.png', scale=0.4, animation_time=90):
        super().__init__(game=game, path=path, scale=scale, animation_time=animation_time)
        self.images = deque (
            [pg.transform.smoothscale(img, (self.image.get_width() * scale, self.image.get_height() * scale))
             for img in self.images])
        self.weapon_pos = (HALF_WIDTH - self.images[0].get_width() // 2, HEIGHT - self.images[0].get_height())
        self.reloading = False 
        self.magazine_reload = False
        self.reload_started = 0
        self.muzzle_until = 0
        self.num_images = len(self.images)
        self.frame_counter = 0
        self.damage = 50
        self.base_weapon_pos = self.weapon_pos
        self.bob_time = 0

    def fire(self):
        self.muzzle_until = pg.time.get_ticks() + 90
        self.game.camera_shake = max(self.game.camera_shake, 8)
        self.reloading = True
        self.magazine_reload = False
        self.reload_started = pg.time.get_ticks()

    def start_reload(self):
        if not self.reloading and self.game.player.shells < STARTING_SHELLS:
            self.reloading = True
            self.magazine_reload = True
            self.reload_started = pg.time.get_ticks()

    def animate_shot(self):
        if self.reloading:
            self.game.player.shot = False
            if self.animation_trigger:
                self.images.rotate(-1)
                self.image = self.images[0]
                self.frame_counter += 1
                if self.frame_counter == self.num_images:
                    self.reloading = False
                    self.frame_counter = 0
                    if self.magazine_reload:
                        self.game.player.shells = STARTING_SHELLS
                        self.magazine_reload = False

    def draw(self):
        moving = abs(self.game.player.rel) + int(pg.key.get_pressed()[pg.K_w] or pg.key.get_pressed()[pg.K_s])
        self.bob_time += self.game.delta_time * (0.012 if moving else 0.004)
        bob_x = int(pg.math.Vector2(1, 0).rotate(self.bob_time * 55).x * (3 if moving else 1))
        bob_y = int(abs(pg.math.Vector2(1, 0).rotate(self.bob_time * 55).y) * (3 if moving else 1))
        recoil = -self.frame_counter * 3 if self.reloading else 0
        position = (self.base_weapon_pos[0] + bob_x, self.base_weapon_pos[1] + bob_y + recoil)
        self.game.screen.blit(self.images[0], position)
        if self.muzzle_until > pg.time.get_ticks():
            flash = pg.Surface((180, 180), pg.SRCALPHA)
            pg.draw.polygon(flash, (255, 218, 84, 220), [(90, 0), (125, 65), (180, 90), (125, 115), (90, 180), (55, 115), (0, 90), (55, 65)])
            self.game.screen.blit(flash, (HALF_WIDTH - 90, HEIGHT - 310))

    def update(self):
        self.check_animation_time()
        self.animate_shot()