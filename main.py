from random import randrange

from PIL import Image, ImageDraw
import pygame
from numpy import sin, cos, tan, arctan, deg2rad, array, random
import numpy
from numba import njit
from numba.typed import List
import sys
import os


class Weapon():
    def __init__(self, name, max_reload_timer_value, damage, laser_color_on_map, laser_color, model_no_shoot,
                 model_shoot, *reload_models):
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

    def fire(self, map_image, playerAngle, playerViewDepth, playerX, playerY, mapX, mapY):
        if self.can_shoot:
            level_map = map_image.load()
            draw = ImageDraw.Draw(map_image)
            EyeX = cos(playerAngle)
            EyeY = sin(playerAngle)
            distanceToWall = 0
            hitWall = False
            while distanceToWall < playerViewDepth and not hitWall:
                distanceToWall += 0.1
                RayPointX = int(playerX + EyeX * distanceToWall) - 1
                RayPointY = int(playerY + EyeY * distanceToWall) - 1
                if RayPointX < 0 or RayPointX >= mapX or RayPointY < 0 or RayPointY >= mapY:
                    hitWall = True
                    distanceToWall = playerViewDepth
                elif level_map[RayPointX, RayPointY] == (0, 0, 0, 255) or level_map[RayPointX, RayPointY] == (
                        128, 128, 128, 255):
                    hitWall = True
            laserX = playerX
            laserY = playerY
            laserXEnd = RayPointX
            laserYEnd = RayPointY
            draw.line((laserX, laserY, laserXEnd, laserYEnd), fill=self.laser_color_on_map, width=1)
            # print(f'playerAngle in fire {playerAngle}, laser coords: {(laserX, laserY, laserXEnd, laserYEnd)}')
            self.lasers_list.append([laserX, laserY, laserXEnd, laserYEnd, playerAngle])
            self.can_shoot = False
            self.set_model(self.model_shoot)
            self.clock.tick()
            return level_map

    def clear_laser(self, map_image):
        draw = ImageDraw.Draw(map_image)
        level_map = map_image.load()
        if self.lasers_list:
            draw.line((self.lasers_list[0][0], self.lasers_list[0][1], self.lasers_list[0][2], self.lasers_list[0][3]),
                      fill=(255, 255, 255, 255), width=1)
            self.lasers_list.remove(self.lasers_list[0])
        return level_map

    def get_laser_list(self):
        return self.lasers_list

    def reload(self):
        self.reload_timer += 1
        j = 0
        d = self.max_reload_timer_value // len(self.reload_models)
        if self.clock.tick() > 10 and self.reload_timer < d and not self.can_shoot:
            self.set_model(self.reload_models[1])
        if self.reload_timer > 1:
            for i in range(0, self.max_reload_timer_value, d):
                if self.reload_timer in [i - d // 2, i, i + d // 2]:
                    self.set_model(self.reload_models[j])
                j += 1
            if self.reload_timer >= self.max_reload_timer_value:
                self.set_model(self.model_no_shoot)
                self.reload_timer = 0
                self.can_shoot = True

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

    def fire(self, map_image, playerAngle, playerViewDepth, playerX, playerY, mapX, mapY):
        if self.can_hit:
            level_map = map_image.load()
            draw = ImageDraw.Draw(map_image)
            cosx = cos(playerAngle)
            siny = sin(playerAngle)
            hitX = playerX + cosx
            hitY = playerY + siny
            if 0 <= hitX < mapX and 0 <= hitY < mapY:
                draw.line((hitX, hitY, hitX + cosx, hitY + siny), fill=self.laser_color_on_map, width=1)
                self.hits_list.append([hitX, hitY, hitX + cosx, hitY + siny, playerAngle])
                self.can_hit = False
                self.set_model(self.model_shoot)
                self.clock.tick()
            map_image.save('after_hit.png')
            return level_map

    def clear_laser(self, map_image):
        draw = ImageDraw.Draw(map_image)
        level_map = map_image.load()
        if self.hits_list:
            draw.line((self.hits_list[0][0], self.hits_list[0][1], self.hits_list[0][2], self.hits_list[0][3]),
                      fill=(255, 255, 255, 255), width=1)
            self.hits_list.remove(self.hits_list[0])
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


class Creature():
    def __init__(self, creatureX, creatureY, creatureAngle, creatureFOV, health, scale, sprite_sheet, dead_sprite,
                 steps_frame_number):
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

    def ai(self, clock_koeff, level_map, mapX, mapY, playerX, playerY, playerHealth, playerAngle):
        # level_map_list = PixelAccess_to_list(level_map, (mapX, mapY))
        seePlayer = check_for_player(playerX, playerY, self.creatureX, self.creatureY, self.creatureAngle,
                                     self.creatureFOV, level_map, mapX, mapY, k)
        if seePlayer:
            self.creatureAngle = numpy.pi + angle_to_player(playerX, playerY, self.creatureX, self.creatureY)
            print(playerAngle, ' | ', self.creatureAngle)
        speed = 1
        move_koeff = speed * clock_koeff
        x = self.creatureX + numpy.cos(self.creatureAngle) * move_koeff
        y = self.creatureY + numpy.sin(self.creatureAngle) * move_koeff
        collision_colors = [(0, 0, 0, 255), (128, 128, 128, 255)]
        breakReason = 0
        for d in range(1, int(move_koeff * 20)):
            d /= 20
            if x - d <= 0 or y - d <= 0 or x + d >= mapX - 1 or y + d >= mapY - 1 or self.creatureX - d <= 0 or \
                    self.creatureY - d <= 0 or self.creatureX + d >= mapX - 1 or self.creatureY + d >= mapY - 1:
                breakReason = 3
                break
            if not (level_map[int(x - d)][int(y)] in collision_colors or level_map[int(x + d)][
                int(y)] in collision_colors or level_map[int(x)][int(y - d)] in collision_colors or level_map[int(x)][
                        int(y + d)] in collision_colors):
                continue

            elif not (level_map[int(self.creatureX - d)][int(y)] in collision_colors or
                      level_map[int(self.creatureX + d)][int(y)] in collision_colors or level_map[int(self.creatureX)][
                          int(y - d)] in collision_colors or level_map[int(self.creatureX)][
                          int(y + d)] in collision_colors):
                breakReason = 1
                break

            elif not (level_map[int(x - d)][int(self.creatureY)] in collision_colors or level_map[int(x + d)][
                int(self.creatureY)] in collision_colors or level_map[int(x)][
                          int(self.creatureY - d)] in collision_colors or level_map[int(x)][
                          int(self.creatureY + d)] in collision_colors):
                breakReason = 2
                break
            else:
                breakReason = 3
                break
        if breakReason == 0:
            self.creatureX, self.creatureY = x, y
        elif breakReason == 1:
            if not seePlayer:
                rv = randrange(2)
                if rv == 1:
                    self.creatureAngle = (self.creatureAngle + numpy.pi / 4)
                else:
                    self.creatureAngle = (self.creatureAngle - numpy.pi / 4)
                if self.creatureAngle >= numpy.pi:
                    self.creatureAngle -= numpy.pi * (self.creatureAngle % numpy.pi)
            self.creatureY = y
        elif breakReason == 2:
            if not seePlayer:
                rv = randrange(2)
                if rv == 1:
                    self.creatureAngle = (self.creatureAngle + numpy.pi / 4)
                else:
                    self.creatureAngle = (self.creatureAngle - numpy.pi / 4)
                if self.creatureAngle >= numpy.pi:
                    self.creatureAngle -= numpy.pi * (self.creatureAngle % numpy.pi)
            self.creatureX = x
        elif breakReason == 3:
            if not seePlayer:
                rv = randrange(2)
                if rv == 1:
                    self.creatureAngle = (self.creatureAngle + numpy.pi / 4)
                else:
                    self.creatureAngle = (self.creatureAngle - numpy.pi / 4)
        listx = [int(playerX) - 1, int(playerX), int(playerX) + 1]
        listy = [int(playerY) - 1, int(playerY), int(playerY) + 1]
        if int(self.creatureX) in listx and int(self.creatureY) in listy:
            playerHealth -= 20
        return playerHealth

    def get_creatureFOV(self):
        return self.creatureFOV


@njit()
def angle_to_player(playerX, playerY, creatureX, creatureY):
    angle = numpy.arctan((creatureY - playerY) / (creatureX - playerX))
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
              floor, wall, k, frame):
    for i in range(horizontalResolution):
        playerAngle_i = playerAngle + numpy.deg2rad(i / mod - 30)
        delta_x, delta_y = numpy.cos(playerAngle_i), numpy.sin(playerAngle_i)
        delta_cos = numpy.cos(numpy.deg2rad(i / mod - 30))

        x, y = playerX, playerY
        while level_map[int(x) % size][int(y) % size] != (0, 0, 0, 255):
            x += 0.02 * delta_x * k
            y += 0.02 * delta_y * k

        n = abs((x - playerX) / delta_x)
        WallHeight = int((HalfOfVerticalResolution * k) / (n * delta_cos + 0.0001))
        xx = int(x * 2 % 1 * 100)

        if x % 1 < 0.02 or x % 1 > 0.98:
            xx = int(y * 2 % 1 * 100)

        yy = numpy.linspace(0, 99, WallHeight * 2) % 99
        shade = WallHeight / HalfOfVerticalResolution

        if shade > 1:
            shade = 1

        for pixels in range(WallHeight * 2):
            if 0 < HalfOfVerticalResolution - WallHeight + pixels < 2 * HalfOfVerticalResolution:
                frame[i, HalfOfVerticalResolution - WallHeight + pixels] = shade * wall[xx][
                    int(yy[pixels])] / 255

        for j in range(HalfOfVerticalResolution - WallHeight):
            n = (HalfOfVerticalResolution / (HalfOfVerticalResolution - j)) / delta_cos
            x, y = playerX + delta_x * n * 2, playerY + delta_y * n * 2

            xx, yy = int(x * 2 % 1 * 100), int(y * 2 % 1 * 100)
            shade = (1 - (j / HalfOfVerticalResolution))

            frame[i][HalfOfVerticalResolution * 2 - j - 1] = shade * floor[xx][yy] / 255
            frame[i][j] = shade * floor[xx][yy] / 255
    return frame


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
    collision_colors = [(0, 0, 0, 255), (128, 128, 128, 255)]
    breakReason = 0
    for d in range(1, int(move_koeff * 20)):
        d /= 20
        if x - d <= 0 or y - d <= 0 or x + d >= mapX - 1 or y + d >= mapY - 1 or playerX - d <= 0 or playerY - d <= 0 or \
                playerX + d >= mapX - 1 or playerY + d >= mapY - 1:
            breakReason = 3
            break
        if not (level_map[int(x - d)][int(y)] in collision_colors or level_map[int(x + d)][
            int(y)] in collision_colors or
                level_map[int(x)][int(y - d)] in collision_colors or level_map[int(x)][int(y + d)] in collision_colors):
            continue

        elif not (level_map[int(playerX - d)][int(y)] in collision_colors or level_map[int(playerX + d)][
            int(y)] in collision_colors or level_map[int(playerX)][int(y - d)] in collision_colors or
                  level_map[int(playerX)][
                      int(y + d)] in collision_colors):
            breakReason = 1
            break

        elif not (level_map[int(x - d)][int(playerY)] in collision_colors or level_map[int(x + d)][
            int(playerY)] in collision_colors or level_map[int(x)][int(playerY - d)] in collision_colors or
                  level_map[int(x)][
                      int(playerY + d)] in collision_colors):
            breakReason = 2
            break
        else:
            breakReason = 3
            break
    if breakReason == 0:
        playerX, playerY = x, y
    elif breakReason == 1:
        playerY = y
    elif breakReason == 2:
        playerX = x
    if playerAngle < 0:
        playerAngle = numpy.pi * 2 + playerAngle
    if playerAngle > numpy.pi * 2:
        playerAngle = playerAngle - numpy.pi * 2
    return playerX, playerY, playerAngle


