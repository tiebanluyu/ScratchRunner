import turtle
import xml.etree.ElementTree as ET
 
 
def draw_svg(svg_file):
    # 创建turtle画布
    screen = turtle.Screen()
    screen.setup(800, 600)
    screen.bgcolor("white")
 
    # 创建turtle对象
    t = turtle.Turtle()
    t.speed(0)  # 设置速度为最快，如果想要慢慢欣赏可以调节速度
 
    # 解析SVG文件
    tree = ET.parse(svg_file)
    root = tree.getroot()
 
    # 绘制SVG元素
    for element in root.iter():
        tag = element.tag.split('}')[-1]
        print(element.attrib)
        if tag == 'circle':
            draw_circle(t, element.attrib)
            
        elif tag == 'rect':
            draw_rect(t, element.attrib)
        elif tag == 'line':
            draw_line(t,element.attrib)
            # 可以继续添加其他元素的绘制函数
 
    # 隐藏turtle并显示绘制结果
    t.hideturtle()
    turtle.done()
 
 
def draw_circle(t, attribs):
    cx = 0-(float(attribs['cx'])-400)
    cy = 0-(float(attribs['cy'])-300)
    r = float(attribs['r'])
    t.penup()
    t.goto(cx, cy)
    t.pendown()
    t.circle(r)
 
 
def draw_rect(t, attribs):
    x = float(attribs['x'])-400
    y = 0-(float(attribs['y'])-300)
    width = float(attribs['width'])
    height = float(attribs['height'])
    t.penup()
    t.goto(x, y)
    t.pendown()
    for _ in range(2):
        t.forward(width)
        t.right(90)
        t.forward(height)
        t.right(90)
 
def draw_line(t, attrib):
    x1 = float(attrib['x1'])-400
    y1 = 0-(float(attrib['y1'])-300)
    x2 = float(attrib['x2'])-400
    y2 = 0-(float(attrib['y2'])-300)
    t.penup()
    t.goto(x1, y1)
    t.pendown()
    t.goto(x2, y2)
# 可以继续添加其他元素的绘制函数
 
if __name__ == "__main__":
    svg_file = r"927d672925e7b99f7813735c484c6922 copy.svg"
    draw_svg(svg_file)