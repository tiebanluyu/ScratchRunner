import pygame
def drawtext(sprite,surface):
    rect=sprite.rect
    font = pygame.font.Font("MSYH.TTC", 32)
    text=sprite.words
    fontColor = (255, 221, 85)
    textsurface=font.render(text,True, fontColor)
    pygame.draw.rect(surface, (255, 0, 0), (*rect.topright, *textsurface.get_size()),0)
    surface.blit(textsurface,rect.topright)
    
