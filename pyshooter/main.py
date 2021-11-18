from entities import Ship, Missile, Base
from particlesys import ParticleSystem
import ai
from os import path
import pygame
import sys
import copy
from water import Water
from pygame import mixer
WIDTH = 800
HEIGHT = 600
flag=0
screen = pygame.display.set_mode((WIDTH,HEIGHT))
game_folder = path.dirname(__file__)
img_folder = path.join(game_folder,"img")
pygame.init()
mixer.music.load('war-preview-full.wav')
mixer.music.play(-1)
def get_image(filename, colorkey = None):
    img = pygame.image.load(path.join(img_folder,filename)).convert()
    img.set_colorkey(colorkey)
    return img
	
w1 = Water()
def moving_water():
    for i in range(w1.wave_len):
        for j in range(w1.wave_wid):
            screen.blit(w1.W_wave_img[i][j], (w1.W_wave_X[i][j], w1.W_wave_Y[i][j]))
            w1.wave_move()
main_menu_bg = get_image("wp2874399.jpg", 'WHITE')
psys = ParticleSystem()
def text_objects(text,font):
    textsurface = font.render(text,True,'WHITE')
    return textsurface,textsurface.get_rect()
''' Key bindings for both players '''
KEY_BINDINGS_1 = {pygame.K_LEFT: "left",
                pygame.K_RIGHT: "right",
                pygame.K_UP: "up",
                pygame.K_DOWN: "down",
                pygame.K_n: "gun_left",
                pygame.K_COMMA: "gun_right",
                pygame.K_m: "gun_fire"}
KEY_BINDINGS_2 = {pygame.K_a: "left",
                pygame.K_d: "right",
                pygame.K_w: "up",
                pygame.K_s: "down",
                pygame.K_g: "gun_left",
                pygame.K_j: "gun_right",
                pygame.K_h: "gun_fire"}
'''                                '''

input_listener = []
keys_pressed = []

def check_collisions(world, entity,screen):
    for p, e1 in world:
        if e1 != entity and (e1.owner != entity and entity.owner!=e1) and e1.collide_entities(entity):
            if isinstance(e1, Ship):
                if isinstance(entity, Missile):
                    e1.damage(entity)
                    psys.explosion(entity.location[0], entity.location[1],screen)
                if isinstance(entity, Ship):
                    entity.step_back()
                    e1.step_back()

def render_gui(screen,Ship1,Ship2):
    pygame.draw.rect(screen, pygame.Color(0, 10,100 ), (0, 0, 500, 60))
    pygame.draw.rect(screen, pygame.Color(0x44, 0x44, 0x44), (300, 540, 500, 60))
    
    missile = pygame.image.load("missile.gif")
    
    missile_rect = missile.get_rect()
    for i in range(Ship2.ammo):
        screen.blit(missile, [480-missile_rect[2]*i*2, 20])
    
    missile_rect = missile.get_rect()
    for i in range(Ship1.ammo):
        screen.blit(missile, [WIDTH - missile_rect[2]*i*2, HEIGHT-40])
    
    pygame.draw.rect(screen, pygame.Color(0, 0, 0), (10, 25, 200, 20), 2)
    pygame.draw.rect(screen, pygame.Color(0, 0, 0), (10, 25, Ship2.health*200/Ship.MAX_HEALTH, 20))
    
    pygame.draw.rect(screen, pygame.Color(0, 128, 0), (10, 10, 200, 10), 2)
    pygame.draw.rect(screen, pygame.Color(0, 128, 0), (10, 10, Ship2.shoot_reload*200/Ship.RELOAD_TIME, 10))

    
    pygame.draw.rect(screen, pygame.Color(128, 0, 0), (310, 565, 200, 20), 2)
    pygame.draw.rect(screen, pygame.Color(128, 0, 0), (310, 565, Ship1.health*200/Ship.MAX_HEALTH, 20))
    
    pygame.draw.rect(screen, pygame.Color(0, 128, 0), (310, 550, 200, 10), 2)
    pygame.draw.rect(screen, pygame.Color(0, 128, 0), (310, 550, Ship1.shoot_reload*200/Ship.RELOAD_TIME, 10))
        

