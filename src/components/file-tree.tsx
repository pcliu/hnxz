"use client";

import { useState } from 'react';
import { ChevronRight, ChevronDown, Folder, File } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FileNode {
  id: string;
  name: string;
  type: 'file' | 'directory';
  children?: FileNode[];
  path: string;
}

interface FileTreeProps {
  files: FileNode[];
  onSelectFile: (path: string) => void;
}

export function FileTree({ files, onSelectFile }: FileTreeProps) {
  return (
    <div className="file-tree">
      <h3 className="text-sm font-medium mb-2">文件列表</h3>
      <div className="space-y-1">
        {files.map((file) => (
          <FileTreeNode 
            key={file.id} 
            node={file} 
            level={0} 
            onSelectFile={onSelectFile} 
          />
        ))}
      </div>
    </div>
  );
}

interface FileTreeNodeProps {
  node: FileNode;
  level: number;
  onSelectFile: (path: string) => void;
}

function FileTreeNode({ node, level, onSelectFile }: FileTreeNodeProps) {
  const [isExpanded, setIsExpanded] = useState(level < 1);
  
  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsExpanded(!isExpanded);
  };
  
  const handleSelect = () => {
    if (node.type === 'file') {
      onSelectFile(node.path);
    } else {
      setIsExpanded(!isExpanded);
    }
  };
  
  return (
    <div>
      <div 
        className={cn(
          "flex items-center py-1 px-2 rounded-md cursor-pointer hover:bg-accent",
          "text-sm"
        )}
        style={{ paddingLeft: `${(level * 12) + 4}px` }}
        onClick={handleSelect}
      >
        {node.type === 'directory' ? (
          <span className="flex items-center" onClick={handleToggle}>
            {isExpanded ? 
              <ChevronDown className="h-4 w-4 mr-1 text-muted-foreground" /> : 
              <ChevronRight className="h-4 w-4 mr-1 text-muted-foreground" />
            }
            <Folder className="h-4 w-4 mr-2 text-blue-500" />
          </span>
        ) : (
          <span className="flex items-center">
            <span className="w-4 mr-1" />
            <File className="h-4 w-4 mr-2 text-muted-foreground" />
          </span>
        )}
        <span className="truncate">{node.name}</span>
      </div>
      
      {node.type === 'directory' && isExpanded && node.children && (
        <div>
          {node.children.map((child) => (
            <FileTreeNode
              key={child.id}
              node={child}
              level={level + 1}
              onSelectFile={onSelectFile}
            />
          ))}
        </div>
      )}
    </div>
  );
}
