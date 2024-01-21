from Spider_engine import main, Weapon, HandHitWeapon

import pygame
from numpy import deg2rad
import os
import sys


def main_menu():
    pygame.init()
    pygame.mouse.set_visible(1)
    pygame.event.set_grab(0)
    screen = pygame.display.set_mode((1000, 700))
    pos = [0, 0]
    while True:
        menu_picture = pygame.image.load(os.path.join('data', 'main_menu_picture_with_text2.png'))
        button_start = pygame.image.load(os.path.join('data', 'button_start.png'))
        button_tutorial = pygame.image.load(os.path.join('data', 'button_tutorial.png'))
        button_exit = pygame.image.load(os.path.join('data', 'button_exit.png'))
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if 20 <= pos[0] <= 220 and 200 <= pos[1] <= 250:
                    main_game()
                elif 20 <= pos[0] <= 220 and 300 <= pos[1] <= 350:
                    how_to_play()
                elif 20 <= pos[0] <= 220 and 400 <= pos[1] <= 450:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                pos = event.pos
        if 20 <= pos[0] <= 220 and 200 <= pos[1] <= 250:
            button_start = pygame.image.load(os.path.join('data', 'button_start_b.png'))
        elif 20 <= pos[0] <= 220 and 300 <= pos[1] <= 350:
            button_tutorial = pygame.image.load(os.path.join('data', 'button_tutorial_b.png'))
        elif 20 <= pos[0] <= 220 and 400 <= pos[1] <= 450:
            button_exit = pygame.image.load(os.path.join('data', 'button_exit_b.png'))
        screen.blit(menu_picture, (0, 0))
        screen.blit(button_start, (20, 200))
        screen.blit(button_tutorial, (20, 300))
        screen.blit(button_exit, (20, 400))
        pygame.display.update()
        pygame.display.flip()


def how_to_play():
    k = 2
    file = 'studing_map1.png'
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    running = True
    while running:
        screen.fill((64, 64, 64))
        font = pygame.font.Font(None, 30)
        text1 = font.render('Используйте WSAD для перемещения.', True, (255, 255, 255))
        text2 = font.render('Чтобы разговаривать [с пауком] подойдите к нему и нажмите "e".', True, (255, 255, 255))
        text3 = font.render('Чтобы пролистывать фразы при разговоре нажимайте "t".', True, (255, 255, 255))
        text1_x = 1000 // 2 - text1.get_width() // 2
        text2_x = 1000 // 2 - text2.get_width() // 2
        text3_x = 1000 // 2 - text3.get_width() // 2
        text_y = 700 // 2 - text1.get_height() // 2
        texts = [(text1, text1_x, text_y), (text2, text2_x, text_y), (text3, text3_x, text_y)]
        for i in range(len(texts)):
            screen.blit(texts[i][0], (texts[i][1], texts[i][2] - i * 35))

        font = pygame.font.Font(None, 20)
        text = font.render("Нажмите любую клавишу, чтобы продолжить.", True, (100, 255, 100))
        text_x = 1000 // 2 - text.get_width() // 2
        text_y = 700 // 2 - text.get_height() // 2 + 40
        screen.blit(text, (text_x, text_y))
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                running = False
        pygame.display.update()
        pygame.time.wait(200)

    laser = Weapon('laser', 400, 20, (255, 106, 0, 255), (255, 0, 0, 255), 'laser_gun_no_shoot5.1.png',
                   'laser_gun_shoot6.png', None, None, 'laser_gun_no_shoot5.1.png', 'laser_gun_no_shoot5.2.png',
                   'laser_gun_no_shoot5.3.png', 'laser_gun_no_shoot5.4.png')
    gun = Weapon('gun', 120, 5, (255, 16, 0, 255), (0, 0, 0, 0), 'spider_gun_no_shoot_f6.png',
                 'spider_gun_shoot.2.png', 10 ** 3, 10 ** 3, 'spider_gun_no_shoot_f0.2.png',
                 'spider_gun_no_shoot_f1.png',
                 'spider_gun_no_shoot_f2.png', 'spider_gun_no_shoot_f3.png', 'spider_gun_no_shoot_f4.png',
                 'spider_gun_no_shoot_f5.png', 'spider_gun_no_shoot_f6.png')
    hands = HandHitWeapon('hands', 40, 5, (0, 0, 255, 255), 'spider_hands_no_hit2.png',
                          'spider_hands_hit2.png', 'spider_hands_no_hit2.png', 'spider_hands_no_hit2.png')
    text = ['Сзади меня на стене есть красная кнопка.', 'Подойди к ней на нажми на "e", чтобы открыть дверь.',
            'Когда дверь откроется, зайди туда.', 'Каждый уровень основной игры имеет такие двери.',
            'При входе в такую дверь, ты переходишь на следующий уровень.']
    weapon_list = [hands]
    result, surf, weapon_list = main(file, k, deg2rad(-90), False, weapon_list, gun, laser, text, 255)
    if result == -1:
        main_menu()
        pygame.quit()
        sys.exit()
    if result:
        file2 = 'studing_map2.png'
        text = ['Сзади меня стоит клетка с осой.', 'Открой клетку с помощью кнопки и сразись с осой.',
                'Нажимай левую кнопку мыши, чтобы бить.', 'Когда победишь, открой дверь с помощью другой кнопки.',
                'В каждом уровне основной игры нужно уничтожить всех врагов.',
                'Только тогда можно переходить на следующий.']
        result, surf, weapon_list = main(file2, k, deg2rad(-90), False, weapon_list, gun, laser, text, 255)
        if result == -1:
            main_menu()
            pygame.quit()
            sys.exit()
        if result:
            file2 = 'studing_map2.png'
            weapon_list = []
            text = ['А теперь я дам тебе пушку, стреляющую осколками от роботов.',
                    'Нажимай левую кнопку мыши, чтобы стрелять.',
                    'Когда победишь, собери осколки с осы и переходи на следующий этап.']
            result, surf, weapon_list = main(file2, k, deg2rad(-90), True, weapon_list, gun, laser, text, 255)
            if result == -1:
                main_menu()
                pygame.quit()
                sys.exit()
            if result:
                file2 = 'studing_map3.png'
                text = ['Теперь попробуй победить лазерного врага - скорпиона.',
                        'Если победишь его, то сможешь взять его лазерную пушку.',
                        'После этого попробуй лазер на осе, которая находится в другой клетке.',
                        'Если захочишь сменить пушку используй кнопки цифр.']
                result, surf, weapon_list = main(file2, k, deg2rad(-90), False, weapon_list, gun, laser, text, 255)
                if result == -1:
                    main_menu()
                    pygame.quit()
                    sys.exit()
    running = True
    screen.blit(surf, (0, 0))
    while running:
        if result:
            font = pygame.font.Font(None, 75)
            text = font.render("Вы прошли обучение!", True, (0, 255, 100))
            text_x = 1000 // 2 - text.get_width() // 2
            text_y = 700 // 2 - text.get_height() // 2
            screen.blit(text, (text_x, text_y))
        else:
            font = pygame.font.Font(None, 75)
            text = font.render("Попробуйте ещё раз!", True, (255, 100, 100))
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
    main_menu()
    pygame.quit()
    sys.exit()


