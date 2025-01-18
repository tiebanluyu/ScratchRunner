# 讲一下project.json的格式
这里的project.json是指在scratch中打开的项目文件，位于项目文件夹中，文件名为project.json。
project分为targets 和monitors两大部分和extension meta两小部分
# targets
targets是一个列表，存储的对象代表scratch角色（含舞台）
含有以下参数
## isStage
这个角色是舞台，为true
不是的话，为False
## name
是显示在scratch角色名字栏里的字符
舞台在编辑器中不能设定名字，在文件中标记为"Stage"
## variables
存储角色局部变量的字典，全局变量存储在舞台的variables字典中，
舞台没有自己的局部变量。
键为乱码字符串，长为20位，代表变量的id
值是一个由两个元素组成的字典，0号元素为这个变量的名称，1号元素为这个变量的值
如果在保存时变量的值为整数或小数，则存储为整数或小数。
否则，格式为字符串。


## lists
存储角色局部变量的字典
同变量类似，不过值是一个列表，所有列表元素都是字符串string型。

## broadcasts 

顾名思义为广播，id同变量列表。
键为id，值为名称。

## blocks
字典，存储所有积木块。
键为积木块的id，是从a到z，再A到Z，再符号。
用完之后会用两个符号表示，接下来的就复杂了
具体值取决于各个块的具体实际，大部分都是看得明白的。
以下是通用的几个属性

| 属性 | 解释 |
| ----------- | ----------- |
| opcode | 积木名称，取名很简单 |
| next | 连在这个积木下面的积木的id |
| parent | 上一个积木的id |、
| shadow | 不知道 |
| topLevel | 积木可能会重叠在一起，toplevel为true则显示在最上端 |
| x | 如果一个积木上面没积木（不一定是控制类，也可以是弃块）|
| y | 会提供x，y坐标，以便在积木区放在一个合适的位置 |
| inputs |大部分块的输入 |
| fields |少部分块的输入 ,以选择什么的块居多|
| currentCostume | 角色当前的造型，在costumes列表中的索引 |
| costumes | 角色所有造型的列表 |
| sounds | 角色所有声音的列表 |
|volume | 声音的音量 |
| layerOrder | 积木层级，越大越上层 |
| rotationStyle | 旋转方式 ，用数字表示|
| visible | 是否可见 ，可见为true |
