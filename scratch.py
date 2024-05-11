import json 
import pygame # type: ignore
# 设置窗口大小
size = (480, 360)
position = (0,0)
origin_x = size[0] // 2
origin_y = size[1] // 2
 
# 自定义坐标转换函数
def positionmap(x:int, y):
    new_x = x + origin_x
    new_y = -y + origin_y
    return new_x, new_y


t=json.loads(open("project.json","r",encoding="utf-8").read())

class Sprite():
    def __init__(self,dict1) -> None:

        self.__dict__.update(dict1)
        #print(self.name)
    def draw(self):
        image = pygame.image.load(self.costumes[self.currentCostume]["md5ext"])
        screen.blit(image, positionmap(self.x, self.y))
    codes={"forward":lambda self,x:exec("self.x+=x")}    
def runcode(sprite,flag):
    code=sprite.block[flag]
    if code["opcode"]=="motion_turnright":
        self.angle+=###########################################
def run(sprite):
    for flag,code in sprite.block.items():
        if code["opcode"]=="event_whenflagclicked":
            flag=code[next]
            runcode(sprite,flag)

            
    
list1=[]
for i in t["targets"]:
    
    o=Sprite(i)
    list1.append(o)
    print(o,o.name)


# 初始化Pygame
pygame.init()

# 设置窗口大小
size = (480, 360)
position = (0,0)

screen = pygame.display.set_mode(size)

# 设置窗口标题
pygame.display.set_caption("My Game")



done = False

while not done:
    # 处理事件
    list1[1].x+=__import__("random").random()*0.01
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # 填充窗口颜色
    screen.fill((255, 255, 255))
    for i in list1:
        if not i.isStage:
            i.draw()

    

    # 更新窗口
    pygame.display.update()

# 退出Pygame 