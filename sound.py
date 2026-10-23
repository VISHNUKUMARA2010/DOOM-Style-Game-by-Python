import pygame as pg 
from settings import resource_path


class SilentSound:
    def play(self):
        pass


class Sound:
    def __init__(self, game):
        self.game = game
        self.enabled = True
        try:
            if not pg.mixer.get_init():
                pg.mixer.init()
        except pg.error:
            self.enabled = False

        if not self.enabled:
            self.shotgun = SilentSound()
            self.npc_pain = SilentSound()
            self.npc_death = SilentSound()
            self.npc_shot = SilentSound()
            self.player_pain = SilentSound()
            return

        self.path = resource_path('resources/sound')
        self.shotgun = pg.mixer.Sound(self.path + 'shotgun.wav')
        self.npc_pain = pg.mixer.Sound(self.path + 'npc_pain.wav')
        self.npc_death = pg.mixer.Sound(self.path + 'npc_death.wav')
        self.npc_shot = pg.mixer.Sound(self.path + 'npc_attack.wav')
        self.npc_shot.set_volume(0.2)
        self.player_pain = pg.mixer.Sound(self.path + 'player_pain.wav')
        self.theme = pg.mixer.music.load(self.path + 'theme.mp3')
        pg.mixer.music.set_volume(0.3)