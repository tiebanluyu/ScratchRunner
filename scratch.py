"""
ScratchRunner - Python实现的Scratch项目运行器

ScratchRunner是一个用Python编写的Scratch项目(.sb3文件)运行器，它能够：
1. 解析和加载Scratch 3.0项目文件
2. 执行Scratch积木逻辑和脚本
3. 渲染角色、舞台和视觉效果
4. 处理用户输入（键盘、鼠标）事件
5. 支持多线程执行和克隆功能

主要特性：
- 完整的Scratch积木支持（运动、外观、声音、事件、控制、侦测等）
- 多线程执行模型，支持并发脚本执行
- 精确的坐标系转换（Scratch ↔ Pygame）
- 变量和列表监控器支持
- 克隆体功能实现
- 自定义过程（函数）支持

架构概述：
-------------------------------
1. 初始化阶段：
   - 加载并解压SB3项目文件（ZIP格式）
   - 解析project.json描述文件
   - 创建Sprite对象和Stage对象
   - 初始化变量、列表和监视器

2. 线程管理：
   - ThreadManager类统一管理所有执行线程
   - 为每个"当绿旗被点击"事件创建独立线程
   - 支持线程的安全启动、停止和清理

3. 主渲染循环：
   - 处理Pygame事件（键盘、鼠标、窗口事件）
   - 渲染所有角色、舞台和监视器
   - 管理克隆体的创建和销毁
   - 处理碰撞检测和边界检查

4. 积木执行引擎：
   - runcode函数：执行积木逻辑的核心
   - S_eval函数：参数求值和解析
   - 支持条件判断、循环、变量操作等复杂逻辑

核心组件：
- ThreadManager: 线程生命周期管理
- Position: 坐标系转换工具类
- Sprite: 角色/舞台的基类，包含所有积木方法
- runcode: 积木执行入口函数
- Monitor: 变量和列表监视器显示

坐标系系统：
- Scratch坐标系：原点在舞台中心(0,0)，x向右为正(-240到240)，y向上为正(-180到180)
- Pygame坐标系：原点在左上角(0,0)，x向右为正(0到480)，y向下为正(0到360)
- Show坐标系：用于2倍缩放显示(960x720)，提供更好的视觉效果

文件结构：
- project.sb3: Scratch 3.0项目文件（ZIP格式）
- project.json: 项目描述文件（包含所有角色、积木、变量信息）
- 各种资源文件：角色造型、背景、声音等

依赖库：
- pygame (>=2.0.0): 图形渲染、输入处理和事件循环
- threading: 多线程执行支持
- json: 项目文件解析
- zipfile: SB3文件解压
- logging: 运行日志记录
- math: 数学运算和三角函数
- random: 随机数生成
- time: 时间相关功能
- os: 文件系统操作
- sys: 系统功能
- traceback: 错误追踪

使用说明：
1. 将Scratch项目文件命名为project.sb3放在同一目录
2. 运行python scratch.py启动程序
3. 按ESC键退出程序

注意事项：
- 程序会解压SB3文件到当前目录，退出时自动清理
- 支持大多数Scratch 3.0功能，但某些高级功能可能不完全支持
- 性能取决于项目复杂度和硬件配置

版本兼容性：
- 支持Scratch 3.0格式项目文件
- 需要Python 3.7+版本
- 需要安装所有依赖库

作者：语翔
项目地址：https://github.com/tiebanluyu/ScratchRunner
"""
import json
import pygame
import threading
import traceback
from math import sin, cos, radians
import math
import logging
import random
import zipfile
import os
import time
import sys
from typing import List, Tuple, Literal
from drawtext import drawtext, drawvariable, drawlist
from rotate import blitRotate
from variable import safe_int, safe_str, safe_bool, safe_float, IsNum

# 配置日志
logging.basicConfig(
    level=logging.DEBUG, format="[%(levelname)s] line%(lineno)s %(funcName)s -%(message)s"
)

class ThreadManager:
    """
    线程管理器 - 统一管理Scratch项目中的所有执行线程
    
    这个类负责管理所有由Scratch积木创建的线程，包括：
    - 绿旗点击事件线程
    - 克隆体执行线程
    - 其他异步执行的脚本线程
    
    特性：
    - 线程安全的线程管理（使用锁机制）
    - 优雅的线程停止和清理
    - 防止线程泄漏和僵尸线程
    
    线程状态说明：
    - 活动线程：正在执行Scratch积木逻辑的线程
    - 已完成线程：执行完毕等待清理的线程
    - 僵尸线程：异常终止需要清理的线程
    """
    
    def __init__(self):
        """初始化线程管理器"""
        self.threads = []  # 存储所有活动线程的列表
        self.lock = threading.Lock()  # 线程安全锁
    
    def add_thread(self, thread: threading.Thread) -> None:
        """
        添加一个新线程到管理器
        
        参数:
        thread: 要添加的线程对象
        
        说明:
        - 线程会自动启动（调用start()方法）
        - 线程会被设置为守护线程（daemon=True）
        - 线程名称应包含角色名和积木标识符以便调试
        """
        with self.lock:
            self.threads.append(thread)
    
    def remove_thread(self, thread: threading.Thread) -> None:
        """
        从管理器中移除指定线程
        
        参数:
        thread: 要移除的线程对象
        
        说明:
        - 如果线程仍在运行，会先尝试停止
        - 线程移除后会被垃圾回收
        - 线程安全操作，使用锁保护
        """
        with self.lock:
            if thread in self.threads:
                self.threads.remove(thread)
    
    def stop_all_threads(self) -> None:
        """
        停止所有线程并等待它们结束
        
        说明:
        - 优雅停止：给线程0.5秒时间完成当前操作
        - 强制清理：超时后强制移除线程引用
        - 防止内存泄漏：确保所有线程资源被释放
        
        使用场景:
        - 程序退出时
        - 项目重新加载时
        - 用户强制停止时
        """
        with self.lock:
            for thread in self.threads:
                if thread.is_alive():
                    # 给线程0.5秒时间优雅退出
                    thread.join(timeout=0.5)
            # 清空线程列表，释放所有引用
            self.threads.clear()

# 创建全局线程管理器实例
thread_manager = ThreadManager()

class Position:
    """
    处理Scratch坐标系与Pygame坐标系之间的转换
    
    坐标系说明：
    - Scratch坐标系：原点在舞台中心(0,0)，x向右为正(-240到240)，y向上为正(-180到180)
    - Pygame坐标系：原点在左上角(0,0)，x向右为正(0到480)，y向下为正(0到360)
    - Show坐标系：用于2倍缩放显示(960x720)，提供更好的视觉效果
    
    支持三种模式：
    1. 'scratch': 直接使用Scratch坐标
    2. 'pygame': 将Pygame坐标转换为Scratch坐标
    3. 'show': 将显示坐标转换为Scratch坐标
    
    转换公式：
    - Scratch → Pygame: (x + 240, 180 - y)
    - Pygame → Scratch: (x - 240, 180 - y)
    - Scratch → Show: (x*2 + 240, 360 - y*2)
    - Show → Scratch: (x/2 - 240, 180 - y/2)
    """
    def __init__(self, x: int, y: int, mode: str = "scratch") -> None:
        """
        初始化位置对象
        
        参数:
        x, y: 坐标值
        mode: 坐标系模式 ('scratch', 'pygame', 'show')
        
        说明:
        - 根据不同的坐标系模式，自动进行坐标转换
        - 内部始终以Scratch坐标系存储坐标值
        """
        if mode == "scratch":
            self.x = x
            self.y = y
        elif mode == "pygame":
            self.x, self.y = positionmap2(x, y)
        elif mode == "show":
            self.x = x/2 - 240
            self.y = 180 - y/2
    
    def __str__(self) -> str:
        """返回位置的可读字符串表示"""
        return f"POSITION({self.x},{self.y})"   
    
    def __repr__(self) -> str:
        """返回位置的正式字符串表示（用于调试）"""
        return f"POSITION({self.x},{self.y})"    
    
    def scratch(self) -> Tuple[int, int]:
        """
        获取Scratch坐标系坐标
        
        返回:
        (x, y): Scratch坐标系中的坐标值
        """
        return self.x, self.y
    
    def pygame(self) -> Tuple[int, int]:
        """
        获取Pygame坐标系坐标
        
        返回:
        (x, y): Pygame坐标系中的坐标值
        """
        return positionmap1(self.x, self.y)
    
    def show(self) -> Tuple[int, int]:
        """
        获取显示坐标系坐标（2倍缩放）
        
        返回:
        (x, y): 显示坐标系中的坐标值
        """
        return self.x*2 + 240, 360 - self.y*2          
