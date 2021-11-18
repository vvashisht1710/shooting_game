'''
Created on 23.11.2012

@author: Alex
'''
import pygame
from math import fabs

def rot_center(image, rect, angle):
    """rotate an image while keeping its center"""
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = rot_image.get_rect(center=rect.center)
    return rot_image, rot_rect

def sign(x):
    if x == 0:
        return 0
    return x / fabs(x)