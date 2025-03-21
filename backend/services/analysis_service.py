import asyncio
import json
import uuid
from typing import Dict, Any, List
from openmanus.app.agent.manus import Manus
from openmanus.app.tool import FileOperatorsTool

class AnalysisService:
    """分析服务，处理与OpenManus的交互进行文档分析"""
    
    def __init__(self):
        self.analysis_results = {}  # 存储分析结果
    
    async def analyze(self, document_id: str, query: str) -> Dict[str, Any]:
        """分析文档内容"""
        analysis_id = str(uuid.uuid4())
        
        # 创建OpenManus代理
        agent = Manus()
        file_tool = FileOperatorsTool()
        agent.available_tools.add_tool(file_tool)
        
        # 构建分析提示语
        prompt = f"""
你是一个专业的法律分析助手，需要分析刑事案件文档并回答用户的问题。

用户问题: {query}
文档ID: {document_id}

请按照以下步骤进行分析：

1. 首先，使用 file_operators 工具列出工作区中的所有目录，了解文件组织结构
2. 根据目录结构，逐个查看与问题相关的文件
3. 分析文件内容，找出与用户问题相关的信息
4. 提供详细的分析结果，包括引用的文件和具体内容

请开始你的分析工作。
"""
        
        try:
            # 运行代理，设置超时时间为300秒（5分钟）
            result = await asyncio.wait_for(agent.run(prompt), timeout=300)
            
            # 保存分析结果
            analysis_result = {
                "id": analysis_id,
                "document_id": document_id,
                "query": query,
                "result": result,
                "status": "completed",
                "timestamp": asyncio.get_event_loop().time()
            }
            
            self.analysis_results[analysis_id] = analysis_result
            return analysis_result
            
        except Exception as e:
            # 处理错误
            error_result = {
                "id": analysis_id,
                "document_id": document_id,
                "query": query,
                "result": f"分析过程中出现错误: {str(e)}",
                "status": "error",
                "timestamp": asyncio.get_event_loop().time()
            }
            
            self.analysis_results[analysis_id] = error_result
            return error_result
    
    async def analyze_evidence(self, document_content: str) -> Dict[str, Any]:
        """分析证据链完整性"""
        # 创建OpenManus代理
        agent = Manus()
        file_tool = FileOperatorsTool()
        agent.available_tools.add_tool(file_tool)
        
        # 构建分析提示语
        prompt = """
你是一个专业的法律分析助手，需要分析刑事案件的证据链完整性。

请按照以下步骤进行分析：

1. 使用 file_operators 工具查看案件相关文件
2. 重点关注物证、书证和证人证言之间的对应关系
3. 检查证据之间是否存在矛盾或不一致
4. 评估证据链的完整性和可靠性

请提供详细的分析结果，包括发现的问题和建议。
"""
        
        try:
            # 运行代理，设置超时时间为300秒（5分钟）
            result = await asyncio.wait_for(agent.run(prompt), timeout=300)
            
            return {
                "status": "success",
                "result": result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "result": f"分析过程中出现错误: {str(e)}"
            }
    
    async def verify_legal_provisions(self, document_content: str) -> Dict[str, Any]:
        """验证法律条文适用性"""
        # 创建OpenManus代理
        agent = Manus()
        file_tool = FileOperatorsTool()
        agent.available_tools.add_tool(file_tool)
        
        # 构建分析提示语
        prompt = """
你是一个专业的法律分析助手，需要验证刑事案件中法律条文的适用性。

请按照以下步骤进行分析：

1. 使用 file_operators 工具查看案件相关文件
2. 识别案件中引用的法律条文
3. 评估罪名与法条的匹配度
4. 检查法律适用是否准确和合理

请提供详细的分析结果，包括发现的问题和建议。
"""
        
        try:
            # 运行代理，设置超时时间为300秒（5分钟）
            result = await asyncio.wait_for(agent.run(prompt), timeout=300)
            
            return {
                "status": "success",
                "result": result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "result": f"分析过程中出现错误: {str(e)}"
            }
    
    async def check_timeline(self, document_content: str) -> Dict[str, Any]:
        """检查时间线逻辑"""
        # 创建OpenManus代理
        agent = Manus()
        file_tool = FileOperatorsTool()
        agent.available_tools.add_tool(file_tool)
        
        # 构建分析提示语
        prompt = """
你是一个专业的法律分析助手，需要检查刑事案件的时间线逻辑。

请按照以下步骤进行分析：

1. 使用 file_operators 工具查看案件相关文件
2. 提取案件中的关键时间节点
3. 检查侦查、批捕、起诉等时间节点的合规性
4. 评估时间线是否存在逻辑问题

请提供详细的分析结果，包括发现的问题和建议。
"""
        
        try:
            # 运行代理，设置超时时间为300秒（5分钟）
            result = await asyncio.wait_for(agent.run(prompt), timeout=300)
            
            return {
                "status": "success",
                "result": result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "result": f"分析过程中出现错误: {str(e)}"
            }
