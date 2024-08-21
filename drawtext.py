import pygame,logging
def drawtext(sprite,surface):
    if sprite.words=="":
        return
    rect=sprite.rect
    font = pygame.font.Font("MSYH.TTC", 16)
    text=sprite.words
    fontColor = (0, 0, 0)
    textsurface=font.render(text,True, fontColor)
    
    pygame.draw.rect(surface, (255, 255, 255), (*rect.topright, *textsurface.get_size()),0)
    pygame.draw.rect(surface, (0, 0, 0), (rect.topright[0]-5,rect.topright[1]-5, textsurface.get_size()[0]+10,textsurface.get_size()[1]+10),2)
    surface.blit(textsurface,rect.topright)
def drawvariable(moniter,text,surface):
    font = pygame.font.Font("MSYH.TTC", 16)
    fontColor = (255, 255, 255)
    textsurface=font.render(" "+text+" ",True, fontColor)
    position=(moniter.x,moniter.y)
    pygame.draw.rect(surface, (255, 140, 26), (*position, *textsurface.get_size()),0)
    surface.blit(textsurface,position)
    
    #logging.debug("drawvariable")
        
    
