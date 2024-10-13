import pygame
from pygameinputs.TextBox import TextBox
import os
# 初始化 Pygame
pygame.init()
screen = pygame.display.set_mode((500, 400))
pygame.display.set_caption("Pygame 输入示例")

# 创建一个文本输入框
input_box = TextBox(100, 100, 300, 40)
input_box.text="1111"
input_box.font_size = 20
input_box.active=True

# 主循环
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 处理输入框的事件
        input_box.typing(event)

    # 清屏
    screen.fill((0, 0, 0))

    # 更新和渲染输入框
    #input_box.update()
    input_box.draw(screen)


    # 显示当前输入的内容
    #print(input_box.get_text())

    pygame.display.flip()

pygame.quit()
