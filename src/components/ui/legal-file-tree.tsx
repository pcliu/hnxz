"use client";

import { useState } from 'react';
import { 
  ChevronRight, 
  ChevronDown, 
  Folder, 
  File, 
  FileText, 
  FilePen, 
  FileCheck,
  Scale,
  Gavel,
  UserRound,
  Clock,
  Search
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Input } from './input';
import { Badge } from './badge';
import { Button } from './button';
import { ScrollArea } from './scroll-area';

interface FileNode {
  id: string;
  name: string;
  type: 'file' | 'directory';
  children?: FileNode[];
  path: string;
  fileType?: string;
  metadata?: {
    date?: string;
    author?: string;
    status?: string;
    tags?: string[];
  };
}

interface LegalFileTreeProps {
  files: FileNode[];
  onSelectFile: (path: string) => void;
  className?: string;
}

export function LegalFileTree({ files, onSelectFile, className }: LegalFileTreeProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [filter, setFilter] = useState<string | null>(null);

  // 过滤文件
  const filteredFiles = searchQuery || filter
    ? filterFiles(files, searchQuery, filter)
    : files;

  const fileTypes = [
    { value: 'all', label: '全部' },
    { value: 'evidence', label: '证据' },
    { value: 'testimony', label: '证词' },
    { value: 'indictment', label: '起诉书' },
    { value: 'judgment', label: '判决书' },
    { value: 'investigation', label: '侦查报告' },
  ];

  return (
    <div className={cn("flex flex-col h-full", className)}>
      <div className="p-3 border-b">
        <h3 className="text-sm font-medium mb-2">案件文件</h3>
        <div className="relative mb-2">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="搜索文件..."
            className="pl-8"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="flex flex-wrap gap-1 mt-2">
          {fileTypes.map((type) => (
            <Badge
              key={type.value}
              variant={filter === type.value || (filter === null && type.value === 'all') ? "default" : "outline"}
              className="cursor-pointer"
              onClick={() => setFilter(type.value === 'all' ? null : type.value)}
            >
              {type.label}
            </Badge>
          ))}
        </div>
      </div>
      
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {filteredFiles.length === 0 ? (
            <div className="text-sm text-muted-foreground p-2">
              没有找到匹配的文件
            </div>
          ) : (
            filteredFiles.map((file) => (
              <FileTreeNode 
                key={file.id} 
                node={file} 
                level={0} 
                onSelectFile={onSelectFile} 
              />
            ))
          )}
        </div>
      </ScrollArea>
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

  // 根据文件类型选择图标
  const getFileIcon = () => {
    if (node.type === 'directory') {
      return isExpanded ? 
        <ChevronDown className="h-4 w-4 mr-1 text-muted-foreground" /> : 
        <ChevronRight className="h-4 w-4 mr-1 text-muted-foreground" />;
    }

    // 根据文件名或类型选择图标
    const fileName = node.name.toLowerCase();
    if (fileName.includes('判决') || fileName.includes('裁定')) {
      return <Gavel className="h-4 w-4 mr-2 text-blue-500" />;
    } else if (fileName.includes('起诉')) {
      return <FilePen className="h-4 w-4 mr-2 text-orange-500" />;
    } else if (fileName.includes('证据') || fileName.includes('物证') || fileName.includes('书证')) {
      return <FileCheck className="h-4 w-4 mr-2 text-green-500" />;
    } else if (fileName.includes('法律') || fileName.includes('条文')) {
      return <Scale className="h-4 w-4 mr-2 text-purple-500" />;
    } else if (fileName.includes('证人') || fileName.includes('证词')) {
      return <UserRound className="h-4 w-4 mr-2 text-amber-500" />;
    } else if (fileName.includes('时间') || fileName.includes('日程')) {
      return <Clock className="h-4 w-4 mr-2 text-red-500" />;
    } else {
      return <FileText className="h-4 w-4 mr-2 text-muted-foreground" />;
    }
  };
  
  return (
    <div>
      <div 
        className={cn(
          "flex items-center py-1 px-2 rounded-md cursor-pointer hover:bg-accent group",
          "text-sm"
        )}
        style={{ paddingLeft: `${(level * 12) + 4}px` }}
        onClick={handleSelect}
      >
        <span className="flex items-center">
          {node.type === 'directory' ? (
            <span className="flex items-center" onClick={handleToggle}>
              {getFileIcon()}
              <Folder className="h-4 w-4 mr-2 text-blue-500" />
            </span>
          ) : (
            <span className="flex items-center">
              <span className="w-4 mr-1" />
              {getFileIcon()}
            </span>
          )}
          <span className="truncate">{node.name}</span>
        </span>
        
        {node.metadata?.date && (
          <span className="ml-auto text-xs text-muted-foreground opacity-0 group-hover:opacity-100">
            {node.metadata.date}
          </span>
        )}
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

// 过滤文件函数
function filterFiles(files: FileNode[], query: string, filter: string | null): FileNode[] {
  return files.map(file => {
    // 检查当前文件是否匹配
    const matchesSearch = query ? file.name.toLowerCase().includes(query.toLowerCase()) : true;
    const matchesFilter = filter ? (file.fileType === filter || file.type === 'directory') : true;
    
    // 如果是目录，递归过滤子文件
    if (file.type === 'directory' && file.children) {
      const filteredChildren = filterFiles(file.children, query, filter);
      
      // 如果子文件有匹配项，或者当前目录自身匹配，则保留
      if (filteredChildren.length > 0 || (matchesSearch && matchesFilter)) {
        return {
          ...file,
          children: filteredChildren
        };
      }
      
      // 如果目录及其子文件都不匹配，则过滤掉
      return null;
    }
    
    // 如果是文件，根据匹配条件决定是否保留
    return (matchesSearch && matchesFilter) ? file : null;
  }).filter(Boolean) as FileNode[];
}
