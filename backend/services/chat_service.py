import asyncio
import json
import uuid
from typing import AsyncGenerator, Dict, List, Optional, Any
from openmanus.app.agent.manus import Manus
from openmanus.app.tool import FileOperatorsTool

class ChatService:
    """聊天服务，处理与OpenManus的交互"""
    
    def __init__(self):
        self.chat_histories = {}  # 存储聊天历史
        self.analysis_status = {}  # 存储分析状态
    
    async def process_message(self, message: str, chat_id: Optional[str] = None, document_id: Optional[str] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """处理用户消息，返回流式响应"""
        # 如果没有聊天ID，创建一个新的
        if not chat_id:
            chat_id = str(uuid.uuid4())
            self.chat_histories[chat_id] = []
        
        # 保存用户消息
        user_message = {
            "id": str(uuid.uuid4()),
            "role": "user",
            "content": message,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        if chat_id in self.chat_histories:
            self.chat_histories[chat_id].append(user_message)
        else:
            self.chat_histories[chat_id] = [user_message]
        
        # 返回用户消息确认
        yield {
            "type": "message",
            "content": user_message,
            "chat_id": chat_id
        }
        
        # 创建思考中的消息
        thinking_id = str(uuid.uuid4())
        thinking_message = {
            "id": thinking_id,
            "role": "thinking",
            "content": "正在分析问题...",
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # 返回思考中的消息
        yield {
            "type": "thinking",
            "content": thinking_message,
            "chat_id": chat_id,
            "thinking_id": thinking_id
        }
        
        # 创建OpenManus代理
        agent = Manus()
        file_tool = FileOperatorsTool()
        agent.available_tools.add_tool(file_tool)
        
        # 更明确的分析提示语
        prompt = f"""你是一个专业的法律分析助手，需要回答用户关于刑事案件的问题。

用户问题: {message}

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
   - 例如，搜索所有包含"证据"或"供述"的文件

5. 在阅读过程中，请特别关注：
   - 证据链完整性：物证/书证/证人证言之间的对应关系是否一致
   - 法律条文适用性：罪名与法条的匹配度是否合理
   - 时间线逻辑：侦查/批捕/起诉时间节点是否合规

6. 请特别注意比较不同文件中的信息，检查是否存在矛盾：
   - 证人证言之间是否一致
   - 物证与证人证言是否匹配
   - 鉴定意见与案件事实是否吻合
   - 供述与其他证据是否存在冲突

7. 最后，请以下面的结构化格式提供分析报告：

```json
{{
  "案件名称": "张振荣、张振伟被杀案",
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
  "回答用户问题": "",
  "总结与建议": ""
}}
```

请开始你的分析工作。在分析过程中，请清晰地指出你正在查看的文件和你从中发现的关键信息。最后，确保直接回答用户的问题：{message}
"""
        
        try:
            # 添加调试日志
            print("开始运行OpenManus代理")
            
            # 设置工作目录为 business 文件夹
            import os
            # 获取项目根目录，而不是 backend 目录
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            business_dir = os.path.join(project_root, "business")
            print(f"设置工作目录为: {business_dir}")
            os.chdir(business_dir)
            
            # 设置超时时间
            try:
                # 运行代理，并设置超时时间为300秒（5分钟）
                result = await asyncio.wait_for(agent.run(prompt), timeout=300)
                print(f"OpenManus代理运行完成，结果: {result[:100]}...")
            except asyncio.TimeoutError:
                print("代理运行超时，返回默认答案")
                result = "对不起，分析过程超时。请尝试提问更具体的问题，或者简化您的问题。"
            
            # 创建助手回复
            assistant_message = {
                "id": str(uuid.uuid4()),
                "role": "assistant",
                "content": result,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # 保存助手回复
            self.chat_histories[chat_id].append(assistant_message)
            
            # 返回最终结果
            yield {
                "type": "message",
                "content": assistant_message,
                "chat_id": chat_id,
                "remove_thinking": thinking_id
            }
            
        except Exception as e:
            # 添加详细的错误日志
            print(f"OpenManus代理运行出错: {str(e)}")
            import traceback
            print(f"错误详情: {traceback.format_exc()}")
            
            # 处理错误
            error_message = {
                "id": str(uuid.uuid4()),
                "role": "system",
                "content": f"分析过程中出现错误: {str(e)}",
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # 保存错误消息
            self.chat_histories[chat_id].append(error_message)
            
            # 返回错误消息
            yield {
                "type": "error",
                "content": error_message,
                "chat_id": chat_id,
                "remove_thinking": thinking_id
            }
    
    async def get_history(self, chat_id: str) -> List[Dict[str, Any]]:
        """获取聊天历史"""
        return self.chat_histories.get(chat_id, [])
    
    async def delete_chat(self, chat_id: str) -> bool:
        """删除聊天记录"""
        if chat_id in self.chat_histories:
            del self.chat_histories[chat_id]
            return True
        return False
    
    async def get_analysis_status(self, analysis_id: str) -> Dict[str, Any]:
        """获取分析状态"""
        return self.analysis_status.get(analysis_id, {"status": "not_found"})
