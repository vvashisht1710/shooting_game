'''
Created on 25.11.2012

@author: Steffen
'''

import pygame
import entities
from entities import Ship, Base, Entity, Missile
import math
import random
import main
import copy
import tools


class AntiGravity():
    
    def wall_error(self, x, y):
        Ex = 1 / x**2 - 1 / math.fabs((x - main.WIDTH) ** 2)
        Ex *= main.WIDTH**2
        Ey = 1 / y**2 - 1 / math.fabs((y - main.HEIGHT) ** 2)
        Ey *= main.HEIGHT**2
        return [Ex, Ey]
        
    def point_error(self, location, p, force):
        [x, y] = location
        e = force / (math.hypot((x - p[0]),(y - p[1])) ** 2)
        return [(x-p[0]) * e, (y-p[1])*e]
    
    def continious_gradient(self, location, p, force):
        [x, y] = location
        e = force / (math.hypot((x - p[0]),(y - p[1])))
        return [(x-p[0]) * e, (y-p[1])*e]
    
    def add_gravity_point(self, x, y, force):
        self.gravity_points.append([x, y, force])

class PIDControl():
    
    def __init__(self, params):
        self.error = [0., 0., 0.]
        self.params = params
        self.last_error = 0.
        self.current_error = 0.
    
    def pid(self, current_error):
        # P
        self.error[0] = current_error
        # I
        self.error[1] += self.error[0]
        # D
        self.error[2] = self.last_error - self.error[0]
        
        self.last_error = self.error[0]
        return sum([self.error[i] * self.params[i] for i in range(3)])

#wait = 2
#direction = 1
#last_diff = 0
#observations = []
#targets = []
#model = neural.Model(20,10,10)
rnd = random.Random()
actions = [[0, 0],
           [0, 1],
           [1, 0]]

def angle_between(Ship1, Ship2):
    [dx, dy] = [Ship2.location[i] - Ship1.location[i] for i in [0,1]]
    g = Ship1.aim_direction
    [bx, by] = [-math.sin(g), -math.cos(g)]
    
    s = site([dx, dy], [bx, by])
    
    [x, y] = Ship1.location
    
    a = angle([dx, dy], [bx, by])
    return (a, s)

def site(a, b):
    return tools.sign(b[0]*a[1] - b[1]*a[0])

def angle(a, b, abs=False):
    scalar = a[0]*b[0] + a[1]*b[1]
    if abs: scalar=math.fabs(scalar)
    return math.acos((scalar) /
              (math.hypot(a[0], a[1]) * math.hypot(b[0], b[1])))

def world_repr(Ship, opponent, world):
    rep = []
    rep.extend(Ship.get_repr())
    rep.extend(opponent.get_repr())
    a, s = angle_between(Ship, opponent)
    rep.append(a*s)
    a, s = angle_between(opponent, Ship)
    rep.append(a*s)
    return rep

def distance_to_line(a, b, g):
    [x1, y1] = a
    [x2, y2] = b
    [xg, yg] = [-math.sin(g), -math.cos(g)]
    d = -yg * (x2 - x1) + xg * (y2 - y1)
    xf = [-yg * d, xg * d]
    return [math.fabs(d), xf]
    
def observe(Ship, opponent, world, screen):
    pass
#    global last_error, actions, last_action, wait, direction, model, observations, targets
#    return
#    angle, site = angle_between(Ship, opponent)
#    direction = pid(angle*site, params)
    #print distance_to_gunline(Ship, opponent)
#    if direction < 0:
#        Ship.perform_action(aim = 1)
#    else:
#        Ship.perform_action(aim = -1)
#    r = world_repr(Ship, opponent, world)
#    observations.append(r)
#    targets.append(expand_targets(Ship.last_action))
#    if len(observations) > 100:
#        print 'performing an update'
#        X = numpy.array(observations)
#        Y = numpy.array(targets)
#        for i in range(10):
#            grad1, grad2 = model.gradients(X, Y)
#            model.update(grad1, grad2, 0.05)
#        observations = []
#        targets = []
    #print "  ".join([str(int(r[i] * 100)/100.) for i in range(len(r))])

def expand_targets(t):
    return [t[0],
             t[1],
             t[0] == t[1],
             t[2],
             t[3],
             t[2] == t[3],
             t[4],
             t[5],
             t[4] == t[5],
             t[6]]

