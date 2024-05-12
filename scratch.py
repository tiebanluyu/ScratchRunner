import json #需要读取project.json
import pygame #vscode检测不到pygame type: ignore
import threading#多线程并行需要
from math import sin,cos

# 设置窗口大小
STAGE_SIZE = (480, 360)
POSITION = (0,0)

 
# 自定义坐标转换函数
ORIGIN_X = STAGE_SIZE[0] // 2
ORIGIN_Y = STAGE_SIZE[1] // 2
#本应将这两个放入positionmap函数，但每次都要除一次太费事了
def positionmap(x:int, y:int)->tuple:
    """
    自定义坐标转换函数
    pygame的坐标系不一样，要将其转换成sctatch的坐标系
    
    
    """
    new_x = x + ORIGIN_X
    new_y = -y + ORIGIN_Y
    return new_x, new_y




def S_eval(sprite,flag:str)->dict:

    result={}
    input1=sprite.blocks[flag]["inputs"]
    for i,j in input1.items():
        if isinstance(j[1],list):
            result[i]=j[1][1]################
        else:
            result[i]=runcode(j[1])
    return result        
class Sprite():
    def __init__(self,dict1:dict) -> None:

        self.__dict__.update(dict1)
        #print(self.name)
    def draw(self)->None:
        image = pygame.image.load(self.costumes[self.currentCostume]["md5ext"])
        image = pygame.transform.rotate(image, self.direction+90)
        screen.blit(image, positionmap(self.x, self.y))
    def motion_turnright(self,flag):
        addition=S_eval(self,flag)["DEGREES"]
        self.direction+=int(addition)
    def event_whenflagclicked(self,flag):
        runcode(self,self.blocks[flag]["next"]  ) 
    def control_if(self,flag):
        if S_eval(self,flag):
            runcode(self,flag)  
    def control_forever(self,flag):
        while 1:
            runcode(self,self.blocks[flag]["inputs"]["SUBSTACK"][1])           

def runcode(sprite:Sprite,flag:str)->any:
    global done
    if done:
        exit()

    #code=sprite.blocks[flag]
    #print(sprite.blocks[flag]["opcode"],flag)
    sprite.__getattribute__(sprite.blocks[flag]["opcode"])(flag)
    clock.tick(20)    
def run(sprite):
    flag:str
    code:dict
    
    for flag,code in sprite.blocks.items():#code是字母后面的括号
        if code["opcode"]=="event_whenflagclicked":
            print(flag)
            flag=code["next"]
            runcode(sprite,flag)


#主程序从这里开始            
t=json.loads(open("project.json","r",encoding="utf-8").read())    
sprite_list=[]
threads=[]
done = False
clock = pygame.time.Clock()
for i in t["targets"]:
    
    o=Sprite(i)
    sprite_list.append(o)
    print(o,o.name)
    td = threading.Thread(target=run, name=o.name,args=(o,))
    threads.append(td)
    td.start()


# 初始化Pygame
pygame.init()
screen = pygame.display.set_mode(STAGE_SIZE)

# 设置窗口标题
pygame.display.set_caption("My Game")




sprite_list[1].x=0;sprite_list[1].y=0;sprite_list[1].direction=0
while not done:
    # 处理事件
    #list1[1].forward(1)
    #breakpoint()
    #list1[1].motion_turnright("c")
    #list1[1].direction+=1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # 填充窗口颜色
    screen.fill((255, 255, 255))

    for i in sprite_list:
        if not i.isStage:
            i.draw()

    
    

    # 更新窗口
    pygame.display.update()
    clock.tick(20)

# 退出Pygame 
