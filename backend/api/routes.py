from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse
from typing import Optional, List, Dict, Any, AsyncGenerator
from services.document_service import DocumentService
from services.analysis_service import AnalysisService
from services.chat_service_flow import ChatServiceFlow
from services.chat_service import ChatService
from pydantic import BaseModel
import json
import asyncio

# 创建路由器
router = APIRouter()

# 服务实例
document_service = DocumentService()
analysis_service = AnalysisService()
chat_service = ChatService()
# chat_service = ChatServiceFlow()

# 请求模型
class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None
    document_id: Optional[str] = None

class AnalysisRequest(BaseModel):
    document_id: str
    query: str

# 文档相关路由
@router.get("/documents")
async def get_documents():
    """获取所有文档列表"""
    return await document_service.get_all_documents()

@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    """获取单个文档内容"""
    document = await document_service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    return document

# 分析相关路由
@router.post("/analysis")
async def analyze_document(request: AnalysisRequest):
    """分析文档内容"""
    if not request.document_id or not request.query:
        raise HTTPException(status_code=400, detail="缺少必要参数")
    
    return await analysis_service.analyze(request.document_id, request.query)

# 聊天相关路由
@router.post("/chat")
async def chat(request: ChatRequest):
    """处理聊天请求（流式响应）"""
    if not request.message:
        raise HTTPException(status_code=400, detail="缺少消息内容")
    
    async def event_generator():
        try:
            async for result in chat_service.process_message(request.message, request.chat_id, request.document_id):
                # 将结果转换为SSE格式
                yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.01)  # 小延迟，防止过快响应
        except Exception as e:
            error_data = {"status": "error", "message": str(e)}
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@router.get("/chat/{chat_id}/history")
async def get_chat_history(chat_id: str):
    """获取聊天历史"""
    return await chat_service.get_history(chat_id)

@router.get("/analysis/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """获取分析状态"""
    return await chat_service.get_analysis_status(analysis_id)

@router.delete("/chat/{chat_id}")
async def delete_chat(chat_id: str):
    """删除聊天记录"""
    success = await chat_service.delete_chat(chat_id)
    if not success:
        raise HTTPException(status_code=404, detail="聊天记录不存在")
    return {"message": "聊天记录已删除"}

# 证据分析路由
@router.post("/evidence-analysis")
async def analyze_evidence(request: AnalysisRequest):
    """分析证据链完整性"""
    if not request.document_id:
        raise HTTPException(status_code=400, detail="缺少文档ID")
    
    document = await document_service.get_document(request.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    document_content = document.get("content", "")
    return await analysis_service.analyze_evidence(document_content)

# 法律条文验证路由
@router.post("/legal-verification")
async def verify_legal_provisions(request: AnalysisRequest):
    """验证法律条文适用性"""
    if not request.document_id:
        raise HTTPException(status_code=400, detail="缺少文档ID")
    
    document = await document_service.get_document(request.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    document_content = document.get("content", "")
    return await analysis_service.verify_legal_provisions(document_content)

# 时间线检查路由
@router.post("/timeline-check")
async def check_timeline(request: AnalysisRequest):
    """检查时间线逻辑"""
    if not request.document_id:
        raise HTTPException(status_code=400, detail="缺少文档ID")
    
    document = await document_service.get_document(request.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    document_content = document.get("content", "")
    return await analysis_service.check_timeline(document_content)
