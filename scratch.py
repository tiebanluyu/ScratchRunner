import json  # 需要读取project.json
import pygame
import threading  # 多线程并行需要
from math import sin, cos, radians
import math
import logging
import random
import zipfile
import os
from drawtext import *
import time
from typing import List, Tuple,Literal

logging.basicConfig(
    level=logging.DEBUG, format="[%(levelname)s] line%(lineno)s-%(message)s"
)

from time import sleep
from rotate import blitRotate
from variable import *
FPS:int = 50
TPS:int = 50
# 设置窗口大小
STAGE_SIZE = (480, 360)
STAGE_SHOW_SIZE=(960, 720)
POSITION = (0, 0)


# 自定义坐标转换函数
def positionmap1(x: int, y: int) -> tuple[int,int]:
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


def positionmap2(x: int, y: int) -> tuple[int,int]:
    """
    自定义坐标转换函数
    pygame的坐标系不一样，要将其转换成sctatch的坐标系
    从pygame到scratch

    """
    ORIGIN_X = STAGE_SIZE[0] // 2
    ORIGIN_Y = STAGE_SIZE[1] // 2
    new_x = x - ORIGIN_X
    new_y = ORIGIN_Y - y
    return new_x, new_y


def S_eval(sprite: "Sprite", flag: str) -> dict:
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

    
    input1: dict = sprite.blocks[flag]["inputs"].copy()#要改动
    field1: dict = sprite.blocks[flag]["fields"]
    result = {}
    words_shouldnotrun=["SUBSTACK","SUBSTACK2","SUBSTACK3"]
    for key, value in input1.copy().items():#copy防止修改原字典报错
        if key.upper() in words_shouldnotrun:
            result[key.upper()]=value[1]
            input1.pop(key)
    for key, value in field1.items():
        if "VARIABLE" == key:#variable有两个属性，取第二个id，第一个是变量名
            result[key.upper()] = value[1]
        else:
            result[key.upper()] = value[0]
    for key, value in input1.items():
        #logging.debug((key, value))
        if value[1][0].__class__==int:
            result[key.upper()] = value[1][1]
        else:
            result[key.upper()]=runcode(sprite,value[1])    
        

    #logging.debug(result) 
    return result   
def getvaluable(sprite,id) -> str:
    
    if id in stage.variables:
        return safe_str(stage.variables[id])
    if id in sprite.variables:
        return safe_str(sprite.variables[id])
    
def setvaluable(sprite,id,obj) -> None:
    #print(sprite,id,obj)
    logging.debug(stage.variables)
    if id in stage.variables:
        stage.variables[id]= safe_str(obj)
        
    elif id in sprite.variables:
        sprite.variables[id]=safe_str(obj)
def getlist(sprite,id):
    #logging.debug((sprite,id,stage.lists,sprite.lists))
    if id in stage.lists:
        return stage.lists[id]
    if id in sprite.lists:
        return sprite.lists[id]


