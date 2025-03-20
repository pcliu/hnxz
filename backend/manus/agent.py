import asyncio
from typing import Dict, Any, List, AsyncGenerator, Optional
import os
import sys
import json
import markdown

# 添加OpenManus到Python路径
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'openmanus'))

# 导入OpenManus相关模块
from app.agent.manus import Manus
from app.config import config
from app.tool.str_replace_editor import StrReplaceEditor
from app.tool.python_execute import PythonExecute

class LegalAnalysisAgent:
    """法律文档分析Agent，基于OpenManus实现"""
    
    def __init__(self):
        # 初始化OpenManus的Manus Agent
        self.manus_agent = Manus()
        
        # 设置工作目录
        config.workspace_root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'business')
    
    async def analyze_document(self, document_content: str, query: str) -> AsyncGenerator[Dict[str, Any], None]:
        """分析文档内容"""
        # 创建任务计划
        tasks = [
            {"name": "document_parsing", "description": "解析文档内容"},
            {"name": "evidence_analysis", "description": "分析证据链完整性"},
            {"name": "legal_verification", "description": "验证法律条文适用性"},
            {"name": "timeline_check", "description": "检查时间线逻辑"},
            {"name": "generate_response", "description": "生成综合分析结果"}
        ]
        
        # 更新用户查询，添加任务信息
        enhanced_query = f"""请分析以下文档内容，回答用户的问题：{query}

文档内容：
{document_content[:2000]}...

请执行以下任务：
1. 解析文档内容
2. 分析证据链完整性（物证/书证/证人证言对应关系）
3. 验证法律条文适用性（罪名与法条匹配度）
4. 检查时间线逻辑（侦查/批捕/起诉时间节点合规性）
5. 生成综合分析结果

对于每个任务，请提供详细的分析过程和结果。"""
        
        # 执行任务计划
        results = []
        current_task_index = 0
        
        # 首先返回任务计划
        yield {
            "status": "planning", 
            "tasks": tasks,
            "message": "正在规划分析任务..."
        }
        
        # 处理第一个任务：解析文档
        current_task = tasks[current_task_index]
        yield {
            "status": "processing", 
            "current_task": current_task["name"], 
            "description": current_task["description"]
        }
        
        # 使用OpenManus进行文档解析
        try:
            # 初始化Manus Agent的运行环境
            self.manus_agent.memory.add_user_message(enhanced_query)
            
            # 开始执行任务
            async for step_result in self._run_agent_with_progress(tasks):
                # 返回中间结果
                yield step_result
                
                # 如果是任务完成结果，添加到结果列表
                if step_result.get("status") == "completed":
                    results.append(step_result.get("result", {}))
            
            # 返回最终结果
            final_result = self._combine_results(results)
            yield {"status": "finished", "result": final_result}
            
        except Exception as e:
            # 处理异常
            error_message = f"分析过程中发生错误: {str(e)}"
            yield {"status": "error", "message": error_message}
    
    async def _run_agent_with_progress(self, tasks: List[Dict[str, str]]) -> AsyncGenerator[Dict[str, Any], None]:
        """运行Agent并返回进度信息"""
        for i, task in enumerate(tasks):
            # 更新当前任务状态
            yield {"status": "processing", "current_task": task["name"], "description": task["description"]}
            
            # 构建特定任务的提示
            task_prompt = f"执行任务: {task['description']}"
            self.manus_agent.memory.add_user_message(task_prompt)
            
            # 运行一步Agent
            await self.manus_agent.step()
            
            # 获取Agent的响应
            last_message = self.manus_agent.memory.messages[-1].content if self.manus_agent.memory.messages else ""
            
            # 返回任务完成结果
            task_result = {
                "task": task["name"],
                "description": task["description"],
                "analysis": last_message
            }
            
            yield {"status": "completed", "task": task["name"], "result": task_result}
    
    def _combine_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """合并所有任务结果"""
        # 提取各个任务的分析结果
        document_parsing = next((r for r in results if r.get("task") == "document_parsing"), {})
        evidence_analysis = next((r for r in results if r.get("task") == "evidence_analysis"), {})
        legal_verification = next((r for r in results if r.get("task") == "legal_verification"), {})
        timeline_check = next((r for r in results if r.get("task") == "timeline_check"), {})
        final_response = next((r for r in results if r.get("task") == "generate_response"), {})
        
        # 提取引用信息
        references = self._extract_references(results)
        
        return {
            "summary": final_response.get("analysis", "综合分析结果"),
            "document_parsing": document_parsing,
            "evidence_analysis": evidence_analysis,
            "legal_verification": legal_verification,
            "timeline_check": timeline_check,
            "references": references
        }
    
    def _extract_references(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取文档引用"""
        references = []
        
        # 从各个任务结果中提取引用
        for result in results:
            analysis = result.get("analysis", "")
            if isinstance(analysis, str):
                # 简单的引用提取逻辑，实际应用中可能需要更复杂的实现
                # 这里假设引用格式为："参见文档：xxx，第y页"
                import re
                ref_matches = re.findall(r'参见文档：([^，]+)，第(\d+)页', analysis)
                
                for doc_name, page in ref_matches:
                    references.append({
                        "document": doc_name.strip(),
                        "page": int(page),
                        "context": "引用上下文"
                    })
        
        return references
    
    async def analyze_evidence(self, document_content: str) -> Dict[str, Any]:
        """分析证据链完整性"""
        query = "分析以下文档中的证据链完整性（物证/书证/证人证言对应关系）"
        async for result in self.analyze_document(document_content, query):
            if result.get("status") == "finished":
                return result.get("result", {}).get("evidence_analysis", {})
        return {"status": "error", "message": "分析失败"}
    
    async def verify_legal_provisions(self, document_content: str) -> Dict[str, Any]:
        """验证法律条文适用性"""
        query = "验证以下文档中的法律条文适用性（罪名与法条匹配度）"
        async for result in self.analyze_document(document_content, query):
            if result.get("status") == "finished":
                return result.get("result", {}).get("legal_verification", {})
        return {"status": "error", "message": "验证失败"}
    
    async def check_timeline(self, document_content: str) -> Dict[str, Any]:
        """检查时间线逻辑"""
        query = "检查以下文档中的时间线逻辑（侦查/批捕/起诉时间节点合规性）"
        async for result in self.analyze_document(document_content, query):
            if result.get("status") == "finished":
                return result.get("result", {}).get("timeline_check", {})
        return {"status": "error", "message": "检查失败"}
