# 讲述Scratch中变量的相关操作
# 三个函数
在sprite类以外，设置了getvaluable，setvaluable,getlist.
显然，setlist没有那么简单，而且scratch没有一次性修改整个列表的功能。

这三个函数的原因是，当程序拿到变量及其id后，不知道这个是全局变量还是局部变量，要寻找变量的具体位置，就需要用到这三个函数。

# 变量
id：变量的唯一标识符，是乱码字符串。

## 初始化
sprite在初始化时，会提取到sprite.variables和variables_name两个字典中，
variables_name是id到变量名的映射，全局统一，因为不会冲突
sprite.variables是会随着程序运行而变化的变量字典，id到变量值的映射。
因为每个sprite都有自己的变量。全局变量存储在stage.variables中。
这也是为什么在scratch中，舞台不允许拥有自己的局部变量。
project.json中是这么定义的，不是我确定的。

##动态修改变量
全局函数setvaluable和getvaluable是用来动态读取修改变量的函数。
setvaluable(id,value)可以修改变量的值，getvaluable(id)可以获取变量的值。
这个是python层的。
scratch层的变量读取，直接包含在对应积木的参数中，没有自己独立的积木
scratch层的修改通过data_setvariableto积木实现。
同时，data_changevariableby可以给变量增加或减少值。