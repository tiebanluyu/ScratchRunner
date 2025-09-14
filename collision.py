import pygame

def check_collision(rect1, image1, rect2, image2):
    """
    检测两个不规则图像之间的碰撞
    
    参数:
    rect1, rect2: pygame.Rect 对象，表示图像的位置和大小
    image1, image2: pygame.Surface 对象，表示要检测的图像
    
    返回:
    bool: 如果发生碰撞返回 True，否则返回 False
    """
    # 第一步：使用矩形碰撞检测进行快速筛选
    if not rect1.colliderect(rect2):
        return False
    
    # 第二步：创建图像的遮罩（mask）
    mask1 = pygame.mask.from_surface(image1)
    mask2 = pygame.mask.from_surface(image2)
    
    # 第三步：计算两个矩形之间的偏移量
    offset_x = rect2.x - rect1.x
    offset_y = rect2.y - rect1.y
    
    # 第四步：使用遮罩检测实际像素碰撞
    overlap = mask1.overlap(mask2, (offset_x, offset_y))
    
    # 如果有重叠像素，返回 True，否则返回 False
    return overlap is not None


# 使用示例
def example_usage():
    # 初始化 Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # 创建两个示例图像（实际使用时替换为你的图像）
    # 注意：这些图像应该具有透明背景以便正确检测碰撞
    image1 = pygame.Surface((100, 100), pygame.SRCALPHA)
    pygame.draw.circle(image1, (255, 0, 0), (50, 50), 50)  # 红色圆形
    
    image2 = pygame.Surface((80, 80), pygame.SRCALPHA)
    pygame.draw.polygon(image2, (0, 0, 255), [(40, 0), (0, 80), (80, 80)])  # 蓝色三角形
    
    # 创建对应的矩形
    rect1 = image1.get_rect(center=(200, 300))
    rect2 = image2.get_rect(center=(400, 300))
    
    # 移动速度
    speed1 = [2, 1]
    speed2 = [-1, 2]
    
    # 游戏循环
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # 更新位置
        rect1.move_ip(speed1)
        rect2.move_ip(speed2)
        
        # 边界检测
        if rect1.left < 0 or rect1.right > 800:
            speed1[0] *= -1
        if rect1.top < 0 or rect1.bottom > 600:
            speed1[1] *= -1
            
        if rect2.left < 0 or rect2.right > 800:
            speed2[0] *= -1
        if rect2.top < 0 or rect2.bottom > 600:
            speed2[1] *= -1
        
        # 检测碰撞
        collision = check_collision(rect1, image1, rect2, image2)
        
        # 绘制
        screen.fill((0, 0, 0))
        screen.blit(image1, rect1)
        screen.blit(image2, rect2)
        
        # 显示碰撞状态
        font = pygame.font.Font(None, 36)
        text = font.render(f"collision:{collision}", True, (255, 255, 255))
        screen.blit(text, (20, 20))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

# 运行示例
if __name__ == "__main__":
    example_usage()