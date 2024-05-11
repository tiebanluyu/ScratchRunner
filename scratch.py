import json ,pygame
t=json.loads(open("project.json","r",encoding="utf-8").read())

class Sprite:
    def __init__(self,dict1) -> None:

        self.__dict__.update(dict1)
        #print(self.name)


    
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

# 设置矩形位置和大小
rect_x = 50
rect_y = 50
rect_width = 50
rect_height = 50

# 设置颜色
red = (255, 0, 0)

# 游戏循环
done = False
while not done:
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # 填充窗口颜色
    screen.fill((255, 255, 255))

    pygame.blit("costume1.svg")

    # 更新窗口
    pygame.display.update()

# 退出Pygame 