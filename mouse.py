import pygame


# 初始化 Pygame
pygame.init()

# 创建一个窗口
#screen = pygame.display.set_mode((800, 600))

# 定义颜色
white = (255, 255, 255)

# 初始化鼠标位置和时间
previous_mouse_pos = pygame.mouse.get_pos()
previous_time = pygame.time.get_ticks()

# 事件循环
running = True
def get_mouse_speed():
    global previous_mouse_pos, previous_time
    

    # 获取当前鼠标位置和时间
    current_mouse_pos = pygame.mouse.get_pos()
    current_time = pygame.time.get_ticks()

    # 计算时间差和位置差
    time_diff = current_time - previous_time
    pos_diff = (current_mouse_pos[0] - previous_mouse_pos[0], current_mouse_pos[1] - previous_mouse_pos[1])

    # 计算速度（像素/秒）
    if time_diff > 0:
        speed = (pos_diff[0] / time_diff * 1000, pos_diff[1] / time_diff * 1000)
    else:
        speed = (0, 0)

    # 更新前一个位置和时间
    previous_mouse_pos = current_mouse_pos
    previous_time = current_time
    return speed[0]/2,speed[1]/2    
