'''
Created on 23.11.2012

This file contains the entities involved in the game. All entities use
the base class implementation 'Entity'.
'''
import math
import tools
import pygame
import copy
map = pygame.Rect(0, 0, 800, 600)

class Entity():
    
    def __init__(self, x, y, img, priority):
        self.location = [x, y]
        self.angle = 0
        self.velocity = 0
        self.acceleration = 0
        self.turn_velocity = 0
        self.turn_acceleration = 0
        self.img = img
        self.bufimg = self.img
        if self.bufimg != None: self.bufrect = self.bufimg.get_rect()
        self.map_rect = map
        self.priority = priority
    
    def set_angle(self, angle):
        self.angle = angle
        if self.bufimg != None:
            self.bufimg, self.bufrect = tools.rot_center(self.img, self.img.get_rect(), self.angle * 180 / math.pi)
			
    
    def tick(self):
        self.location[0] -= math.sin(self.angle) * self.velocity
        self.location[1] -= math.cos(self.angle) * self.velocity
        return self.alive()
    
    def render(self, screem):
        screem.blit(self.bufimg, [self.location[i] - self.bufrect[i+2]/2 for i in [0, 1]])
    
    def get_radius(self):
        return (self.img.get_rect()[2] + self.img.get_rect()[3]) / 4
    
    def collide(self, x, y):
        return self.get_radius()**2 > (self.location[0] - x)**2 + (self.location[1] - y)**2
    
    def collide_entities(self, other):
        return 0.3*(self.get_radius()+other.get_radius())**2 > (self.location[0] - other.location[0])**2 + (self.location[1] - other.location[1])**2

    def alive(self):
        return True

