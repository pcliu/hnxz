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

请按照以下步骤回答问题：

1. 首先使用 file_operators 工具列出当前目录下的文件：
   {{"action": "list_directory", "path": "."}}

2. 查看“故意杀人起诉 诉讼文书卷”目录下的文件：
   {{"action": "list_directory", "path": "故意杀人起诉 诉讼文书卷"}}

3. 阅读“故意杀人起诉 诉讼文书卷/起诉书.md”文件内容：
   {{"action": "read_file", "path": "故意杀人起诉 诉讼文书卷/起诉书.md"}}

4. 阅读“故意杀人起诉 诉讼文书卷/判决书.md”文件内容：
   {{"action": "read_file", "path": "故意杀人起诉 诉讼文书卷/判决书.md"}}

5. 根据以上文件内容，简要回答用户问题。包括案件的基本情况、罪名、判决结果等。

请直接执行上述步骤，不要添加额外的分析或解释。
"""
        
        # OpenManus的Manus对象没有set_output_callback方法
        # 我们将在运行代理后直接处理结果
        
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
                # 运行代理，并设置超时时间为30秒
                result = await asyncio.wait_for(agent.run(prompt), timeout=30)
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
