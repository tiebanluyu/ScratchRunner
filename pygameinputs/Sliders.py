import pygame

pygame.init()


class VerticalSlider(object):
    def __init__(self, x: int = 30, y: int = 30, width: int = 5, height: int = 200, handleWidth: int = 10,
                 color: tuple = (20, 20, 20), sliderColor: tuple = (200, 0, 0), handleColor: tuple = (50, 50, 50),
                 sliderPercent: int = 50, visible: bool = True):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.handle = handleWidth
        self.handleColor = handleColor
        self.color = color
        self.sliderColor = sliderColor
        self.sliderPercent = sliderPercent
        self.visible = visible
        self.hover = False
        self.active = False

    def draw(self, window):
        if self.visible:
            self.isHover()
            pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))

            if self.active:
                mouse = pygame.mouse.get_pos()[1]
                if mouse <= self.y:
                    handlePosY = self.y
                elif mouse >= self.y + self.height - self.handle:
                    handlePosY = self.y + self.height - self.handle
                else:
                    handlePosY = mouse
                self.sliderPercent = (50 * (self.handle + (2 * handlePosY) - (2 * self.y))) / self.height
            else:
                handlePosY = round(self.y + (self.height * (self.sliderPercent / 100)) - (round(self.handle / 2)))
            height = handlePosY - self.y
            handlePosX = self.x - (self.handle // 2) + self.width // 2
            pygame.draw.rect(window, self.sliderColor, (self.x, self.y, self.width, height))
            pygame.draw.rect(window, self.handleColor, (handlePosX, handlePosY, self.handle, self.handle))

    def isHover(self):
        mouse = pygame.mouse.get_pos()

        if mouse[0] >= self.x - (self.handle // 2) and mouse[0] <= self.x + (self.handle // 2):
            if mouse[1] >= self.y and mouse[1] <= self.y + self.height:
                self.hover = True
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                self.hover = False
        else:
            self.hover = False

    def getPressed(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.hover:
            self.active = True
            return True
        elif self.active and event.type == pygame.MOUSEBUTTONUP:
            self.active = False
            return False
        else:
            return False

    def getPercent(self):
        return self.sliderPercent

    def setPercent(self, percent: int):
        if percent < 0 or percent > 100:
            raise Exception(f"Slider Error: Takes an integer between 0 and 100 not {percent}")
        self.sliderPercent = percent

    def setVisible(self, visible: bool):
        self.visible = visible


class HorizontalSlider(object):
    def __init__(self, x: int = 0, y: int = 5, width: int = 200, height: int = 5, handleWidth: int = 10,
                 color: tuple = (20, 20, 20), sliderColor: tuple = (200, 0, 0), handleColor: tuple = (50, 50, 50),
                 sliderPercent: int = 50, visible: bool = True):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.handle = handleWidth
        self.handleColor = handleColor
        self.color = color
        self.sliderColor = sliderColor
        self.sliderPercent = sliderPercent
        self.visible = visible
        self.hover = False
        self.active = False

    def draw(self, window):
        if self.visible:
            self.isHover()
            pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))

            if self.active:
                mouse = pygame.mouse.get_pos()[0]
                if mouse <= self.x:
                    handlePosX = self.x
                elif mouse >= self.x + self.width - self.handle:
                    handlePosX = self.x + self.width - self.handle
                else:
                    handlePosX = mouse
                self.sliderPercent = (50 * (self.handle + (2 * handlePosX) - (2 * self.x))) / self.width
            else:
                handlePosX = round(self.x + (self.width * (self.sliderPercent / 100)) - (round(self.handle / 2)))
            width = handlePosX - self.x
            handlePosY = self.y - (self.handle // 2) + self.height // 2
            pygame.draw.rect(window, self.sliderColor, (self.x, self.y, width, self.height))
            pygame.draw.rect(window, self.handleColor, (handlePosX, handlePosY, self.handle, self.handle))

    def isHover(self):
        mouse = pygame.mouse.get_pos()

        if mouse[0] >= self.x and mouse[0] <= self.x + self.width:
            if mouse[1] >= self.y - (self.handle // 2) and mouse[1] <= self.y + (self.handle // 2):
                self.hover = True
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                self.hover = False
        else:
            self.hover = False

    def getPressed(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.hover:
            self.active = True
            return True
        elif self.active and event.type == pygame.MOUSEBUTTONUP:
            self.active = False
            return False
        else:
            return False

    def getPercent(self):
        return self.sliderPercent

    def setPercent(self, percent: int):
        if percent < 0 or percent > 100:
            raise Exception(f"Slider Error: Takes an integer between 0 and 100 not {percent}")
        self.sliderPercent = percent

    def setVisible(self, visible: bool):
        self.visible = visible