class Sprite(pygame.sprite.Sprite):
    def __init__(self, dict1: dict) -> None:
        super().__init__()
        for name, value in dict1.items():  # 原来仅仅改变__dict__会带来问题
            setattr(self, name, value)
        self.words=""    #没说话

    def __str__(self) ->str:
        return self.name

    def __repr__(self)->str:
        return self.name

    def draw(self) -> None:
        costume = self.costumes[self.currentCostume]
        
        try:
            image = pygame.image.load(costume["md5ext"])
        except:
            image = pygame.image.load(costume["assetId"]+"."+costume["dataFormat"])    
        if "svg" != costume["dataFormat"]:
            image = pygame.transform.rotozoom(
                image, 0, 0.5
            )  # 位图精度高（否则一个一个点不美观），实际储存时图像会大一些
        if self.isStage:
            screen.blit(image, (0, 0))
            return
        if not self.visible:
            return
        
        image = pygame.transform.rotozoom(
                image, 0, self.size/100
            )
        direction = self.direction % 360  # 不是stage才有direction
        x, y = positionmap1(self.x, self.y)
        rotatecentre = costume["rotationCenterX"]*(self.size/100), costume["rotationCenterY"]*(self.size/100)
        self.image,self.rect=blitRotate(
            screen, image, (x, y), rotatecentre, 90 - direction
        )  # 他山之石可以攻玉
        self.mask = pygame.mask.from_surface(self.image)
        drawtext(self,screen)

    def motion_goto(self, flag) -> None:
        dict1 = S_eval(self, flag)
        to = dict1["TO"]
        self.x, self.y = to

    def motion_goto_menu(self, flag) -> tuple[float, float]|None:
        dict1 = S_eval(self, flag)

        to = dict1["TO"]
        if to == "_random_":
            

            y = random.uniform(-180, 180)
            x = random.uniform(-240, 240)
            return (x, y)
        if to == "_mouse_":
            mousepos = pygame.mouse.get_pos()
            return positionmap2(mousepos[0], mousepos[1])
        return None

    motion_glideto_menu = motion_goto_menu

    def motion_movesteps(self, flag: str) -> None:
        steps: int = safe_int(S_eval(self, flag)["STEPS"])
        # logging.info(self.direction)

        x = steps * sin(radians(self.direction))
        y = steps * cos(radians(self.direction))
        self.x += x
        self.y += y

    def motion_gotoxy(self, flag: str) -> None:
        dic = S_eval(self, flag)
        self.x = safe_int(dic["X"])
        self.y = safe_int(dic["Y"])
        #print(dic)

    def motion_turnright(self, flag: str) -> None:
        addition = S_eval(self, flag)["DEGREES"]
        self.direction += safe_int(addition)

    def motion_turnleft(self, flag: str) -> None:
        addition = S_eval(self, flag)["DEGREES"]
        self.direction -= safe_int(addition)

    def event_whenflagclicked(self, flag) -> None:
        runcode(self, self.blocks[flag]["next"])

    def control_if(self, flag: str) -> None:
        dic=S_eval(self,flag)
        logging.debug(dic)
        if dic["CONDITION"]=="True":
            runcode(self,dic["SUBSTACK"])
    def control_if_else(self, flag: str) -> None:
        dic=S_eval(self,flag)
        logging.debug(dic)
        if dic["CONDITION"]=="True":
            runcode(self, dic["SUBSTACK"])
        else:
            runcode(self, dic["SUBSTACK2"])   
    def control_wait_until(self,flag):
        dic=S_eval(self,flag)
        condition=dic["CONDITION"]
        logging.debug(condition)
        while 1:
            if runcode(self,condition)=="True":
                break         
    def control_repeat(self, flag) -> None:
        dic = S_eval(self, flag)
        for _ in range(safe_int(dic["TIMES"])):
            if self.clone_mode==2:
                break
            runcode(self, self.blocks[flag]["inputs"]["SUBSTACK"][1])

    def control_forever(self, flag: str) -> None:

        while 1:
            # self.x=1
            if self.clone_mode==2:
                break
            runcode(self, self.blocks[flag]["inputs"]["SUBSTACK"][1])

    def control_wait(self, flag: str) -> None:

        sleeptime = float(S_eval(self, flag)["DURATION"])
        sleep(sleeptime)

    def motion_pointindirection(self, flag:str) -> None:
        direction = float(S_eval(self, flag)["DIRECTION"])
        self.direction = direction

    def motion_glideto(self, flag) -> None:
        dic = S_eval(self, flag)
        secs, to = dic["SECS"], dic["TO"]
        vec = ((to[0] - self.x) / 100, (to[1] - self.y) / 100)
        for _ in range(100):
            sleep(float(secs) / 100)
            self.x += vec[0]
            self.y += vec[1]

    def motion_glidesecstoxy(self, flag:str) -> None:
        dic = S_eval(self, flag)
        secs, x, y = dic["SECS"], dic["X"], dic["Y"]
        x = float(x)
        y = float(y)
        vec = ((x - self.x) / 100, (y - self.y) / 100)
        for _ in range(100):
            sleep(float(secs) / 100)
            self.x += vec[0]
            self.y += vec[1]

    def motion_setx(self, flag:str) -> None:
        x = S_eval(self, flag)["X"]
        self.x = float(x)

    def motion_sety(self, flag:str) -> None:
        y = S_eval(self, flag)["Y"]
        self.y = float(y)

    def motion_changexby(self, flag:str) -> None:
        dx = S_eval(self, flag)["DX"]
        self.x += float(dx)

    def motion_changeyby(self, flag:str) -> None:
        dy = S_eval(self, flag)["DY"]
        self.y += float(dy)

    def motion_pointtowards(self, flag:str) -> None:
        dic = S_eval(self, flag)
        self.direction = safe_float(dic["TOWARDS"])

    def motion_pointtowards_menu(self, flag:str):
        dic = S_eval(self, flag)
        if dic["TOWARDS"] == "_mouse_":
            mousepos = pygame.mouse.get_pos()
            mousepos = positionmap2(mousepos[0], mousepos[1])
            dx = mousepos[0] - self.x
            dy = mousepos[1] - self.y
            direction = 90 - math.degrees(math.atan2(dy, dx))
            return direction
        else:
            import random

            direction = random.uniform(0, 360)
            return direction

    def motion_ifonedgebounce(self, flag:str=None):
        # 其实遇到边缘就反弹没有任何参数   
        #logging.debug((self.x>0,((self.direction%360)>180)))    
        if not (0 <=self.rect.left <= self.rect.right <= 480):
            
            if (self.x>0)+((self.direction%360)>180)==1:#在已经转向的情况下不会转回去
                self.direction = -self.direction
                logging.debug("碰撞")
            """
            if self.x < 0:
                self.x = -480 - self.x
            else:
                self.x = 480 - self.x"""

        #logging.debug((self.y>0,( (90<(self.direction%360)<270)))) 
        if not (0 <= self.rect.top <= self.rect.bottom <= 360):
            if bool(self.y>0)+(90<(self.direction%360)<270)==1:#没好
                #self.direction = -self.direction
                logging.debug("碰撞")
               
                    #if (self.y>0)+(not (90<(self.direction%360)<270))==1:#在已经转向的情况下不会转回去
                #self.direction = -self.direction
                #logging.debug("碰撞")
                self.direction = 180 - self.direction
            #logging.debug("碰撞")
    def motion_xposition(self,flag=None) ->str:#取前9位，否则变量显示太难看
        return safe_str(self.x)[0:9]
    def motion_yposition(self,flag=None) ->str:
        return safe_str(self.y)[0:9]
    def motion_direction(self,flag=None) ->str:
        return safe_str(self.direction)[0:9]            
    def operator_add(self,flag) -> str:
        #logging.debug("hello")
        dic=S_eval(self,flag)
        num1=safe_float(dic["NUM1"])
        num2=safe_float(dic["NUM2"])     
        #logging.debug(safe_str(num1+num2))   
        return safe_str(num1+num2)
    def operator_subtract(self,flag) -> str:
        dic=S_eval(self,flag)
        num1=safe_float(dic["NUM1"])
        num2=safe_float(dic["NUM2"])        
        return safe_str(num1-num2)
    def operator_multiply(self,flag) -> str:
        dic=S_eval(self,flag)
        num1=safe_float(dic["NUM1"])
        num2=safe_float(dic["NUM2"])        
        return safe_str(num1*num2)    
    def operator_divide(self,flag) -> str:
        dic=S_eval(self,flag)
        num1=safe_float(dic["NUM1"])
        num2=safe_float(dic["NUM2"])        
        return safe_str(num1/num2)   
    def looks_say(self,flag):
        dic=S_eval(self,flag)
        message=dic["MESSAGE"]
        self.words=message
    looks_think=looks_say    
    def looks_sayforsecs(self,flag):
        dic=S_eval(self,flag)
        secs=safe_float(dic["SECS"])
        message=safe_str(dic["MESSAGE"])
        self.words=message
        sleep(secs)
        self.words=""
    looks_thinkforsecs=looks_sayforsecs    
    def looks_switchcostumeto(self,flag):
        #logging.debug("dic")
        dic=S_eval(self,flag)
        logging.debug(dic)
        # self.currentcostome=
        count=0
        for costume in self.costumes:
            #logging.debug(costome["name"])
            #logging.debug(dic["COSTUME"])
            if costume["name"]==dic["COSTUME"]:
                self.currentCostume=count                
                break
            count+=1
    def looks_costume(self,flag):
        dic=S_eval(self,flag)
        #logging.debug(dic)
        return dic["COSTUME"]
    def looks_show(self,flag=None):
        self.visible=True
    def looks_hide(self,flag):
        self.visible=False    
    def looks_nextcostume(self,flag=None):
        costumecount=len(self.costumes)
        self.currentCostume+=1
        if self.currentCostume==costumecount:
            self.currentCostume=0    
    def looks_changesizeby(self,flag):
        dic=S_eval(self,flag)
        #logging.debug(dic)
        self.size+=float(dic["CHANGE"]) 
    def looks_setsizeto(self,flag):
        dic=S_eval(self,flag)
        #logging.debug(dic)       
        self.size=float(dic["SIZE"]) 
    def looks_switchbackdropto(self,flag):
        dic=S_eval(self,flag)
        #logging.debug(dic) 
        #stage.currentCostume=dic["BACKDROP"]
        count=0
        for costume in stage.costumes:
            if costume["name"]==dic["BACKDROP"]:
                stage.currentCostume=count                
                break
            count+=1
    def looks_backdrops(self,flag):
        dic=S_eval(self,flag)
        #logging.debug(dic)
        return dic["COSTUME"]
    def looks_nextbackdrop(self,flag=None):
        costumecount=len(stage.costumes)
        stage.currentCostume+=1
        if stage.currentCostume==costumecount:
            stage.currentCostume=0    
    def looks_costumenumbername(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        if dic["TYPE"]=="number":
            return safe_str(self.currentCostume+1)  
        elif dic["TYPE"]=="name":
            return safe_str(self.costumes[self.currentCostume]["name"])  
    def looks_size(self,flag=None) -> str:
        return safe_str(self.size)
    def looks_backdropnumbername(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        if dic["TYPE"]=="number":
            return safe_str(stage.currentCostume+1)  
        elif dic["TYPE"]=="name":
            return safe_str(stage.costumes[stage.currentCostume]["name"])
    def operator_random(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        _from=dic["FROM"] 
        to=dic["TO"]
        if "." in _from+to:#浮点数
            _from=safe_float(_from);to=safe_float(to)
            _from,to=sorted((_from,to))
            return random.uniform(_from,to)
        else:
            _from=safe_int(_from);to=safe_int(to)
            _from,to=sorted((_from,to))
            return random.randint(_from,to)
          
    def operator_gt(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)    
        if IsNum(dic["OPERAND1"]) and IsNum(dic["OPERAND2"]):
            operand1=safe_float(dic["OPERAND1"])
            operand2=safe_float(dic["OPERAND2"])
        
            logging.debug((operand1,operand2))
            return safe_str(operand1>operand2)
        else:
            return safe_str(dic["OPERAND1"]>dic["OPERAND2"])        
    def operator_lt(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)    
        if IsNum(dic["OPERAND1"]) and IsNum(dic["OPERAND2"]):
            operand1=safe_float(dic["OPERAND1"])
            operand2=safe_float(dic["OPERAND2"])
        
            logging.debug((operand1,operand2))
            return safe_str(operand1<operand2)
        else:
            return safe_str(dic["OPERAND1"]<dic["OPERAND2"])
    def operator_equals(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)    
        if IsNum(dic["OPERAND1"]) and IsNum(dic["OPERAND2"]):
            operand1=safe_float(dic["OPERAND1"])
            operand2=safe_float(dic["OPERAND2"])
        
            logging.debug((operand1,operand2))
            return safe_str(math.isclose(operand1,operand2))
        else:
            return safe_str(dic["OPERAND1"]==dic["OPERAND2"])    
    def operator_and(self,flag) -> str:
        dic=S_eval(self,flag)
        #logging.debug(dic)
        return safe_str(safe_bool(dic["OPERAND1"]) and safe_bool(dic["OPERAND2"]))
    def operator_or(self,flag) -> str:
        dic=S_eval(self,flag)
        #logging.debug(dic)
        return safe_str(safe_bool(dic["OPERAND1"]) or safe_bool(dic["OPERAND2"]))
    def operator_not(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        return safe_str(not safe_bool(dic["OPERAND"]))
    def operator_join(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        return safe_str(dic["STRING1"]+dic["STRING2"])
    def operator_letter_of(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        return safe_str(dic["STRING"][safe_int(dic["LETTER"])])
    def operator_length(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        return safe_str(len(dic["STRING"]))
    def operator_contains(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        return safe_str(dic["STRING2"] in dic["STRING1"])
    def operator_mod(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        num1=safe_int(dic["NUM1"])
        num2=safe_int(dic["NUM2"])
        return safe_str(num1%num2)
    def operator_round(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        return safe_str(round(safe_float(dic["NUM"])))
    def data_setvariableto(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        variable=dic["VARIABLE"]
        value=dic["VALUE"]
        #自己设置不可行，因为可能要动全局变量
        #self.variables[variable]=safe_str(value)
        setvaluable(self,variable,safe_str(value))
        logging.debug(self.variables)
    def data_changevariableby(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        variable=dic["VARIABLE"]
        value=dic["VALUE"]
        logging.debug((safe_float(value),safe_float(getvaluable(self,variable)),self.variables))
        setvaluable(self,
                    variable,
                    safe_str(safe_float(value)+safe_float(getvaluable(self,variable)))
                    )
        logging.debug(self.variables)
        logging.debug(stage.variables)
    def control_stop(self,flag):
        global done
        #logging.error("结束了")
        done=True
    def data_addtolist(self,flag):
        dic=S_eval(self,flag)
        #logging.debug(dic)
        thelist=getlist(self,dic["LIST"])
        thelist.append(safe_str(dic["ITEM"]))
        #logging.debug(thelist)   
    def data_deleteoflist(self,flag):
        dic=S_eval(self,flag)   
        logging.debug(dic)
        thelist:list[str]=getlist(self,dic["LIST"])
        thelist.pop(safe_int(dic["INDEX"])-1)

    def data_deletealloflist(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        thelist:list[str]=getlist(self,dic["LIST"])
        #thelist.pop(safe_int(dic["INDEX"])-1)
        thelist.clear()
    def data_itemoflist(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        thelist:list[str]=getlist(self,dic["LIST"])
        return safe_str(thelist[safe_int(dic["INDEX"])-1])
    def data_insertatlist(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        thelist:list[str]=getlist(self,dic["LIST"])
        thelist.insert(safe_int(dic["INDEX"])-1,safe_str(dic["ITEM"]))
    def data_replaceitemoflist(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        thelist:list[str]=getlist(self,dic["LIST"])
        thelist[safe_int(dic["INDEX"])-1]=safe_str(dic["ITEM"])  
    def data_itemnumoflist(self,flag):  
        dic=S_eval(self,flag)
        logging.debug(dic)
        thelist:list[str]=getlist(self,dic["LIST"]) 
        for i in thelist:
            if i==safe_str(dic["ITEM"]):
                return safe_str(thelist.index(i)+1)
        return safe_str(0)
    def data_lengthoflist(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        thelist:list[str]=getlist(self,dic["LIST"])
        return safe_str(len(thelist))
    def data_listcontainsitem(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        thelist:list[str]=getlist(self,dic["LIST"])
        return safe_str(safe_str(dic["ITEM"]) in thelist)
    def data_showlist(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        #thelist:list[str]=getlist(self,dic["LIST"])
        for i in moniter_list:
            if i.id==dic["LIST"]:
                i.visible=True
    def data_hidelist(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        #thelist:list[str]=getlist(self,dic["LIST"])
        for i in moniter_list:
            if i.id==dic["LIST"]:
                i.visible=False
    def control_create_clone_of(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        import copy
        newsprite=self.copy()
        newsprite.clone_mode=1
        clone_list.append(newsprite)
        thread_list=[]
        for flag, code in newsprite.blocks.items():
            if code["opcode"] == "control_start_as_clone":

                thread = threading.Thread(
                    name=str(newsprite) + flag+" clone", target=runcode, args=(newsprite, flag)
                )
                thread_list.append(thread)
                thread.start()
    def control_create_clone_of_menu(self,flag)-> dict:        
        dic=S_eval(self,flag)
        logging.debug(dic)
        return dic["CLONE_OPTION"]
    def copy(self):
        import copy
        return self.__class__(copy.copy(self.__dict__))
    def control_start_as_clone(self,flag):
        
        runcode(self,self.blocks[flag]["next"])
    def control_delete_this_clone(self,flag):
        if self.clone_mode==1:
            self.clone_mode=2   
    def sensing_keypressed(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        import keymap
        return safe_str(keys_pressed[keymap.keymap[dic["KEY_OPTION"]]])
    def sensing_keyoptions(self,flag):  
        dic=S_eval(self,flag)
        logging.debug(dic)
        return dic['KEY_OPTION']   
    def sensing_timer(self,flag=None):
        return safe_str(time.time()-stage.time)
    def sensing_resettimer(self,flag=None):
        stage.time=time.time()
    def collision(self,others:"Sprite"|Literal["_mouse_"]):
        logging.debug(others)   
        if others=="_mouse_":
            mouse_x,mouse_y=pygame.mouse.get_pos()
            others=Sprite({"x":mouse_x,"y":mouse_y,"name":"mouse"})
            others.mask=pygame.mask.Mask((10,10),True)
            logging.debug(others.mask)
        offset_x = others.x - self.x
        offset_y = others.y - self.y
        if self.mask.overlap(others.mask, (offset_x, offset_y)):
            print("角色碰撞了！")   
            return True 
        else:
            print("角色没碰撞")
            return False
    def sensing_touchingobject(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        if dic["TOUCHINGOBJECTMENU"]=="_mouse_":
            return safe_str(self.collision("_mouse_"))
        for i in sprite_list:
            if i.name==dic["TOUCHINGOBJECTMENU"]:
                return safe_str(self.collision(i))
        else:
            raise Exception("没有找到"+dic["TOUCHINGOBJECTMENU"]+"这个角色")    
    def sensing_touchingobjectmenu(self,flag):
        dic=S_eval( self,flag)  
        logging.debug(dic)
        return dic['TOUCHINGOBJECTMENU']
        
    
    
            
        


class Moniter:
    def __init__(self,dict1):
        for name, value in dict1.items():
            #logging.debug((name, value))
            setattr(self, name, value)
            
        if self.mode=="list":
            self.show_y=0    
        #logging.debug(self.mode)
    def draw(self):
        #logging.debug(self.__dict__)
        if not self.visible:
            return
        variablename=self.id
        sprite=stage#全局变量默认从stage中找
        for i in sprite_list:               
            if str(i)==self.spriteName:
                sprite=i
        if self.opcode=="data_variable":
                    
            value=getvaluable(sprite,variablename)
            #logging.debug(self.params["VARIABLE"])
            #logging.debug(value)
            text=" "+self.params["VARIABLE"]+":"+value+" "
            if sprite!=stage:
                text=" "+str(sprite)+text
            drawvariable(self,text,screen)
        elif self.opcode=="data_listcontents":
            thelist=getlist(sprite,self.id)
            drawlist(self,thelist,screen)    
        else:
            value=getattr(sprite,self.opcode)()
            front=" "+str(sprite)+":"+self.opcode.replace("motion_","")
            drawvariable(self,front+value,screen)

         

def runcode(sprite: Sprite, flag: str)  :
    
    global done
    #done:bool
    if done:
        exit()

    if flag == None:
        return
    if not sprite.isStage:
        sprite.direction %= 360  # 这里解决角度超出[0,360]范围的问题

    logging.info("将进入" + sprite.name + "的" + sprite.blocks[flag]["opcode"] + "函数")
    result = None
    try:
        func = sprite.__getattribute__(sprite.blocks[flag]["opcode"])
        #print(func)
    except AttributeError:
        logging.error("缺少函数" + sprite.blocks[flag]["opcode"])
    else:
        result=func(flag)    
    clock.tick(TPS)
    if sprite.blocks[flag]["next"] != None and sprite.clone_mode!=2:  # 如果还有接着的积木，执行下去
        runcode(sprite=sprite, flag=sprite.blocks[flag]["next"])
    #logging.debug(keys_pressed)    
    return result



    

    # 主程序从这里开始
    # 初始化Pygame
pygame.init()
    
show_screen = pygame.display.set_mode(STAGE_SHOW_SIZE)
screen=pygame.Surface(STAGE_SIZE)
    
with zipfile.ZipFile("project.sb3") as f:
    filenamelist=f.namelist()
    #logging.debug(f.namelist())
    f.extractall()

t = json.loads(open("project.json", "r", encoding="utf-8").read())
sprite_list = []  # 角色们
clone_list=[]

done = False  # done是用来标记程序是否运行，False代表运行，true代表结束
clock = pygame.time.Clock()
    
for i in t["targets"]:
    i: dict
    i["clone_mode"]=0
    #clone_mode=0表示不是克隆
    #clone_mode=1表示克隆
    #clone_mode=2表示克隆体被删除
    sprite = Sprite(i)
    
    sprite_list.append(sprite)
    sprite.variables={}
    sprite.lists={}
    variables_name={}
    #logging.debug(sprite.variables)
    for j in i["variables"].items():
        #logging.debug(j)
        sprite.variables[j[0]]=safe_str(j[1][1])
        variables_name[j[0]]=safe_str(j[1][0])
    for j in i["lists"].items():
        #logging.debug(j)
        thelist=j[1][1]
        thelist=[safe_str(k) for k in thelist]
        sprite.lists[j[0]]=thelist
        #variables_name[j[0]]=safe_str(j[1][0])    
    logging.info(f"提取{sprite}的变量"  )  
    logging.info(sprite.variables)
    logging.info(variables_name)    
    if sprite.isStage:
        stage=sprite
        stage.time=time.time()
    for flag, code in sprite.blocks.items():
        if code["opcode"] == "event_whenflagclicked":
            # print(flag)
            flag = code["next"]
            thread = threading.Thread(
                name=str(sprite) + flag, target=runcode, args=(sprite, flag)
            )
            thread.start()
            # runcode(sprite,flag)
moniter_list=[]            
for i in t["monitors"]:
    moniter=Moniter(i)
    moniter_list.append(moniter)

# 设置窗口标题
pygame.display.set_caption("scratch")    
# 渲染线程主循环
while not done:
    # 处理事件
    event = pygame.event.poll()
    #logging.debug(event)
    if event.type != pygame.NOEVENT:
        #print(event)
        if event.type == pygame.KEYDOWN:
            print(event.key)
    if event.type == pygame.QUIT:
        done = True
    keys_pressed = pygame.key.get_pressed() 
    if any(keys_pressed):
        pass
        #logging.debug(keys_pressed)
        import keymap
        for i in sprite_list+clone_list:
            if i.clone_mode==2:#克隆体被删除
                continue
                    
            for flag, code in i.blocks.items():
                if code["opcode"] == "event_whenkeypressed":
                    if keys_pressed[keymap.keymap[code["fields"]["KEY_OPTION"][0]]]:
                        #logging.debug(code)
                        flag = code["next"]
                        thread = threading.Thread(
                            name=str(i) + flag, target=runcode, args=(i, flag)
                        )
                        thread.start()
                        # runcode(i,flag)

        

    
            

  

    # 填充窗口颜色
    screen.fill((255, 255, 255))

    # 逐个角色更新窗口
    
    for i in sprite_list+clone_list:
        if i.clone_mode==2:#克隆体被删除
            continue
        try:
            i.draw() 
        except:
            done=True 
            raise Exception
            
              
    for i in moniter_list:
        try:
            i.draw() 
        except:
            done=True 
            raise Exception      

        # 更新窗口
        
    scaled_screen=pygame.transform.scale(screen,(960,720))
    
    show_screen.blit(scaled_screen,(0,0))
    

    pygame.display.update()
        
    clock.tick(FPS)
        

        

# 退出Pygame
logging.info("退出程序")
sleep(0.25)
for filename in filenamelist:
    if logging.getLogger().level<=10:
        break
    os.remove(filename)



