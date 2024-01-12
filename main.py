from random import randrange

from PIL import Image, ImageDraw
import pygame
from numpy import sin, cos, tan, arctan, deg2rad, array, random
import numpy
from numba import njit
from numba.typed import List
import sys
import os


class GunTypeWeapon():
    def __init__(self, name, max_reload_timer_value, damage, model_no_shoot, model_shoot, *reload_models):
        self.name = name
        self.model_no_shoot = model_no_shoot
        self.model_shoot = model_shoot
        self.can_shoot = True
        self.reload_timer = 0
        self.max_reload_timer_value = max_reload_timer_value
        self.is_shooting = False
        self.reload_models = reload_models
        self.model = model_no_shoot
        self.damage = damage
        self.clock = pygame.time.Clock()

    def fire(self, map_image, playerAngle, playerViewDepth, playerX, playerY, mapX, mapY):
        if self.can_shoot:
            level_map = map_image.load()
            draw = ImageDraw.Draw(map_image)
            EyeX = sin(playerAngle)
            EyeY = cos(playerAngle)
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
            self.can_shoot = False
            self.set_model(self.model_shoot)
            return level_map

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
        # print(type(self.model), self.model)
        return self.model

    def get_timer(self):
        return self.reload_timer


class LaserTypeWeapon(GunTypeWeapon):
    def __init__(self, name, max_reload_timer_value, damage, model_no_shoot, model_shoot, *reload_models):
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

    def fire(self, map_image, playerAngle, playerViewDepth, playerX, playerY, mapX, mapY):
        if self.can_shoot:
            level_map = map_image.load()
            # last_map = map_image.copy()
            draw = ImageDraw.Draw(map_image)
            # print(type(map_image), type(level_map), type(draw))
            # print(bool(map_image), bool(level_map), bool(draw))
            EyeX = sin(playerAngle)
            EyeY = cos(playerAngle)
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
            laserX = playerX + sin(playerAngle) * 0.5 - 1
            laserY = playerY + cos(playerAngle) * 0.5 - 1
            laserXEnd = RayPointX  # - sin(playerAngle)
            laserYEnd = RayPointY  # - cos(playerAngle)
            # print(laserX, laserY, laserXEnd, laserYEnd)
            draw.line((laserX, laserY, laserXEnd, laserYEnd), fill=(255, 106, 0, 255), width=1)
            # map_image.save(os.join('data', 'laser_shoot.png'))
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


class Creature():
    def __init__(self, creatureX, creatureY, creatureAngle, scale):
        self.creatureX = creatureX
        self.creatureY = creatureY
        self.creatureAngle = creatureAngle
        self.angleDifference = numpy.pi
        self.distanceToPlayer = 999
        self.scale = scale

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
    for d in range(2, int(move_koeff * 10)):
        d /= 10
        if x <= 0 or y <= 0 or x >= mapX or y >= mapY:
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

    return playerX, playerY, playerAngle


@njit()
def islasers(level_map_list):
    for el in level_map_list:
        if (255, 106, 0, 255) in el:
            return True
    return False