from time import sleep
from rotate import blitRotate
from variable import *

# 帧率设置
FPS: int = 50  # 图形渲染帧率（Frames Per Second）
TPS: int = 50  # 逻辑更新帧率（Ticks Per Second）

# 窗口大小设置
STAGE_SIZE = (480, 360)  # 舞台实际渲染尺寸（Pygame坐标系）
STAGE_SHOW_SIZE = (960, 720)  # 舞台显示尺寸（2倍缩放，用于更好的视觉效果）
POSITION = (0, 0)  # 默认位置常量


# 自定义坐标转换函数
def positionmap1(x: int, y: int) -> tuple[int, int]:
    """
    将Scratch坐标系坐标转换为Pygame坐标系坐标
    
    参数:
    x, y: Scratch坐标系中的坐标值
    
    返回:
    (new_x, new_y): Pygame坐标系中的坐标值
    
    转换公式:
    new_x = x + 240
    new_y = 180 - y
    
    说明:
    - Scratch坐标系: 原点在中心(0,0)，x向右为正，y向上为正
    - Pygame坐标系: 原点在左上角(0,0)，x向右为正，y向下为正
    """
    ORIGIN_X = STAGE_SIZE[0] // 2  # 舞台中心x坐标 (240)
    ORIGIN_Y = STAGE_SIZE[1] // 2  # 舞台中心y坐标 (180)
    new_x = x + ORIGIN_X
    new_y = -y + ORIGIN_Y
    return new_x, new_y


def positionmap2(x: int, y: int) -> tuple[int, int]:
    """
    将Pygame坐标系坐标转换为Scratch坐标系坐标
    
    参数:
    x, y: Pygame坐标系中的坐标值
    
    返回:
    (new_x, new_y): Scratch坐标系中的坐标值
    
    转换公式:
    new_x = x - 240
    new_y = 180 - y
    
    说明:
    - 这是positionmap1的逆变换
    - 用于将鼠标位置等Pygame坐标转换为Scratch坐标
    """
    ORIGIN_X = STAGE_SIZE[0] // 2  # 舞台中心x坐标 (240)
    ORIGIN_Y = STAGE_SIZE[1] // 2  # 舞台中心y坐标 (180)
    new_x = x - ORIGIN_X
    new_y = ORIGIN_Y - y
    return new_x, new_y


def S_eval(sprite: "Sprite", flag: str) -> dict:
    """
    参数求值函数 - 解析Scratch积木的参数并求值
    
    这个函数根据角色和积木标识符(flag)，解析积木的输入参数和字段，
    执行必要的求值操作，并返回包含所有参数值的字典。
    
    参数:
    sprite: 执行积木的角色对象
    flag: 积木的唯一标识符
    
    返回:
    dict: 包含所有参数名称（大写）和对应值的字典
    
    输入参数类型说明:
    - 类型1 (value[0] == 1): 常数或可执行积木
      - 如果value[1]是字符串: 这是一个可执行积木，需要运行runcode
      - 否则: 这是一个常数，直接取值value[1][1]
    - 类型2 (value[0] == 2): 分支块（SUBSTACK等），作为参数传递但不执行
    - 类型3 (value[0] == 3): 变量或列表引用，需要获取变量值
    
    字段类型说明:
    - VARIABLE字段: 包含变量ID和名称，取ID值
    - 其他字段: 直接取值
    
    示例:
    输入积木:
    "a": {
        "opcode": "motion_gotoxy",
        "inputs": { "X": [1, [4, "0"]], "Y": [1, [4, "0"]] },
        "fields": {}
    }
    返回: {'X': '0', 'Y': '0'}
    """

    if flag is None:
        # 有些积木没有flag（如编辑器中的圆角监视器块）
        return {}
    
    # 复制输入和字段字典，避免修改原始数据
    _input: dict = sprite.blocks[flag]["inputs"].copy()
    _field: dict = sprite.blocks[flag]["fields"].copy()
    result = {}
    
    # 处理字段（fields）参数
    for key, value in _field.items():
        if "VARIABLE" == key:
            # 变量字段：包含[变量名, 变量ID]，取第二个值（ID）
            result[key.upper()] = value[1]
        else:
            # 其他字段：直接取第一个值
            result[key.upper()] = value[0]

    # 处理输入（inputs）参数
    for key, value in _input.items():
        logging.debug((key, value))
        
        if value[0] == 1:  # 类型1：常数或可执行积木
            if value[1].__class__ == str:
                # 字符串类型：这是一个可执行积木（如"移到x:y:"块）
                result[key.upper()] = runcode(sprite, value[1])
            else:
                # 其他类型：常数，直接取值
                result[key.upper()] = value[1][1]
                
        elif value[0] == 2:  # 类型2：分支块（不执行）
            # 分支块（SUBSTACK等）作为参数传递时不执行
            result[key] = value[1]
            
        elif value[0] == 3:  # 类型3：变量或列表引用
            if value[1][0].__class__ == str:
                # 字符串类型：可执行积木
                result[key.upper()] = runcode(sprite, value[1])
            else:
                # 其他类型：变量引用，获取变量值
                result[key.upper()] = getvaluable(sprite, value[1][2])
                
        else:
            logging.error(f"未知的参数标签：{value[0]}")

    logging.debug(result) 
    return result   
def getvaluable(sprite, id) -> str:
    """
    获取变量值
    
    参数:
    sprite: 角色对象
    id: 变量ID
    
    返回:
    str: 变量的字符串表示
    
    说明:
    - 先在全局变量中查找，然后在角色变量中查找
    - 使用safe_str确保返回安全的字符串
    """
    if id in stage.variables:
        return safe_str(stage.variables[id])
    if id in sprite.variables:
        return safe_str(sprite.variables[id])
    
def setvaluable(sprite, id, obj) -> None:
    """
    设置变量值
    
    参数:
    sprite: 角色对象
    id: 变量ID
    obj: 要设置的值
    
    说明:
    - 先在全局变量中查找，然后在角色变量中查找
    - 使用safe_str确保存储安全的字符串
    """
    logging.debug(stage.variables)
    if id in stage.variables:
        stage.variables[id] = safe_str(obj)
    elif id in sprite.variables:
        sprite.variables[id] = safe_str(obj)
        
def getlist(sprite, id):
    """
    获取列表对象
    
    参数:
    sprite: 角色对象
    id: 列表ID
    
    返回:
    list: 列表对象
    
    说明:
    - 先在全局列表中查找，然后在角色列表中查找
    - 如果找不到列表，抛出ValueError异常
    """
    #logging.debug((sprite,id,stage.lists,sprite.lists))
    if id in stage.lists:
        #logging.debug(stage.lists[id])
        return stage.lists[id]
    elif id in sprite.lists:
        logging.debug(sprite.lists[id])
        return sprite.lists[id]
    else:
        raise ValueError("list not found:"+id)
list_name_to_id={} 



