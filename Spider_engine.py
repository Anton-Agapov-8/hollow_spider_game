from random import randrange

from PIL import Image, ImageDraw
import pygame
from numpy import sin, cos, tan, deg2rad, random
import numpy
from numba import njit
from numba.typed import List
import sys
import os


class Weapon():
    def __init__(self, name, max_reload_timer_value, damage, laser_color_on_map, laser_color, model_no_shoot,
                 model_shoot, max_ammo, start_ammo, *reload_models):
        self.name = name
        self.model_no_shoot = model_no_shoot
        self.model_shoot = model_shoot
        self.can_shoot = True
        self.reload_timer = 0
        self.max_reload_timer_value = max_reload_timer_value
        self.is_shooting = False
        self.reload_models = reload_models
        self.lasers_list = []
        self.model = model_no_shoot
        self.damage = damage
        self.clock = pygame.time.Clock()
        self.laser_color_on_map = laser_color_on_map
        self.laser_color = laser_color
        self.max_ammo = max_ammo
        self.ammo = start_ammo
        if not (self.ammo is None):
            if self.ammo <= 0:
                self.isammo = False
            else:
                self.isammo = True
        else:
            self.isammo = True

    def fire(self, map_image, level_map_list, playerAngle, playerViewDepth, playerX, playerY, mapX, mapY, k):
        level_map = map_image.load()
        if not (self.ammo is None):
            if self.ammo <= 0:
                self.isammo = False
            else:
                self.isammo = True
        if self.can_shoot and self.isammo:
            self.reload_timer = 0
            draw = ImageDraw.Draw(map_image)
            color_list = [(0, 0, 0, 255), (128, 128, 128, 255), (127, 0, 55, 255), (64, 64, 64, 255)]
            coord_list = [playerX, playerY]
            d, RayPointX, RayPointY, hitWall = get_distance(level_map_list, mapX, mapY, playerAngle,
                                                            List(coord_list), 100, List(color_list),
                                                            List([(-1, -1), (-1, -1)]))
            laserX = playerX
            laserY = playerY
            laserXEnd = RayPointX - cos(playerAngle) * k
            laserYEnd = RayPointY - sin(playerAngle) * k
            draw.line((laserX, laserY, laserXEnd, laserYEnd), fill=self.laser_color_on_map, width=1)
            # print(f'playerAngle in fire {playerAngle}, laser coords: {(laserX, laserY, laserXEnd, laserYEnd)}')
            self.lasers_list.append([laserX, laserY, laserXEnd, laserYEnd, playerAngle])
            self.can_shoot = False
            if not (self.max_ammo is None or self.ammo is None):
                self.ammo -= 1
            self.set_model(self.model_shoot)
            self.clock.tick()
        return level_map

    def clear_laser(self, map_image):
        draw = ImageDraw.Draw(map_image)
        level_map = map_image.load()
        for i in range(len(self.lasers_list)):
            if self.lasers_list:
                draw.line(
                    (self.lasers_list[i][0], self.lasers_list[i][1], self.lasers_list[i][2], self.lasers_list[i][3]),
                    fill=(255, 255, 255, 255), width=1)
        self.lasers_list = []
        return level_map

    def get_laser_list(self):
        return self.lasers_list

    def reload(self):
        if not (self.ammo is None):
            if self.ammo <= 0:
                self.isammo = False
            else:
                self.isammo = True
        else:
            self.isammo = True
        if self.isammo:
            self.reload_timer += 1
            j = 0
            d = self.max_reload_timer_value // len(self.reload_models)
            if self.clock.tick() > 10 and self.reload_timer < d and not self.can_shoot:
                self.set_model(self.reload_models[1])
            if self.reload_timer > 1:
                for i in range(0, self.max_reload_timer_value, d):
                    if self.reload_timer in [i - d // 2, i, i + d // 2]:
                        try:
                            self.set_model(self.reload_models[j])
                        except(IndexError):
                            self.set_model(self.reload_models[-1])
                    j += 1
                if self.reload_timer >= self.max_reload_timer_value:
                    self.set_model(self.model_no_shoot)
                    self.can_shoot = True
        else:
            self.set_model(self.reload_models[1])

    def get_can_shoot(self):
        return self.can_shoot

    def get_name(self):
        return self.name

    def set_sooting(self, value):
        self.is_shooting = bool(value)

    def set_model(self, new_model):
        self.model = new_model

    def get_model(self):
        return self.model

    def get_timer(self):
        return self.reload_timer

    def get_laser_map_color(self):
        return self.laser_color_on_map

    def get_laser_color(self):
        return self.laser_color

    def get_damage(self):
        return self.damage

    def get_ammo(self):
        return self.ammo

    def get_max_ammo(self):
        return self.max_ammo

    def set_ammo(self, new_ammo):
        self.ammo = new_ammo
        if not (self.ammo is None):
            if self.ammo <= 0:
                self.isammo = False
            else:
                self.isammo = True

    def is_ammmo_weapon(self):
        if self.ammo is None:
            return False
        return True


class HandHitWeapon():
    def __init__(self, name, max_reload_timer_value, damage, hit_color_on_map, model_no_shoot, model_shoot,
                 *reload_models):
        self.name = name
        self.model_no_shoot = model_no_shoot
        self.model_shoot = model_shoot
        self.can_hit = True
        self.reload_timer = 0
        self.max_reload_timer_value = max_reload_timer_value
        self.is_shooting = False
        self.reload_models = reload_models
        self.hits_list = []
        self.model = model_no_shoot
        self.damage = damage
        self.clock = pygame.time.Clock()
        self.laser_color_on_map = hit_color_on_map

    def fire(self, map_image, level_map_list, playerAngle, playerViewDepth, playerX, playerY, mapX, mapY, k):
        if self.can_hit:
            level_map = map_image.load()
            draw = ImageDraw.Draw(map_image)
            k_range = k // 3
            if k_range <= 0:
                k_range = 1
            cosx = cos(playerAngle) * k_range
            siny = sin(playerAngle) * k_range
            hitX = playerX + cosx
            hitY = playerY + siny
            if 0 <= hitX < mapX and 0 <= hitY < mapY and level_map[hitX, hitY] not in [(0, 0, 0, 255),
                                                                                       (64, 64, 64, 255),
                                                                                       (128, 128, 128, 255)] and \
                    level_map[hitX, hitY][3] == 255 and level_map[hitX + cosx, hitY + siny] not in [(0, 0, 0, 255),
                                                                                                    (64, 64, 64, 255),
                                                                                                    (128, 128, 128,
                                                                                                     255)] and \
                    level_map[hitX + cosx, hitY + siny][3] == 255:
                draw.line((hitX, hitY, hitX + cosx, hitY + siny), fill=self.laser_color_on_map, width=1)
                self.hits_list.append([hitX, hitY, hitX + cosx, hitY + siny, playerAngle])
                self.can_hit = False
                self.set_model(self.model_shoot)
                self.clock.tick()
            # map_image.save('after_hit.png')
            return level_map

    def clear_laser(self, map_image):
        draw = ImageDraw.Draw(map_image)
        level_map = map_image.load()
        for i in range(len(self.hits_list)):
            draw.line((self.hits_list[i][0], self.hits_list[i][1], self.hits_list[i][2], self.hits_list[i][3]),
                      fill=(255, 255, 255, 255), width=1)
        self.hits_list = []
        return level_map

    def get_laser_list(self):
        return self.hits_list

    def reload(self):
        self.reload_timer += 1
        j = 0
        d = self.max_reload_timer_value // len(self.reload_models)
        if self.clock.tick() > 10 and self.reload_timer < d and not self.can_hit:
            self.set_model(self.reload_models[1])
        if self.reload_timer > 1:
            for i in range(0, self.max_reload_timer_value, d):
                if self.reload_timer in [i - d // 2, i, i + d // 2]:
                    self.set_model(self.reload_models[j])
                j += 1
        if self.reload_timer >= self.max_reload_timer_value:
            self.set_model(self.model_no_shoot)
            self.reload_timer = 0
            self.can_hit = True

    def get_can_shoot(self):
        return self.can_hit

    def get_name(self):
        return self.name

    def set_sooting(self, value):
        self.is_shooting = bool(value)

    def set_model(self, new_model):
        self.model = new_model

    def get_model(self):
        return self.model

    def get_timer(self):
        return self.reload_timer

    def get_laser_map_color(self):
        return self.laser_color_on_map

    def get_damage(self):
        return self.damage

    def is_ammmo_weapon(self):
        return False


class Creature():
    def __init__(self, creatureX, creatureY, creatureAngle, creatureFOV, damage, reload_time, health, scale,
                 sprite_sheet, dead_sprite, steps_frame_number, k, speed=1):
        self.creatureX = creatureX
        self.creatureY = creatureY
        self.creatureAngle = creatureAngle
        self.creatureFOV = float(creatureFOV)
        self.angleDifference = numpy.pi
        self.distanceToPlayer = 999
        self.scale = scale
        self.sprite_sheet = sprite_sheet
        self.steps_frame_number = steps_frame_number
        self.start_health = health
        self.health = health
        self.dead_sprite = dead_sprite
        self.reload_timer_clock = pygame.time.Clock()
        self.reload_timer = 0
        self.damage = damage
        self.reload_time = reload_time
        self.ammo_for_player = 5
        self.speed = speed * (k / 5)

    def get_scale(self):
        return self.scale

    def get_position(self):
        return self.creatureX, self.creatureY

    def get_angle(self):
        return self.creatureAngle

    def set_angleDifference(self, newAngleDifference):
        self.angleDifference = newAngleDifference

    def set_distanceToPlayer(self, newDistanceToPlayer):
        self.distanceToPlayer = newDistanceToPlayer

    def get_angleDifference(self):
        return self.angleDifference

    def get_distanceToPlayer(self):
        return self.distanceToPlayer

    def get_sprites(self):
        if self.health > 0:
            return self.sprite_sheet
        else:
            return [[self.dead_sprite]]

    def get_steps_frame_number(self):
        return self.steps_frame_number

    def set_health(self, new_health):
        self.health = new_health

    def get_health(self):
        return self.health

    def ai(self, clock_koeff, level_map, map_image, k, mapX, mapY, playerX, playerY, playerHealth):
        # level_map_list = PixelAccess_to_list(level_map, (mapX, mapY))
        seePlayer = check_for_player(playerX, playerY, self.creatureX, self.creatureY, self.creatureAngle,
                                     self.creatureFOV, level_map, mapX, mapY, k)
        if seePlayer:
            self.creatureAngle = numpy.pi + angle_to_player(playerX, playerY, self.creatureX, self.creatureY)
            # print(playerAngle, ' | ', self.creatureAngle)
        move_koeff = self.speed * clock_koeff
        x = self.creatureX + numpy.cos(self.creatureAngle) * move_koeff
        y = self.creatureY + numpy.sin(self.creatureAngle) * move_koeff
        collision_colors = [(0, 0, 0, 255), (128, 128, 128, 255), (64, 64, 64, 255)]
        self.creatureX, self.creatureY, breakReason = collision(x, y, self.creatureX, self.creatureY, move_koeff,
                                                                level_map, mapX, mapY, collision_colors)
        if breakReason == 1:
            if not seePlayer:
                rv = randrange(2)
                if rv == 1:
                    self.creatureAngle = (self.creatureAngle + numpy.pi / 4)
                else:
                    self.creatureAngle = (self.creatureAngle - numpy.pi / 4)
                if self.creatureAngle >= numpy.pi:
                    self.creatureAngle -= numpy.pi * (self.creatureAngle % numpy.pi)
        elif breakReason == 2:
            if not seePlayer:
                rv = randrange(2)
                if rv == 1:
                    self.creatureAngle = (self.creatureAngle + numpy.pi / 4)
                else:
                    self.creatureAngle = (self.creatureAngle - numpy.pi / 4)
                if self.creatureAngle >= numpy.pi:
                    self.creatureAngle -= numpy.pi * (self.creatureAngle % numpy.pi)
        elif breakReason == 3:
            if not seePlayer:
                rv = randrange(2)
                if rv == 1:
                    self.creatureAngle = (self.creatureAngle + numpy.pi / 4)
                else:
                    self.creatureAngle = (self.creatureAngle - numpy.pi / 4)

        k_range = k // 5
        if k_range <= 0:
            k_range = 1
        listx = list(range(int(playerX) - 1 * k_range, int(playerX) + 1 * k_range))
        listy = list(range(int(playerY) - 1 * k_range, int(playerY) + 1 * k_range))
        self.reload_timer += self.reload_timer_clock.tick()
        if int(self.creatureX) in listx and int(self.creatureY) in listy and self.reload_timer > self.reload_time:
            playerHealth -= self.damage
            self.reload_timer = 0
        return playerHealth, map_image.load()

    def get_creatureFOV(self):
        return self.creatureFOV

    def get_ammo_for_player(self):
        return self.ammo_for_player

    def set_ammo_for_player(self, new_ammo):
        self.ammo_for_player = new_ammo


class LaserCreature():
    def __init__(self, creatureX, creatureY, creatureAngle, creatureFOV, damage, reload_time, laser_color_on_map,
                 laser_color, health, scale, sprite_sheet, dead_sprite, steps_frame_number, k, speed=1):
        self.creatureX = creatureX
        self.creatureY = creatureY
        self.creatureAngle = creatureAngle
        self.creatureFOV = float(creatureFOV)
        self.angleDifference = numpy.pi
        self.distanceToPlayer = 999
        self.scale = scale
        self.sprite_sheet = sprite_sheet
        self.steps_frame_number = steps_frame_number
        self.start_health = health
        self.health = health
        self.dead_sprite = dead_sprite
        self.reload_timer_clock = pygame.time.Clock()
        self.reload_timer = 0
        self.lasers_list = []
        self.laser_color_on_map = laser_color_on_map
        self.laser_color = laser_color
        self.damage = damage
        self.reload_time = reload_time
        self.ammo_for_player = 5
        self.speed = speed * (k / 5)

    def get_scale(self):
        return self.scale

    def get_position(self):
        return self.creatureX, self.creatureY

    def get_angle(self):
        return self.creatureAngle

    def set_angleDifference(self, newAngleDifference):
        self.angleDifference = newAngleDifference

    def set_distanceToPlayer(self, newDistanceToPlayer):
        self.distanceToPlayer = newDistanceToPlayer

    def get_angleDifference(self):
        return self.angleDifference

    def get_distanceToPlayer(self):
        return self.distanceToPlayer

    def get_sprites(self):
        if self.health > 0:
            return self.sprite_sheet
        else:
            return [[self.dead_sprite]]

    def get_steps_frame_number(self):
        return self.steps_frame_number

    def set_health(self, new_health):
        self.health = new_health

    def get_health(self):
        return self.health

    def fire(self, map_image, mapX, mapY, level_map_list, k):
        level_map = map_image.load()
        self.reload_timer += self.reload_timer_clock.tick()
        if self.reload_timer > self.reload_time:
            # print(self.reload_timer)
            self.reload_timer = 0
            d = 50
            draw = ImageDraw.Draw(map_image)
            color_list = [(0, 0, 0, 255), (128, 128, 128, 255), (127, 0, 55, 255), (64, 64, 64, 255)]
            coord_list = [self.creatureX, self.creatureY]
            d, RayPointX, RayPointY, hitWall = get_distance(level_map_list, mapX, mapY, self.creatureAngle,
                                                            List(coord_list), 100, List(color_list),
                                                            List([(-1, -1), (-1, -1)]))
            laserX = self.creatureX
            laserY = self.creatureY
            laserXEnd = RayPointX - cos(self.creatureAngle) * k
            laserYEnd = RayPointY - sin(self.creatureAngle) * k
            draw.line((laserX, laserY, laserXEnd, laserYEnd), fill=self.laser_color_on_map, width=1)
            self.lasers_list.append([laserX, laserY, laserXEnd, laserYEnd, self.creatureAngle])
        return level_map

    def ai(self, clock_koeff, level_map, map_image, k, mapX, mapY, playerX, playerY, playerHealth):
        # level_map_list = PixelAccess_to_list(level_map, (mapX, mapY))
        seePlayer = check_for_player(playerX, playerY, self.creatureX, self.creatureY, self.creatureAngle,
                                     self.creatureFOV, level_map, mapX, mapY, k)
        if seePlayer:
            deltaAngle = randrange(-1 * int(numpy.pi), int(numpy.pi)) / 20
            # print(deltaAngle)
            self.creatureAngle = numpy.pi + angle_to_player(playerX, playerY, self.creatureX,
                                                            self.creatureY) + deltaAngle
            # print(playerAngle, ' | ', self.creatureAngle)
            level_map = self.fire(map_image, mapX, mapY, level_map, k)
            for xx in [-1, 0, 1]:
                for yy in [-1, 0, 1]:
                    if 0 <= playerX + xx < mapX and 0 <= playerY + yy < mapY:
                        if level_map[playerX + xx, playerY + yy] == self.laser_color_on_map:
                            playerHealth -= self.damage
            return playerHealth, level_map
        speed = 1
        move_koeff = speed * clock_koeff
        x = self.creatureX + numpy.cos(self.creatureAngle) * move_koeff
        y = self.creatureY + numpy.sin(self.creatureAngle) * move_koeff
        collision_colors = List([(0, 0, 0, 255), (128, 128, 128, 255), (64, 64, 64, 255)])
        self.creatureX, self.creatureY, breakReason = collision(x, y, self.creatureX, self.creatureY, move_koeff,
                                                                level_map, mapX, mapY, collision_colors)
        if breakReason == 1:
            if not seePlayer:
                rv = randrange(2)
                if rv == 1:
                    self.creatureAngle = (self.creatureAngle + numpy.pi / 4)
                else:
                    self.creatureAngle = (self.creatureAngle - numpy.pi / 4)
                if self.creatureAngle >= numpy.pi:
                    self.creatureAngle -= numpy.pi * (self.creatureAngle % numpy.pi)
        elif breakReason == 2:
            if not seePlayer:
                rv = randrange(2)
                if rv == 1:
                    self.creatureAngle = (self.creatureAngle + numpy.pi / 4)
                else:
                    self.creatureAngle = (self.creatureAngle - numpy.pi / 4)
                if self.creatureAngle >= numpy.pi:
                    self.creatureAngle -= numpy.pi * (self.creatureAngle % numpy.pi)
        elif breakReason == 3:
            if not seePlayer:
                rv = randrange(2)
                if rv == 1:
                    self.creatureAngle = (self.creatureAngle + numpy.pi / 4)
                else:
                    self.creatureAngle = (self.creatureAngle - numpy.pi / 4)
        k_range = k // 5
        if k_range <= 0:
            k_range = 1
        listx = list(range(int(playerX) - 1 * k_range, int(playerX) + 1 * k_range))
        listy = list(range(int(playerY) - 1 * k_range, int(playerY) + 1 * k_range))
        level_map = map_image.load()
        return playerHealth, level_map

    def get_creatureFOV(self):
        return self.creatureFOV

    def get_laser_map_color(self):
        return self.laser_color_on_map

    def get_laser_color(self):
        return self.laser_color

    def clear_laser(self, map_image):
        # print('__________________________________________________')
        draw = ImageDraw.Draw(map_image)
        level_map = map_image.load()
        for i in range(len(self.lasers_list)):
            if self.lasers_list:
                draw.line(
                    (self.lasers_list[i][0], self.lasers_list[i][1], self.lasers_list[i][2], self.lasers_list[i][3]),
                    fill=(255, 255, 255, 255), width=1)
                self.lasers_list.remove(self.lasers_list[i])
        return level_map

    def get_laser_list(self):
        return self.lasers_list

    def get_ammo_for_player(self):
        return self.ammo_for_player

    def set_ammo_for_player(self, new_ammo):
        self.ammo_for_player = new_ammo


class Spider():
    def __init__(self, spiderX, spiderY, spiderAngle, scale, sprite_sheet, steps_frame_number, text_list,
                 button_number, give_gun, gun=None):
        self.spiderX = spiderX
        self.spiderY = spiderY
        self.spiderAngle = spiderAngle
        self.angleDifference = numpy.pi
        self.distanceToPlayer = 999
        self.scale = scale
        self.sprite_sheet = sprite_sheet
        self.steps_frame_number = steps_frame_number
        self.text_list = text_list
        self.button_number = button_number
        self.give_gun = give_gun
        self.gun = gun

    def get_scale(self):
        return self.scale

    def get_position(self):
        return self.spiderX, self.spiderY

    def get_angle(self):
        return self.spiderAngle

    def set_angleDifference(self, newAngleDifference):
        self.angleDifference = newAngleDifference

    def set_distanceToPlayer(self, newDistanceToPlayer):
        self.distanceToPlayer = newDistanceToPlayer

    def get_angleDifference(self):
        return self.angleDifference

    def get_distanceToPlayer(self):
        return self.distanceToPlayer

    def get_sprites(self):
        return self.sprite_sheet

    def get_steps_frame_number(self):
        return self.steps_frame_number

    def talk(self, playerX, playerY, button_list, k, screen, weapon_list):
        dist = ((playerX - self.spiderX) ** 2 + (playerY - self.spiderY) ** 2) ** 0.5
        can_talk = False
        # weapon_number = 0
        if dist < k:
            if self.button_number != 255:
                for btn in button_list:
                    if btn.number == self.button_number:
                        if btn.isActive():
                            can_talk = True
            else:
                can_talk = True
            if can_talk:
                for el in self.text_list:
                    talk_in_process = True
                    while talk_in_process:
                        rect = pygame.Rect((0, 0, 1000, 50))
                        screen.fill((64, 64, 64), rect)
                        font = pygame.font.Font(None, 30)
                        text = font.render(el, True, (255, 255, 255))
                        screen.blit(text, (10, 10))
                        for event in pygame.event.get():
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_t:
                                    talk_in_process = False
                        pygame.display.update()
                        pygame.display.flip()
                if self.give_gun:
                    weapon_list.append(self.gun)
                    # weapon_number = -1
        return self.give_gun, weapon_list


class Button():
    def __init__(self, buttonX, buttonY, color):
        self.buttonX = buttonX
        self.buttonY = buttonY
        self.color = color
        self.orientation = color[0]
        self.door_length = color[1]
        self.when_open = color[2]
        self.number = color[3]
        self.activated = False

    def open(self, playerX, playerY, map_image, k, enemies, button_list):
        level_map = map_image.load()
        draw = ImageDraw.Draw(map_image)
        dist = ((playerX - self.buttonX) ** 2 + (playerY - self.buttonY) ** 2) ** 0.5
        can_be_activated = True
        if self.when_open == 0:
            f = pygame.font.Font(None, 1)
            s = f.render(".", True, (0, 0, 0))
            comparizon_creature = LaserCreature(0, 0, 0, deg2rad(60), 40, 80, (255, 100, 0, 255),
                                                (255, 0, 0, 255), 10, 0, s, s, 0, 0)
            comparizon_creature2 = Creature(0, 0, 0, deg2rad(60), 40, 80, 10, 0, s, s, 0, 0)
            for en in enemies:
                if type(en) in [type(comparizon_creature), type(comparizon_creature2)]:
                    if en.get_health() > 0:
                        can_be_activated = False
        elif 0 < self.when_open < 255:
            can_be_activated = False
            for btn in button_list:
                if btn.number == self.when_open:
                    if btn.isActive():
                        can_be_activated = True
        if dist < k and can_be_activated:
            self.activated = True
            if self.orientation == 1:
                sx = self.buttonX - 1
                sy = self.buttonY
                ex = self.buttonX - self.door_length
                ey = self.buttonY
            elif self.orientation == 2:
                sx = self.buttonX
                sy = self.buttonY - 1
                ex = self.buttonX
                ey = self.buttonY - self.door_length
            elif self.orientation == 3:
                sx = self.buttonX + 1
                sy = self.buttonY
                ex = self.buttonX + self.door_length
                ey = self.buttonY
            else:
                sx = self.buttonX
                sy = self.buttonY + 1
                ex = self.buttonX
                ey = self.buttonY + self.door_length
            draw.line((sx, sy, ex, ey), fill=(255, 255, 255, 255), width=1)
        return level_map

    def isActive(self):
        return self.activated


@njit()
def angle_to_player(playerX, playerY, creatureX, creatureY):
    angle = numpy.arctan((creatureY - playerY) / (creatureX - playerX + 0.000001))
    if abs(playerX + numpy.cos(angle) - creatureX) > abs(playerX - creatureX):
        angle = (angle - numpy.pi) % (2 * numpy.pi)
    return angle


def PixelAccess_to_list(PixelAccess, size):
    result = List()
    for i in range(size[0]):
        result.append(List([PixelAccess[i, j] for j in range(size[1])]))
    return result


@njit()
def new_frame(horizontalResolution, HalfOfVerticalResolution, playerX, playerY, playerAngle, level_map, size, mod,
              floor, wall, wall2, buttons, k, frame):
    wall_colors = [(0, 0, 0, 255), (64, 64, 64, 255)]
    for i in range(horizontalResolution):
        playerAngle_i = playerAngle + numpy.deg2rad(i / mod - 30)
        delta_x, delta_y = numpy.cos(playerAngle_i), numpy.sin(playerAngle_i)
        delta_cos = numpy.cos(numpy.deg2rad(i / mod - 30))
        x, y = playerX, playerY
        while level_map[int(x) % size][int(y) % size] not in wall_colors and level_map[int(x) % size][int(y) % size][
            3] == 255:
            x += 0.02 * delta_x * k
            y += 0.02 * delta_y * k
        texture = wall
        if level_map[int(x) % size][int(y) % size][3] < 255:
            texture = buttons
        elif level_map[int(x) % size][int(y) % size] == wall_colors[1]:
            texture = wall2

        n = abs((x - playerX) / delta_x)
        WallHeight = int((HalfOfVerticalResolution * k) / (n * delta_cos + 0.0001))
        xx = int(x % 1 * (100 // k))

        if x % 1 < 0.02 or x % 1 > (4 / k):
            xx = int(y % 1 * (100 // k))

        yy = numpy.linspace(0, 99, WallHeight * 2) % 99
        shade = WallHeight / HalfOfVerticalResolution

        if shade > 1:
            shade = 1

        for pixels in range(WallHeight * 2):
            if 0 < HalfOfVerticalResolution - WallHeight + pixels < 2 * HalfOfVerticalResolution:
                frame[i, HalfOfVerticalResolution - WallHeight + pixels] = shade * texture[xx][
                    int(yy[pixels])] / 255

        for j in range(HalfOfVerticalResolution - WallHeight):
            n = (HalfOfVerticalResolution / (HalfOfVerticalResolution - j)) / delta_cos
            x, y = playerX + delta_x * n * 2, playerY + delta_y * n * 2

            xx, yy = int(x * 2 % 1 * 100), int(y * 2 % 1 * 100)
            shade = (1 - (j / HalfOfVerticalResolution))

            frame[i][HalfOfVerticalResolution * 2 - j - 1] = shade * floor[xx][yy] / 255
            frame[i][j] = shade * floor[xx][yy] / 255
    return frame


@njit()
def collision(x, y, playerX, playerY, move_koeff, level_map, mapX, mapY, collision_colors):
    breakReason = 0
    for d in range(0, int(move_koeff * 50)):
        d /= 50
        if x - d <= 0 or y - d <= 0 or x + d >= mapX - 1 or y + d >= mapY - 1 or playerX - d <= 0 or playerY - d <= 0 or \
                playerX + d >= mapX - 1 or playerY + d >= mapY - 1:
            breakReason = 3
            break
        if not (level_map[int(x - d)][int(y)] in collision_colors or level_map[int(x + d)][
            int(y)] in collision_colors or level_map[int(x)][int(y - d)] in collision_colors or
                level_map[int(x)][int(y + d)] in collision_colors or level_map[int(x - d)][int(y)][3] < 255
                or level_map[int(x + d)][int(y)][3] < 255 or level_map[int(x)][int(y - d)][3] < 255 or
                level_map[int(x)][int(y + d)][3] < 255):
            continue

        elif not (level_map[int(playerX - d)][int(y)] in collision_colors or level_map[int(playerX + d)][
            int(y)] in collision_colors or level_map[int(playerX)][int(y - d)] in collision_colors or
                  level_map[int(playerX)][
                      int(y + d)] in collision_colors or level_map[int(playerX - d)][int(y)][3] < 255 or
                  level_map[int(playerX + d)][
                      int(y)][3] < 255 or level_map[int(playerX)][int(y - d)][3] < 255 or
                  level_map[int(playerX)][
                      int(y + d)][3] < 255):
            breakReason = 1
            break

        elif not (level_map[int(x - d)][int(playerY)] in collision_colors or level_map[int(x + d)][
            int(playerY)] in collision_colors or level_map[int(x)][int(playerY - d)] in collision_colors or
                  level_map[int(x)][
                      int(playerY + d)] in collision_colors or level_map[int(x - d)][int(playerY)][3] < 255 or
                  level_map[int(x + d)][
                      int(playerY)][3] < 255 or level_map[int(x)][int(playerY - d)][3] < 255 or
                  level_map[int(x)][
                      int(playerY + d)][3] < 255):
            breakReason = 2
            break
        else:
            breakReason = 3
            break
    if breakReason == 0:
        return x, y, breakReason
    elif breakReason == 1:
        return playerX, y, breakReason
    elif breakReason == 2:
        return x, playerY, breakReason
    return playerX, playerY, breakReason


def movements(playerX, playerY, playerAngle, move_koeff, clock_koeff, level_map, keys, mapX, mapY):
    move_koeff *= clock_koeff
    x, y = playerX, playerY
    if keys[pygame.K_w]:
        x = playerX + numpy.cos(playerAngle) * move_koeff
        y = playerY + numpy.sin(playerAngle) * move_koeff
    if keys[pygame.K_s]:
        x = playerX - numpy.cos(playerAngle) * move_koeff
        y = playerY - numpy.sin(playerAngle) * move_koeff
    if keys[pygame.K_d]:
        x = playerX - numpy.sin(playerAngle) * move_koeff
        y = playerY + numpy.cos(playerAngle) * move_koeff
    if keys[pygame.K_a]:
        x = playerX + numpy.sin(playerAngle) * move_koeff
        y = playerY - numpy.cos(playerAngle) * move_koeff
    p_mouse = pygame.mouse.get_rel()
    playerAngle += numpy.clip((p_mouse[0]) / 200, -0.2, 0.2)
    collision_colors = List([(0, 0, 0, 255), (128, 128, 128, 255), (64, 64, 64, 255)])
    playerX, playerY, b = collision(x, y, playerX, playerY, move_koeff, level_map, mapX, mapY, collision_colors)
    if playerAngle < 0:
        playerAngle = numpy.pi * 2 + playerAngle
    if playerAngle > numpy.pi * 2:
        playerAngle = playerAngle - numpy.pi * 2
    return playerX, playerY, playerAngle


@njit()
def islasers(level_map_list, color):
    for el in level_map_list:
        if color in el:
            return True
    return False


def cut_sprite_sheet(file_name, sheetX, sheetY, steps_frame_number):
    sprite_sheet = pygame.image.load(os.path.join('data', file_name))
    sprites = []
    spriteX = (sheetX // steps_frame_number)
    spriteY = (sheetY // 4)
    for i in range(steps_frame_number):
        xx = i * spriteX
        sprites.append([])
        for j in range(4):
            yy = j * spriteY
            subsurf = pygame.Surface.subsurface(sprite_sheet, (xx, yy, spriteX, spriteY))
            # subsurf = pygame.transform.scale(subsurf, (spriteX * 10, spriteY * 10))
            sprites[i].append(subsurf)
    print(sprites)
    return sprites


def place_sprites(level_map, mapX, mapY, color1, color1_2, color2, color3, scale_koeff1, scale_koeff2, scale_koeff3,
                  sprite_sheet_wasp, dead_sprite_wasp, sprite_sheet_wasp2, dead_sprite_wasp2, sprite_sheet_scorpion,
                  dead_sprite_scorpion, sprite_sheet_spider, steps_frame_number_wasp, steps_frame_number_scorpion,
                  steps_frame_number_spider, text_list, button_number, give_gun, k, gun=None):
    sprites = []
    for enemyX in range(mapX):
        for enemyY in range(mapY):
            if level_map[enemyX, enemyY] == color1:
                sprites.append(
                    Creature(enemyX, enemyY, 0, deg2rad(30), 20, 100, 10, scale_koeff1, sprite_sheet_wasp,
                             dead_sprite_wasp,
                             steps_frame_number_wasp, k, 2))
            if level_map[enemyX, enemyY] == color1_2:
                sprites.append(
                    Creature(enemyX, enemyY, 0, deg2rad(30), 20, 100, 15, scale_koeff1, sprite_sheet_wasp2,
                             dead_sprite_wasp2,
                             steps_frame_number_wasp, k, 3))
            if level_map[enemyX, enemyY] == color2:
                sprites.append(
                    LaserCreature(enemyX, enemyY, 0, deg2rad(30), 40, 2000, (255, 100, 0, 255),
                                  (255, 0, 0, 255), 20, scale_koeff2, sprite_sheet_scorpion, dead_sprite_scorpion,
                                  steps_frame_number_scorpion, k))
            if level_map[enemyX, enemyY] == color3:
                sprites.append(
                    Spider(enemyX, enemyY, deg2rad(90), scale_koeff3, sprite_sheet_spider, steps_frame_number_spider,
                           text_list, button_number, give_gun, gun))
    return sprites


def draw_sprites(surface, enemies, scrY, scrX, cycle_timer, sprite_img_size, enAngleDiff):
    f = pygame.font.Font(None, 1)
    s = f.render(".", True, (0, 0, 0))
    comparizon_creature = LaserCreature(0, 0, 0, deg2rad(60), 40, 80, (255, 100, 0, 255),
                                        (255, 0, 0, 255), 10, 0, s, s, 0, 0)
    comparizon_creature2 = Creature(0, 0, 0, deg2rad(60), 40, 80, 10, 0, s, s, 0, 0)
    for en in range(len(enemies)):
        # print(type(enemies[en]))
        if type(enemies[en]) in [type(comparizon_creature), type(comparizon_creature2)]:
            if enemies[en].get_health() > 0:
                cycle = int(cycle_timer) % enemies[en].get_steps_frame_number()
            else:
                cycle = 0
                enAngleDiff = 0
        else:
            cycle = int(cycle_timer) % enemies[en].get_steps_frame_number()
        sprite_sheet = enemies[en].get_sprites()
        sprites_scaling = enemies[en].get_scale()
        distance = enemies[en].get_distanceToPlayer()
        if distance > 10:
            break
        sprite_size = sprite_img_size
        antifish = cos(enemies[en].get_angleDifference())
        scaling = (min(distance, 2) / antifish) * sprites_scaling

        vertical = scrY // 2 + (scrY // 2) * (min(distance, 2) / antifish)
        horizontal = (scrX // 2) - scrX * sin(enemies[en].get_angleDifference())
        sprite_im = pygame.transform.scale(sprite_sheet[cycle][int(enAngleDiff)],
                                           (sprite_size[0] * scaling, sprite_size[1] * scaling))
        surface.blit(sprite_im,
                     (horizontal - (sprite_size[0] * scaling) // 2, vertical - (sprite_size[1] * scaling)))
    return surface


@njit()
def check_for_player(playerX, playerY, creatureX, creatureY, creatureAngle, creatureFOV, level_map, mapX, mapY, k):
    distanceToWall = 0
    creatureViewDepth = 20 * k
    hitPlayer = False
    if (abs(playerX - creatureX) ** 2 + abs(playerX - creatureX) ** 2) ** (1 / 2) < 6 * k:
        return True
    for x in range(0, 1000, int(k * 2)):
        angle = (creatureAngle - creatureFOV / 2) + (x / 100) * creatureFOV
        EyeX = cos(angle)
        EyeY = sin(angle)
        distanceToWall = 0
        hitWall = False
        while distanceToWall < creatureViewDepth and not hitWall and not hitPlayer:
            distanceToWall += 0.1
            RayPointX = int(creatureX + EyeX * distanceToWall) - 1
            RayPointY = int(creatureY + EyeY * distanceToWall) - 1
            if RayPointX < 0 or RayPointX >= mapX or RayPointY < 0 or RayPointY >= mapY:
                hitWall = True
            elif level_map[RayPointX][RayPointY] == (0, 0, 0, 255) or level_map[RayPointX][RayPointY] == (
                    128, 128, 128, 255) or level_map[RayPointX][RayPointY] == (
                    64, 64, 64, 255):
                hitWall = True
            elif RayPointX == int(playerX) and RayPointY == int(playerY):
                hitPlayer = True
        if hitPlayer:
            break
    return hitPlayer


@njit()
def get_distance(level_map, mapX, mapY, angle, position, viewDepth, colors, coords):
    EyeX = float(cos(angle))
    EyeY = float(sin(angle))
    distanceToWall = float(0)
    hitWall = False
    x, y = position
    # print(2)
    RayPointX, RayPointY = 0, 0
    while distanceToWall < viewDepth and not hitWall:
        distanceToWall += 0.1
        RayPointX = int(x + EyeX * distanceToWall)
        RayPointY = int(y + EyeY * distanceToWall)
        if RayPointX <= 0 or RayPointX >= mapX - 1 or RayPointY <= 0 or RayPointY >= mapY - 1:
            hitWall = True
            distanceToWall = viewDepth
        elif level_map[RayPointX][RayPointY] in colors or (RayPointX, RayPointY) in coords or \
                level_map[RayPointX][RayPointY][3] < 255:
            hitWall = True
    return distanceToWall, RayPointX, RayPointY, hitWall


def main(file, k, playerAngle, give_gun, weapon_list, gun, laser, text, buttun_number, playerHealth=1500):
    pygame.init()

    walls_texture = 'дерево.png'
    floor_textire = 'дерево.png'
    buttons_texture = 'button.png'
    buttons_background_texture = 'button_background.png'
    walls2_texture = 'button_background.png'

    scrX = 1000
    scrY = 700
    screen = pygame.display.set_mode((scrX, scrY))
    im = Image.open(os.path.join('data', file))
    # im = im.rotate(90)
    mapX, mapY = im.size
    level_map = im.load()
    playerX = 1
    playerY = 1
    button_list = []
    for i in range(mapX):
        for j in range(mapY):
            if level_map[i, j] == (255, 0, 0, 255):
                playerX = i
                playerY = j
            if level_map[i, j][3] < 255:
                button_list.append(Button(i, j, level_map[i, j]))
    # playerAngle = 0
    playerFOV = 60
    playerFOVrad = deg2rad(playerFOV)
    playerViewDepth = 100 * k
    laser_width = 120
    draw = ImageDraw.Draw(im)
    distanceToImage = tan(playerFOVrad / 2) / (scrX // 2)
    lpos = [0, 0]
    pygame.mouse.set_visible(0)
    gun_i = 0
    gun_k = 0
    fps = 100
    clock = pygame.time.Clock()
    clock2 = pygame.time.Clock()
    clock_en = pygame.time.Clock()

    horizontalResolution = 120
    HalfOfVerticalResolution = 100
    mod = horizontalResolution // playerFOV

    floor = pygame.surfarray.array3d(pygame.image.load(os.path.join('data', floor_textire)))
    wall = pygame.surfarray.array3d(pygame.image.load(os.path.join('data', walls_texture)))
    wall2 = pygame.surfarray.array3d(pygame.image.load(os.path.join('data', walls2_texture)))

    buttons_surf = pygame.image.load(os.path.join('data', buttons_texture))
    buttons_surf = pygame.transform.scale(buttons_surf, (100 // k, 100 // k))
    buttons_texture = pygame.image.load(os.path.join('data', buttons_background_texture))
    buttons_texture = buttons_texture.convert_alpha()
    buttons_texture = pygame.transform.scale(buttons_texture, (100 // k, 100))
    buttons_texture.blit(buttons_surf, (0, 50 - (100 // (k * 2))))

    buttons = pygame.surfarray.array3d(buttons_texture)

    # weapon_list = [hands]  # , gun, laser

    sprite_sheet = cut_sprite_sheet('wasp_sheet2.png', 400, 1001, 2)
    sprite_sheet2 = cut_sprite_sheet('wasp_sheet_b.png ', 800, 2002, 2)
    sprite_sheet_scorp = cut_sprite_sheet('scorpion_sheet.png', 1940, 1660, 4)
    sprite_sheet_spider = cut_sprite_sheet('spider_sheet2.png', 300, 1912, 1)
    dead_sprite = pygame.image.load(os.path.join('data', 'wasp_dead.png'))
    dead_sprite2 = pygame.image.load(os.path.join('data', 'wasp_dead_b.png'))
    dead_sprite_scorp = pygame.image.load(os.path.join('data', 'scorpion_dead.png'))
    enemies = place_sprites(level_map, mapX, mapY, (255, 216, 0, 255), (255, 216, 106, 255), (0, 255, 0, 255),
                            (0, 255, 255, 255), 5, 4.5, 5, sprite_sheet, dead_sprite, sprite_sheet2, dead_sprite2,
                            sprite_sheet_scorp, dead_sprite_scorp, sprite_sheet_spider, 2, 4, 1, text,
                            buttun_number, give_gun, k, gun)

    frame = random.uniform(0, 0, (horizontalResolution, HalfOfVerticalResolution * 2, 3))

    move_koeff = k

    draw_floor_and_cellind = False
    # print(0)
    level_map_list = PixelAccess_to_list(level_map, (mapX, mapY))
    # print(1)
    pygame.event.set_grab(1)
    size = min(mapX, mapY)
    # playerHealth = 1000

    comparizon_creature = LaserCreature(0, 0, 0, deg2rad(60), 40, 80, (255, 100, 0, 255),
                                        (255, 0, 0, 255), 10, 0, sprite_sheet, dead_sprite, 0, 0)
    comparizon_creature2 = Creature(0, 0, 0, deg2rad(60), 40, 80, 10, 0, sprite_sheet, dead_sprite, 0, 0)
    # print(type(comparizon_creature))
    clear_events = []
    # print(enemies)
    enemies2 = enemies.copy()
    for en in range(len(enemies)):
        if type(enemies[en]) == type(comparizon_creature):
            clear_events.append([pygame.USEREVENT + 2 + en, en])
            # print(en)
            # type(enemies[en])
    weapon = ''
    if weapon_list:
        weapon = weapon_list[0]
    bullet_img = pygame.image.load(os.path.join('data', 'bullet_image.png'))
    while True:
        # draw.line((playerX, playerY, playerX, playerY), fill=(106, 0, 255, 255), width=1)
        # print(playerHealth)
        cycle_timer = pygame.time.get_ticks() / 200
        y_gun = int(sin(gun_i) * gun_k)
        screen.fill((255, 255, 0))
        clear_lasers = pygame.USEREVENT + 1
        laser_reload = pygame.USEREVENT + 2
        gun_i += 1
        if weapon:
            if weapon.get_can_shoot():
                pygame.time.set_timer(laser_reload, 0)
            else:
                pygame.time.set_timer(laser_reload, 10)
            if weapon.get_laser_list:
                pygame.time.set_timer(clear_lasers, 50)
            else:
                pygame.time.set_timer(clear_lasers, 0)
        if draw_floor_and_cellind:
            for i in range(horizontalResolution):
                playerAngle_i = playerAngle + numpy.deg2rad(i / mod - 30)
                delta_x, delta_y = numpy.cos(playerAngle_i), numpy.sin(playerAngle_i)
                delta_cos = numpy.cos(numpy.deg2rad(i / mod - 30))
                for j in range(HalfOfVerticalResolution):
                    n = (HalfOfVerticalResolution / (HalfOfVerticalResolution - j)) / delta_cos
                    x, y = playerX + delta_x * n, playerY + delta_y * n
                    xx, yy = int(x * 2 % 1 * 100), int(y * 2 % 1 * 100)

                    shade = 0.2 + 0.8 * (1 - (j / HalfOfVerticalResolution))

                    frame[i][HalfOfVerticalResolution * 2 - j - 1] = shade * floor[xx][yy] / 255
                    frame[i][j] = shade * floor[xx][yy] / 255

            surface = pygame.surfarray.make_surface(frame * 255)
            surface = pygame.transform.scale(surface, (scrX, scrY))
            screen.blit(surface, (0, 0))
        # print('start')
        frame = new_frame(horizontalResolution, HalfOfVerticalResolution, playerX, playerY, playerAngle, level_map_list,
                          size, mod, floor, wall, wall2, buttons, k, frame)
        # print('done')
        surface = pygame.surfarray.make_surface(frame * 255)
        surface = pygame.transform.scale(surface, (scrX, scrY))

        # sprites:
        enAngleDiff = 0
        clock_koeff_en = clock_en.tick() / 500
        # enemies_pos_list = []
        for i in range(len(clear_events)):
            if enemies2[clear_events[i][1]].get_laser_list:
                pygame.time.set_timer(clear_events[i][0], 10)
            else:
                pygame.time.set_timer(clear_events[i][0], 0)
        pygame.time.set_timer(laser_reload, 10)
        wall_colors = [(0, 0, 0, 255), (64, 64, 64, 255)]
        for en in range(len(enemies)):
            enx, eny = enemies[en].get_position()
            angle = numpy.arctan((eny - playerY) / (enx - playerX + 0.00001))
            if abs(playerX + cos(angle) - enx) > abs(playerX - enx):
                angle = (angle - numpy.pi) % (2 * numpy.pi)
            angle_difference = (playerAngle - angle) % (2 * numpy.pi)
            if angle_difference > (11 * numpy.pi / 6) or angle_difference < (numpy.pi / 4):
                distanceToSprite = (numpy.sqrt((playerX - enx) ** 2 + (playerY - eny) ** 2)) / k
                enAngleDiff = ((enemies[en].get_angle() - playerAngle - 3 * numpy.pi / 4) % (2 * numpy.pi)) / (
                        numpy.pi / 2)
                enemies[en].set_angleDifference(angle_difference)
                enemies[en].set_distanceToPlayer(1 / distanceToSprite)
                RayX, RayY = enx, eny
                Raykoeff = 0.01
                RayAngleX, RayAngleY = Raykoeff * (playerX - enx) / distanceToSprite, Raykoeff * (
                        playerY - eny) / distanceToSprite
                for i in range(int(distanceToSprite / Raykoeff)):
                    RayX += RayAngleX
                    RayY += RayAngleY
                    # print(enx, eny)
                    if type(enemies[en]) in [type(comparizon_creature), type(comparizon_creature2)]:
                        if level_map[RayX, RayY] in wall_colors:
                            enemies[en].set_distanceToPlayer(999)
                    else:
                        if level_map[RayX, RayY] in wall_colors or level_map[RayX, RayY] == (128, 128, 128, 255):
                            enemies[en].set_distanceToPlayer(999)
            else:
                enemies[en].set_distanceToPlayer(999)
            if type(enemies[en]) in [type(comparizon_creature), type(comparizon_creature2)]:
                if enemies[en].get_health() > 0:
                    playerHealth, level_map = enemies[en].ai(clock_koeff_en, level_map_list, im, k, mapX, mapY, playerX,
                                                             playerY, playerHealth)
                    level_map_list = PixelAccess_to_list(level_map, (mapX, mapY))

                else:
                    if int(playerX) == int(enemies[en].get_position()[0]) and int(playerY) == int(
                            enemies[en].get_position()[1]):
                        if type(enemies[en]) == type(comparizon_creature):
                            have_laser = False
                            if weapon_list:
                                for el in weapon_list:
                                    name = el.get_name()
                                    if name == 'laser':
                                        have_laser = True
                                        break
                            if not have_laser:
                                weapon_list.append(laser)
                                weapon = weapon_list[-1]
                        if weapon:
                            if weapon.is_ammmo_weapon():
                                if enemies[en].get_ammo_for_player():
                                    if weapon.get_ammo() < weapon.get_max_ammo():
                                        if enemies[en].get_ammo_for_player() > (
                                                weapon.get_max_ammo() - weapon.get_ammo()):
                                            weapon.set_ammo(weapon.get_max_ammo())
                                            enemies[en].set_ammo_for_player(
                                                enemies[en].get_ammo_for_player() - (
                                                        weapon.get_max_ammo() - weapon.get_ammo()))
                                        else:
                                            weapon.set_ammo(weapon.get_ammo() + enemies[en].get_ammo_for_player())
                                            enemies[en].set_ammo_for_player(0)
        enemies.sort(key=lambda enemy: enemy.get_distanceToPlayer())
        surface = draw_sprites(surface, enemies, scrY, scrX, cycle_timer, (100, 100), enAngleDiff)
        # print(angle_difference, enx, eny, playerX, playerY)

        screen.blit(surface, (0, 0))

        # end sprites
        en_laser_map_color = laser.get_laser_map_color()
        en_laser_color = laser.get_laser_color()
        draw_lasers = False
        draw_lasers1 = islasers(level_map_list, laser.get_laser_map_color())
        for en in range(len(enemies)):
            if type(enemies[en]) == type(comparizon_creature):
                en_laser_map_color = enemies[en].get_laser_map_color()
                en_laser_color = enemies[en].get_laser_color()
                draw_lasers = islasers(level_map_list, enemies[en].get_laser_map_color())
        if draw_lasers1:
            draw_lasers = draw_lasers1

        if draw_lasers:
            for x in range(0, scrX, int(k * 2)):
                hitLaser = False
                distanceToLaser = 0
                RayAngle = (playerAngle - playerFOVrad / 2) + (x / scrX) * playerFOVrad
                EyeX = cos(RayAngle)
                EyeY = sin(RayAngle)
                while distanceToLaser < playerViewDepth and not hitLaser:
                    distanceToLaser += 0.3
                    RayPointX = int(playerX + EyeX * distanceToLaser)
                    RayPointY = int(playerY + EyeY * distanceToLaser)
                    if RayPointX < 0 or RayPointX >= mapX or RayPointY < 0 or RayPointY >= mapY or level_map[
                        RayPointX, RayPointY] == (0, 0, 0, 255):
                        break
                    elif level_map[RayPointX, RayPointY] == laser.get_laser_map_color() or level_map[
                        RayPointX, RayPointY] == en_laser_map_color:
                        hitLaser = True
                if hitLaser:
                    LaserHeight = (laser_width / distanceToLaser)
                    # print(RayPointX, RayPointY)
                    if distanceToLaser >= playerViewDepth:
                        LaserHeight = 0
                        # print(1)
                    if level_map_list[RayPointX][RayPointY] == en_laser_map_color:
                        rgb = en_laser_color
                        # print(0)
                    else:
                        rgb = laser.get_laser_color()

                    r = int(rgb[0] - (rgb[0] * (distanceToLaser / playerViewDepth) ** 0.75))
                    g = int(rgb[1] - (rgb[1] * (distanceToLaser / playerViewDepth) ** 0.75))
                    b = int(rgb[2] - (rgb[2] * (distanceToLaser / playerViewDepth) ** 0.75))
                    if LaserHeight:
                        pygame.draw.line(screen, (r, g, b, 255), (x, scrY // 2 + int(LaserHeight / 2)),
                                         (x, scrY // 2 - int(LaserHeight / 2)), width=k * 2)

        keys = pygame.key.get_pressed()
        clock_koeff = clock2.tick() / 500
        playerX, playerY, playerAngle = movements(playerX, playerY, playerAngle, move_koeff, clock_koeff,
                                                  level_map_list, keys, mapX, mapY)
        if not (keys[pygame.K_d] or keys[pygame.K_a] or keys[pygame.K_w] or keys[pygame.K_s]):
            gun_k = 0
            gun_i = 0
        else:
            gun_k = 5
        if keys[pygame.K_ESCAPE]:
            im.save('after_esc.png')
            # return False, screen, weapon_list
            pause = True
            pygame.mouse.set_visible(1)
            pygame.event.set_grab(0)
            surf_scr = screen.copy()
            pos = [0, 0]
            while pause:
                screen.blit(surf_scr, (0, 0))
                button_menu = pygame.image.load(os.path.join('data', 'button_menu.png'))
                button_continue = pygame.image.load(os.path.join('data', 'button_continue.png'))
                font = pygame.font.Font(None, 75)
                text = font.render("ПАУЗА", True, (255, 100, 100))
                text_x = 1000 // 2 - text.get_width() // 2
                text_y = 700 // 2 - text.get_height() // 2
                screen.blit(text, (text_x, text_y))
                # font = pygame.font.Font(None, 30)
                # text = font.render("Нажмите любую клавишу, чтобы продолжить.", True, (100, 255, 100))
                # text_x = 1000 // 2 - text.get_width() // 2
                # text_y = 700 // 2 - text.get_height() // 2 + 40
                # screen.blit(text, (text_x, text_y))
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        pause = False
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = event.pos
                        if 220 <= pos[0] <= 420 and 500 <= pos[1] <= 550:
                            return -1, screen, weapon_list
                        if 520 <= pos[0] <= 720 and 500 <= pos[1] <= 550:
                            pause = False
                    elif event.type == pygame.MOUSEMOTION:
                        pos = event.pos
                if 220 <= pos[0] <= 420 and 500 <= pos[1] <= 550:
                    button_menu = pygame.image.load(os.path.join('data', 'button_menu_b.png'))
                if 520 <= pos[0] <= 720 and 500 <= pos[1] <= 550:
                    button_continue = pygame.image.load(os.path.join('data', 'button_continue_b.png'))
                screen.blit(button_menu, (220, 500))
                screen.blit(button_continue, (520, 500))
                pygame.display.update()
            pygame.mouse.set_visible(0)
            pygame.event.set_grab(1)
        if keys[pygame.K_1]:
            if weapon_list:
                weapon = weapon_list[0]
        if keys[pygame.K_2]:
            if len(weapon_list) > 1:
                weapon = weapon_list[1]
        if keys[pygame.K_3]:
            if len(weapon_list) > 2:
                weapon = weapon_list[2]
        if keys[pygame.K_e]:
            for en in enemies:
                if type(en) not in [type(comparizon_creature), type(comparizon_creature2)]:
                    give, weap_l = en.talk(playerX, playerY, button_list, k, screen, weapon_list)
                    if give:
                        weapon_list = weap_l
                        if weapon_list:
                            weapon = weapon_list[-1]
            for el in button_list:
                level_map = el.open(playerX, playerY, im, k, enemies, button_list)
            level_map_list = PixelAccess_to_list(level_map, (mapX, mapY))
        p_mouse = pygame.mouse.get_rel()
        playerAngle += numpy.clip((p_mouse[0]) / 200, -0.2, .2)
        for event in pygame.event.get():
            if event.type == clear_lasers:
                if weapon:
                    level_map = weapon.clear_laser(im)
            for i in range(len(clear_events)):
                if event.type == clear_events[i][0]:
                    enemies2[clear_events[i][1]].clear_laser(im)
            if weapon:
                if event.type == laser_reload:
                    weapon.reload()
                if event.type == pygame.MOUSEBUTTONDOWN and weapon.get_can_shoot():
                    # l_im = im.copy()
                    # print(f'playerAngle in main {playerAngle}')
                    level_map = weapon.fire(im, level_map_list, playerAngle, playerViewDepth, playerX, playerY, mapX,
                                            mapY, k)
                    level_map_list = PixelAccess_to_list(level_map, (mapX, mapY))
                    for en in range(len(enemies)):
                        if type(enemies[en]) in [type(comparizon_creature), type(comparizon_creature2)]:
                            en_pos = enemies[en].get_position()
                            breaked = False
                            # print(enemies[en].get_health())
                            k_range = list(range(-k // 5, k // 5))
                            if len(k_range) <= 1:
                                k_range = range(-1, 1)
                            for xx in k_range:
                                for yy in k_range:
                                    if 0 <= en_pos[0] + xx < mapX and 0 <= en_pos[1] + yy < mapY:
                                        # print(level_map[en_pos[0] + xx, en_pos[1] + yy])
                                        if level_map[en_pos[0] + xx, en_pos[1] + yy] == weapon.get_laser_map_color():
                                            enemies[en].set_health(enemies[en].get_health() - weapon.get_damage())
                                            breaked = True
                                            break
                                if breaked:
                                    break

                # draw.line((playerX, playerY, playerX, playerY),
                #           fill=(255, 106, 106, 255), width=1)
        image = pygame.image.load(os.path.join('data', 'health.png'))
        screen.blit(image, (0, 0))
        if playerHealth > 0:
            pygame.draw.line(screen, (255, 0, 0, 255), (60, 20), (60 + (playerHealth // 10), 20), width=10)
        if weapon:
            gun_image = pygame.image.load(os.path.join('data', weapon.get_model()))
            if weapon.get_name() != 'gun':
                screen.blit(gun_image, (-30, y_gun + 5))
            else:
                screen.blit(gun_image, (-30, y_gun + 5 + 30))
        col = screen.get_at((530, 350))
        m_col = max(col[0], col[1], col[2])
        if m_col > 128:
            cross_image = pygame.image.load(os.path.join('data', 'прицел.png'))
        else:
            cross_image = pygame.image.load(os.path.join('data', 'прицел_w.png'))
        screen.blit(cross_image, (-30, 0))
        if weapon:
            if weapon.is_ammmo_weapon():
                # print(0)
                ammo_font = pygame.font.Font(None, 40)
                ammo_val = ammo_font.render(str(weapon.get_ammo()), True, (255, 170, 0))
                screen.blit(bullet_img, (10, scrY - 200))
                screen.blit(ammo_val, (50, scrY - 190))

        if playerHealth < 0:
            return False, screen, weapon_list
        if level_map[playerX, playerY] == (127, 0, 55, 255):
            return True, screen, weapon_list
        clock.tick(fps)
        pygame.display.update()
        pygame.display.flip()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    # k = 20
    # file = 'map.v15.png'
    k = 5
    file = 'lvl1.5.png'
    pygame.init()
    laser = Weapon('laser', 400, 20, (255, 106, 0, 255), (255, 0, 0, 255), 'laser_gun_no_shoot5.1.png',
                   'laser_gun_shoot6.png', None, None, 'laser_gun_no_shoot5.1.png', 'laser_gun_no_shoot5.2.png',
                   'laser_gun_no_shoot5.3.png', 'laser_gun_no_shoot5.4.png')
    gun = Weapon('gun', 120, 5, (255, 16, 0, 255), (0, 0, 0, 0), 'spider_gun_no_shoot_f6.png',
                 'spider_gun_shoot.2.png', 10, 10, 'spider_gun_no_shoot_f0.2.png', 'spider_gun_no_shoot_f1.png',
                 'spider_gun_no_shoot_f2.png', 'spider_gun_no_shoot_f3.png', 'spider_gun_no_shoot_f4.png',
                 'spider_gun_no_shoot_f5.png', 'spider_gun_no_shoot_f6.png')
    hands = HandHitWeapon('hands', 40, 5, (0, 0, 255, 255), 'spider_hands_no_hit2.png',
                          'spider_hands_hit2.png', 'spider_hands_no_hit2.png', 'spider_hands_no_hit2.png')
    screen = pygame.display.set_mode((1000, 700))
    weapon_list = [hands, gun]
    give_gun = True
    result, surf, weapon_list = main(file, k, deg2rad(270), give_gun, weapon_list, gun, laser, ['Spider', 'Wasp'], 100)
    if result != -1:
        running = True
        screen.blit(surf, (0, 0))
        while running:
            if result:
                font = pygame.font.Font(None, 75)
                text = font.render("Вы выиграли!", True, (0, 255, 100))
                text_x = 1000 // 2 - text.get_width() // 2
                text_y = 700 // 2 - text.get_height() // 2
                screen.blit(text, (text_x, text_y))
            else:
                font = pygame.font.Font(None, 75)
                text = font.render("Вы проиграли!", True, (255, 100, 100))
                text_x = 1000 // 2 - text.get_width() // 2
                text_y = 700 // 2 - text.get_height() // 2
                screen.blit(text, (text_x, text_y))
            font = pygame.font.Font(None, 40)
            text = font.render("Нажмите любую клавишу.", True, (100, 255, 100))
            text_x = 1000 // 2 - text.get_width() // 2
            text_y = 700 // 2 - text.get_height() // 2 + 40
            screen.blit(text, (text_x, text_y))
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    running = False
            pygame.display.update()
            pygame.time.wait(200)
    pygame.quit()
    sys.exit()
