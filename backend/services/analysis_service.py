from typing import Dict, Any, List, Optional
import asyncio
from services.document_service import DocumentService
from manus.agent import LegalAnalysisAgent

class AnalysisService:
    """分析服务，用于处理文档分析"""
    
    def __init__(self):
        self.document_service = DocumentService()
        self.agent = LegalAnalysisAgent()
    
    async def analyze(self, document_id: str, query: str) -> Dict[str, Any]:
        """分析文档内容"""
        # 获取文档内容
        document = await self.document_service.get_document(document_id)
        if not document:
            return {"error": "文档不存在"}
        
        document_content = document.get("content", "")
        
        # 使用Agent进行分析
        analysis_results = []
        async for result in self.agent.analyze_document(document_content, query):
            analysis_results.append(result)
        
        # 返回最终结果
        if analysis_results:
            return analysis_results[-1]
        else:
            return {"error": "分析失败"}
    
    async def analyze_evidence(self, document_content: str) -> Dict[str, Any]:
        """分析证据链完整性"""
        # 调用Agent的证据分析功能
        return await self.agent.analyze_evidence(document_content)
    
    async def verify_legal_provisions(self, document_content: str) -> Dict[str, Any]:
        """验证法律条文适用性"""
        # 调用Agent的法律验证功能
        return await self.agent.verify_legal_provisions(document_content)
    
    async def check_timeline(self, document_content: str) -> Dict[str, Any]:
        """检查时间线逻辑"""
        # 调用Agent的时间线检查功能
        return await self.agent.check_timeline(document_content)
