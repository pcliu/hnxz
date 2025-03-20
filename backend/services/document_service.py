import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

class DocumentService:
    """文档服务，用于处理文档的读取和管理"""
    
    def __init__(self):
        # 文档根目录
        self.documents_dir = Path(os.getcwd()) / "business"
    
    async def get_all_documents(self) -> List[Dict[str, Any]]:
        """获取所有文档列表"""
        documents = []
        
        # 递归获取文件夹中的所有文件
        for path in self.documents_dir.glob("**/*"):
            if path.is_file():
                relative_path = path.relative_to(os.getcwd())
                documents.append({
                    "id": str(relative_path),
                    "name": path.name,
                    "path": str(relative_path),
                    "type": "file"
                })
        
        return documents
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """获取单个文档内容"""
        # 构建完整路径
        full_path = Path(os.getcwd()) / document_id
        
        # 安全检查：确保文件路径不超出项目根目录
        try:
            relative_path = full_path.relative_to(os.getcwd())
            if str(relative_path).startswith("..") or os.path.isabs(str(relative_path)):
                return None
        except ValueError:
            return None
        
        # 检查文件是否存在
        if not full_path.exists() or not full_path.is_file():
            return None
        
        # 读取文件内容
        content = full_path.read_text(encoding="utf-8")
        
        return {
            "id": document_id,
            "name": full_path.name,
            "path": str(relative_path),
            "content": content
        }
    
    async def get_document_metadata(self, document_id: str) -> Optional[Dict[str, Any]]:
        """获取文档元数据"""
        document = await self.get_document(document_id)
        if not document:
            return None
        
        # 移除内容，只返回元数据
        if "content" in document:
            del document["content"]
        
        return document