class Ship(Entity):
    MAX_SPEED = 3
    MAX_TURN_SPEED = 0.01 * math.pi
    MAX_AMMO = 10
    MAX_HEALTH = 100
    RELOAD_TIME = 100
    DCL_AIM = 0.005 * math.pi
    DCL_TURN = 0.0005 * math.pi
    DCL_MOVE = 0.2
    
    def __init__(self, x, y, img, top_img, key_binding):
        Entity.__init__(self, x, y, img, 10)
        self.aim_direction = 0
        self.top_img = top_img
        self.top_bufimg = top_img
        if self.top_bufimg != None: self.top_bufrect = top_img.get_rect()
        #self.w_img = w_img
        #self.w_imgrect = w_img
        #if self.w_img != None: self.w_imgrect = w_img.get_rect()
        self.aim_velocity = 0
        self.aim_acceleration = 0
        self.old_location = self.location
        self.shoot_reload = 0
        self.key_binding = key_binding
        self.ammo = Ship.MAX_AMMO
        self.health = Ship.MAX_HEALTH
        self.last_action = [0, 0, 0]
        self.base = None
        self.owner = None
        self.sprites = []
        self.sprites.append(pygame.image.load('water_ripple_medium_000.png'))
        self.sprites.append(pygame.image.load('water_ripple_medium_001.png'))
        self.sprites.append(pygame.image.load('water_ripple_medium_002.png'))
        self.sprites.append(pygame.image.load('water_ripple_medium_003.png'))
        self.sprites.append(pygame.image.load('water_ripple_medium_004.png'))
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        #self.rect.topleft = [self.location[0],self.location[1]]
    
    def update(self,speed):
        #if self.attack_animation == True:
        self.current_sprite += speed
        if int(self.current_sprite) >= len(self.sprites):
            self.current_sprite = 0
            #self.attack_animation = False
        self.image = self.sprites[int(self.current_sprite)]
    def set_base(self, base):
        self.base = base
    
    def ready_to_shoot(self):
        return self.shoot_reload == Ship.RELOAD_TIME and self.ammo > 0
    
    def step_back(self):
        self.location = self.old_location[:]
    
    def to_base(self, base):
        if base.owner == self:
            self.ammo = Ship.MAX_AMMO
    
    def decelerate(self, acc, vel, dec, limit, mult=1):
        if acc != 0:
            vel = max(min(vel + acc*dec*mult, limit), -limit)
        elif vel > 0:
            vel = max(vel - dec, 0)
        elif vel < 0:
            vel = min(vel + dec, 0)
        return vel
            
    def tick(self):
        # save copy of old location
        self.old_location = self.location[:]
        
        # update velocities
        self.aim_velocity = self.decelerate(self.aim_acceleration, self.aim_velocity, Ship.DCL_AIM, Ship.MAX_TURN_SPEED)
        self.turn_velocity = self.decelerate(self.turn_acceleration, self.turn_velocity, Ship.DCL_TURN, Ship.MAX_TURN_SPEED)
        mult = 0.25 if self.velocity * self.acceleration > 0 else 1
        self.velocity = self.decelerate(self.acceleration, self.velocity, Ship.DCL_MOVE, Ship.MAX_SPEED, mult)
        
        # update positions
        self.rotate_gun_to(self.aim_direction + self.aim_velocity)
        self.set_angle(self.angle + self.turn_velocity)
        self.image, self.rect = tools.rot_center(self.image, self.image.get_rect(), self.angle * 180 / math.pi)
        Entity.tick(self)
        
        # check if position is valid
        self.check_borders()        
        
        # reload the gun
        self.shoot_reload = min(self.shoot_reload+1, Ship.RELOAD_TIME)
        
        # prevent to get killed
        return self.alive()
    
    def move_copy(self, action):
        Ship = Ship(self.location[0], self.location[1], self.img, self.top_img, None)
        Ship.aim_direction = self.aim_direction
        Ship.aim_velocity = self.aim_velocity
        Ship.aim_acceleration = self.aim_acceleration
        Ship.old_location = self.old_location[:]
        Ship.shoot_reload = self.shoot_reload
        Ship.ammo = self.ammo
        Ship.health = self.health
        Ship.last_action = action
        Ship.perform_action(action)
        Ship.tick()
        return Ship
        
    def copy1(self):
        ship = Ship(self.location[0], self.location[1], self.img, self.top_img, None)
        ship.aim_direction = self.aim_direction
        ship.aim_velocity = self.aim_velocity
        ship.aim_acceleration = self.aim_acceleration
        ship.old_location = self.old_location[:]
        ship.shoot_reload = self.shoot_reload
        ship.ammo = self.ammo
        ship.health = self.health
        ship.tick()
        return ship
		
		
    def check_borders(self):
        for i in [0, 1]:
            if self.location[i]-self.bufrect[i+2]/2 < self.map_rect[i]:
                self.location[i] = self.map_rect[i] + self.bufrect[i+2]/2
            if self.location[i]+self.bufrect[i+2]/2 > self.map_rect[i]+self.map_rect[i+2]:
                self.location[i] = self.map_rect[i]+self.map_rect[i+2] - self.bufrect[i+2]/2
    
    def rotate_gun_to(self, angle):
        self.aim_direction = angle % (math.pi * 2)
        if self.top_bufimg != None:
            self.top_bufimg, self.top_bufrect = tools.rot_center(self.top_img, self.top_img.get_rect(), self.aim_direction * 180 / math.pi)
    
    def render(self, screen):
        Entity.render(self, screen)
        rect = self.top_bufrect
        screen.blit(self.top_bufimg, [self.location[i] - rect[i+2]/2 for i in [0, 1]])
        rect1 = self.rect
        #screen.blit(self.image, ([self.location[0] - rect1[0+2]/2,self.location[1] + 10 - rect1[1+2]/2]))
    
    def damage(self, missile):
        if missile.owner != self:
            self.health -= missile.damage
            missile.destroy()
    
    def alive(self):
        return self.health > 0

    def shoot(self):
        if self.ready_to_shoot():
            x, y = (self.location[0] - math.sin(self.aim_direction) * 40),\
                    (self.location[1] - math.cos(self.aim_direction) * 40)
            missile = Missile(x, y, pygame.image.load("missile.gif"), self)
            self.ammo -= 1
            self.shoot_reload = 0
            self.world.append([missile.priority, missile])
    
    def set_world(self, world):
        self.world = world
    
    def on_input(self, keys):
        # TODO improve this
        actions = []
        for key in keys:
            if key in self.key_binding.keys():
                actions.append(self.key_binding[key])
        #
        
        self.last_action = [int("up" in actions),
                            int("down" in actions),
                            int("left" in actions),
                            int("right" in actions),
                            int("gun_left" in actions),
                            int("gun_right" in actions),
                            int("gun_fire" in actions)]
        self.perform_action(self.last_action)
    
    def perform_action(self, actions):
        move = actions[0] - actions[1]
        turn = actions[2] - actions[3]
        aim = actions[4] - actions[5]
        self.last_action = actions[:]
        self.perform_action_move(move, turn, aim)
        if actions[6]: self.shoot()
    
    def perform_action_move(self, move=0, turn=0, aim=0):
        self.acceleration = int(move)
        self.turn_acceleration = int(turn)
        self.aim_acceleration = int(aim)
    
    def get_repr(self):
        return [self.location[0] / self.map_rect.width,
                self.location[1] / self.map_rect.height,
                self.angle / (math.pi * 2.),
                self.velocity / Ship.MAX_SPEED,
                self.aim_direction / (math.pi * 2),
                self.aim_velocity / Ship.MAX_TURN_SPEED,
                self.turn_velocity / Ship.MAX_TURN_SPEED,
                self.ammo / float(Ship.MAX_AMMO),
                self.health / float(Ship.MAX_HEALTH)]
	
	
                
                    
class Missile(Entity):
    
    def __init__(self, x, y, img, owner):
        Entity.__init__(self, x, y, img, 5)
        self.velocity = 10
        self.owner = owner
        self.set_angle(owner.aim_direction)
        self.ttl = 200
        self.damage = 10
    
    def destroy(self):
        self.ttl = 0
    
    def alive(self):
        return (self.ttl > 0) and (self.velocity > 2)
    
    def tick(self):
        Entity.tick(self)
        self.ttl -= 1
        if self.location[0] < 0 or self.location[0] > self.map_rect.width or \
            self.location[1] < 0 or self.location[1] > self.map_rect.height:
            self.destroy()
        
        return self.alive()

class Base(Entity):
    
    def __init__(self, x, y, img, owner):
        Entity.__init__(self, x, y, img, 0)
        self.owner = owner
        self.preparation_time = 0
        self.owner.set_base(self)
    
    def get_radius(self):
        return 10
    
    def tick(self):
        if self.owner.collide_entities(self) and self.preparation_time == 0:
            while (self.owner.ammo < 10):
                self.preparation_time += 50
                self.owner.ammo += 1
        self.preparation_time = max(self.preparation_time - 1, 0)
        return True
        