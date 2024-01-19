from Spider_engine import main, Weapon, HandHitWeapon

import pygame
from numpy import deg2rad
import sys

k = 5
file = 'level_1.png'
pygame.init()
laser = Weapon('laser', 400, 20, (255, 106, 0, 255), (255, 0, 0, 255), 'laser_gun_no_shoot5.1.png',
               'laser_gun_shoot6.png', None, None, 'laser_gun_no_shoot5.1.png', 'laser_gun_no_shoot5.2.png',
               'laser_gun_no_shoot5.3.png', 'laser_gun_no_shoot5.4.png')
gun = Weapon('gun', 120, 5, (255, 16, 0, 255), (0, 0, 0, 0), 'spider_gun_no_shoot_f6.png',
             'spider_gun_shoot.2.png', 10, 10, 'spider_gun_no_shoot_f0.2.png', 'spider_gun_no_shoot_f1.png',
             'spider_gun_no_shoot_f2.png', 'spider_gun_no_shoot_f3.png', 'spider_gun_no_shoot_f4.png',
             'spider_gun_no_shoot_f5.png', 'spider_gun_no_shoot_f6.png')
hands = HandHitWeapon('hands', 40, 2, (0, 0, 255, 255), 'spider_hands_no_hit2.png',
                      'spider_hands_hit2.png', 'spider_hands_no_hit2.png', 'spider_hands_no_hit2.png')
screen = pygame.display.set_mode((1000, 700))
weapon_list = [hands]
result, surf, weapon_list = main(file, k, 0, weapon_list, gun, laser, [], 101)
k = 10
if result:
    file2 = 'level_2.3.png'
    text = ['Спасибо, что спас меня из клетки.',
            'Я сделал пушку, которая стреляет осколками от этих роботов. Возми её.',
            'Я видел роботов, которые стреляют лазерами. Будь осторожен.']
    result, surf, weapon_list = main(file2, k, 0, weapon_list, gun, laser, text, 101)
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