def game_loop(Ship1, Ship2, world,two_p):
    '''
    This method implements the game loop.
    The game loop basically consists of steps:
    (i) check if any events occurred. If that's the case, broadcast
    events to all event listeners
    (ii) Perform an update (tick) on all entities in the world.
    This includes the Ships, bases, missiles and the particle system.
    (iii) Render the new configuration of the world. Start with basic
    elements like the background and the bases. Afterwards, render the
    missiles, the Ships and at last the GUI elements. The order used
    for rendering is defined by the >priority< of each entity. The world
    list is sorted before rendering is performed in order to guarantee
    the order specified above
    (iv) Finally, we wait some time before performing the next loop
    '''
    
    starttime = 0
    while 1:
        starttime = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                keys_pressed.append(event.key)
            elif event.type == pygame.KEYUP:
                keys_pressed.remove(event.key)
        for l in input_listener:
            l.on_input(keys_pressed)
        img = pygame.image.load('dirt.jpg')
        img = pygame.transform.scale(img, (WIDTH, HEIGHT))
        screen.fill('BLUE')
        #screen.blit(img, img.get_rect())
        #world.sort()
        moving_water()
        world_copy = [copy.copy(world[i]) for i in range(len(world))]
        Ship1_copy = Ship1.copy1()
        Ship2_copy = Ship2.copy1()
#        ai.observe(Ship1, Ship2_copy, world_copy, screen)
#        ai.observe(Ship2, Ship1_copy, world_copy, screen)
        #ai.perform_action(Ship1, Ship2_copy, world_copy)
        if two_p == 0:
            Ship1.action(Ship2_copy, world_copy)
        #Ship2.action(Ship1_copy, world_copy)
        Ship1.update(0.25)
        Ship2.update(0.25)
        psys.update1(1)
        for [p, entity] in world:
            if not entity.tick():
                world.remove([entity.priority, entity])
                print('wat')
                print(Ship1.health)
                #pygame.quit()
            else:
                check_collisions(world, entity,screen)
                entity.render(screen)
        if psys.attack_animation == True:
            psys.render(screen)
        #psys.tick()
       # psys.render(screen)
        
        render_gui(screen,Ship1,Ship2)
        #Ship2.draw(screen)
        pygame.display.flip()
        span = pygame.time.get_ticks() - starttime

        while (span < 20):
            pygame.time.wait(1)
            print('wait for %d seconds ' % span)
            span = pygame.time.get_ticks() - starttime
        if Ship2.health==0 or Ship1.health==0:
            #flag = flag+1
            break
            #sys.exit()
    game_intro()	

pygame.init()

size = width, height = WIDTH, HEIGHT
white = 0xff, 0xff, 0xff
def button(two_p,msg,x,y,w,h,ic,ac,action=None):
    mouse = pygame.mouse.get_pos()
    clk = pygame.mouse.get_pressed()
    if x+w > mouse[0] > x and y+h > mouse[1]>y:
        pygame.draw.rect(screen,ic,(x,y,w,h))
        if clk[0]==1 and action!=None:
            if action == "play":
                new_game(two_p)
            elif action == "quit":
                pygame.quit()
            elif action == "two":
                #print("#here2")
                two_p = two_p + 1
                new_game(two_p)
            elif action == "menu":
                game_intro()
            elif action == "pause":
                paused()
            elif action == "unpause":
                unpaused()
    else:
        pygame.draw.rect(screen,ic,(x,y,w,h))
    pygame.font.init()
    smalltext = pygame.font.Font('freesansbold.ttf',20)
    textsurf, textrect = text_objects(msg,smalltext)
    textrect.center = ((x+(w/2)),(y+(h/2)))
    screen.blit(textsurf,textrect)
def draw_text(text,fonts,color,surface,x,y):
    textobj = fonts.render(text,1,color)
    textrect = textobj.get_rect()
    textrect.topleft = (x,y)
    surface.blit(textobj,textrect)
def new_game(two_p):
    #pygame.mixer.music.load(path.join(img_folder, "gamemenu.mp3"))
    #pygame.mixer.music.play(-1)
    #global score
    #score = 0
    #player.lives = 2
    #player.health = 100
    game(two_p)

