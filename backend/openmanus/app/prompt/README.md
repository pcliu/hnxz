# Prompt 模块

Prompt 模块是 OpenManus 的提示模板系统，为代理提供结构化的指令和上下文，指导大语言模型生成高质量的响应。

## 功能概述

Prompt 模块提供以下核心功能：

- **提示模板**：为不同代理和场景提供专用的提示模板
- **上下文管理**：管理和组织提示的上下文信息
- **动态格式化**：支持动态插入变量和参数
- **多场景支持**：支持规划、浏览器操作、代码生成等多种场景

## 模块结构

```
prompt/
├── __init__.py     # 模块初始化
├── manus.py        # Manus 代理提示
├── browser.py      # 浏览器代理提示
├── planning.py     # 规划提示
└── ...             # 其他专用提示
```

## 主要提示模板

### 系统提示 (System Prompts)

系统提示定义了代理的角色、能力和行为准则：

- **Manus 系统提示**：定义 Manus 代理的通用能力和行为
- **浏览器代理系统提示**：定义浏览器代理的网页交互能力
- **规划系统提示**：定义规划代理的任务分解和规划能力

### 步骤提示 (Step Prompts)

步骤提示指导代理执行具体的步骤和决策：

- **下一步提示**：指导代理决定下一步行动
- **思考提示**：指导代理进行推理和分析
- **执行提示**：指导代理执行具体操作

## 使用示例

```python
from app.prompt.manus import SYSTEM_PROMPT, NEXT_STEP_PROMPT

# 格式化系统提示
formatted_system_prompt = SYSTEM_PROMPT.format(
    directory="/path/to/workspace"
)

# 在代理中使用提示
class CustomAgent(BaseAgent):
    system_prompt = formatted_system_prompt
    next_step_prompt = NEXT_STEP_PROMPT
    
    # 使用提示进行思考和决策
    async def think(self):
        # 使用提示指导 LLM 思考
        pass
```

## 提示设计原则

OpenManus 的提示设计遵循以下原则：

1. **明确指令**：提供清晰、具体的指令
2. **角色定义**：明确定义代理的角色和能力
3. **上下文管理**：提供足够但不过多的上下文
4. **步骤引导**：引导代理按步骤思考和行动
5. **错误处理**：指导代理处理错误和异常情况

## 扩展指南

要创建新的提示模板，可以遵循以下步骤：

1. 在 `prompt/` 目录下创建新的模块文件
2. 定义常量字符串作为提示模板
3. 使用 `{variable}` 语法添加动态变量
4. 在代理中使用 `.format()` 方法填充变量
