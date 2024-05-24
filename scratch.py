import json #需要读取project.json
import pygame #vscode检测不到pygame type: ignore
import threading#多线程并行需要
from math import sin,cos,radians
import logging
# 设置窗口大小
STAGE_SIZE = (480, 360)
POSITION = (0,0)
flag:str
logging.basicConfig(level=logging.DEBUG)
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




def S_eval(sprite:"Sprite",flag:str)->dict:

    result={}
    input1:dict=sprite.blocks[flag]["inputs"]
    for i,j in input1.items():
        if isinstance(j[1],list):
            result[i]=j[1][1]
        else:
            result[i]=runcode(j[1])
    return result        
class Sprite():
    def __init__(self,dict1:dict) -> None:
        for name,value in dict1.items():#原来仅仅改变__dict__会带来问题

            setattr(self, name, value)
        #self.x=1
        #print(self.name)
    def draw(self)->None:
        image = pygame.image.load(self.costumes[self.currentCostume]["md5ext"])
        image = pygame.transform.rotate(image, self.direction+90)
        screen.blit(image, positionmap(self.x, self.y))
        #self.x=1
        #print(self.x,self.y)
    def motion_movesteps(self,flag:str) -> None :
        steps:int=int(S_eval(self,flag)["STEPS"]) 
        #logging.info(self.direction)

        x=steps*sin(radians(self.direction))
        y=steps*cos(radians(self.direction))
        self.x+=x;self.y+=y
    def motion_gotoxy(self,flag:str) -> None:
        dic=S_eval(self,flag)
        self.x=int(dic["X"])  
        self.y=int(dic["Y"])
    def motion_turnright(self,flag:str) -> None:
        addition=S_eval(self,flag)["DEGREES"]
        self.direction+=int(addition)
    def event_whenflagclicked(self,flag) -> None:
        runcode(self,self.blocks[flag]["next"]  ) 
    def control_if(self,flag:str) -> None:

        if S_eval(self,flag):
            runcode(self,flag)  
    def control_forever(self,flag:str) -> None:
        #logging.debug("111")
        
        while 1:
            #self.x=1
            runcode(self,self.blocks[flag]["inputs"]["SUBSTACK"][1])           

def runcode(sprite:Sprite,flag:str)->any:
    global done
    if done:
        
        exit()
    logging.info("将进入"+sprite.name+"的"+sprite.blocks[flag]["opcode"]+"函数")
    sprite.__getattribute__(sprite.blocks[flag]["opcode"])(flag)
    clock.tick(20)
    if sprite.blocks[flag]["next"]!=None:#如果还有接着的积木，执行下去  
        runcode(sprite=sprite,flag=sprite.blocks[flag]["next"])  
def run(sprite:"Sprite") -> None:
    flag:str
    code:dict

    logging.info(sprite.name+"进入run函数")
    
    
    for flag,code in sprite.blocks.items():#code是字母后面的括号
        if code["opcode"]=="event_whenflagclicked":
            #print(flag)
            flag=code["next"]
            runcode(sprite,flag)


#主程序从这里开始            
t=json.loads(open("project.json","r",encoding="utf-8").read())   
#print(t["targets"][1]["y"]) 
sprite_list=[]
threads=[]
done = False#done是用来标记程序是否运行，False代表运行，true代表结束
clock = pygame.time.Clock()
for i in t["targets"]:
    i:dict
    
    sprite=Sprite(i)
    sprite_list.append(sprite)
    #sprite.x=t["targets"][1]["y"]
    #print(sprite,sprite.name)
    td = threading.Thread(target=run, name=sprite.name,args=(sprite,))
    threads.append(td)
    td.start()


# 初始化Pygame
pygame.init()
screen = pygame.display.set_mode(STAGE_SIZE)

# 设置窗口标题
pygame.display.set_caption("My Game")




#sprite_list[1].x=0;sprite_list[1].y=0;sprite_list[1].direction=0#我那天脑残写了这行
while not done:
    # 处理事件
    #sprite_list[1].motion_gotoxy("a")
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
            #i.x=100
            i.draw()

    
    

    # 更新窗口
    pygame.display.update()
    clock.tick(20)

# 退出Pygame 
logging.info("退出程序")