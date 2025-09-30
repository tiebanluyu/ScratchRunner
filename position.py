from typing import List, Tuple, Literal
class Position:
    """
    处理Scratch坐标系与Pygame坐标系之间的转换
    
    坐标系说明：
    - Scratch坐标系：原点在舞台中心(0,0)，x向右为正(-240到240)，y向上为正(-180到180)
    - Pygame坐标系：原点在左上角(0,0)，x向右为正(0到960)，y向下为正(0到960)
    - Show坐标系：用于2倍缩放显示(960x720)，提供更好的视觉效果
    
    
    """
    SCRATCH=(-240,240,-180,180) # 最左边x,最右边x,最下边y,最上边y
    PYGAME=(0,960,720,0)
    SHOW=(0,960,720,0)
    @staticmethod
    def position_map(from_tuple:Tuple[int,int,int,int],destination_tuple:Tuple[int,int,int,int],x:int,y:int)->Tuple[int,int]:
        """
        通用坐标转换函数
        
        参数:
        from_tuple: 源坐标系范围 (x_min, x_max, y_min, y_max)
        destination_tuple: 目标坐标系范围 (x_min, x_max, y_min, y_max)
        x, y: 源坐标系中的坐标值
        
        返回:
        (new_x, new_y): 目标坐标系中的坐标值
        
        说明:
        - 通过线性映射实现任意两个坐标系之间的转换
        - 保持相对位置和比例不变
        """
        from_x_min, from_x_max, from_y_min, from_y_max = from_tuple
        dest_x_min, dest_x_max, dest_y_min, dest_y_max = destination_tuple
        
        # 计算比例因子
        scale_x = (dest_x_max - dest_x_min) / (from_x_max - from_x_min)
        scale_y = (dest_y_max - dest_y_min) / (from_y_max - from_y_min)
        
        # 进行线性映射
        new_x = dest_x_min + (x - from_x_min) * scale_x
        new_y = dest_y_min + (y - from_y_min) * scale_y
        
        return int(new_x), int(new_y)
        



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
            self.x, self.y = self.position_map(self.PYGAME,self.SCRATCH,x, y)
        elif mode == "show":
            self.x, self.y = self.position_map(self.SHOW,self.SCRATCH,x, y)
    
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
        return self.position_map(self.SCRATCH,self.PYGAME,self.x, self.y)
    
    def show(self) -> Tuple[int, int]:
        """
        获取显示坐标系坐标（2倍缩放）
        
        返回:
        (x, y): 显示坐标系中的坐标值
        """
        return self.position_map(self.SCRATCH,self.SHOW,self.x, self.y)