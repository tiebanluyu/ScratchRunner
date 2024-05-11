import turtle

import json
t=json.loads(open("project.json","r",encoding="utf-8").read())

class Sprite:
    def __init__(self,dict1) -> None:

        self.__dict__.update(dict1)
        #print(self.name)
    def draw(self):
        t=turtle.Turtle()
        turtle.register_shape("1.gif")

        t.shape("1.gif")

    
list1=[]
for i in t["targets"]:
    o=Sprite(i)
    list1.append(o)
    print(o,o.name)
turtle.setworldcoordinates(-240, -180, 240, 180)
turtle.tracer(False)

while 1:
    turtle.clear()
    for sprite in list1:
        sprite.draw()
    turtle.update()