import uuid
from typing import Dict, Any, List, Optional, AsyncGenerator
from services.document_service import DocumentService
from manus.agent import LegalAnalysisAgent

class ChatService:
    """聊天服务，用于处理聊天交互和文档分析"""
    
    def __init__(self):
        self.document_service = DocumentService()
        self.agent = LegalAnalysisAgent()
        # 内存中存储聊天历史，实际应用中应该使用数据库
        self.chat_history = {}
        # 存储正在进行的分析任务
        self.active_analyses = {}
    
    async def process_message(self, message: str, chat_id: Optional[str] = None, document_id: Optional[str] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """处理聊天消息，返回分析进度和结果"""
        # 如果没有聊天ID，创建一个新的
        if not chat_id:
            chat_id = str(uuid.uuid4())
            self.chat_history[chat_id] = []
        
        # 如果聊天ID不存在，创建一个新的
        if chat_id not in self.chat_history:
            self.chat_history[chat_id] = []
        
        # 添加用户消息到历史记录
        self.chat_history[chat_id].append({
            "role": "user",
            "content": message
        })
        
        # 获取文档内容
        document_content = None
        document = None
        if document_id:
            document = await self.document_service.get_document(document_id)
            if document:
                document_content = document.get("content", "")
        
        # 初始化分析任务
        analysis_id = str(uuid.uuid4())
        self.active_analyses[analysis_id] = {
            "chat_id": chat_id,
            "document_id": document_id,
            "query": message,
            "status": "planning",
            "tasks": [],
            "completed_tasks": [],
            "current_task": None,
            "references": []
        }
        
        # 返回初始状态
        yield {
            "analysis_id": analysis_id,
            "chat_id": chat_id,
            "status": "planning",
            "message": "正在分析您的问题..."
        }
        
        # 如果没有文档内容，返回错误
        if not document_content and document_id:
            error_response = {
                "analysis_id": analysis_id,
                "chat_id": chat_id,
                "status": "error",
                "message": "无法获取文档内容，请确认文档ID是否正确。"
            }
            
            # 添加系统回复到历史记录
            self.chat_history[chat_id].append({
                "role": "assistant",
                "content": error_response["message"]
            })
            
            yield error_response
            return
        
        try:
            # 使用Agent分析文档
            if document_content:
                # 如果有文档内容，使用Agent分析
                async for result in self.agent.analyze_document(document_content, message):
                    # 更新分析状态
                    self._update_analysis_status(analysis_id, result)
                    
                    # 返回分析进度
                    yield {
                        "analysis_id": analysis_id,
                        "chat_id": chat_id,
                        "status": result.get("status", "processing"),
                        "current_task": result.get("current_task", ""),
                        "task_description": result.get("description", ""),
                        "message": self._format_result_message(result)
                    }
                    
                    # 如果分析完成，更新历史记录
                    if result.get("status") == "finished":
                        final_result = result.get("result", {})
                        final_message = final_result.get("summary", "分析完成")
                        references = final_result.get("references", [])
                        
                        # 添加系统回复到历史记录
                        self.chat_history[chat_id].append({
                            "role": "assistant",
                            "content": final_message,
                            "references": references
                        })
                        
                        # 返回最终结果
                        yield {
                            "analysis_id": analysis_id,
                            "chat_id": chat_id,
                            "status": "finished",
                            "message": final_message,
                            "references": references
                        }
            else:
                # 如果没有文档内容，直接回复
                response_message = "请选择一个文档进行分析，或者提供更具体的问题。"
                
                # 添加系统回复到历史记录
                self.chat_history[chat_id].append({
                    "role": "assistant",
                    "content": response_message
                })
                
                # 返回结果
                yield {
                    "analysis_id": analysis_id,
                    "chat_id": chat_id,
                    "status": "finished",
                    "message": response_message
                }
        except Exception as e:
            # 处理异常
            error_message = f"分析过程中发生错误: {str(e)}"
            
            # 添加系统回复到历史记录
            self.chat_history[chat_id].append({
                "role": "assistant",
                "content": error_message
            })
            
            # 返回错误
            yield {
                "analysis_id": analysis_id,
                "chat_id": chat_id,
                "status": "error",
                "message": error_message
            }
        
        # 分析完成后清理活动分析任务
        if analysis_id in self.active_analyses:
            del self.active_analyses[analysis_id]
    
    def _update_analysis_status(self, analysis_id: str, result: Dict[str, Any]) -> None:
        """更新分析状态"""
        if analysis_id not in self.active_analyses:
            return
        
        analysis = self.active_analyses[analysis_id]
        status = result.get("status")
        
        if status == "planning":
            analysis["status"] = "planning"
            analysis["tasks"] = result.get("tasks", [])
        elif status == "processing":
            analysis["status"] = "processing"
            analysis["current_task"] = result.get("current_task")
        elif status == "completed":
            task = result.get("task")
            task_result = result.get("result", {})
            analysis["completed_tasks"].append({
                "task": task,
                "result": task_result
            })
        elif status == "finished":
            analysis["status"] = "finished"
            analysis["result"] = result.get("result", {})
            analysis["references"] = result.get("result", {}).get("references", [])
    
    def _format_result_message(self, result: Dict[str, Any]) -> str:
        """格式化结果消息"""
        status = result.get("status")
        
        if status == "planning":
            return "正在规划分析任务..."
        elif status == "processing":
            current_task = result.get("current_task", "")
            description = result.get("description", "")
            return f"正在执行任务: {description}"
        elif status == "completed":
            task = result.get("task", "")
            task_result = result.get("result", {})
            return f"任务完成: {task}"
        elif status == "finished":
            return "分析完成"
        elif status == "error":
            return result.get("message", "分析过程中发生错误")
        else:
            return "正在处理..."
    
    async def get_history(self, chat_id: str) -> List[Dict[str, Any]]:
        """获取聊天历史"""
        return self.chat_history.get(chat_id, [])
    
    async def get_analysis_status(self, analysis_id: str) -> Dict[str, Any]:
        """获取分析状态"""
        if analysis_id in self.active_analyses:
            return self.active_analyses[analysis_id]
        return {"status": "not_found", "message": "分析任务不存在"}
    
    async def delete_chat(self, chat_id: str) -> bool:
        """删除聊天记录"""
        if chat_id in self.chat_history:
            del self.chat_history[chat_id]
            return True
        return False
