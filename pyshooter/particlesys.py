'''
Created on 24.11.2012

This file contains the basic implementation of a simple particle system.
'''

import pygame, math
import random

class ParticleSystem:
    
    def __init__(self):
        #self.particles = []
        #self.random = random.Random()
        self.attack_animation = False
        self.sprites = []
        self.x = 0
        self.y = 0
        img1 = pygame.image.load('explosion00.png')
        img2 = pygame.image.load('explosion01.png')
        img3 = pygame.image.load('explosion02.png')
        img4 = pygame.image.load('explosion03.png')
        img5 = pygame.image.load('explosion04.png')
        img6 = pygame.image.load('explosion05.png')
        img7 = pygame.image.load('explosion06.png')
        img8 = pygame.image.load('explosion07.png')
        img9 = pygame.image.load('explosion08.png')
        self.sprites.append(pygame.transform.scale(img1, (50, 30)))
        self.sprites.append(pygame.transform.scale(img2, (50, 30)))
        self.sprites.append(pygame.transform.scale(img3, (50, 30)))
        self.sprites.append(pygame.transform.scale(img4, (50, 30)))
        self.sprites.append(pygame.transform.scale(img5, (50, 30)))
        self.sprites.append(pygame.transform.scale(img6, (50, 30)))
        self.sprites.append(pygame.transform.scale(img7, (50, 30)))
        self.sprites.append(pygame.transform.scale(img8, (50, 30)))
        self.sprites.append(pygame.transform.scale(img9, (50, 30)))
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect()
    def update1(self,speed):
        if self.attack_animation == True:
            self.current_sprite += speed
        if int(self.current_sprite) >= len(self.sprites):
            self.current_sprite = 0
            self.attack_animation = False
        self.image = self.sprites[int(self.current_sprite)]
    def add_particle(self, particle):
        self.particles.append(particle)
    
    def render(self, screen):
        rect1 = self.rect
        #screen.blit(self.image, ([self.x - rect1[0+2]/10,self.y + 10 - rect1[1+2]/10]))
        screen.blit(self.image, ([self.x,self.y]))
    
    def tick(self):
        for particle in self.particles:
            if not particle.move():
                self.particles.remove(particle)
    
    def explosion(self, x, y,screen):
        self.attack_animation = True
        self.x = x
        self.y = y
        
        
class Particle():
    
    def __init__(self, x, y, v, r, ttl):
        self.velocity = v
        self.angle = r
        self.ttl = ttl
        self.location = [x, y]
    
    def alive(self):
        return (self.ttl > 0)
    
    def move(self):
        self.location[0] -= math.sin(self.angle) * self.velocity
        self.location[1] -= math.cos(self.angle) * self.velocity
        self.ttl -= 1
        return self.alive()
        
    def render(self, screen):
        pygame.draw.rect(screen, pygame.Color(0x44, 0x44, 0x44), (self.location[0]-1, self.location[1]-1, 3, 3))