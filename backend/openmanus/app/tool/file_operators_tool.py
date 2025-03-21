"""File operations tool for agent to interact with the file system."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from pydantic import Field

from app.config import config
from app.exceptions import ToolError
from app.tool.base import BaseTool, ToolResult
from app.tool.file_operators import LocalFileOperator, PathLike


class FileOperatorsTool(BaseTool):
    """Tool for file operations."""

    name: str = "file_operators"
    description: str = "Tool for reading files and directories in the workspace"
    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["read_file", "list_directory", "search_files"],
                "description": "Action to perform",
            },
            "path": {
                "type": "string",
                "description": "Path to file or directory (relative to workspace)",
            },
            "query": {
                "type": "string",
                "description": "Search query for search_files action",
            },
        },
        "required": ["action", "path"],
    }

    # 使用 Field 定义默认值
    file_operator: LocalFileOperator = Field(default_factory=LocalFileOperator)
    workspace_root: Path = Field(default_factory=lambda: Path(config.workspace_root))
    
    class Config:
        arbitrary_types_allowed = True

    def _resolve_path(self, path: str) -> Path:
        """Resolve a path relative to the workspace root."""
        path_obj = Path(path)
        if path_obj.is_absolute():
            return path_obj
        return self.workspace_root / path

    async def read_file(self, path: str) -> Dict[str, Union[str, bool]]:
        """Read a file and return its content."""
        resolved_path = self._resolve_path(path)
        try:
            if not await self.file_operator.exists(resolved_path):
                return {"success": False, "error": f"File not found: {path}"}
            
            if await self.file_operator.is_directory(resolved_path):
                return {"success": False, "error": f"{path} is a directory, not a file"}
            
            content = await self.file_operator.read_file(resolved_path)
            return {"success": True, "content": content}
        except Exception as e:
            return {"success": False, "error": f"Error reading file {path}: {str(e)}"}

    async def list_directory(self, path: str) -> Dict[str, Union[List[str], bool, str]]:
        """List contents of a directory."""
        resolved_path = self._resolve_path(path)
        try:
            if not await self.file_operator.exists(resolved_path):
                return {"success": False, "error": f"Directory not found: {path}"}
            
            if not await self.file_operator.is_directory(resolved_path):
                return {"success": False, "error": f"{path} is a file, not a directory"}
            
            # Use os.listdir to get directory contents
            contents = os.listdir(resolved_path)
            
            # Separate files and directories
            files = []
            directories = []
            for item in contents:
                item_path = resolved_path / item
                if item_path.is_dir():
                    directories.append(f"{item}/")
                else:
                    files.append(item)
            
            return {
                "success": True, 
                "directories": sorted(directories), 
                "files": sorted(files)
            }
        except Exception as e:
            return {"success": False, "error": f"Error listing directory {path}: {str(e)}"}

    async def search_files(self, path: str, query: Optional[str] = None) -> Dict[str, Union[List[str], bool, str]]:
        """Search for files in a directory containing the query string."""
        if not query:
            return {"success": False, "error": "Search query is required"}
        
        resolved_path = self._resolve_path(path)
        try:
            if not await self.file_operator.exists(resolved_path):
                return {"success": False, "error": f"Directory not found: {path}"}
            
            if not await self.file_operator.is_directory(resolved_path):
                return {"success": False, "error": f"{path} is a file, not a directory"}
            
            # Run a grep-like command to search for files containing the query
            cmd = f'grep -l -r "{query}" {resolved_path} 2>/dev/null || true'
            returncode, stdout, stderr = await self.file_operator.run_command(cmd)
            
            if returncode != 0:
                return {"success": False, "error": f"Error searching files: {stderr}"}
            
            # Process results
            results = []
            for line in stdout.strip().split('\n'):
                if line:
                    # Convert absolute path to relative path from workspace
                    try:
                        rel_path = Path(line).relative_to(self.workspace_root)
                        results.append(str(rel_path))
                    except ValueError:
                        results.append(line)
            
            return {"success": True, "matches": results}
        except Exception as e:
            return {"success": False, "error": f"Error searching files: {str(e)}"}

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the file operations tool."""
        action = kwargs.get("action")
        path = kwargs.get("path")
        
        if not action:
            return ToolResult(error="Action is required")
        
        if not path:
            return ToolResult(error="Path is required")
        
        if action == "read_file":
            result = await self.read_file(path)
        elif action == "list_directory":
            result = await self.list_directory(path)
        elif action == "search_files":
            query = kwargs.get("query")
            result = await self.search_files(path, query)
        else:
            return ToolResult(error=f"Unknown action: {action}")
        
        if not result.get("success", False):
            return ToolResult(error=result.get("error", "Unknown error"))
        
        # Remove success flag from result
        if "success" in result:
            del result["success"]
        
        # 将结果转换为字符串
        import json
        output_str = json.dumps(result, ensure_ascii=False, indent=2)
            
        return ToolResult(output=output_str)
