import pygame

pygame.init()

# 加载图像
image = pygame.image.load("dc05463bfd05f0b5e4e39ea4e94e43fe.svg")

# 设置图像旋转点
image_center = image.get_rect().center
rotated_image = pygame.transform.rotate(image, 45)
rotated_image_rect = rotated_image.get_rect(center=image_center)

# 创建窗口并显示旋转后的图像
screen = pygame.display.set_mode(rotated_image.get_rect().size)
screen.blit(rotated_image, rotated_image_rect.topleft)
pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
