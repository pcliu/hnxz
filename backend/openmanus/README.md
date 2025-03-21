# OpenManus

OpenManus 是一个强大的 AI Agent 框架，专为构建复杂的智能代理系统而设计。它提供了一套完整的工具和组件，使开发者能够创建能够规划、执行和监控任务的智能代理。

## 核心特性

- **智能规划**：基于大型语言模型的任务规划和执行
- **工具集成**：丰富的内置工具集，包括文件操作、网络搜索、Python 执行等
- **浏览器控制**：支持 Web 浏览和交互
- **可扩展性**：模块化设计，易于扩展和定制

## 系统架构

```
openmanus/
├── app/                  # 核心应用代码
│   ├── agent/            # 代理实现
│   ├── flow/             # 工作流管理
│   ├── prompt/           # 提示模板
│   ├── tool/             # 工具集合
│   ├── sandbox/          # 沙盒环境
│   ├── llm.py            # 大语言模型接口
│   └── config.py         # 配置管理
├── workspace/            # 工作空间目录
├── main.py               # 主入口点
└── run_flow.py           # 工作流执行
```

## 快速开始

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 配置环境变量：
   - 设置 OpenAI API 密钥或其他 LLM 服务配置

3. 运行示例：
   ```bash
   python main.py
   ```

## 集成到项目

OpenManus 可以作为库集成到其他 Python 项目中：

```python
from app.agent.manus import Manus

async def process_request(prompt):
    agent = Manus()
    result = await agent.run(prompt)
    return result
```

## 许可证

请参阅项目根目录下的许可证文件。