def main_game():
    k = 5
    file = 'level_1.2.png'
    pygame.init()
    laser = Weapon('laser', 400, 20, (255, 106, 0, 255), (255, 0, 0, 255), 'laser_gun_no_shoot5.1.png',
                   'laser_gun_shoot6.png', None, None, 'laser_gun_no_shoot5.1.png', 'laser_gun_no_shoot5.2.png',
                   'laser_gun_no_shoot5.3.png', 'laser_gun_no_shoot5.4.png')
    gun = Weapon('gun', 120, 5, (255, 16, 0, 255), (0, 0, 0, 0), 'spider_gun_no_shoot_f6.png',
                 'spider_gun_shoot.2.png', 10, 0, 'spider_gun_no_shoot_f0.2.png', 'spider_gun_no_shoot_f1.png',
                 'spider_gun_no_shoot_f2.png', 'spider_gun_no_shoot_f3.png', 'spider_gun_no_shoot_f4.png',
                 'spider_gun_no_shoot_f5.png', 'spider_gun_no_shoot_f6.png')
    hands = HandHitWeapon('hands', 40, 2, (0, 0, 255, 255), 'spider_hands_no_hit2.png',
                          'spider_hands_hit2.png', 'spider_hands_no_hit2.png', 'spider_hands_no_hit2.png')
    screen = pygame.display.set_mode((1000, 700))
    weapon_list = [hands]
    result, surf, weapon_list = main(file, k, 0, True, weapon_list, gun, laser, [], 101)
    if result == -1:
        main_menu()
        pygame.quit()
        sys.exit()
    k = 10
    if result:
        file2 = 'level_2.5.png'
        text = ['Спасибо, что спас меня из клетки.',
                'Я сделал пушку, которая стреляет осколками от этих роботов. Возми её.',
                'Я видел роботов, которые стреляют лазерами. Будь осторожен.']
        result, surf, weapon_list = main(file2, k, 0, True, weapon_list, gun, laser, text, 101)
        if result == -1:
            main_menu()
            pygame.quit()
            sys.exit()
        if result:
            k = 5
            file2 = 'level3.png'
            text = []
            result, surf, weapon_list = main(file2, k, deg2rad(-90), False, weapon_list, gun, laser, text, 101)
            if result == -1:
                main_menu()
                pygame.quit()
                sys.exit()
            if result:
                k = 3
                file2 = 'level4.2.png'
                text = []
                result, surf, weapon_list = main(file2, k, deg2rad(-90), False, weapon_list, gun, laser, text, 101)
                if result == -1:
                    main_menu()
                    pygame.quit()
                    sys.exit()
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
    main_menu()
    pygame.quit()
    sys.exit()


main_menu()
