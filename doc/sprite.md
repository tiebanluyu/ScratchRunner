# scratch.py 下的 sprite 类
## 定义
传入一个字典，包含 sprite 相关的属性，按照字典的键值对进行初始化。
同时额外加入word 和argument_dict参数，分别表示 sprite 显示的文字和参数字典。
argument_dict 是一个字典，用于自定义函数的取值时，
如下
'''{(<Thread(121f, started 25228)>, 'content'): '你好', (<Thread(121f, started 25228)>, 'secs'): '1'}'''
表示 Thread(121f, started 25228) 线程的 content 参数的值为 '你好'，secs 参数的值为 '1'。
因为不同的线程可能执行不同的函数，所以需要传入线程和参数的元组作为键。
## 方法
### draw
绘制 sprite 到屏幕上。
costume是一个字典，包含所要显示的图片相关信息，包括图片路径、位置、旋转角度等。
然后根据costume从目录中加载图片，并根据位置、旋转角度进行绘制。
其中blitRotate是从网络上找的函数，用于绘制旋转图片。
然后由drawtext方法绘制说的话。
## scratch积木块
取名我进行了偷懒，project.json中是怎么命名的我就怎么命名。
这样一进行解析就可以直接将积木块对应到spite类的方法上。
或许会出问题，不过可以先这样。
### 定义
因为在初始化时会使project.json中角色的blocks属性赋给sprite的blocks属性，所以这里参数是flag 
这是一个字符串，代表project.json中积木对应的key值。
然后根据flag找到对应的block 
通过S_eval 进行解析，得到对应的参数，然后实现相应的功能。
### motion 运动
逐个模仿scratch的动作，包括移动、旋转。

### event 事件
主要是绿旗，引发程序运作。
### control 控制
控制程序的执行流程，包括循环、分支、停止等。
### data 数据
主要是变量、链表等。
### looks 外观
主要是改变角色的外貌，大小等。
特效暂时实现不了。
### operator 运算
大于、小于、等于、乘除、加减等。
#### 在大于小于等于时，分两类
1.浮点数比较（大于、小于、等于用math.isclose()）
2.字符串比较可以很合适得兼容数字的比较。
 
#### 在and or not 运算时，可以直接用python的逻辑运算符。
但是用户可能不会往里面丢积木，经过测试，默认为false。
但是project.json中这个参数是缺失的，
不能简单切片，用dic.get("OPERAND1",False)

#### 字符串处理用python自带的，简单

## data 变量
另起




