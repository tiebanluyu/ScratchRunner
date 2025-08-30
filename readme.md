# scratch runner
## 1. 介绍
scratch runner 是一个基于pygame的scratch运行器。

## 2. 功能
- 运行Scratch项目
- 没有别的了

## 3. 重构更新

对项目进行了全面的代码重构和文档完善：
- **代码结构优化**：重新组织模块和类结构，提高可读性和可维护性
- **完整注释和文档**：为所有关键类、函数和方法添加了详细的文档字符串
- **坐标系转换优化**：改进Scratch坐标系与Pygame坐标系之间的转换逻辑
- **线程管理和错误处理**：增强多线程角色控制的稳定性和错误处理
- **监视器系统改进**：优化变量和列表监视器的显示和更新逻辑

## 4. 项目结构

项目的主要文件和目录结构如下：

```
ScratchRunner/
├── doc/                  # 项目文档
│   ├── data.md           # 数据结构文档
│   ├── project.md        # 项目文件结构文档
│   └── sprite.md         # 角色相关文档
├── pygameinputs/         # Pygame输入组件库
│   ├── __init__.py
│   ├── Button.py         # 按钮组件
│   ├── Label.py          # 标签组件
│   ├── Sliders.py        # 滑块组件
│   └── TextBox.py        # 文本框组件
├── scratch.py            # 主程序入口
├── blocks.py             # 积木块执行逻辑
├── sprite.py             # 角色类定义
├── variable.py           # 变量处理
├── readme.md             # 项目说明文档
├── LICENSE               # 许可证文件
└── ...                   # 其他文件
```

## 5. 运行
### 5.1 傻瓜式安装
- 从releaase页面下载最新版的scratch_runner.zip
- 解压到任意目录
- 将project.sb3文件换成自己的项目文件
- 双击运行scratch_runner.exe
