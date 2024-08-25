import pygame,logging
from mouse import get_mouse_speed
pygame.font.init()
try:
    font = pygame.font.SysFont("simhei",20)
except:#不排除其他国家没有宋体        
    font = pygame.font.SysFont(None,16)
def drawtext(sprite,surface):
    if sprite.words=="":
        return
    rect=sprite.rect
    
    text=sprite.words
    fontColor = (0, 0, 0)
    textsurface=font.render(text,True, fontColor)
    
    pygame.draw.rect(surface, (255, 255, 255), (*rect.topright, *textsurface.get_size()),0)
    pygame.draw.rect(surface, (0, 0, 0), (rect.topright[0]-5,rect.topright[1]-5, textsurface.get_size()[0]+10,textsurface.get_size()[1]+10),2)
    surface.blit(textsurface,rect.topright)
def drawvariable(moniter,text,surface):
    #font =pygame.font.Font("HarmonyOS_Sans_SC_Regular.ttf",24)
    if not moniter.visible:
        return
    fontColor = (255, 255, 255)
    textsurface=font.render(text,True, fontColor)
    position=(moniter.x,moniter.y)
    pygame.draw.rect(surface, (255, 140, 26), (*position, *textsurface.get_size()),0)
    surface.blit(textsurface,position)
    
    #logging.debug("drawvariable")
def drawlist(moniter,thelist,screen):
    slice_lict=[]
    fontColor = (0, 0, 0)
    for i in thelist:
        if len(i)>10:
            i=i[:10]+"..."
        slice_lict.append(i)
    y=moniter.show_y+30
    x=5
    backgroundsurface=pygame.surface.Surface((moniter.width,moniter.height))
    backgroundrect=pygame.draw.rect(screen, (255, 140, 26), (moniter.x,moniter.y, *backgroundsurface.get_size()),0)
    backgroundsurface.fill((230,240,255))
    
    #backgroundsurface.blit(textsurface,rect)    
    for text in thelist: 
        
        #y+=textsurface.get_size()[1]+5
          
        textsurface=font.render(text,True, fontColor)
        
        if y>=0:
            rect=pygame.draw.rect(backgroundsurface, (255, 140, 26), (x,y, *textsurface.get_size()),0)
            backgroundsurface.blit(textsurface,rect)
            
        y+=textsurface.get_size()[1]+5
        if y>moniter.height:
            break
    #绘制列表名称
    textsurface=font.render(moniter.params["LIST"],True, fontColor)
    rect=pygame.draw.rect(backgroundsurface, (255,255,255), (0,0, *textsurface.get_size()))

    backgroundsurface.blit(textsurface,rect)
    
    rect=pygame.draw.rect(backgroundsurface, (0, 0, 0), (0,0, *backgroundsurface.get_size()),2)#在背景上画一个边框
    #0，0在background的坐标系中，width，height为矩形的宽和高    
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_x/=2
    mouse_y/=2
    is_mouse_over = backgroundrect.collidepoint(mouse_x, mouse_y)
    is_mouse_down = pygame.mouse.get_pressed()[0]
    #logging.debug(pygame.mouse.get_pressed())
    # 判断鼠标是否悬停在图像上
    if is_mouse_over and is_mouse_down:
        # 鼠标悬停在图像上

        moniter.show_y=moniter.show_y+get_mouse_speed()[1]/10

        #上移有界
        if moniter.show_y>0:
            moniter.show_y=0
        
        logging.debug("show_y:"+str(moniter.show_y))
    else:
        pass
        # 鼠标不在图像上
        #print("Mouse is not over the image")
    

    screen.blit(backgroundsurface,backgroundrect)    

    
    
    