#def perform_action(Ship, opponent, world):
#    r = world_repr(Ship, opponent, world)
#    X = numpy.array(r)
#    h, y = model.compute(X)
#    tank.perform_action(sample(y))

def sample(x):
    global rnd
    actions = [0, 0, 0, 0, 0, 0]
    shoot = int(rnd.random() < x[9])
    probs = [math.exp(x[i]) for i in range(9)]
    for i in range(3):
        s = 0.
        for j in range(3):
            s += probs[i*3+j]
        actions[i*2] = int(rnd.random() < probs[i*3]/s)
        actions[i*2+1] = int(rnd.random() < probs[i*3+1]/s)
    actions.append(shoot)
    return actions

class AIBot(Ship):
    
    def __init__(self, x, y, img, top_img, key_binding=None):
        Ship.__init__(self, x, y, img, top_img, key_binding)
        self.pid_aim = PIDControl([10., 0., 1.])
        self.pid_turn = PIDControl([20., 0., 0.])
        self.anti_gravity = AntiGravity()
        #self.w_img = w_img
    
    def action(self, opponent, world):
        global actions, wait, direction, model, observations, targets, pid_aim, pid_move, pid_turn
        a, s = angle_between(self, opponent)
        direction = self.pid_aim.pid(a*s)
        aim = [0, 0]
        if direction < 0: aim = [1, 0]
        else: aim = [0, 1]
        
        g = self.compute_error(opponent, world)
        
        if g[0] == 0 and g[1] == 0:
            return
        
#        [x, y] = self.location[:]
#        [x0, y0] = [x+10*g[0], y+10*g[1]]
#        pygame.draw.line(main.screen, pygame.Color(0, 128, 0), (x,y), (x0,y0), 5)
        
        a = [-math.sin(self.angle),-math.cos(self.angle)]
#        [x1, y1] = [x+100*a[0], y+100*a[1]]
#        pygame.draw.line(main.screen, pygame.Color(0, 0, 128), (x,y), (x1,y1), 5)
        
        r = angle(a, g)
        s = site(a, g)
        
        t = self.pid_turn.pid(min(r, math.fabs(math.pi-r))*s)
        turn = [0, 0]
        if t < 0: turn = [0, 1]
        else: turn = [1, 0]
        
        move = [0, 0]
        if r > math.pi/2: move = [0, 1]
        else: move = [1, 0]
        
        shoot = [0]
        if (r < math.pi/8): shoot = [1]
        
        best_action = move + turn + aim + shoot
    
        self.perform_action(best_action)

    def missile_error(self, world):
        g1, g2 = 0,0
        for m in world:
            entity = m[1]
            if isinstance(entity, Missile) and entity.owner != self:
                [d, dv] = distance_to_line(self.location, entity.location, entity.angle)
                xf = [self.location[i] + dv[i] for i in range(2)]
                [g1_, g2_] = self.anti_gravity.point_error(self.location, xf, 50000)
                g1+=g1_
                g2+=g2_
                pygame.draw.rect(main.screen, pygame.Color(200,0,0),(xf[0],xf[1],20,20))
        return g1, g2

    def compute_error(self, opponent, world):
        [x, y] = self.location
        [d, dv] = distance_to_line(self.location, opponent.location, opponent.aim_direction)
        xf = [x+dv[0], y+dv[1]]
        pygame.draw.rect(main.screen, pygame.Color(0,128,0),(xf[0],xf[1],10,10))
        g = self.anti_gravity.wall_error(x, y)
        
        # avoid gunline
        r, s = angle_between(opponent, self)
        g1, g2 = 0, 0
        if r < math.pi/2:
            g1, g2 = self.anti_gravity.point_error([x, y], xf, 10000)
        
        # avoid missiles
        m_error = self.missile_error(world)
        
        # go to base
        g_base = [0,0]
        if self.location[0] != self.base.location[0] or self.location[1] != self.base.location[1]:
            g_base = self.anti_gravity.continious_gradient(self.location, self.base.location, -1000/(0.1+self.ammo**2))
        
        g[0] += g1 + m_error[0] + g_base[0]
        g[1] += g2 + m_error[1] + g_base[1]
        return g