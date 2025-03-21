# Agent 模块

Agent 模块是 OpenManus 的核心组件，负责实现智能代理的基本行为和决策逻辑。

## 模块结构

```
agent/
├── base.py       # 代理基类定义
├── browser.py    # 浏览器代理实现
├── manus.py      # Manus 通用代理实现
└── ...           # 其他专用代理
```

## 核心组件

### BaseAgent

`BaseAgent` 是所有代理的抽象基类，定义了代理的基本行为和状态管理：

- **状态管理**：维护代理的运行状态（空闲、运行中、完成、错误等）
- **内存系统**：存储对话历史和上下文信息
- **执行循环**：实现基于步骤的执行模式
- **防循环检测**：检测并处理代理陷入循环的情况

### Manus

`Manus` 是一个通用的智能代理实现，继承自 `BrowserAgent`，具有以下特点：

- **多工具集成**：集成了 Python 执行、浏览器控制、文件编辑等多种工具
- **上下文感知**：能够根据对话上下文调整行为
- **灵活规划**：支持任务分解和规划

### BrowserAgent

`BrowserAgent` 是一个专门用于网络浏览和交互的代理：

- **网页访问**：支持访问和解析网页内容
- **交互操作**：支持在网页上执行点击、输入等操作
- **内容提取**：能够从网页中提取结构化信息

## 使用示例

```python
from app.agent.manus import Manus

# 创建 Manus 代理实例
agent = Manus()

# 运行代理处理请求
async def process_request(prompt):
    result = await agent.run(prompt)
    return result
```

## 扩展指南

要创建自定义代理，可以继承 `BaseAgent` 或其子类：

```python
from app.agent.base import BaseAgent

class CustomAgent(BaseAgent):
    name = "CustomAgent"
    description = "A specialized agent for specific tasks"
    
    async def step(self):
        # 实现单步执行逻辑
        pass
```