@njit()
def islasers(level_map_list):
    for el in level_map_list:
        if (255, 106, 0, 255) in el:
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


def place_sprites(level_map, mapX, mapY, color, scale_koeff, sprite_sheet, dead_sprite, steps_frame_number):
    sprites = []
    for enemyX in range(mapX):
        for enemyY in range(mapY):
            if level_map[enemyX, enemyY] == color:
                sprites.append(
                    Creature(enemyX, enemyY, 0, deg2rad(60), 10, scale_koeff, sprite_sheet, dead_sprite,
                             steps_frame_number))
    return sprites


def draw_sprites(surface, enemies, scrY, scrX, cycle_timer, sprite_img_size, enAngleDiff):
    for en in range(len(enemies)):
        if enemies[en].get_health() > 0:
            cycle = int(cycle_timer) % enemies[en].get_steps_frame_number()
        else:
            cycle = 0
            enAngleDiff = 0
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
        # print(horizontal, vertical, '|', surface.get_size(), "|", scrX, scrY)
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
    for angle in range(int((creatureAngle - (creatureFOV / 2)) * 100), int((creatureAngle + (creatureFOV / 2)) * 100)):
        angle /= 100
        EyeX = cos(angle)
        EyeY = sin(angle)
        hitWall = False
        while distanceToWall < creatureViewDepth and not hitWall and not hitPlayer:
            distanceToWall += 0.1
            RayPointX = int(creatureX + EyeX * distanceToWall)
            RayPointY = int(creatureY + EyeY * distanceToWall)
            if RayPointX < 0 or RayPointX >= mapX or RayPointY < 0 or RayPointY >= mapY:
                hitWall = True
            elif level_map[RayPointX][RayPointY] == (0, 0, 0, 255) or level_map[RayPointX][RayPointY] == (
                    128, 128, 128, 255):
                hitWall = True
            elif RayPointX == int(playerX) or RayPointY == int(playerY):
                hitPlayer = True
        if hitPlayer:
            break
    return hitPlayer


