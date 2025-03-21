# Tool 模块

Tool 模块是 OpenManus 的工具集合，提供了丰富的功能组件，使代理能够执行各种操作和任务。

## 模块结构

```
tool/
├── __init__.py           # 模块初始化
├── base.py               # 工具基类定义
├── tool_collection.py    # 工具集合管理
├── bash.py               # Bash 命令执行工具
├── python_execute.py     # Python 代码执行工具
├── browser_use_tool.py   # 浏览器控制工具
├── file_operators.py     # 文件操作工具
├── str_replace_editor.py # 文本编辑工具
├── planning.py           # 规划工具
├── web_search.py         # 网络搜索工具
├── search/               # 搜索工具集合
└── ...                   # 其他专用工具
```

## 核心组件

### BaseTool

`BaseTool` 是所有工具的抽象基类，定义了工具的基本接口和行为：

- **参数定义**：定义工具的输入参数
- **执行接口**：提供统一的执行接口
- **结果处理**：处理工具执行结果

### ToolCollection

`ToolCollection` 是工具集合管理类，用于管理和协调多个工具：

- **工具注册**：注册和管理多个工具
- **工具查找**：根据名称查找工具
- **执行分发**：将执行请求分发到相应的工具

### 主要工具

- **PythonExecute**：执行 Python 代码
- **BrowserUseTool**：控制浏览器进行网页访问和交互
- **StrReplaceEditor**：编辑文本内容
- **Bash**：执行 Bash 命令
- **FileOperators**：执行文件操作（读取、写入、删除等）
- **PlanningTool**：创建和管理任务计划
- **WebSearch**：执行网络搜索

## 使用示例

```python
from app.tool import ToolCollection
from app.tool.python_execute import PythonExecute
from app.tool.file_operators import FileOperators

# 创建工具集合
tools = ToolCollection(
    PythonExecute(),
    FileOperators()
)

# 执行工具
async def execute_tool(tool_name, **params):
    result = await tools.execute(tool_name, **params)
    return result
```

## 扩展指南

要创建自定义工具，可以继承 `BaseTool`：

```python
from app.tool.base import BaseTool

class CustomTool(BaseTool):
    name = "custom_tool"
    description = "A custom tool for specific operations"
    parameters = {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "First parameter"},
            "param2": {"type": "integer", "description": "Second parameter"}
        },
        "required": ["param1"]
    }
    
    async def execute(self, **kwargs):
        # 实现工具执行逻辑
        pass
```
