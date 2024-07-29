import json #需要读取project.json
import pygame 
import threading#多线程并行需要
from math import sin,cos,radians
import logging
import time
from rotate import blitRotate
FPS=50
TPS=50
# 设置窗口大小
STAGE_SIZE = (480, 360)
POSITION = (0,0)

logging.basicConfig(level=logging.DEBUG,format='[%(levelname)s] line%(lineno)s-%(message)s')


# 自定义坐标转换函数
def positionmap1(x:int, y:int)->tuple:
    """

    自定义坐标转换函数
    pygame的坐标系不一样，要将其转换成sctatch的坐标系 
    从scratch坐标系到pygame   
    
    """
    ORIGIN_X = STAGE_SIZE[0] // 2
    ORIGIN_Y = STAGE_SIZE[1] // 2
    new_x = x + ORIGIN_X
    new_y = -y + ORIGIN_Y
    return new_x, new_y
def positionmap2(x:int, y:int)->tuple:
    """
    自定义坐标转换函数
    pygame的坐标系不一样，要将其转换成sctatch的坐标系    
    从pygame到scratch
    
    """
    ORIGIN_X = STAGE_SIZE[0] // 2
    ORIGIN_Y = STAGE_SIZE[1] // 2
    new_x =  x-ORIGIN_X
    new_y =  ORIGIN_Y-y
    return new_x, new_y



def S_eval(sprite:"Sprite",flag:str)->dict:
    """
    这个函数是根据角色和flag,求值.返回一个dict,其中整合了参数
    如sprite的flag的内容如下
    "a": {
          "opcode": "motion_gotoxy",
          "next": "b",
          "parent": "e",
          "inputs": { "X": [1, [4, "0"]], "Y": [1, [4, "0"]] },
          "fields": {},
          "shadow": false,
          "topLevel": false
        }
    
    则返回值为
    {'X': '0', 'Y': '0'}
     
    """
    

    result={}
    input1:dict=sprite.blocks[flag]["inputs"]
    if sprite.blocks[flag]["opcode"]=="motion_goto_menu" :
        #logging.debug(sprite.blocks[flag]["fields"]["TO"][0])
        return {"TO":sprite.blocks[flag]["fields"]["TO"][0]}
    for i,j in input1.items():
        if isinstance(j[1],list):
            result[i]=j[1][1]
        else:
            result[i]=runcode(sprite,j[1])
    logging.debug(result)
    
    return result   
     
class Sprite():
    def __init__(self,dict1:dict) -> None:        
        for name,value in dict1.items():#原来仅仅改变__dict__会带来问题
            setattr(self, name, value)
    def __str__(self):
        return self.name
    def __repr__(self):
        return self.name
    
    def draw(self)->None:
        costume=self.costumes[self.currentCostume]
        
        image = pygame.image.load(costume["md5ext"])
        if "svg" != costume["dataFormat"]:
            image=pygame.transform.rotozoom(image, 0, 0.5)#位图精度高，实际储存时图像会大一些
        if self.isStage:            
            screen.blit(image,(0,0))
            return
        
        direction=self.direction#不是stage才有direction
        
        #logging.debug(image.get_size())
        #logging.info(self.x+costume["rotationCenterX"])  +(w*cos(radians(direction-180))-h) -(h-h*cos(radians(direction-90)))
        #image = pygame.transform.rotate(image, -(self.direction-90))
        direction%=360
        #image=custom_rotate(image, 90-direction, (100,0))
        #这里解决角度超出[0,360]范围的问题，角度来不及换算会带来问题
        x,y=positionmap1(self.x,self.y)   
        #blitRotate(screen, image, pos, (w/2, h/2), angle) 
        #screen.blit(image,(x,y))
                    
        w, h = image.get_size() 
        #logging.debug((w,h))     
        rotatecentre=costume["rotationCenterX"],costume["rotationCenterY"] 
        #pos = (screen.get_width()/2, screen.get_height()/2)
        #logging.info((x,y,w,h))
        blitRotate(screen, image, (x,y), rotatecentre, 90-direction)
        
        #scratch造型的rotationCenterY是以左上角为原点，向右向下为正表述的
    def motion_goto(self,flag) -> None:
        dict1=S_eval(self,flag)
        logging.debug(dict1)
        to=dict1["TO"]
        self.x,self.y=to    
    def motion_goto_menu(self,flag)-> tuple[float, float]:
        dict1=S_eval(self,flag)
        logging.debug(dict1)
        to=dict1["TO"]
        if to=="_random_":
            import random
            y=random.uniform(-180,180)
            x=random.uniform(-240,240)
            logging.debug(positionmap2(x,y))
            return (x,y)
        if to=="_mouse_":
            mousepos=pygame.mouse.get_pos()
            
            return positionmap2(mousepos[0],mousepos[1])
            
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
    def motion_turnleft(self,flag:str) -> None:
        addition=S_eval(self,flag)["DEGREES"]
        self.direction-=int(addition)    
    def event_whenflagclicked(self,flag) -> None:
        runcode(self,self.blocks[flag]["next"]  ) 
    def control_if(self,flag:str) -> None:

        if S_eval(self,flag):
            runcode(self,flag)  
    def control_repeat(self,flag)-> None:
        dic=S_eval(self,flag)
        for _ in range(int(dic["TIMES"])):
            runcode(self,self.blocks[flag]["inputs"]["SUBSTACK"][1])       
    def control_forever(self,flag:str) -> None:
        #logging.debug("111")
        
        while 1:
            #self.x=1
            runcode(self,self.blocks[flag]["inputs"]["SUBSTACK"][1])  
    def control_wait(self,flag:str) -> None:        
        
        sleeptime=float(S_eval(self,flag)["DURATION"])
        time.sleep(sleeptime)   
    def motion_pointindirection(self,flag)->None:
        direction=float(S_eval(self,flag)["DIRECTION"])
        self.direction=direction                  

