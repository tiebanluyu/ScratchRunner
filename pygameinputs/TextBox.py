import pygame
import time

pygame.init()


class TextBox(object):
    def __init__(self, x:int = 0, y:int = 0, width:int = 200, height:int = 50, placeholder:str = "", font:str = "calibri",
                 fontSize:int = 11, color:tuple = (0, 0, 0), background:tuple = (230, 230, 230), backgroundHover:tuple = (200, 200, 200),
                 borderColour:tuple = (230, 230, 230), borderHoverColour:tuple = (200, 200, 200), borderWeight:int = 1, bold:bool = False, italic:bool = False,
                 minlen:int = 0, maxlen:int = 0, borderRadius: int = -1):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.placeholder = placeholder
        self.text = ""
        self.font = font
        self.fs = fontSize
        self.bold = bold
        self.italic = italic
        self.color = color
        self.bg = background
        self.minlen = minlen
        self.maxlen = maxlen
        self.bgHover = backgroundHover
        self.border = borderColour
        self.hborder = borderHoverColour
        self.borderWidth = borderWeight
        self.hover = False
        self.active = False
        self.counter = time.time()
        self.borderRadius = borderRadius

    def draw(self, window):
        self.isHover()
        if self.hover or self.active:
            pygame.draw.rect(window, self.bgHover, (self.x, self.y, self.width, self.height), 0, self.borderRadius)
            pygame.draw.rect(window, self.hborder, (self.x, self.y, self.width, self.height), self.borderWidth,
                             self.borderRadius)
        else:
            pygame.draw.rect(window, self.bg, (self.x, self.y, self.width, self.height), 0, self.borderRadius)
            pygame.draw.rect(window, self.border, (self.x, self.y, self.width, self.height), self.borderWidth,
                             self.borderRadius)

        font = pygame.font.SysFont(self.font, self.fs, self.bold, self.italic)
        if self.text == "":
            text = font.render(self.placeholder, True, self.color)
        else:
            text = font.render(self.text, True, self.color)

        text_rect = text.get_rect()
        width = text_rect.width
        height = text_rect.height

        textX = (self.x + (self.width // 2)) - width // 2
        textY = (self.y + (self.height // 2)) - height // 2

        window.blit(text, (textX, textY))

        if 1 <= time.time() - self.counter <= 2 and self.active:
            text = font.render('|', True, self.color)
            window.blit(text, (textX + width, textY))
            #print("XD")
        elif time.time() - self.counter >= 2:
            self.counter = time.time()

    # deprecated code

    def backspacePressed(self):
        text = list(self.text)
        if text.__len__() >= 1:
            text.pop()
        self.text = ''.join(text)

    def textAppend(self, character:str):
        text = list(self.text)
        if text.__len__() < self.maxlen or self.maxlen <= 0:
            text.append(character)
        self.text = ''.join(text)

    # end of deprecated code

    def typing(self, event):
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.backspacePressed()
            else:
                self.textAppend(event.unicode)

    def getPressed(self, event):
        if self.hover and event.type == pygame.MOUSEBUTTONUP:
            self.active = True
            return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.active = False
            return False

    def events(self, event):
        self.getPressed(event)
        self.typing(event)

    def isHover(self):
        mouse = pygame.mouse.get_pos()

        if mouse[0] >= self.x and mouse[0] <= self.x + self.width:
            if mouse[1] >= self.y and mouse[1] <= self.y + self.height:
                self.hover = True
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            else:
                self.hover = False
        else:
            self.hover = False
        return self.hover

