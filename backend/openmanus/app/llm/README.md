# LLM 模块

LLM 模块是 OpenManus 的大语言模型接口，负责与各种语言模型服务进行通信，为代理系统提供智能决策和自然语言处理能力。

## 功能概述

LLM 模块提供了以下核心功能：

- **模型调用**：支持 OpenAI、Azure OpenAI 等多种 LLM 服务
- **令牌计数**：精确计算文本和图像的令牌使用量
- **多模态支持**：支持文本和图像的混合输入
- **工具调用**：支持函数调用和工具使用
- **错误处理**：提供重试机制和错误恢复
- **配置管理**：支持多种模型配置和切换

## 主要组件

### LLM 类

`LLM` 类是模块的核心，提供了与语言模型交互的统一接口：

- **单例模式**：每个配置名称对应一个实例
- **异步接口**：所有方法都是异步的，支持高效的并发操作
- **多种调用方式**：支持直接对话、工具调用、流式响应等

### TokenCounter 类

`TokenCounter` 类负责计算输入内容的令牌数量：

- **文本令牌计算**：计算文本内容的令牌数
- **图像令牌计算**：根据图像尺寸和细节级别计算令牌数
- **消息令牌计算**：计算完整消息列表的令牌数

## 使用示例

```python
from app.llm import LLM
from app.schema import Message

# 创建 LLM 实例
llm = LLM()

# 发送简单请求
async def ask_question(question):
    messages = [Message.user_message(question)]
    response = await llm.ask(messages)
    return response.content

# 使用工具
async def use_tool(question, tools):
    messages = [Message.user_message(question)]
    response = await llm.ask_tool(messages, tools=tools)
    return response
```

## 配置示例

LLM 模块支持通过配置文件进行配置：

```python
# 配置示例
llm_config = {
    "default": {
        "model": "gpt-4",
        "max_tokens": 4096,
        "temperature": 0.7,
        "api_type": "openai",
        "api_key": "your-api-key"
    },
    "fast": {
        "model": "gpt-3.5-turbo",
        "max_tokens": 2048,
        "temperature": 0.5,
        "api_type": "openai",
        "api_key": "your-api-key"
    }
}

# 使用特定配置
llm = LLM(config_name="fast")
```

## 扩展指南

要支持新的 LLM 服务，可以扩展 `LLM` 类：

1. 在 `__init__` 方法中添加新的 API 类型判断
2. 添加相应的客户端初始化逻辑
3. 在 `_call_llm` 方法中添加新的调用逻辑
