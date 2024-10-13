import pygame
import webbrowser
import os

pygame.init()


class Button(object):
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 50, text: str = "TEXT HERE",
                 font: str = 'calibri', fontsize: int = 11, color: tuple = (0, 0, 0),
                 background: tuple = (230, 230, 230), backgroundHover: tuple = (200, 200, 200),
                 borderColour: tuple = (230, 230, 230), borderHoverColour: tuple = (200, 200, 200),
                 borderWeight: int = 1, bold: bool = False, italic: bool = False, borderRadius: int = -1):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.font = font
        self.fs = fontsize
        self.bold = bold
        self.italic = italic
        self.color = color
        self.bg = background
        self.bgHover = backgroundHover
        self.border = borderColour
        self.hBorder = borderHoverColour
        self.borderWidth = borderWeight
        self.visible = True
        self.hover = False
        self.borderRadius = borderRadius

    def draw(self, window):
        if self.visible:
            self.isHover()
            if self.hover:
                pygame.draw.rect(window, self.bgHover, (self.x, self.y, self.width, self.height), 0, self.borderRadius)
                if self.borderWidth > 0:
                    pygame.draw.rect(window, self.hBorder, (self.x, self.y, self.width, self.height), self.borderWidth,
                                     self.borderRadius)
            else:
                pygame.draw.rect(window, self.bg, (self.x, self.y, self.width, self.height), 0, self.borderRadius)
                if self.borderWidth > 0:
                    pygame.draw.rect(window, self.border, (self.x, self.y, self.width, self.height), self.borderWidth,
                                     self.borderRadius)
            if self.font.endswith(".ttf"):
                font = pygame.font.Font(self.font, self.fs)
                font.bold = self.bold
                font.italic = self.italic
            else:
                font = pygame.font.SysFont(self.font, self.fs, self.bold, self.italic)
            text = font.render(self.text, True, self.color)
            text_rect = text.get_rect()
            width = text_rect.width
            height = text_rect.height

            textX = (self.x + (self.width // 2)) - width // 2
            textY = (self.y + (self.height // 2)) - height // 2

            window.blit(text, (textX, textY))
        else:
            self.hover = False

    def isHover(self):
        mouse = pygame.mouse.get_pos()

        if mouse[0] >= self.x and mouse[0] <= self.x + self.width:
            if mouse[1] >= self.y and mouse[1] <= self.y + self.height:
                self.hover = True
                pygame.mouse.set_cursor(pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND))
            else:
                self.hover = False
        else:
            self.hover = False
        return self.hover

    def getPressed(self, event):
        if event.type == pygame.MOUSEBUTTONUP and self.hover:
            return True
        else:
            return False


class LinkButton(Button):
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 50, text: str = "TEXT HERE",
                 font: str = 'calibri', fontsize: int = 11, color: tuple = (0, 0, 0),
                 background: tuple = (230, 230, 230), backgroundHover: tuple = (200, 200, 200),
                 borderColour: tuple = (230, 230, 230), borderHoverColour: tuple = (200, 200, 200),
                 borderWeight: int = 1, bold: bool = False, italic: bool = False, link: str = "https://google.com/"):
        super().__init__(x, y, width, height, text, font, fontsize, color, background, backgroundHover, borderColour,
                         borderHoverColour, borderWeight, bold, italic)
        self.link = link

    def getPressed(self, event):
        if event.type == pygame.MOUSEBUTTONUP and self.hover:
            webbrowser.open(self.link, new=2)
            return True
        else:
            return False


class AppButton(Button):
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 50, text: str = "TEXT HERE",
                 font: str = 'calibri', fontsize: int = 11, color: tuple = (0, 0, 0),
                 background: tuple = (230, 230, 230), backgroundHover: tuple = (200, 200, 200),
                 borderColour: tuple = (230, 230, 230), borderHoverColour: tuple = (200, 200, 200),
                 borderWeight: int = 1, bold: bool = False, italic: bool = False,
                 app: str = "C:\\Windows\\System32\\notepad.exe"):
        super().__init__(x, y, width, height, text, font, fontsize, color, background, backgroundHover, borderColour,
                         borderHoverColour, borderWeight, bold, italic)
        self.app = app

    def getPressed(self, event):
        if event.type == pygame.MOUSEBUTTONUP and self.hover:
            os.startfile(self.app)
            return True
        else:
            return False


class ImageButton(Button):
    def __init__(self, x: int = 0, y: int = 0, width: int = 200, height: int = 50,
                 image: str = "button.png", hoverImage: str = "button.png"):
        text = font = ""
        fontsize = borderWeight = 0
        color = background = backgroundHover = borderColour = borderHoverColour = (0, 0, 0)
        bold = italic = False
        super().__init__(x, y, width, height, text, font, fontsize, color, background, backgroundHover, borderColour,
                         borderHoverColour, borderWeight, bold, italic)
        self.img = image
        self.hImg = hoverImage

    def draw(self, window):
        if self.visible:
            self.isHover()
            if not self.hover:
                img = pygame.image.load(self.img)
            else:
                img = pygame.image.load(self.hImg)
            window.blit(img, (self.x, self.y))
        else:
            self.hover = False
