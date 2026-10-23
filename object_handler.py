from sprite_object import *
from npc import *
from pathfinding import PathFinding
from random import choices, randrange
import math


class ObjectHandler:
    def __init__(self, game):
        self.game = game
        self.sprite_list = []
        self.npc_list = []
        self.npc_sprite_list = 'resources/sprites/npc/'
        self.static_sprite_path = 'resources/sprites/static_sprites/'
        self.anim_sprite_path = 'resources/sprites/animated_sprites/'
        add_sprite = self.add_sprite
        add_npc = self.add_npc
        self.npc_positions = {}
        self.pickups = [
            {'kind': 'health', 'pos': (2.5, 5.5), 'amount': 25},
            {'kind': 'armor', 'pos': (4.5, 6.5), 'amount': 40},
            {'kind': 'ammo', 'pos': (6.5, 6.5), 'amount': 8},
        ]
        self.doors = {(7, 6): False, (12, 12): False}
        self.switches = {(6.5, 7.5): (7, 6), (11.5, 11.5): (12, 12)}
        self.explosions = []

        # spawn npc
        self.enemies = 20 # npc count
        self.npc_types = [SoldierNPC, CacoDemonNPC, CyberDemonNPC]
        self.weights = [70, 20, 10]
        self.restricted_area = {(i, j) for i in range(10) for j in range(10)}
        self.spawn_npc()

        # sprite map
        add_sprite(AnimatedSprite(game))
        add_sprite(AnimatedSprite(game, pos=(1.5, 1.5)))
        add_sprite(AnimatedSprite(game, pos=(1.5, 7.5)))
        add_sprite(AnimatedSprite(game, pos=(5.5, 3.25)))
        add_sprite(AnimatedSprite(game, pos=(5.5, 4.75)))
        add_sprite(AnimatedSprite(game, pos=(7.5, 2.5)))
        add_sprite(AnimatedSprite(game, pos=(7.5, 5.5)))
        add_sprite(AnimatedSprite(game, pos=(14.5, 1.5)))
        add_sprite(AnimatedSprite(game, pos=(14.5, 4.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 5.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 7.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(12.5, 7.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(9.5, 7.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 12.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(9.5, 20.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(10.5, 20.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(3.5, 14.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(3.5, 18.5)))
        add_sprite(AnimatedSprite(game, pos=(14.5, 24.5)))
        add_sprite(AnimatedSprite(game, pos=(14.5, 30.5)))
        add_sprite(AnimatedSprite(game, pos=(1.5, 30.5)))
        add_sprite(AnimatedSprite(game, pos=(1.5, 24.5)))

        # npc map
        # add_npc(SoldierNPC(game, pos=(11.0, 19.0)))
        # add_npc(SoldierNPC(game, pos=(11.5, 4.5)))
        # add_npc(SoldierNPC(game, pos=(13.5, 6.5)))
        # add_npc(SoldierNPC(game, pos=(2.0, 20.0)))
        # add_npc(SoldierNPC(game, pos=(4.0, 29.0)))
        # add_npc(CacoDemonNPC(game, pos=(5.5, 14.5)))
        # add_npc(CacoDemonNPC(game, pos=(5.5, 16.5)))
        # add_npc(CacoDemonNPC(game, pos=(14.5, 25.5)))

    def spawn_npc(self):
        for i in range(self.enemies):
                npc = choices(self.npc_types, self.weights)[0]
                pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
                while (pos in self.game.map.world_map) or (pos in self.restricted_area):
                    pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
                self.add_npc(npc(self.game, pos=(x + 0.5, y + 0.5)))

    def check_win(self):
        if not len(self.npc_positions):
            self.game.end_game('win')

    def update(self):
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}
        self.update_pickups()
        self.update_explosions()
        [sprite.update() for sprite in self.sprite_list]
        [npc.update() for npc in self.npc_list]
        self.check_win()

    def update_pickups(self):
        player = self.game.player
        remaining = []
        for pickup in self.pickups:
            if math.hypot(player.x - pickup['pos'][0], player.y - pickup['pos'][1]) < 0.65:
                if pickup['kind'] == 'health':
                    player.health = min(PLAYER_MAX_HEALTH, player.health + pickup['amount'])
                elif pickup['kind'] == 'armor':
                    player.armor = min(PLAYER_MAX_ARMOR, player.armor + pickup['amount'])
                else:
                    player.shells = min(MAX_SHELLS, player.shells + pickup['amount'])
                self.game.object_renderer.show_message(f"{pickup['kind'].upper()} +{pickup['amount']}")
            else:
                remaining.append(pickup)
        self.pickups = remaining

    def interact(self):
        player = self.game.player
        for switch_pos, door_pos in self.switches.items():
            if math.hypot(player.x - switch_pos[0], player.y - switch_pos[1]) < 1.2:
                self.doors[door_pos] = True
                self.game.map.world_map.pop(door_pos, None)
                self.game.pathfinding = PathFinding(self.game)

    def add_explosion(self, pos, radius=1.4, damage=25):
        self.explosions.append((pos, pg.time.get_ticks() + 250))
        for npc in self.npc_list:
            distance = math.hypot(npc.x - pos[0], npc.y - pos[1])
            if npc.alive and distance <= radius:
                npc.apply_damage(max(1, int(damage * (1 - distance / radius))))

    def update_explosions(self):
        now = pg.time.get_ticks()
        self.explosions = [explosion for explosion in self.explosions if explosion[1] > now]

    def add_npc(self, npc):
        self.npc_list.append(npc)

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)