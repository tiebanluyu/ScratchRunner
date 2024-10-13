import pygame

pygame.init()


class Label(object):
    def __init__(self, x: int = 0, y: int = 0, maxwidth: int = 0, text: str = "Text", font: str = 'calibri',
                 fontSize:int = 11, bold: bool = False, italic: bool = False, color: tuple = (0, 0, 0),
                 background: tuple = (255, 255, 255), transparentBackground: bool = True, visible: bool = True,
                 centered: bool = False):
        self.x = x
        self.y = y
        self.maxwidth = maxwidth
        self.text = text
        self.font = font
        self.fs = fontSize
        self.bold = bold
        self.italic = italic
        self.color = color
        self.bg = background
        self.transparent = transparentBackground
        self.visible = visible
        self.center = centered

    def draw(self, win):
        if self.visible:
            if not self.transparent:
                bg = self.bg
            else:
                bg = None
            fs = self.fs
            if not self.font.endswith(".ttf"):
                font = pygame.font.SysFont(self.font, fs, self.bold, self.italic)
            else:
                font = pygame.font.Font(self.font, self.fs)
                font.bold = self.bold
                font.italic = self.italic
            text = font.render(self.text, True, self.color, bg)
            text_width = text.get_width()
            if self.maxwidth > 0:
                while text_width > self.maxwidth:
                    fs -= 1
                    font = pygame.font.SysFont(self.font, fs, self.bold, self.italic)
                    text = font.render(self.text, True, self.color, bg)
                    text_width = text.get_width()
            if self.maxwidth > 0 and self.center:
                textX = (self.x + (self.maxwidth // 2)) - text_width // 2
            else:
                textX = self.x
            win.blit(text, (textX, self.y))

    def changeText(self, text: str):
        self.text = text

    def toggleVisibility(self):
        self.visible = not self.visible

    def getVisibility(self):
        return self.visible




