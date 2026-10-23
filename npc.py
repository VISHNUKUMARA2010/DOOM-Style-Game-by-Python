from sprite_object import *
from random import randint, random


class NPC(AnimatedSprite):
    def __init__(self, game, path='resources/sprites/npc/soldier/0.png', pos=(10.5, 5.5),
                 scale=0.6, shift=0.38, animation_time=180):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_images = self.get_images(self.path + '/attack')
        self.death_images = self.get_images(self.path + '/death')
        self.idle_images = self.get_images(self.path + '/idle')
        self.pain_images = self.get_images(self.path + '/pain')
        self.walk_images= self.get_images(self.path + '/walk')

        self.attack_dist = randint(3, 6)
        self.speed = 0.03
        self.size = 20
        self.health = 100
        self.attack_damage = 10
        self.accuracy = 0.15
        self.alive = True
        self.pain = False
        self.ray_cast_value = False
        self.frame_counter = 0
        self.player_search_trigger = False
        self.cover_pos = None
        self.cover_check_time = 0
        self.last_seen = self.map_pos
        self.search_until = 0
        self.patrol_target = None

    def update(self):
        self.check_animation_time()
        self.get_sprite()
        self.run_logic()
        # Self.draw_ray_cast()

    def check_wall(self, x, y):
        return (x, y) not in self.game.map.world_map

    def check_wall_collision(self, dx, dy):
        if self.check_wall(int(self.x + dx * self.size), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * self.size)):
            self.y += dy

    def movement(self, target=None):
        target = target or self.game.player.map_pos
        next_pos = self.game.pathfinding.get_path(self.map_pos, target)
        next_x, next_y = next_pos

        # pg.draw.rect(self.game.screen, 'blue', (100 * next_x, 100 * next_y, 100, 100))
        if next_pos not in self.game.object_handler.npc_positions:
            angle = math.atan2(next_y + 0.5 - self.y, next_x + 0.5 - self.x)
            dx = math.cos(angle) * self.speed
            dy = math.sin(angle) * self.speed
            self.check_wall_collision(dx, dy)

    def attack(self):
        if self.animation_trigger:
            self.game.sound.npc_shot.play()
            if random() < self.accuracy:
                self.game.player.get_damage(self.attack_damage)

    def animate_death(self):
        if not self.alive:
            if self.game.global_trigger and self.frame_counter < len(self.death_images) - 1:
                self.death_images.rotate(-1)
                self.image = self.death_images[0]
                self.frame_counter += 1

    def animate_pain(self):
        self.animate(self.pain_images)
        if self.animation_trigger:
            self.pain = False

    def check_hit_in_npc(self):
        if self.ray_cast_value and self.game.player.shot:
            if HALF_WIDTH -self.sprite_half_width < self.screen_x < HALF_WIDTH + self.sprite_half_width:
                self.game.sound.npc_pain.play()
                self.game.player.shot = False
                self.pain = True
                self.health -= self.game.weapon.damage
                self.game.object_renderer.show_damage(self.game.weapon.damage, self.screen_x, HALF_HEIGHT - self.sprite_half_width)
                self.check_health()
                self.game.object_handler.add_explosion((self.x, self.y), 1.2, self.game.weapon.damage // 2)

    def check_health(self):
        if self.health < 1:
            self.alive = False
            self.game.sound.npc_death.play()

    def apply_damage(self, damage):
        self.health -= damage
        self.pain = True
        self.check_health()

    def run_logic(self):
        if self.alive:
            self.ray_cast_value = self.ray_cast_player_npc()
            self.check_hit_in_npc()
            now = pg.time.get_ticks()
            if self.ray_cast_value:
                self.last_seen = self.game.player.map_pos
                self.search_until = now + 2400

            if self.pain:
                self.animate_pain()

            elif self.ray_cast_value and self.dist < self.attack_dist:
                self.cover_pos = None
                self.player_search_trigger = True
                self.animate(self.attack_images)
                self.attack()

            elif self.ray_cast_value:
                if self.cover_pos is None or pg.time.get_ticks() > self.cover_check_time:
                    self.cover_pos = self.find_cover()
                    self.cover_check_time = pg.time.get_ticks() + 1200
                self.player_search_trigger = True 
                self.animate(self.walk_images)
                self.movement(self.cover_pos)

            elif self.player_search_trigger:
                if (self.cover_pos == self.map_pos and
                        pg.time.get_ticks() > self.cover_check_time):
                    self.cover_pos = None
                self.animate(self.walk_images)
                self.movement(self.last_seen if now < self.search_until else self.get_patrol_target())

            else:
                self.player_search_trigger = True
                self.animate(self.idle_images)
                self.movement(self.get_patrol_target())
        else:
            self.animate_death()

    @property
    def map_pos(self):
        return int(self.x), int(self.y)

    def ray_cast_player_npc(self):
        player_x, player_y = self.game.player.pos
        distance = math.hypot(self.x - player_x, self.y - player_y)
        if distance == 0:
            return True

        steps = max(1, int(distance / 0.08))
        for step in range(1, steps):
            progress = step / steps
            tile = int(self.x + (player_x - self.x) * progress), int(self.y + (player_y - self.y) * progress)
            if tile in self.game.map.world_map:
                return False
        return True

    def find_cover(self):
        player_pos = self.game.player.map_pos
        candidates = []
        for position in self.game.pathfinding.graph:
            if position in self.game.object_handler.npc_positions or position == self.map_pos:
                continue
            distance = math.hypot(position[0] + 0.5 - self.game.player.x,
                                  position[1] + 0.5 - self.game.player.y)
            if distance > 2 and not self.has_line_of_sight(position, player_pos):
                candidates.append((distance, position))
        return min(candidates, default=(0, None))[1]

    def has_line_of_sight(self, start, goal):
        start_x, start_y = start[0] + 0.5, start[1] + 0.5
        goal_x, goal_y = goal[0] + 0.5, goal[1] + 0.5
        distance = math.hypot(goal_x - start_x, goal_y - start_y)
        steps = max(1, int(distance / 0.08))
        return all((int(start_x + (goal_x - start_x) * step / steps),
                    int(start_y + (goal_y - start_y) * step / steps)) not in self.game.map.world_map
                   for step in range(1, steps))

    def get_patrol_target(self):
        if self.patrol_target not in self.game.pathfinding.graph or self.patrol_target == self.map_pos:
            options = list(self.game.pathfinding.graph)
            self.patrol_target = options[(self.map_pos[0] * 7 + self.map_pos[1] * 13) % len(options)]
        return self.patrol_target

    def draw_ray_cast(self):
        pg.draw.circle(self.game.screen, 'red', (100 * self.x, 100 * self.y), 15)
        if self.ray_cast_player_npc():
            pg.draw.line(self.game.screen, 'orange', (100 * self.game.player.x, 100 * self.game.player.y),
                         (100 * self.x, 100 * self.y), 2)


class SoldierNPC(NPC):
    def __init__(self, game, path='resources/sprites/npc/soldier/0.png', pos=(10.5, 5.5),
                 scale=0.6, shift=0.38, animation_time=180):
        super().__init__(game, path, pos, scale, shift, animation_time)

class CacoDemonNPC(NPC):
    def __init__(self, game, path='resources/sprites/npc/caco_demon/0.png', pos=(10.5, 6.5),
                 scale=0.7, shift=0.27, animation_time=250):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_dist = 1.0
        self.health = 150
        self.attack_damage = 25
        self.speed = 0.05
        self.accuracy = 0.35

class CyberDemonNPC(NPC):
    def __init__(self, game, path='resources/sprites/npc/cyber_demon/0.png', pos=(11.5, 6.0),
                 scale=1.0, shift=0.04, animation_time=210):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_dist = 6
        self.health = 350
        self.attack_damage = 15
        self.speed = 0.055
        self.accuracy = 0.25
        