import os
import asyncio
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

class DocumentService:
    """文档服务，处理文件读取和管理"""
    
    def __init__(self):
        # 设置业务文件目录
        self.business_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../business')))
        self.documents_cache = {}  # 缓存文档内容
    
    async def get_all_documents(self) -> List[Dict[str, Any]]:
        """获取所有文档列表"""
        documents = []
        
        # 递归遍历业务目录
        for root, dirs, files in os.walk(self.business_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.business_dir)
                    
                    # 创建文档对象
                    document = {
                        "id": rel_path,
                        "name": file,
                        "path": rel_path,
                        "type": "file",
                        "size": os.path.getsize(file_path),
                        "last_modified": os.path.getmtime(file_path)
                    }
                    
                    documents.append(document)
        
        # 按路径排序
        documents.sort(key=lambda x: x["path"])
        
        return documents
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """获取单个文档内容"""
        # 检查缓存
        if document_id in self.documents_cache:
            return self.documents_cache[document_id]
        
        # 构建文件路径
        file_path = os.path.join(self.business_dir, document_id)
        
        # 检查文件是否存在
        if not os.path.isfile(file_path):
            return None
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 创建文档对象
            document = {
                "id": document_id,
                "name": os.path.basename(file_path),
                "path": document_id,
                "content": content,
                "type": "file",
                "size": os.path.getsize(file_path),
                "last_modified": os.path.getmtime(file_path)
            }
            
            # 缓存文档
            self.documents_cache[document_id] = document
            
            return document
            
        except Exception as e:
            print(f"读取文档错误: {str(e)}")
            return None
    
    async def get_directory_structure(self) -> Dict[str, Any]:
        """获取目录结构"""
        def build_tree(path):
            result = {}
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    result[item] = build_tree(item_path)
                elif item.endswith('.md'):
                    result[item] = None
            return result
        
        return build_tree(self.business_dir)
