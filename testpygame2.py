import pygame
import tkinter as tk
from tkinter import simpledialog

# 初始化 Pygame
pygame.init()
window_size = (500, 400)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("文本输入框示例")

# 字体设置
font = pygame.font.SysFont('Arial', 32)
text = ''

# 创建一个 Tkinter 窗口
root = tk.Tk()
root.withdraw()  # 隐藏主窗口

# 创建输入框函数
def get_input():
    global text
    text = simpledialog.askstring("输入", "请输入文本：", parent=root)

# 主循环
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # 按下空格键时弹出输入框
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            pass
        get_input()  # 获取输入

    screen.fill((0, 0, 0))
    # 渲染用户输入的文本
    text_surface = font.render(text, True, (255, 255, 255))
    screen.blit(text_surface, (100, 100))

    pygame.display.flip()