def main(file, k, walls_texture, floor_textire, playerAngle):
    pygame.init()
    scrX = 1000
    scrY = 700
    screen = pygame.display.set_mode((scrX, scrY))
    im = Image.open(os.path.join('data', file))
    # im = im.rotate(90)
    mapX, mapY = im.size
    level_map = im.load()
    playerX = 1
    playerY = 1
    for i in range(mapX):
        for j in range(mapY):
            if level_map[i, j] == (255, 0, 0, 255):
                playerX = i
                playerY = j
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
    fps = 40
    clock = pygame.time.Clock()
    clock2 = pygame.time.Clock()
    clock_en = pygame.time.Clock()
    laser = Weapon('laser', 400, 20, (255, 106, 0, 255), (255, 0, 0, 255), 'laser_gun_no_shoot5.1.png',
                   'laser_gun_shoot6.png', 'laser_gun_no_shoot5.1.png', 'laser_gun_no_shoot5.2.png',
                   'laser_gun_no_shoot5.3.png', 'laser_gun_no_shoot5.4.png')
    hands = HandHitWeapon('hands', 40, 5, (0, 0, 255, 255), 'spider_hands_no_hit.png',
                          'spider_hands_hit.png', 'spider_hands_no_hit.png', 'spider_hands_no_hit.png')

    horizontalResolution = 120
    HalfOfVerticalResolution = 100
    mod = horizontalResolution // playerFOV
    floor = pygame.surfarray.array3d(pygame.image.load(os.path.join('data', floor_textire)))

    wall = pygame.surfarray.array3d(pygame.image.load(os.path.join('data', walls_texture)))

    sprite_sheet = cut_sprite_sheet('test_sprites_list.png', 300, 400, 3)
    dead_sprite = pygame.image.load(os.path.join('data', 'test sprite_dead.png'))
    enemies = place_sprites(level_map, mapX, mapY, (255, 216, 0, 255), 5, sprite_sheet, dead_sprite, 3)

    frame = random.uniform(0, 0, (horizontalResolution, HalfOfVerticalResolution * 2, 3))

    move_koeff = k

    draw_floor_and_cellind = False
    level_map_list = PixelAccess_to_list(level_map, (mapX, mapY))
    pygame.event.set_grab(1)
    size = min(mapX, mapY)
    playerHealth = 100

    weapon = hands
    while True:
        print(playerHealth)
        cycle_timer = pygame.time.get_ticks() / 200
        y_gun = int(sin(gun_i) * gun_k)
        screen.fill((255, 255, 0))
        clear_lasers = pygame.USEREVENT + 1
        laser_reload = pygame.USEREVENT + 2
        gun_i += 1
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
                          size, mod, floor, wall, k, frame)
        # print('done')
        surface = pygame.surfarray.make_surface(frame * 255)
        surface = pygame.transform.scale(surface, (scrX, scrY))

        # sprites:
        enAngleDiff = 0
        clock_koeff_en = clock_en.tick() / 500
        # enemies_pos_list = []
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
                    if level_map[RayX, RayY] == (0, 0, 0, 255):
                        enemies[en].set_distanceToPlayer(999)
            else:
                enemies[en].set_distanceToPlayer(999)
            if enemies[en].get_health() > 0:
                creatureAngle = enemies[en].get_angle()

                playerHealth = enemies[en].ai(clock_koeff_en, level_map_list, mapX, mapY, playerX, playerY,
                                              playerHealth, playerAngle)
                # enemies_pos_list.append(tuple(map(int, enemies[en].get_position())))
        enemies.sort(key=lambda enemy: enemy.get_distanceToPlayer())
        surface = draw_sprites(surface, enemies, scrY, scrX, cycle_timer, (100, 100), enAngleDiff)
        # print(angle_difference, enx, eny, playerX, playerY)

        screen.blit(surface, (0, 0))

        # end sprites

        draw_lasers = islasers(level_map_list)

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
                    elif level_map[RayPointX, RayPointY] == laser.get_laser_map_color():
                        hitLaser = True

                if hitLaser:
                    hitLaser = True
                    LaserHeight = (laser_width / distanceToLaser)
                    if distanceToLaser == playerViewDepth:
                        LaserHeight = 0
                    rgb = laser.get_laser_color()
                    r = int(rgb[0] - (rgb[0] * (distanceToLaser / playerViewDepth) ** 0.75))
                    g = int(rgb[1] - (rgb[1] * (distanceToLaser / playerViewDepth) ** 0.75))
                    b = int(rgb[2] - (rgb[2] * (distanceToLaser / playerViewDepth) ** 0.75))
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
            pygame.quit()
            sys.exit()
        if keys[pygame.K_1]:
            weapon = hands
        if keys[pygame.K_2]:
            weapon = laser
        if keys[pygame.K_q]:
            if draw_floor_and_cellind:
                draw_floor_and_cellind = False
            else:
                draw_floor_and_cellind = True
        p_mouse = pygame.mouse.get_rel()
        playerAngle += numpy.clip((p_mouse[0]) / 200, -0.2, .2)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == clear_lasers:
                level_map = weapon.clear_laser(im)
            # level_map_list = PixelAccess_to_list(level_map, (mapX, mapY))
            if event.type == laser_reload:
                weapon.reload()
            if event.type == pygame.MOUSEBUTTONDOWN and weapon.get_can_shoot():
                # l_im = im.copy()
                # print(f'playerAngle in main {playerAngle}')
                level_map = weapon.fire(im, playerAngle, playerViewDepth, playerX, playerY, mapX, mapY)
                level_map_list = PixelAccess_to_list(level_map, (mapX, mapY))
                for en in range(len(enemies)):
                    en_pos = enemies[en].get_position()
                    # print(enemies[en].get_health())
                    for xx in [-1, 0, 1]:
                        for yy in [-1, 0, 1]:
                            if 0 <= en_pos[0] + xx < mapX and 0 <= en_pos[1] + yy < mapY:
                                # print(level_map[en_pos[0] + xx, en_pos[1] + yy])
                                if level_map[en_pos[0] + xx, en_pos[1] + yy] == weapon.get_laser_map_color():
                                    enemies[en].set_health(enemies[en].get_health() - weapon.get_damage())
                                draw.line((en_pos[0] + xx, en_pos[1] + yy, en_pos[0] + xx, en_pos[1] + yy),
                                          fill=(255, 0, 106, 255), width=1)

                draw.line((playerX, playerY, playerX, playerY),
                          fill=(255, 106, 106, 255), width=1)
                # im.save('after_shot.png')
                #
                # light_from_laser = pygame.image.load(os.path.join('data', 'laser_shoot_light.png'))
                # screen.blit(light_from_laser, (0, 0))
        gun_image = pygame.image.load(os.path.join('data', weapon.get_model()))
        screen.blit(gun_image, (-30, y_gun + 5))
        cross_image = pygame.image.load(os.path.join('data', 'прицел.png'))
        screen.blit(cross_image, (-30, 0))

        clock.tick(fps)
        pygame.display.update()
        pygame.display.flip()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    # k = 20
    # file = 'map.v15.png'
    k = 5
    file = 'lvl1.png'
    walls_texture = 'дерево.png'
    floor_textire = 'дерево.png'
    main(file, k, walls_texture, floor_textire, deg2rad(270))
