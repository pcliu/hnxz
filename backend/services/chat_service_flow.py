import asyncio
import json
import uuid
from typing import AsyncGenerator, Dict, List, Optional, Any, Union

from openmanus.app.agent.manus import Manus
from openmanus.app.flow.base import FlowType, PlanStepStatus
from openmanus.app.flow.flow_factory import FlowFactory
from openmanus.app.schema import AgentState
from openmanus.app.tool import FileOperatorsTool, PlanningTool


class ChatServiceFlow:
    """基于Flow的聊天服务，处理与OpenManus的交互"""
    
    def __init__(self):
        self.chat_histories = {}  # 存储聊天历史
        self.analysis_status = {}  # 存储分析状态
        self.flows = {}  # 存储每个聊天会话的Flow实例
    
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

        try:
            # 获取或创建Flow实例
            if chat_id not in self.flows:
                # 创建agents
                agents = {
                    "manus": Manus(),  # 主要agent
                }
                
                # 为agents添加工具
                file_tool = FileOperatorsTool()
                planning_tool = PlanningTool()
                agents["manus"].available_tools.add_tool(file_tool)
                agents["manus"].available_tools.add_tool(planning_tool)
                
                # 创建Flow实例
                flow = FlowFactory.create_flow(
                    flow_type=FlowType.PLANNING,
                    agents=agents,
                    plan_id=f"analysis_{chat_id}"  # 为每个聊天会话创建唯一的plan_id
                )
                self.flows[chat_id] = flow
            else:
                flow = self.flows[chat_id]

            # 设置工作目录为 business 文件夹
            import os
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            business_dir = os.path.join(project_root, "business")
            print(f"设置工作目录为: {business_dir}")
            os.chdir(business_dir)

            # 构建更明确的提示词，使agent能够自主执行所有步骤而不需要用户干预
            prompt = f"""你是一个专业的法律分析助手，需要回答用户关于刑事案件的问题。你需要自主完成所有分析步骤，不需要等待用户的进一步指示。

用户问题: {message}

请按照以下步骤进行分析：

1. 首先，使用 planning 工具创建一个分析计划：
   - 使用参数：{{
     "command": "create",
     "plan_id": "case_analysis",
     "title": "案件分析计划",
     "steps": [
       "了解文件组织结构",
       "查看案件基本信息文件",
       "分析证据材料",
       "检查证人证言",
       "分析法律文书",
       "整合信息回答用户问题"
     ]
   }}

2. 使用 file_operators 工具列出工作区中的所有目录，了解文件组织结构
   - 使用参数：{{
     "action": "list_directory",
     "path": "."
   }}

3. 根据目录结构，逐个查看各个文件夹中的文件
   - 例如：{{
     "action": "list_directory",
     "path": "诉讼文书卷"
   }}

4. 选择与案件相关的文件进行阅读，特别关注以下几类文件：
   - 起诉书、判决书等法律文书
   - 证人证言
   - 鉴定意见
   - 物证清单
   - 案件报告
   - 使用参数：{{
     "action": "read_file",
     "path": "文件路径"
   }}

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
  "案件名称": "",
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
    "发现的问题": [""],
  }},
  "法律适用分析": {{
    "罪名适用": "",
    "法条引用": "",
    "量刑建议": "",
    "发现的问题": [""],
  }},
  "时间线分析": {{
    "主要时间节点": [
      {{"时间": "", "事件": ""}}
    ],
    "合规性": "",
    "发现的问题": [""],
  }},
  "回答用户问题": "",
  "总结与建议": ""
}}
```

重要说明：
1. 你必须自主完成所有步骤，不要等待用户的进一步指示
2. 每个步骤完成后，自动继续执行下一个步骤
3. 在分析过程中，请清晰地指出你正在查看的文件和你从中发现的关键信息
4. 最后，确保直接回答用户的问题：{message}
5. 如果遇到任何问题，尝试自行解决，不要等待用户的指示

请立即开始你的分析工作，并自主完成所有步骤。
"""

            # 修改 Manus agent 的行为，使其能够自主执行所有步骤
            agents["manus"].max_steps = 30  # 增加最大步骤数
            agents["manus"].duplicate_threshold = 3  # 提高重复检测阈值
            
            # 修改 flow 的行为，确保能够自主执行
            flow.planning_tool.plans[flow.active_plan_id] = {
                "title": f"分析计划: {message[:30]}...",
                "steps": [
                    "了解文件组织结构",
                    "查看案件基本信息文件",
                    "分析证据材料",
                    "检查证人证言",
                    "分析法律文书",
                    "整合信息回答用户问题"
                ],
                "step_statuses": [PlanStepStatus.NOT_STARTED.value] * 6,
                "step_notes": [""] * 6
            }
            
            # 执行Flow
            result = await asyncio.wait_for(
                flow.execute(prompt),
                timeout=300  # 5分钟超时
            )
            
            # 如果 agent 状态为 RUNNING，强制设置为 FINISHED
            if agents["manus"].state == AgentState.RUNNING:
                agents["manus"].state = AgentState.FINISHED

            # 创建助手回复消息
            assistant_message = {
                "id": str(uuid.uuid4()),
                "role": "assistant",
                "content": result,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # 保存助手回复到聊天历史
            self.chat_histories[chat_id].append(assistant_message)
            
            # 返回助手回复
            yield {
                "type": "message",
                "content": assistant_message,
                "chat_id": chat_id,
                "thinking_id": thinking_id
            }

        except asyncio.TimeoutError:
            error_message = {
                "id": str(uuid.uuid4()),
                "role": "error",
                "content": "分析超时，请尝试简化您的问题。",
                "timestamp": asyncio.get_event_loop().time()
            }
            yield {
                "type": "error",
                "content": error_message,
                "chat_id": chat_id,
                "thinking_id": thinking_id
            }
        except Exception as e:
            error_message = {
                "id": str(uuid.uuid4()),
                "role": "error",
                "content": f"分析过程中出现错误: {str(e)}",
                "timestamp": asyncio.get_event_loop().time()
            }
            yield {
                "type": "error",
                "content": error_message,
                "chat_id": chat_id,
                "thinking_id": thinking_id
            }

    async def get_chat_history(self, chat_id: str) -> List[Dict[str, Any]]:
        """获取指定聊天会话的历史记录"""
        return self.chat_histories.get(chat_id, [])

    def clear_chat_history(self, chat_id: str) -> bool:
        """清除指定聊天会话的历史记录"""
        if chat_id in self.chat_histories:
            del self.chat_histories[chat_id]
            if chat_id in self.flows:
                del self.flows[chat_id]  # 同时清除Flow实例
            return True
        return False