class Sprite(pygame.sprite.Sprite):
    """
    角色类 - 表示Scratch项目中的角色或舞台
    
    这个类继承自pygame.sprite.Sprite，包含了Scratch角色的所有属性和方法，
    实现了Scratch的各种积木功能，包括运动、外观、声音、控制、侦测等。
    
    主要属性:
    - name: 角色名称
    - x, y: Scratch坐标系中的位置
    - direction: 方向角度（0-360度，0=上，90=右）
    - size: 角色大小（百分比，100=原始大小）
    - visible: 是否可见
    - currentCostume: 当前造型索引
    - costumes: 造型列表
    - variables: 角色变量字典
    - blocks: 积木字典
    - isStage: 是否为舞台
    - clone_mode: 克隆状态（0=原始, 1=克隆体, 2=已删除）
    - words: 说话内容
    - argument_dict: 函数参数存储字典
    
    积木方法分类:
    - motion_*: 运动相关积木
    - looks_*: 外观相关积木  
    - control_*: 控制相关积木
    - sensing_*: 侦测相关积木
    - data_*: 数据（变量和列表）相关积木
    - operator_*: 运算相关积木
    - event_*: 事件相关积木
    """
    
    def __init__(self, dict1: dict) -> None:
        """
        初始化角色对象
        
        参数:
        dict1: 包含角色所有属性的字典，来自project.json中的targets项
        
        说明:
        - 使用setattr动态设置所有属性，避免手动定义每个属性
        - 初始化说话内容和函数参数字典
        """
        super().__init__()
        for name, value in dict1.items():  # 原来仅仅改变__dict__会带来问题
            setattr(self, name, value)
        self.words = ""    # 没说话时的默认说话内容
        self.argument_dict = {}  # 这个字典是用来存储函数调用的参数的
        # 以(threadname, argname)为key，argvalue为value的字典

    def __str__(self) -> str:
        """返回角色的字符串表示（角色名称）"""
        return self.name

    def __repr__(self) -> str:
        """返回角色的正式字符串表示（用于调试）"""
        return self.name

    def draw(self) -> None:
        """
        绘制角色到屏幕
        
        说明:
        - 加载当前造型的图像
        - 处理SVG和位图格式的不同缩放
        - 舞台角色特殊处理（没有方向属性）
        - 应用大小缩放和旋转
        - 设置碰撞遮罩
        - 绘制说话内容
        """
        costume = self.costumes[self.currentCostume]
        #logging.debug(costume)
        
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
            return # stage没有direction属性
        if not self.visible:
            return
        
        image = pygame.transform.rotozoom(
                image, 0, self.size/100
            )
        direction = self.direction % 360  # stage没有direction属性
        #x, y = positionmap1(self.x, self.y)
        position = Position(self.x, self.y)
        x, y = position.pygame()
        rotatecentre = costume["rotationCenterX"]*(self.size/100), costume["rotationCenterY"]*(self.size/100)
        self.image, self.rect = blitRotate(
            screen, image, (x, y), rotatecentre, 90 - direction
        )  # 他山之石可以攻玉
        #pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)
        self.mask = pygame.mask.from_surface(self.image)
        drawtext(self, screen)

    def motion_goto(self, flag) -> None:
        """
        移动到指定角色或位置
        
        参数:
        flag: 积木标识符
        
        功能:
        - 移动到指定角色或随机位置或鼠标位置
        - 支持 '_random_' 和 '_mouse_' 特殊目标
        
        说明:
        - 使用 S_eval 解析参数
        - 通过 motion_goto_menu 方法获取目标位置
        - 直接设置角色的 x, y 坐标
        """
        dict1 = S_eval(self, flag)
        to = dict1["TO"]
        self.x, self.y = to.scratch()

    def motion_goto_menu(self, flag) -> Position:
        """
        获取移动到菜单选项的目标位置
        
        参数:
        flag: 积木标识符
        
        返回:
        Position: 目标位置的Position对象
        
        功能:
        - 处理随机位置生成
        - 处理鼠标位置获取
        - 处理指定角色位置获取
        
        特殊目标:
        - '_random_': 在舞台范围内生成随机位置
        - '_mouse_': 获取当前鼠标位置
        - 角色名: 获取指定角色的位置
        """
        dict1 = S_eval(self, flag)
        logging.debug(dict1)
        to = dict1["TO"]
        if to == "_random_":
            # 在舞台范围内生成随机位置 (-240到240, -180到180)
            y = random.uniform(-180, 180)
            x = random.uniform(-240, 240)
            return Position(x, y)
        elif to == "_mouse_":
            # 获取鼠标当前位置并转换为Scratch坐标系
            mousepos = Position(*pygame.mouse.get_pos(),"show")
            return mousepos
        else:
            # 查找指定名称的角色并返回其位置
            for sprite in sprite_list:
                if sprite.name == to:
                    return POSITION(sprite.x, sprite.y)
        return None

    motion_glideto_menu = motion_goto_menu
    """滑行到菜单选项 - 复用motion_goto_menu的功能"""

    def motion_movesteps(self, flag: str) -> None:
        """
        移动指定步数
        
        参数:
        flag: 积木标识符
        
        功能:
        - 根据当前方向移动指定步数
        - 使用三角函数计算x和y方向的位移
        
        数学原理:
        - x位移 = 步数 * sin(方向角度)
        - y位移 = 步数 * cos(方向角度)
        - Scratch方向: 0度=上, 90度=右, 180度=下, 270度=左
        """
        steps: int = safe_int(S_eval(self, flag)["STEPS"])
        # logging.info(self.direction)

        # 使用三角函数计算x和y方向的位移
        x = steps * sin(radians(self.direction))
        y = steps * cos(radians(self.direction))
        self.x += x
        self.y += y

    def motion_gotoxy(self, flag: str) -> None:
        """
        移动到指定坐标
        
        参数:
        flag: 积木标识符
        
        功能:
        - 直接设置角色的x和y坐标
        - 使用Scratch坐标系 (-240到240, -180到180)
        
        说明:
        - 使用safe_int确保坐标值为整数
        - 不进行边界检查，允许角色移动到舞台外
        """
        dic = S_eval(self, flag)
        self.x = safe_int(dic["X"])
        self.y = safe_int(dic["Y"])
        #print(dic)

    def motion_turnright(self, flag: str) -> None:
        """
        向右旋转指定角度
        
        参数:
        flag: 积木标识符
        
        功能:
        - 增加角色的方向角度（顺时针旋转）
        - 之前角度会自动取模保持在0-360度范围内，现在从runcode里检查改为每个改角度的块检查
        
        说明:
        - 正角度值表示顺时针旋转
        - 使用safe_int确保角度值为整数
        """
        addition = S_eval(self, flag)["DEGREES"]
        self.direction += safe_int(addition)            
        sprite.direction %= 360  # 这里解决角度超出[0,360]范围的问题

    def motion_turnleft(self, flag: str) -> None:
        """
        向左旋转指定角度
        
        参数:
        flag: 积木标识符
        
        功能:
        - 减少角色的方向角度（逆时针旋转）
        - 之前角度会自动取模保持在0-360度范围内，现在从runcode里检查改为每个改角度的块检查
        
        说明:
        - 正角度值表示逆时针旋转
        - 使用safe_int确保角度值为整数
        """
        addition = S_eval(self, flag)["DEGREES"]
        self.direction -= safe_int(addition)
        sprite.direction %= 360  # 这里解决角度超出[0,360]范围的问题

    def event_whenflagclicked(self, flag) -> None:
        """
        当绿旗被点击事件处理
        
        参数:
        flag: 积木标识符
        
        功能:
        - 绿旗点击事件的入口点
        - 启动后续积木的执行
        
        说明:
        - 这是Scratch项目的主要启动事件
        - 通常在项目开始时自动执行
        """
        #runcode(self, self.blocks[flag]["next"])
        # 这个积木本身不执行任何操作，只是一个事件入口
        # 后续积木由runcode负责执行，之前这里误加了一条，导致执行两遍
        logging.info("绿旗被点击")
        
        

    def control_if(self, flag: str) -> None:
        """
        条件判断积木（如果...那么...）
        
        参数:
        flag: 积木标识符
        
        功能:
        - 执行条件判断
        - 如果条件为真，执行SUBSTACK中的积木
        - 如果条件为假，跳过SUBSTACK
        
        说明:
        - 条件表达式通过runcode执行并返回字符串"True"或"False"
        - 支持复杂的嵌套条件判断
        """
        dic=S_eval(self,flag)
        logging.debug(dic)
        #breakpoint()
        condition=runcode(self,dic["CONDITION"])
        if condition=="True":
            runcode(self,dic["SUBSTACK"])
            logging.debug("True")
        else:
            logging.debug("False")    
    def control_if_else(self, flag: str) -> None:
        """
        条件判断积木（如果...那么...否则...）
        
        参数:
        flag: 积木标识符
        
        功能:
        - 执行条件判断
        - 如果条件为真，执行SUBSTACK中的积木
        - 如果条件为假，执行SUBSTACK2中的积木
        
        说明:
        - 提供两个分支的执行路径
        - 条件表达式通过runcode执行并返回字符串"True"或"False"
        """
        dic=S_eval(self,flag)
        logging.debug(dic)
        if dic["CONDITION"]=="True":
            runcode(self, dic["SUBSTACK"])
        else:
            runcode(self, dic["SUBSTACK2"])   
    def control_wait_until(self,flag):
        """
        等待直到条件成立
        
        参数:
        flag: 积木标识符
        
        功能:
        - 循环检查条件是否成立
        - 条件成立时退出等待，继续执行后续积木
        - 条件不成立时持续等待
        
        说明:
        - 使用无限循环不断检查条件
        - 条件表达式通过runcode执行并返回字符串"True"或"False"
        - 注意：如果条件永远不成立，会导致线程阻塞
        """
        dic=S_eval(self,flag)
        condition=dic["CONDITION"]
        logging.debug(condition)
        while 1:
            if runcode(self,condition)=="True":
                break         
    def control_repeat(self, flag) -> None:
        """
        重复执行指定次数
        
        参数:
        flag: 积木标识符
        
        功能:
        - 重复执行SUBSTACK中的积木指定次数
        - 支持克隆体状态检查（如果克隆体被删除则停止）
        
        说明:
        - 使用for循环控制重复次数
        - 每次循环都会检查克隆体状态
        - 使用safe_int确保次数为整数
        """
        dic = S_eval(self, flag)
        if self.blocks[flag]["inputs"]["SUBSTACK"][1] is None:
            return
        for _ in range(safe_int(dic["TIMES"])):
            if self.clone_mode==2:
                break
            runcode(self, self.blocks[flag]["inputs"]["SUBSTACK"][1])

    def control_forever(self, flag: str) -> None:
        """
        永远循环执行
        
        参数:
        flag: 积木标识符
        
        功能:
        - 无限循环执行SUBSTACK中的积木
        - 支持克隆体状态检查（如果克隆体被删除则停止）
        
        说明:
        - 使用while True无限循环
        - 每次循环都会检查克隆体状态
        - 通常用于持续性的行为或动画
        """
        while 1:
            # self.x=1
            if self.clone_mode==2:
                break
            runcode(self, self.blocks[flag]["inputs"]["SUBSTACK"][1])

    def control_wait(self, flag: str) -> None:
        """
        等待指定时间
        
        参数:
        flag: 积木标识符
        
        功能:
        - 暂停当前线程执行指定时间
        - 时间单位为秒，支持小数
        
        说明:
        - 使用time.sleep实现等待
        - 等待期间线程阻塞，不执行其他操作
        - 常用于制作延时效果或动画间隔
        """
        sleeptime = float(S_eval(self, flag)["DURATION"])
        sleep(sleeptime)

    def motion_pointindirection(self, flag:str) -> None:
        """
        将方向设定为指定角度
        
        参数:
        flag: 积木标识符
        
        功能:
        - 直接设置角色的方向角度
        - 角度范围: 0-360度（0=上, 90=右, 180=下, 270=左）
        
        说明:
        - 使用float支持小数角度
        - 角度会自动取模保持在0-360度范围内
        """
        direction = float(S_eval(self, flag)["DIRECTION"])
        self.direction = direction

    def motion_glideto(self, flag) -> None:
        """
        在指定时间内滑行到目标位置
        
        参数:
        flag: 积木标识符
        
        功能:
        - 在指定时间内平滑移动到目标位置
        - 使用线性插值计算移动向量
        - 分100步完成移动，实现平滑动画效果
        
        说明:
        - 计算从当前位置到目标位置的向量
        - 将总时间分为100个小时间段
        - 每个时间段移动1/100的距离
        """
        dic = S_eval(self, flag)
        secs, to = dic["SECS"], dic["TO"]
        # 计算移动向量 (Δx/100, Δy/100)
        vec = ((to[0] - self.x) / 100, (to[1] - self.y) / 100)
        for _ in range(100):
            sleep(float(secs) / 100)  # 每次等待总时间的1/100
            self.x += vec[0]  # 移动x坐标
            self.y += vec[1]  # 移动y坐标

    def motion_glidesecstoxy(self, flag:str) -> None:
        """
        在指定时间内滑行到指定坐标
        
        参数:
        flag: 积木标识符
        
        功能:
        - 在指定时间内平滑移动到指定x,y坐标
        - 使用线性插值计算移动向量
        - 分100步完成移动，实现平滑动画效果
        
        说明:
        - 与motion_glideto类似，但直接指定目标坐标
        -
        """

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

    def motion_pointtowards_menu(self, flag:str) -> float:
        dic = S_eval(self, flag)
        def pos2angle(x:int,y:int) -> float:
            dx = x - self.x
            dy = y - self.y
            direction = 90 - math.degrees(math.atan2(dy, dx))
            
            direction = direction%360

            return direction
        if dic["TOWARDS"] == "_mouse_":
            mousepos = pygame.mouse.get_pos()
            mousepos = positionmap2(mousepos[0], mousepos[1])
            return pos2angle(*mousepos)
        elif dic["TOWARDS"] == "_random_":
            import random

            direction = random.uniform(0, 360)
            return direction
        else:
            for sprite in sprite_list:
                if sprite.name == dic["TOWARDS"]:
                    return pos2angle(sprite.x, sprite.y)
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
    def looks_say(self, flag: str) -> None:
        """
        说话积木 - 显示说话内容
        
        参数:
        flag: 积木标识符
        
        功能:
        - 在角色上方显示指定的说话内容
        - 说话内容会一直显示直到被其他说话积木覆盖
        
        说明:
        - 使用self.words属性存储说话内容
        - 说话内容通过drawtext函数在draw方法中渲染
        - 不会自动清除，需要手动设置空字符串来隐藏
        """
        dic = S_eval(self, flag)
        message = safe_str(dic["MESSAGE"])
        self.words = message
    
    looks_think = looks_say
    """思考积木 - 复用说话积木的功能，显示思考内容"""
    
    def looks_sayforsecs(self, flag: str) -> None:
        """
        说话指定时间积木 - 显示说话内容并在指定时间后隐藏
        
        参数:
        flag: 积木标识符
        
        功能:
        - 在角色上方显示指定的说话内容
        - 等待指定时间后自动清除说话内容
        - 使用time.sleep实现定时功能
        
        说明:
        - 支持小数秒数（如0.5秒）
        - 等待期间线程阻塞，不执行其他操作
        - 常用于临时性的对话或提示
        """
        dic = S_eval(self, flag)
        secs = safe_float(dic["SECS"])
        message = safe_str(dic["MESSAGE"])
        self.words = message
        sleep(secs)
        self.words = ""
    
    looks_thinkforsecs = looks_sayforsecs
    """思考指定时间积木 - 复用说话指定时间积木的功能"""
    
    def looks_switchcostumeto(self, flag: str) -> None:
        """
        切换造型积木 - 切换到指定名称的造型
        
        参数:
        flag: 积木标识符
        
        功能:
        - 根据造型名称查找对应的造型索引
        - 设置当前造型索引为找到的造型
        
        说明:
        - 造型名称必须完全匹配（区分大小写）
        - 如果找不到指定名称的造型，保持当前造型不变
        - 造型列表存储在self.costumes属性中
        """
        dic = S_eval(self, flag)
        logging.debug(dic)
        count = 0
        for costume in self.costumes:
            if costume["name"] == dic["COSTUME"]:
                self.currentCostume = count
                break
            count += 1
    
    def looks_costume(self, flag: str) -> str:
        """
        获取当前造型名称积木
        
        参数:
        flag: 积木标识符
        
        返回:
        str: 当前造型的名称
        
        功能:
        - 返回当前造型的名称字符串
        - 用于在表达式中获取造型信息
        
        说明:
        - 造型名称来自costumes列表中的name字段
        - 如果当前造型索引无效，可能返回空字符串
        """
        dic = S_eval(self, flag)
        return dic["COSTUME"]
    
    def looks_show(self, flag: str = None) -> None:
        """
        显示积木 - 让角色可见
        
        参数:
        flag: 积木标识符（可为None，表示无参数积木）
        
        功能:
        - 设置角色的visible属性为True
        - 角色将在下一帧开始显示
        
        说明:
        - 无参数积木，直接设置属性
        - 与looks_hide积木配合使用
        """
        self.visible = True
    
    def looks_hide(self, flag: str) -> None:
        """
        隐藏积木 - 让角色不可见
        
        参数:
        flag: 积木标识符
        
        功能:
        - 设置角色的visible属性为False
        - 角色将在下一帧开始隐藏
        
        说明:
        - 隐藏的角色不会参与碰撞检测
        - 隐藏的角色仍然可以执行积木逻辑
        """
        self.visible = False
    
    def looks_nextcostume(self, flag: str = None) -> None:
        """
        下一个造型积木 - 切换到下一个造型
        
        参数:
        flag: 积木标识符（可为None，表示无参数积木）
        
        功能:
        - 将当前造型索引加1
        - 如果已经是最后一个造型，循环到第一个造型
        
        说明:
        - 支持造型列表的循环切换
        - 常用于制作动画效果
        """
        costumecount = len(self.costumes)
        self.currentCostume += 1
        if self.currentCostume == costumecount:
            self.currentCostume = 0
    
    def looks_changesizeby(self, flag: str) -> None:
        """
        将大小增加指定值积木
        
        参数:
        flag: 积木标识符
        
        功能:
        - 将角色的大小增加指定百分比
        - 大小可以超过100%（放大）或低于100%（缩小）
        
        说明:
        - 大小以百分比表示，100%为原始大小
        - 支持正负值（正数放大，负数缩小）
        """
        dic = S_eval(self, flag)
        self.size += float(dic["CHANGE"])
    
    def looks_setsizeto(self, flag: str) -> None:
        """
        将大小设定为指定值积木
        
        参数:
        flag: 积木标识符
        
        功能:
        - 直接将角色的大小设置为指定百分比
        - 大小可以超过100%（放大）或低于100%（缩小）
        
        说明:
        - 大小以百分比表示，100%为原始大小
        - 支持任意正数值（建议范围：10%-500%）
        """
        dic = S_eval(self, flag)
        self.size = float(dic["SIZE"])
    
    def looks_switchbackdropto(self, flag: str) -> None:
        """
        切换到指定背景积木
        
        参数:
        flag: 积木标识符
        
        功能:
        - 将舞台的背景切换到指定名称的背景
        - 只对舞台角色有效
        
        说明:
        - 背景名称必须完全匹配（区分大小写）
        - 如果找不到指定名称的背景，保持当前背景不变
        - 背景列表存储在stage.costumes属性中
        """
        dic = S_eval(self, flag)
        count = 0
        for costume in stage.costumes:
            if costume["name"] == dic["BACKDROP"]:
                stage.currentCostume = count
                break
            count += 1
    
    def looks_backdrops(self, flag: str) -> str:
        """
        获取当前背景名称积木
        
        参数:
        flag: 积木标识符
        
        返回:
        str: 当前背景的名称
        
        功能:
        - 返回舞台当前背景的名称字符串
        - 用于在表达式中获取背景信息
        
        说明:
        - 只对舞台角色有效
        - 背景名称来自stage.costumes列表中的name字段
        """
        dic = S_eval(self, flag)
        return dic["COSTUME"]
    
    def looks_nextbackdrop(self, flag: str = None) -> None:
        """
        下一个背景积木 - 切换到下一个背景
        
        参数:
        flag: 积木标识符（可为None，表示无参数积木）
        
        功能:
        - 将舞台的当前背景索引加1
        - 如果已经是最后一个背景，循环到第一个背景
        
        说明:
        - 只对舞台角色有效
        - 支持背景列表的循环切换
        """
        costumecount = len(stage.costumes)
        stage.currentCostume += 1
        if stage.currentCostume == costumecount:
            stage.currentCostume = 0
    
    def looks_costumenumbername(self, flag: str) -> str:
        """
        造型编号/名称积木 - 获取造型编号或名称
        
        参数:
        flag: 积木标识符
        
        返回:
        str: 造型编号或名称的字符串表示
        
        功能:
        - 根据TYPE参数返回造型编号或名称
        - "number": 返回当前造型的编号（从1开始）
        - "name": 返回当前造型的名称
        
        说明:
        - 造型编号从1开始（与Scratch界面显示一致）
        - 造型名称来自costumes列表中的name字段
        """
        dic = S_eval(self, flag)
        logging.debug(dic)
        if dic["TYPE"] == "number":
            return safe_str(self.currentCostume + 1)
        elif dic["TYPE"] == "name":
            return safe_str(self.costumes[self.currentCostume]["name"])
    
    def looks_size(self, flag: str = None) -> str:
        """
        获取大小积木 - 返回角色当前大小
        
        参数:
        flag: 积木标识符（可为None，表示无参数积木）
        
        返回:
        str: 角色大小的字符串表示（百分比）
        
        功能:
        - 返回角色当前大小的百分比值
        - 用于在表达式中获取大小信息
        
        说明:
        - 100%表示原始大小
        - 支持小数精度（如123.45%）
        """
        return safe_str(self.size)
    
    def looks_backdropnumbername(self, flag: str) -> str:
        """
        背景编号/名称积木 - 获取背景编号或名称
        
        参数:
        flag: 积木标识符
        
        返回:
        str: 背景编号或名称的字符串表示
        
        功能:
        - 根据TYPE参数返回背景编号或名称
        - "number": 返回当前背景的编号（从1开始）
        - "name": 返回当前背景的名称
        
        说明:
        - 只对舞台角色有效
        - 背景编号从1开始（与Scratch界面显示一致）
        - 背景名称来自stage.costumes列表中的name字段
        """
        dic = S_eval(self, flag)
        logging.debug(dic)
        if dic["TYPE"] == "number":
            return safe_str(stage.currentCostume + 1)
        elif dic["TYPE"] == "name":
            return safe_str(stage.costumes[stage.currentCostume]["name"])
    def operator_random(self, flag):
        """
        在指定范围内生成随机数
        
        参数:
        flag: 积木标识符
        
        返回:
        int或float: 指定范围内的随机数
        
        功能:
        - 根据参数类型决定生成整数还是浮点数随机数
        - 自动确定数值范围并生成范围内的随机数
        - 支持整数范围和浮点数范围
        
        说明:
        - 如果FROM或TO包含小数点，生成浮点数随机数
        - 否则生成整数随机数
        - 自动处理范围的顺序（从小到大）
        """
        dic = S_eval(self, flag)
        logging.debug(dic)
        _from = dic["FROM"] 
        to = dic["TO"]
        if "." in _from + to:  # 浮点数
            _from = safe_float(_from)
            to = safe_float(to)
            _from, to = sorted((_from, to))
            return random.uniform(_from, to)
        else:
            _from = safe_int(_from)
            to = safe_int(to)
            _from, to = sorted((_from, to))
            return random.randint(_from, to)
          
    def operator_gt(self, flag):
        """
        大于比较运算
        
        参数:
        flag: 积木标识符
        
        返回:
        str: "True" 或 "False" 字符串
        
        功能:
        - 比较两个操作数的大小，返回第一个操作数是否大于第二个操作数
        - 自动识别数值和字符串类型进行不同的比较
        
        说明:
        - 如果两个操作数都是数字，进行数值比较
        - 如果任一操作数不是数字，进行字符串字典序比较
        - 使用safe_float确保数值类型的正确转换
        """
        dic = S_eval(self, flag)
        logging.debug(dic)    
        if IsNum(dic["OPERAND1"]) and IsNum(dic["OPERAND2"]):
            operand1 = safe_float(dic["OPERAND1"])
            operand2 = safe_float(dic["OPERAND2"])
        
            logging.debug((operand1, operand2))
            return safe_str(operand1 > operand2)
        else:
            return safe_str(dic["OPERAND1"] > dic["OPERAND2"])        
    def operator_lt(self, flag):
        """
        小于比较运算
        
        参数:
        flag: 积木标识符
        
        返回:
        str: "True" 或 "False" 字符串
        
        功能:
        - 比较两个操作数的大小，返回第一个操作数是否小于第二个操作数
        - 自动识别数值和字符串类型进行不同的比较
        
        说明:
        - 如果两个操作数都是数字，进行数值比较
        - 如果任一操作数不是数字，进行字符串字典序比较
        - 使用safe_float确保数值类型的正确转换
        """
        dic = S_eval(self, flag)
        logging.debug(dic)    
        if IsNum(dic["OPERAND1"]) and IsNum(dic["OPERAND2"]):
            operand1 = safe_float(dic["OPERAND1"])
            operand2 = safe_float(dic["OPERAND2"])
        
            logging.debug((operand1, operand2))
            return safe_str(operand1 < operand2)
        else:
            return safe_str(dic["OPERAND1"] < dic["OPERAND2"])
    def operator_equals(self, flag):
        """
        等于比较运算
        
        参数:
        flag: 积木标识符
        
        返回:
        str: "True" 或 "False" 字符串
        
        功能:
        - 比较两个操作数是否相等
        - 自动识别数值和字符串类型进行不同的比较
        
        说明:
        - 如果两个操作数都是数字，使用math.isclose进行浮点数精度比较
        - 如果任一操作数不是数字，进行字符串相等比较
        - math.isclose处理浮点数精度问题，避免0.1+0.2≠0.3的问题
        """
        dic = S_eval(self, flag)
        logging.debug(dic)    
        if IsNum(dic["OPERAND1"]) and IsNum(dic["OPERAND2"]):
            operand1 = safe_float(dic["OPERAND1"])
            operand2 = safe_float(dic["OPERAND2"])
        
            logging.debug((operand1, operand2))
            return safe_str(math.isclose(operand1, operand2))
        else:
            return safe_str(dic["OPERAND1"] == dic["OPERAND2"])    
    def operator_and(self, flag) -> str:
        """
        逻辑与运算
        
        参数:
        flag: 积木标识符
        
        返回:
        str: "True" 或 "False" 字符串
        
        功能:
        - 对两个操作数进行逻辑与运算
        - 只有两个操作数都为真时才返回"True"
        
        说明:
        - 使用safe_bool进行安全的布尔值转换
        - 提供默认值False，防止用户未放置积木时出错
        - 支持各种类型的真值判断
        """
        dic = S_eval(self, flag)
        #logging.debug(dic)

        # 用户可能不会往框中放置积木，所以默认值是False
        return safe_str(safe_bool(dic.get("OPERAND1", False)) 
                        and safe_bool(dic.get("OPERAND2", False)))
    def operator_or(self, flag) -> str:
        """
        逻辑或运算
        
        参数:
        flag: 积木标识符
        
        返回:
        str: "True" 或 "False" 字符串
        
        功能:
        - 对两个操作数进行逻辑或运算
        - 只要任一操作数为真就返回"True"
        
        说明:
        - 使用safe_bool进行安全的布尔值转换
        - 提供默认值False，防止用户未放置积木时出错
        - 支持各种类型的真值判断
        """
        dic = S_eval(self, flag)
        #logging.debug(dic)
        return safe_str(safe_bool(dic.get("OPERAND1", False)) 
                        or safe_bool(dic.get("OPERAND2", False)))
    def operator_not(self, flag):
        """
        逻辑非运算
        
        参数:
        flag: 积木标识符
        
        返回:
        str: "True" 或 "False" 字符串
        
        功能:
        - 对单个操作数进行逻辑非运算
        - 操作数为真时返回"False"，为假时返回"True"
        
        说明:
        - 使用safe_bool进行安全的布尔值转换
        - 提供默认值False，防止用户未放置积木时出错
        - 支持各种类型的真值判断
        """
        dic = S_eval(self, flag)
        logging.debug(dic)
        return safe_str(not dic.get("OPERAND", False))
    def operator_join(self, flag):
        """
        字符串连接运算
        
        参数:
        flag: 积木标识符
        
        返回:
        str: 连接后的字符串
        
        功能:
        - 将两个字符串连接成一个新的字符串
        - 保持原字符串的顺序（STRING1在前，STRING2在后）
        
        说明:
        - 支持任意类型的字符串连接
        - 使用safe_str确保返回安全的字符串
        - 常用于构建动态文本或消息
        """
        dic = S_eval(self, flag)
        logging.debug(dic)
        return safe_str(dic["STRING1"]) + safe_str(dic["STRING2"])
    def operator_letter_of(self, flag):
        """
        获取字符串中指定位置的字符
        
        参数:
        flag: 积木标识符
        
        返回:
        str: 指定位置的单个字符
        
        功能:
        - 从字符串中提取指定位置的字符
        - 位置编号从1开始（与Scratch界面一致）
        
        说明:
        - 使用safe_int确保位置索引为整数
        - 如果位置超出字符串长度，可能引发IndexError
        - 字符串索引在Python中从0开始，因此需要减1转换
        """
        dic = S_eval(self, flag)
        logging.debug(dic)
        return safe_str(dic["STRING"][safe_int(dic["LETTER"])])
    def operator_length(self, flag):
        """
        获取字符串长度
        
        参数:
        flag: 积木标识符
        
        返回:
        str: 字符串长度的字符串表示
        
        功能:
        - 计算并返回字符串的字符数量
        - 支持Unicode字符和多字节字符的正确计数
        
        说明:
        - 使用Python内置的len()函数计算长度
        - 使用safe_str确保返回安全的字符串
        - 空字符串的长度为0
        """
        dic = S_eval(self, flag)
        logging.debug(dic)
        return safe_str(len(dic["STRING"]))
    def operator_contains(self, flag):
        """
        检查字符串是否包含子串
        
        参数:
        flag: 积木标识符
        
        返回:
        str: "True" 或 "False" 字符串
        
        功能:
        - 检查STRING1是否包含STRING2子串
        - 区分大小写（Scratch默认区分大小写）
        
        说明:
        - 使用Python的in操作符进行子串检查
        - 空字符串总是被认为包含在任何字符串中
        - 支持Unicode字符和多字节字符
        """
        dic = S_eval(self, flag)
        logging.debug(dic)
        return safe_str(dic["STRING2"] in dic["STRING1"])
    def operator_mod(self, flag):
        """
        取模运算（求余数）
        
        参数:
        flag: 积木标识符
        
        返回:
        str: 余数的字符串表示
        
        功能:
        - 计算NUM1除以NUM2的余数
        - 遵循数学上的取模运算规则
        
        说明:
        - 使用safe_int确保操作数为整数
        - 如果NUM2为0，会引发ZeroDivisionError异常
        - 结果为NUM1 % NUM2的数学余数
        """
        dic = S_eval(self, flag)
        logging.debug(dic)
        num1 = safe_int(dic["NUM1"])
        num2 = safe_int(dic["NUM2"])
        return safe_str(num1 % num2)
    def operator_round(self, flag):
        """
        四舍五入运算
        
        参数:
        flag: 积木标识符
        
        返回:
        str: 四舍五入后的整数字符串表示
        
        功能:
        - 对数字进行四舍五入到最接近的整数
        - 遵循标准的四舍五入规则
        
        说明:
        - 使用safe_float确保操作数为浮点数
        - 使用Python内置的round()函数进行四舍五入
        - 处理.5的情况时遵循"银行家舍入法"
        """
        dic = S_eval(self, flag)
        logging.debug(dic)
        return safe_str(round(safe_float(dic["NUM"])))
    def data_setvariableto(self, flag):
        """
        设置变量值积木
        
        参数:
        flag: 积木标识符
        
        功能:
        - 将变量设置为指定的值
        - 支持全局变量和角色局部变量
        
        说明:
        - 使用setvaluable函数处理变量设置
        - 自动区分全局变量和角色变量
        - 使用safe_str确保存储安全的字符串值
        """
        dic = S_eval(self, flag)
        logging.debug(dic)
        variable = dic["VARIABLE"]
        value = dic["VALUE"]
        # 自己设置不可行，因为可能要动全局变量
        # self.variables[variable] = safe_str(value)
        setvaluable(self, variable, safe_str(value))
        logging.debug(self.variables)
    def data_changevariableby(self, flag: str) -> None:
        """
        修改变量值积木（增加/减少指定值）
        
        参数:
        flag: 积木标识符
        
        功能:
        - 将变量的当前值增加或减少指定数值
        - 支持正负值（正数增加，负数减少）
        - 自动处理数值类型转换和计算
        
        说明:
        - 使用safe_float确保数值类型的正确转换
        - 先获取变量的当前值，然后加上变化值
        - 使用setvaluable函数安全地设置新值
        - 支持全局变量和角色局部变量
        """
        dic = S_eval(self, flag)
        logging.debug(dic)
        variable = dic["VARIABLE"]
        value = dic["VALUE"]
        logging.debug((safe_float(value), safe_float(getvaluable(self, variable)), self.variables))
        setvaluable(self,
                    variable,
                    safe_str(safe_float(value) + safe_float(getvaluable(self, variable)))
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
        if (self,dic["LIST"]) in list_name_to_id:
            id=list_name_to_id[(self,dic["LIST"])]
        else:
            id=list_name_to_id[(stage,dic["LIST"])]    
        thelist:list[str]=getlist(self,id)
        thelist.append(safe_str(dic["ITEM"]))
        #logging.debug(thelist)   
    def data_deleteoflist(self,flag):
        dic=S_eval(self,flag)   
        logging.debug(dic)
        if (self,dic["LIST"]) in list_name_to_id:
            id=list_name_to_id[(self,dic["LIST"])]
        else:
            id=list_name_to_id[(stage,dic["LIST"])]    
        thelist:list[str]=getlist(self,id)
        thelist.pop(safe_int(dic["INDEX"])-1)

    def data_deletealloflist(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        logging.debug(list_name_to_id)
        if (self,dic["LIST"]) in list_name_to_id:
            id=list_name_to_id[(self,dic["LIST"])]
        else:
            id=list_name_to_id[(stage,dic["LIST"])]    
        thelist:list[str]=getlist(self,id)
        #thelist.pop(safe_int(dic["INDEX"])-1)
        thelist.clear()
    def data_itemoflist(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        if (self,dic["LIST"]) in list_name_to_id:
            id=list_name_to_id[(self,dic["LIST"])]
        else:
            id=list_name_to_id[(stage,dic["LIST"])]    
        thelist:list[str]=getlist(self,id)
        return safe_str(thelist[safe_int(dic["INDEX"])-1])
    def data_insertatlist(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        if (self,dic["LIST"]) in list_name_to_id:
            id=list_name_to_id[(self,dic["LIST"])]
        else:
            id=list_name_to_id[(stage,dic["LIST"])]    
        thelist:list[str]=getlist(self,id)
        thelist.insert(safe_int(dic["INDEX"])-1,safe_str(dic["ITEM"]))
    def data_replaceitemoflist(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        if (self,dic["LIST"]) in list_name_to_id:
            id=list_name_to_id[(self,dic["LIST"])]
        else:
            id=list_name_to_id[(stage,dic["LIST"])]    
        thelist:list[str]=getlist(self,id)
        thelist[safe_int(dic["INDEX"])-1]=safe_str(dic["ITEM"])  
    def data_itemnumoflist(self,flag):  
        dic=S_eval(self,flag)
        logging.debug(dic)
        if (self,dic["LIST"]) in list_name_to_id:
            id=list_name_to_id[(self,dic["LIST"])]
        else:
            id=list_name_to_id[(stage,dic["LIST"])]    
        thelist:list[str]=getlist(self,id)
        for i in thelist:
            if i==safe_str(dic["ITEM"]):
                return safe_str(thelist.index(i)+1)
        return safe_str(0)
    def data_lengthoflist(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        if (self,dic["LIST"]) in list_name_to_id:
            id=list_name_to_id[(self,dic["LIST"])]
        else:
            id=list_name_to_id[(stage,dic["LIST"])]    
        thelist:list[str]=getlist(self,id)
        return safe_str(len(thelist))
    def data_listcontainsitem(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        if (self,dic["LIST"]) in list_name_to_id:
            id=list_name_to_id[(self,dic["LIST"])]
        else:
            id=list_name_to_id[(stage,dic["LIST"])]    
        thelist:list[str]=getlist(self,id)
        return safe_str(safe_str(dic["ITEM"]) in thelist)
    def data_showlist(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        #thelist:list[str]=getlist(self,dic["LIST"])
        for i in monitor_list:
            if i.id==dic["LIST"]:
                i.visible=True
    def data_hidelist(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        #thelist:list[str]=getlist(self,dic["LIST"])
        for i in monitor_list:
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
        #计时器的数值存储在stage.time中
        return safe_str(time.time()-stage.time)
    def sensing_resettimer(self,flag=None):
        stage.time=time.time()
    def collision(self,others:"Sprite"|Literal["_mouse_"]):
        logging.debug(others)   
        if others=="_mouse_":
            mouse_x,mouse_y=pygame.mouse.get_pos()
            mouse_x/=2
            mouse_y/=2
            rect=pygame.Rect(mouse_x-5,mouse_y-5,10,10)
            others=Sprite({"x":mouse_x,"y":mouse_y,"name":"mouse","rect":rect})
            others.mask=pygame.mask.Mask((10,10),True)
            logging.debug(others.rect)
        if others=="_edge_":
            if not (0 <=self.rect.left <= self.rect.right <= 480):
                return True
            if not (0 <=self.rect.top <= self.rect.bottom <= 360):
                return True
            return False
                 
            
        #粗略检测矩形，后续可以加入精细检测    
        if self.rect.colliderect(others.rect):
            print("角色碰撞了！")
            return True
        else:
            print("角色没有碰撞")
            return False
    def sensing_touchingobject(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        if dic["TOUCHINGOBJECTMENU"]=="_mouse_":
            return safe_str(self.collision("_mouse_"))
        if dic["TOUCHINGOBJECTMENU"]=="_edge_":
            return safe_str(self.collision("_edge_"))
        for i in sprite_list:
            if i.name==dic["TOUCHINGOBJECTMENU"]:
                return safe_str(self.collision(i))
        else:
            raise Exception("没有找到"+dic["TOUCHINGOBJECTMENU"]+"这个角色")    
    def sensing_touchingobjectmenu(self,flag):
        dic=S_eval( self,flag)  
        logging.debug(dic)
        return dic['TOUCHINGOBJECTMENU']
    def sensing_distancetomenu(self,flag) -> Position :
        
        dic=S_eval(self,flag)
        logging.debug(dic)
        if dic["DISTANCETOMENU"]=="_mouse_":
            mouse_x,mouse_y=pygame.mouse.get_pos()
            return Position(mouse_x,mouse_y,"show")
        else:
            for i in sprite_list:
                if i.name==dic["DISTANCETOMENU"]:
                    return Position(i.x,i.y)
    def sensing_distanceto(self,flag) -> str:
        dic=S_eval(self,flag)
        logging.debug(dic)
        
        dest_x,dest_y=dic["DISTANCETOMENU"].scratch()
        
        x,y=self.x,self.y
        logging.debug((x,y))
        x=safe_float(x-dest_x)
        y=safe_float(y-dest_y)
        logging.debug((x,y))
        return safe_str(math.sqrt(x**2+y**2))
    def sensing_mousedown(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        return safe_str(pygame.mouse.get_pressed()[0])
    def sensing_mousex(self,flag):
        """
        由于要传到scratch层，所以按照scratch的坐标系
        """
        dic=S_eval(self,flag)
        logging.debug(dic)
        return safe_str(pygame.mouse.get_pos()[0]/2-240)
    def sensing_mousey(self,flag):
        """
        由于要传到scratch层，所以按照scratch的坐标系
        """
        dic=S_eval(self,flag)
        logging.debug(dic)
        return safe_str(180-pygame.mouse.get_pos()[1]/2)
    def sensing_dayssince2000(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        return safe_str(time.time()/86400-10957)#10957是2000年1月1日距离1970年1月1日的天数
    def sensing_username(self,flag):
        dic=S_eval(self,flag)
        logging.debug(dic)
        return safe_str(os.getlogin())#获取用户名,但获取windows用户名有点扯
    def sensing_loudness(self,flag):
        logging.warning("声音检测功能暂未实现")
        return safe_str(100)
    def procedures_call(self,flag2):
        dic=S_eval(self,flag2)
        #procedures_definition
        tagname=self.blocks[flag2]["mutation"]["proccode"]
        #logging.debug(tagname)
        for flag1, code in self.blocks.items():
            if code["opcode"] == "procedures_prototype":
                flag_procedure_prototype=flag1
                
        for flag1, code in self.blocks.items():  
            try:
                if code["inputs"]["custom_block"][1]== flag_procedure_prototype:
                    flag_procedure_definition=flag1
            except:
                pass         
        self.procedure({
            "flag_procedure_prototype":flag_procedure_prototype,
            "flag_procedure_definition":flag_procedure_definition,
            "tagname":tagname,
            "callerflag":flag2,

        },
        dic
        )           
    def procedure(self,flags,argcs):
        logging.debug((self,flags,argcs))
        
        for key,value in argcs.items():
            #在读取参数时，scratch完全按照名字检索，所以要把id转成名字
            mutation=self.blocks[flags["flag_procedure_prototype"]]["mutation"]
            #去你妈的，mutation["argumentids"]是一个字符串，长得像一个列表，像这样 "["a","b","c"]"
            #在字符状态下，先全部统一大写，然后再用eval转成列表，再用zip和dict转成字典
            #最后实现这样的效果
            #dict1={'FWV;F_+X!EOJ}8AFV[*)': 'content', 'VS}LUVVOE?WQMI#.^D}P': 'secs'}
            mutation["argumentids"]="".join(list(map(str.upper,mutation["argumentids"])))
            dict1=dict(zip(eval(mutation["argumentids"]),eval(mutation["argumentnames"])))
            logging.debug(dict1)
            name=dict1[key]
            
            self.argument_dict[(threading.current_thread(),name)]=value
            logging.debug(self.argument_dict)
        runcode(self,flags["flag_procedure_definition"])

    def argument_reporter_string_number(self,flag):
        #按照变量名获取参数
        #紫色块变量名完全按照名字检索，完全不用考虑id
        #这里变量名放在self.argument_dict[(threading.current_thread(),name)]中
        dic=S_eval(self,flag)
        logging.debug(dic)
        logging.debug(self.argument_dict)
        return self.argument_dict[(threading.current_thread(),dic["VALUE"])]    
            
    procedure_definition=event_whenflagclicked
    
    
            
        


class Monitor:
    def __str__(self):
        return self.params["VARIABLE"]
    @property
    def name(self):
        return self.params["VARIABLE"]
    def __init__(self,dict1):
        for name, value in dict1.items():
            #logging.debug((name, value))
            setattr(self, name, value)
        self.sprite=stage#全局变量默认从stage中找，
        #这是为什么stage不允许局部变量的原因
        #project.json是这么处理的

        if self.spriteName is not  None:
            for i in sprite_list:               
                if str(i)==self.spriteName:
                    self.sprite=i
            
        if self.mode=="list":
            self.show_y=0    
        #logging.debug(self.mode)
    def draw(self):
        #logging.debug(self.__dict__)
        if not self.visible:
            return
        variablename=self.id
        
        sprite=self.sprite        
        if self.opcode=="data_variable":
                    
            value=getvaluable(sprite,variablename)
            #logging.debug(self.params["VARIABLE"])
            #logging.debug(value)
            #text=" "+self.params["VARIABLE"]+":"+value+" "
            """
            if sprite!=stage:
                text=" "+str(sprite)+text"""
            drawvariable(self,value,screen)
        elif self.opcode=="data_listcontents":
            thelist=getlist(sprite,self.id)
            drawlist(self,thelist,screen)    
        else:
            value=getattr(sprite,self.opcode)(None)
            #这些当做显示框的积木都不用输入参数
            #但输入时需要输入参数，所以这里用None代替
            front=" "+str(sprite)+":"+self.opcode.replace("motion_","")
            drawvariable(self,front+value,screen)

         

def runcode(sprite: Sprite, flag: str,should_next: str = True)  :
    """
    next_flag参数用来控制是否执行下一个积木,设置为False时不执行
    这样可以集成一个控制器，防止递归调用
    """
    global done
    if done:
        return

    if flag is None:
        return
        


    logging.info(f"进入{sprite.name}的{sprite.blocks[flag]['opcode']}函数")
    result = None
    try:
        func = getattr(sprite, sprite.blocks[flag]["opcode"])
        result = func(flag)    
    except AttributeError:
        logging.error(f"缺少函数{sprite.blocks[flag]['opcode']}")
    except Exception as e:
        
        logging.error(f"执行积木{flag}时出错: {traceback.format_exc()}")
    
    clock.tick(TPS)
    if should_next:
        #只有积木块第一个积木才会执行这块python代码
        #之后的积木都在这里顺序执行
        logging.debug("进入顺序执行控制器")
        #breakpoint()
        next_flag=sprite.blocks[flag].get("next")
        while next_flag!=None:
            if sprite.clone_mode==2:
                return
        
            runcode(sprite=sprite, flag=next_flag,should_next=False)
            next_flag=sprite.blocks[next_flag].get("next")

        
            
    return result

# 主程序从这里开始
logging.info("开始程序")    
pygame.init()
    
show_screen = pygame.display.set_mode(STAGE_SHOW_SIZE)
screen = pygame.Surface(STAGE_SIZE)
logging.info("初始化pygame")    
with zipfile.ZipFile("project.sb3") as f:
    filenamelist = f.namelist()
    f.extractall()

t = json.loads(open("project.json", "r", encoding="utf-8").read())
logging.info("解析json文件")
sprite_list = []  # 角色们
clone_list = []

done = False  # done是用来标记程序是否运行，False代表运行，true代表结束
clock = pygame.time.Clock()
    
for i in t["targets"]:
    i["clone_mode"] = 0  # 0=原始, 1=克隆体, 2=已删除
    sprite = Sprite(i)
    sprite_list.append(sprite)


    #提取角色的变量和列表
    sprite.variables={}
    sprite.lists={}
    variables_name={}
    #logging.debug(sprite.variables)

    for j in i["variables"].items():
        #logging.debug(j)
        sprite.variables[j[0]]=safe_str(j[1][1])
        variables_name[j[0]]=safe_str(j[1][0])
    for j in i["lists"].items():
        logging.debug(j)
        listid=j[0]
        listname=j[1][0]
        list_name_to_id.update({(sprite,listname):listid})
        thelist=j[1][1]
        thelist=[safe_str(k) for k in thelist]
        sprite.lists[j[0]]=thelist
     
    logging.info(f"提取{sprite}的变量"  )  
    logging.debug(sprite.variables)
    logging.debug(variables_name)

    if sprite.isStage:
        stage = sprite
        stage.time = time.time()
    
    # 注册初始线程
    for flag, code in sprite.blocks.items():
        if code["opcode"] == "event_whenflagclicked":
            thread = threading.Thread(
                name=f"{sprite.name}_{flag}",
                target=runcode,
                args=(sprite, flag),
                daemon=True
            )
            thread.start()
            thread_manager.add_thread(thread)

logging.info("提取变量完成") 
logging.debug(list_name_to_id)         
monitor_list=[]            
for i in t["monitors"]:
    monitor=Monitor(i)
    monitor_list.append(monitor)
logging.info("创建显示框完成")
# 设置窗口标题
pygame.display.set_caption("scratch")

# 渲染线程主循环
logging.info("进入主循环")
try:
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
            
            i.draw() 

                
                
        for i in monitor_list:

            i.draw() 
     

            # 更新窗口
            
        scaled_screen=pygame.transform.scale(screen,(960,720))
        
        show_screen.blit(scaled_screen,(0,0))
        

        pygame.display.update()
            
        clock.tick(FPS)


        
except KeyboardInterrupt:
    logging.error("键盘中断")
except Exception as e:
    logging.error(f"主循环异常: {traceback.format_exc()}")
finally:
    # 优雅退出
    logging.warning("退出程序")
    done = True
    thread_manager.stop_all_threads()
    pygame.quit()
    
    # 清理临时文件
    for filename in filenamelist:
        if logging.getLogger().level <= logging.DEBUG:
            break
        try:
            os.remove(filename)
        except:
            pass