def game_intro():
    #pygame.mixer.music.load(path.join(img_folder, "menumusic.mp3"))
    #pygame.mixer.music.play(-1)
    #global click
    intro = True
    print("hi")
    while True:
        screen.blit(main_menu_bg,(0,0))
        pygame.font.init()
        largetext = pygame.font.Font('freesansbold.ttf', 60)
        TextSurf, TextRect = text_objects("Battleship!!", largetext)
        TextRect.center = ((WIDTH / 2), (HEIGHT / 2 - 200))
        screen.blit(TextSurf, TextRect)
        two_p = 0
        button(two_p,"START",WIDTH/2-75,HEIGHT/2-50,150,50,'BLUE','BRIGHT_BLUE',"play")
        button(two_p,"QUIT",WIDTH/2-75,HEIGHT/2+50,150,50,'RED','BRIGHT_RED',"quit")
        button(two_p,"2-PLAYER",WIDTH/2-75,HEIGHT/2+150,150,50,'RED','BRIGHT_RED',"two")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
        pygame.display.update()
        pygame.time.Clock().tick(60)
#screen = pygame.display.set_mode(size)
def game(two_p):
    #Ship1 = ai.AIBot(100, 500, pygame.image.load("tank1.png"), pygame.image.load("Tank1_top.gif"), KEY_BINDINGS_1)
    if two_p == 1:
        Ship1 = Ship(100, 500, pygame.image.load("tank11.gif"), pygame.image.load("Tank1_top.gif"), KEY_BINDINGS_1)
        print(two_p)
    else:
        Ship1 = ai.AIBot(100, 500, pygame.image.load("tank11.gif"), pygame.image.load("Tank1_top.gif"), KEY_BINDINGS_1)
        print(two_p)
    Ship2 = Ship(700, 100, pygame.image.load("Tank2.png"), pygame.image.load("Tank2_top.gif"), KEY_BINDINGS_2)
    
    if two_p == 1:
        input_listener.append(Ship1)
    input_listener.append(Ship2)
    
    base1 = Base(100, 500, pygame.image.load("base.gif"), Ship1)
    base2 = Base(700, 100, pygame.image.load("base.gif"), Ship2)
    
    img = pygame.image.load('dirt.jpg')
    img = pygame.transform.scale(img, (WIDTH, HEIGHT))
    
    world = []
    world.append(base1)
    world.append(base2)
    world.append(Ship1)
    world.append(Ship2)
    world = [[e.priority, e] for e in world]
    Ship1.set_world(world)
    Ship2.set_world(world)
    mixer.music.stop()
    mixer.music.load('Crisp_Ocean_Waves.wav')
    mixer.music.play(-1)
    game_loop(Ship1, Ship2, world,two_p)
if __name__ == '__main__':
    '''
    This is the program's starting point.
    We initialize the pygame module, create a screen and load
    resources (images etc.) in order to create the entities involved in
    the game.
    All entities are placed in a list, which we call world.
    At last, the game loop can be started using this list.
    '''
    game_intro()
   # Ship1 = ai.AIBot(100, 500, pygame.image.load("Ship1.gif"), pygame.image.load("Ship1_top.gif"), KEY_BINDINGS_1)
    #Ship2 = Ship(700, 100, pygame.image.load("Ship2.png"), pygame.image.load("Ship2_top.gif"), KEY_BINDINGS_2)
    
    #input_listener.append(Ship1)
  #  input_listener.append(Ship2)
    
   # base1 = Base(100, 500, pygame.image.load("base.gif"), Ship1)
    #base2 = Base(700, 100, pygame.image.load("base.gif"), Ship2)
    
    #img = pygame.image.load('dirt.jpg')
    #img = pygame.transform.scale(img, (WIDTH, HEIGHT))
    
    #world = []
    #world.append(base1)
    #world.append(base2)
    #world.append(Ship1)
    #world.append(Ship2)
    #world = [[e.priority, e] for e in world]
    #Ship1.set_world(world)
    #Ship2.set_world(world)
    #game_loop(Ship1, Ship2, world)
