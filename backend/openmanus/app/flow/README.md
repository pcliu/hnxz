# Flow 模块

Flow 模块是 OpenManus 的工作流管理系统，负责协调多个代理和任务的执行流程，实现复杂任务的规划和执行。

## 模块结构

```
flow/
├── base.py          # 工作流基类定义
├── flow_factory.py  # 工作流工厂
├── planning.py      # 规划工作流实现
└── ...              # 其他专用工作流
```

## 核心组件

### BaseFlow

`BaseFlow` 是所有工作流的抽象基类，定义了工作流的基本结构和行为：

- **代理管理**：管理和协调多个代理
- **状态追踪**：跟踪工作流执行状态
- **执行控制**：控制工作流的启动、暂停和终止

### PlanningFlow

`PlanningFlow` 是一个基于规划的工作流实现，具有以下特点：

- **任务规划**：使用 LLM 自动生成执行计划
- **步骤管理**：跟踪和管理计划步骤的执行
- **动态调整**：根据执行结果动态调整计划
- **代理选择**：根据任务类型选择合适的执行代理

### FlowFactory

`FlowFactory` 是一个工厂类，用于创建和配置不同类型的工作流：

- **工作流实例化**：根据配置创建工作流实例
- **代理配置**：配置工作流使用的代理

## 使用示例

```python
from app.flow.planning import PlanningFlow
from app.agent.manus import Manus

# 创建代理
agent = Manus()

# 创建规划工作流
flow = PlanningFlow(agents={"default": agent})

# 执行工作流
async def execute_task(request):
    result = await flow.execute(request)
    return result
```

## 扩展指南

要创建自定义工作流，可以继承 `BaseFlow`：

```python
from app.flow.base import BaseFlow

class CustomFlow(BaseFlow):
    """自定义工作流实现"""
    
    async def execute(self, input_text: str) -> str:
        # 实现工作流执行逻辑
        pass
```
