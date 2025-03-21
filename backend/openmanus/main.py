import asyncio
import os
from pathlib import Path

from app.agent.manus import Manus
from app.config import config
from app.logger import logger
from app.tool import FileOperatorsTool
from app.tool.tool_collection import ToolCollection


async def analyze_criminal_case(agent, case_name):
    """分析刑事案件的证据链和法律适用情况"""
    # 构建详细的分析提示语，引导 Agent 先查看文件清单，然后有选择地阅读文件
    prompt = f"""
你是一个专业的法律分析助手，需要分析{case_name}的证据链完整性和法律适用正确性。

请按照以下步骤进行分析：

1. 首先，使用 file_operators 工具列出工作区中的所有目录，了解文件组织结构
   - 使用参数：{{
     "action": "list_directory",
     "path": "."
   }}

2. 根据目录结构，逐个查看各个文件夹中的文件
   - 例如：{{
     "action": "list_directory",
     "path": "诉讼文书卷"
   }}

3. 选择与案件相关的文件进行阅读，特别关注以下几类文件：
   - 起诉书、判决书等法律文书
   - 证人证言
   - 鉴定意见
   - 物证清单
   - 案件报告
   - 使用参数：{{
     "action": "read_file",
     "path": "文件路径"
   }}

4. 你也可以使用搜索功能查找特定信息：
   - 使用参数：{{
     "action": "search_files",
     "path": ".",
     "query": "关键词"
   }}
   - 例如，搜索所有包含“证据”或“供述”的文件

5. 在阅读过程中，请特别关注：
   - 证据链完整性：物证/书证/证人证言之间的对应关系是否一致
   - 法律条文适用性：罪名与法条的匹配度是否合理
   - 时间线逻辑：侦查/批捕/起诉时间节点是否合规

6. 请特别注意比较不同文件中的信息，检查是否存在矛盾：
   - 证人证言之间是否一致
   - 物证与证人证言是否匹配
   - 鉴定意见与案件事实是否吹合
   - 供述与其他证据是否存在冲突

7. 最后，请以下面的结构化格式提供分析报告：

```json
{{
  "案件名称": "{case_name}",
  "案件概述": {{
    "被告人": "",
    "罪名": "",
    "案件时间": "",
    "案件地点": "",
    "案件简述": ""
  }},
  "证据链分析": {{
    "完整性": "",
    "一致性": "",
    "物证": [""],
    "书证": [""],
    "证人证言": [""],
    "发现的问题": [""]
  }},
  "法律适用分析": {{
    "罪名适用": "",
    "法条引用": "",
    "量刑建议": "",
    "发现的问题": [""]
  }},
  "时间线分析": {{
    "主要时间节点": [
      {{"时间": "", "事件": ""}}
    ],
    "合规性": "",
    "发现的问题": [""]
  }},
  "总结与建议": ""
}}
```

请开始你的分析工作。在分析过程中，请清晰地指出你正在查看的文件和你从中发现的关键信息。
"""
    
    logger.warning(f"开始分析{case_name}...")
    logger.warning(f"工作区路径: {config.workspace_root}")
    
    # 运行代理进行分析
    await agent.run(prompt)
    logger.info("案件分析完成。")


async def main():
    # 创建包含文件操作工具的 Manus 代理
    agent = Manus()
    
    # 添加文件操作工具到代理的工具集合中
    file_tool = FileOperatorsTool()
    agent.available_tools.add_tool(file_tool)
    
    try:
        # 可以根据需要修改案件名称
        # 根据文件内容，使用正确的案件名称
        case_name = "张振荣、张振伟被杀案"
        
        # 分析指定案件
        await analyze_criminal_case(agent, case_name)
    except KeyboardInterrupt:
        logger.warning("操作被中断。")
    except Exception as e:
        logger.error(f"分析过程中出现错误: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