def runcode(sprite:Sprite,flag:str)->any:
    logging.debug(sprite.direction)
    
    global done
    if done:        
        exit()
    #logging.debug(("1234",sprite,flag))
    if flag==None :
        #logging.debug(f"flag==None,{sprite.direction}")
        #sprite.direction+=1
        #time.sleep(1)
        return
    #logging.debug(("34567",sprite,flag))
    
    sprite.direction%=360#这里解决角度超出[0,360]范围的问题

    logging.info("将进入"+sprite.name+"的"+sprite.blocks[flag]["opcode"]+"函数")
    result=None
    try:
        result=sprite.__getattribute__(sprite.blocks[flag]["opcode"])(flag)
    except AttributeError:
        logging.error("缺少函数"+sprite.blocks[flag]["opcode"])    
    clock.tick(TPS)
    if sprite.blocks[flag]["next"]!=None:#如果还有接着的积木，执行下去  
        runcode(sprite=sprite,flag=sprite.blocks[flag]["next"])  
    return result    

def run(sprite:"Sprite") -> None:
    

    flag:str
    code:dict

    logging.info(sprite.name+"进入run函数")   
    for flag,code in sprite.blocks.items():#code是字母后面的括号
        if code["opcode"]=="event_whenflagclicked":
            #print(flag)
            flag=code["next"]
            runcode(sprite,flag)
    logging.info(f"{sprite}执行完毕")        

def main():
    global screen,done,clock
    #主程序从这里开始            
    t=json.loads(open("project.json","r",encoding="utf-8").read())   
    sprite_list=[]#角色们
    threads=[]#执行线程们
    done = False#done是用来标记程序是否运行，False代表运行，true代表结束
    clock = pygame.time.Clock()
    for i in t["targets"]:
        i:dict
    
        sprite=Sprite(i)
        sprite_list.append(sprite)
        td = threading.Thread(target=run, name=sprite.name,args=(sprite,))
        threads.append(td)
        td.start()#开启执行线程


    # 初始化Pygame
    pygame.init()
    screen = pygame.display.set_mode(STAGE_SIZE)

    # 设置窗口标题
    pygame.display.set_caption("My Game")

    # 渲染线程主循环
    while not done:
    # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        # 填充窗口颜色
        screen.fill((255, 255, 255))

        # 逐个角色更新窗口
        for i in sprite_list:        
            i.draw()

        # 更新窗口
        pygame.display.update()
        clock.tick(FPS)

    # 退出Pygame 
    logging.info("退出程序")



if __name__=="__main__":
    main()    