def cut_sprite_sheet(file_name, sheetX, sheetY):
    sprite_sheet = pygame.image.load(os.path.join('data', file_name))
    sprites = []
    spriteX = (sheetX // 3)
    spriteY = (sheetY // 4)
    for i in range(3):
        xx = i * spriteX
        sprites.append([])
        for j in range(4):
            yy = j * spriteY
            subsurf = pygame.Surface.subsurface(sprite_sheet, (xx, yy, spriteX, spriteY))
            # subsurf = pygame.transform.scale(subsurf, (spriteX * 10, spriteY * 10))
            sprites[i].append(subsurf)
    print(sprites)
    return sprites


def place_sprites(level_map, mapX, mapY, color, scale_koeff):
    sprites = []
    for enemyX in range(mapX):
        for enemyY in range(mapY):
            if level_map[enemyX, enemyY] == color:
                sprites.append(Creature(enemyX, enemyY, 0, scale_koeff))
    return sprites


def draw_sprites(surface, sprite_sheet, enemies, scrY, scrX, cycle_timer, sprite_img_size, enAngleDiff):
    cycle = int(cycle_timer) % 4
    if cycle == 3:
        cycle = 1
    for en in range(len(enemies)):
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


def main(file, k, walls_texture, floor_textire):
    pygame.init()
    scrX = 1000
    scrY = 700
    screen = pygame.display.set_mode((scrX, scrY))
    im = Image.open(os.path.join('data', file))
    im = im.rotate(90)
    mapX, mapY = im.size
    level_map = im.load()
    playerX = 1
    playerY = 1
    for i in range(mapX):
        for j in range(mapY):
            if level_map[i, j] == (255, 0, 0, 255):
                playerX = i
                playerY = j
    playerAngle = 0
    playerFOV = 60
    playerFOVrad = deg2rad(playerFOV)
    playerViewDepth = 50 * k
    laser_width = 80
    draw = ImageDraw.Draw(im)
    distanceToImage = tan(playerFOVrad / 2) / (scrX // 2)
    lpos = [0, 0]
    pygame.mouse.set_visible(0)
    gun_i = 0
    gun_k = 0
    fps = 40
    clock = pygame.time.Clock()
    clock2 = pygame.time.Clock()
    laser = LaserTypeWeapon('laser', 400, 20, 'laser_gun_no_shoot5.1.png', 'laser_gun_shoot6.png',
                            'laser_gun_no_shoot5.1.png', 'laser_gun_no_shoot5.2.png', 'laser_gun_no_shoot5.3.png',
                            'laser_gun_no_shoot5.4.png')

    horizontalResolution = 120
    HalfOfVerticalResolution = 100
    mod = horizontalResolution // playerFOV
    floor = pygame.surfarray.array3d(pygame.image.load(os.path.join('data', floor_textire)))

    wall = pygame.surfarray.array3d(pygame.image.load(os.path.join('data', walls_texture)))

    # enemies = random.uniform(0, mapX, (10, 4))
    enemies = place_sprites(level_map, mapX, mapY, (255, 216, 0, 255), 5)

    sprite_sheet = cut_sprite_sheet('test_sprites_list.png', 300, 400)

    # sprite = pygame.image.load(os.path.join('data', 'test sprite.png'))
    # sprite_size = numpy.asarray(sprite.get_size())
    # sprite = pygame.transform.scale(sprite, sprite_size * 10)
    # sprite_size = numpy.asarray(sprite.get_size())

    frame = random.uniform(0, 0, (horizontalResolution, HalfOfVerticalResolution * 2, 3))

    move_koeff = k

    draw_floor_and_cellind = False
    level_map_list = PixelAccess_to_list(level_map, (mapX, mapY))
    pygame.event.set_grab(1)
    size = min(mapX, mapY)
    while True:
        cycle_timer = pygame.time.get_ticks()
        y_gun = int(sin(gun_i) * gun_k)
        screen.fill((255, 255, 0))
        clear_lasers = pygame.USEREVENT + 1
        laser_reload = pygame.USEREVENT + 2
        gun_i += 1
        if laser.get_can_shoot():
            pygame.time.set_timer(laser_reload, 0)
        else:
            pygame.time.set_timer(laser_reload, 10)
        if laser.get_laser_list:
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
        for en in range(len(enemies)):
            enx, eny = enemies[en].get_position()
            angle = numpy.arctan((eny - playerY) / (enx - playerX + 0.00001))
            if abs(playerX + cos(angle) - enx) > abs(playerX - enx):
                angle = (angle - numpy.pi) % (2 * numpy.pi)
            angle_difference = (playerAngle - angle) % (2 * numpy.pi)
            if angle_difference > (11 * numpy.pi / 6) or angle_difference < (numpy.pi / 4):
                distanceToSprite = (numpy.sqrt((playerX - enx) ** 2 + (playerY - eny) ** 2)) / k
                enAngleDiff = ((enemies[en].get_angle() - playerAngle - 3 * numpy.pi / 4) % (2 * numpy.pi)) / (numpy.pi / 2)
                enemies[en].set_angleDifference(angle_difference)
                enemies[en].set_distanceToPlayer(1 / distanceToSprite)
                RayX, RayY = enx, eny
                Raykoeff = 0.01
                RayAngleX, RayAngleY = Raykoeff * (playerX - enx) / distanceToSprite, Raykoeff * (
                        playerY - eny) / distanceToSprite
                for i in range(int(distanceToSprite / Raykoeff)):
                    RayX += RayAngleX
                    RayY += RayAngleY
                    if level_map[RayX, RayY] == (0, 0, 0, 255):
                        enemies[en].set_distanceToPlayer(999)
            else:
                enemies[en].set_distanceToPlayer(999)
        enemies.sort(key=lambda enemy: enemy.get_distanceToPlayer())
        surface = draw_sprites(surface, sprite_sheet, enemies, scrY, scrX, cycle_timer, (100, 100), enAngleDiff)
        # print(angle_difference, enx, eny, playerX, playerY)

        screen.blit(surface, (0, 0))

        # end sprites

        draw_lasers = islasers(level_map_list)

        if draw_lasers:
            for x in range(0, scrX, int(k * 2)):
                hitLaser = False
                distanceToLaser = 0
                RayAngle = (playerAngle - playerFOVrad / 2) + (x / scrX) * playerFOVrad
                EyeX = sin(RayAngle)
                EyeY = cos(RayAngle)
                while distanceToLaser < playerViewDepth and not hitLaser:
                    distanceToLaser += 0.3
                    RayPointX = int(playerX + EyeX * distanceToLaser) - 1
                    RayPointY = int(playerY + EyeY * distanceToLaser) - 1
                    if RayPointX < 0 or RayPointX >= mapX or RayPointY < 0 or RayPointY >= mapY or level_map[
                        RayPointX, RayPointY] == (0, 0, 0, 255):
                        break
                    elif level_map[RayPointX, RayPointY] == (255, 106, 0, 255):
                        hitLaser = True

                if hitLaser:
                    hitLaser = True
                    LaserHeight = (laser_width / distanceToLaser)
                    if distanceToLaser == playerViewDepth:
                        LaserHeight = 0

                    r = int(255 - (255 * (distanceToLaser / playerViewDepth) ** 0.75))
                    g = 0
                    b = 0
                    pygame.draw.line(screen, (r, g, b, 100), (x, scrY // 2 + int(LaserHeight / 2)),
                                     (x, scrY // 2 - int(LaserHeight / 2)), width=k * 2)
        gun_image = pygame.image.load(os.path.join('data', laser.get_model()))
        screen.blit(gun_image, (-30, y_gun + 5))
        cross_image = pygame.image.load(os.path.join('data', 'прицел.png'))
        screen.blit(cross_image, (-30, 0))

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
                level_map = laser.clear_laser(im)
                # level_map_list = PixelAccess_to_list(level_map, (mapX, mapY))
            if event.type == laser_reload:
                laser.reload()
            if event.type == pygame.MOUSEBUTTONDOWN and laser.get_can_shoot():
                # l_im = im.copy()
                level_map = laser.fire(im, playerAngle, playerViewDepth, playerX, playerY, mapX, mapY)
                level_map_list = PixelAccess_to_list(level_map, (mapX, mapY))
        clock.tick(fps)
        pygame.display.update()
        pygame.display.flip()


if __name__ == '__main__':
    k = 20
    file = 'map.v14.png'
    walls_texture = 'дерево.png'
    floor_textire = 'дерево.png'
    main(file, k, walls_texture, floor_textire)
