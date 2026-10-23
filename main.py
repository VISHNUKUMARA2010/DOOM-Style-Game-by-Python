import pygame as pg
import sys 
from settings import *
from map import *
from player import *
from raycasting import *
from object_renderer import *
from sprite_object import *
from object_handler import *
from weapon import *
from sound import *
from pathfinding import *


class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)
        self.screen = pg.display.set_mode(RES)
        pg.event.set_grab(True)
        self.clock = pg.time.Clock()
        self.game_state = 'playing'
        self.camera_shake = 0
        self.difficulty = 'MARINE'
        self.paused = False
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        self.new_game()
        self.intro_active = True

    def new_game(self):
        self.game_state = 'playing'
        self.paused = False
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCating(self)
        self.object_handler = ObjectHandler(self)
        self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)
        if self.sound.enabled:
            pg.mixer.music.play(-1)

    def update(self):
        if self.game_state != 'playing' or getattr(self, 'paused', False):
            return
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.weapon.update()
        self.delta_time = self.clock.tick(FPS)
        self.camera_shake = max(0, self.camera_shake - self.delta_time * 0.04)
        pg.display.set_caption(f'{self.clock.get_fps() :.1f}')

    def draw(self):
        if self.game_state == 'playing':
            self.object_renderer.draw()
            self.weapon.draw()
        else:
            self.object_renderer.draw_end_screen(self.game_state)
        if self.intro_active:
            self.object_renderer.draw_intro()
        elif self.paused:
            self.object_renderer.draw_pause()
        # self.map.draw()
        # Self.player.draw()

    def check_event(self):
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN and event.key == pg.K_p:
                self.paused = not self.paused
                pg.mouse.set_visible(self.paused)
                pg.event.set_grab(not self.paused)
                continue
            elif event.type == pg.KEYDOWN and event.key in (pg.K_F1, pg.K_F2, pg.K_F3):
                self.difficulty = {pg.K_F1: 'RECRUIT', pg.K_F2: 'MARINE', pg.K_F3: 'NIGHTMARE'}[event.key]
                self.object_renderer.show_message(f'DIFFICULTY: {self.difficulty}')
                continue
            elif event.type == pg.KEYDOWN and event.key == pg.K_e:
                self.object_handler.interact()
                continue
            elif self.intro_active:
                if event.type == pg.KEYDOWN and event.key in (pg.K_RETURN, pg.K_SPACE):
                    self.intro_active = False
                    pg.mouse.set_visible(False)
                    pg.event.set_grab(True)
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    self.intro_active = False
                    pg.mouse.set_visible(False)
                    pg.event.set_grab(True)
                continue
            elif self.game_state != 'playing':
                if event.type == pg.KEYDOWN and event.key in (pg.K_RETURN, pg.K_r):
                    self.new_game()
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if self.object_renderer.replay_button.collidepoint(event.pos):
                        self.new_game()
                continue
            elif event.type == self.global_event:
                self.global_trigger = True
            self.player.single_fire_event(event)

    def end_game(self, state):
        self.game_state = state
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)

    def run(self):
        while True:
            self.check_event()
            self.update()
            self.draw()
            pg.display.flip()


if __name__ == '__main__':
    game = Game()
    game.run()
