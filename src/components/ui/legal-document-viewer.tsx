"use client";

import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import remarkGfm from 'remark-gfm';
import { Card, CardContent } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { LegalDocumentHeader } from './legal-document-header';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './tabs';
import { Button } from './button';
import { Separator } from './separator';
import { Badge } from './badge';
import { Highlighter, HighlighterItem } from './highlighter';
import { 
  BookOpen, 
  FileText, 
  MessageSquare, 
  History, 
  AlertTriangle, 
  CheckCircle2, 
  HelpCircle,
  BookMarked,
  Bookmark
} from 'lucide-react';

interface LegalDocumentViewerProps {
  content: string;
  filePath: string | null;
  onHighlight?: (text: string, position: { start: number; end: number }) => void;
}

interface Highlight {
  id: string;
  text: string;
  position: { start: number; end: number };
  type: 'inconsistency' | 'evidence' | 'legal' | 'timeline' | 'note';
  note?: string;
}

interface DocumentMetadata {
  title: string;
  documentType: string;
  caseNumber: string;
  date: string;
  status: "审理中" | "已结案" | "上诉中" | "侦查中" | "起诉中";
}

export function LegalDocumentViewer({ content, filePath, onHighlight }: LegalDocumentViewerProps) {
  const [activeTab, setActiveTab] = useState('document');
  const [highlights, setHighlights] = useState<Highlight[]>([]);
  const [selectedText, setSelectedText] = useState('');
  const [metadata, setMetadata] = useState<DocumentMetadata | null>(null);
  const contentRef = useRef<HTMLDivElement>(null);

  // 模拟从文件路径中提取元数据
  useEffect(() => {
    if (filePath) {
      const fileName = filePath.split('/').pop() || '';
      
      // 根据文件名模拟生成元数据
      const mockMetadata: DocumentMetadata = {
        title: fileName,
        documentType: getDocumentType(fileName),
        caseNumber: '刑事[2023]01234号',
        date: '2023-06-15',
        status: getDocumentStatus(fileName),
      };
      
      setMetadata(mockMetadata);
      
      // 模拟生成一些高亮
      const mockHighlights: Highlight[] = [
        {
          id: '1',
          text: '嫌疑人张某某于2023年1月15日晚',
          position: { start: 120, end: 140 },
          type: 'timeline',
          note: '与其他文件中的时间记录不一致，其他文件记录为1月16日'
        },
        {
          id: '2',
          text: '使用随身携带的折叠刀',
          position: { start: 200, end: 210 },
          type: 'evidence',
          note: '物证清单中未找到该折叠刀'
        },
        {
          id: '3',
          text: '《中华人民共和国刑法》第二百三十四条',
          position: { start: 300, end: 320 },
          type: 'legal',
          note: '该条款适用存在争议，可能需要结合第二百三十五条考虑'
        }
      ];
      
      setHighlights(mockHighlights);
    }
  }, [filePath]);

  // 处理文本选择
  const handleTextSelection = () => {
    const selection = window.getSelection();
    if (selection && selection.toString().trim() !== '') {
      setSelectedText(selection.toString());
    }
  };

  // 添加高亮
  const addHighlight = (type: Highlight['type']) => {
    if (selectedText) {
      const newHighlight: Highlight = {
        id: Date.now().toString(),
        text: selectedText,
        position: { start: 0, end: 0 }, // 实际应用中需要计算准确位置
        type,
      };
      
      setHighlights([...highlights, newHighlight]);
      setSelectedText('');
      
      if (onHighlight) {
        onHighlight(selectedText, newHighlight.position);
      }
    }
  };

  // 根据文件名获取文档类型
  const getDocumentType = (fileName: string): string => {
    if (fileName.includes('起诉书')) return '起诉书';
    if (fileName.includes('判决书')) return '判决书';
    if (fileName.includes('证据')) return '证据材料';
    if (fileName.includes('笔录')) return '询问笔录';
    if (fileName.includes('报告')) return '侦查报告';
    return '法律文书';
  };

  // 根据文件名获取文档状态
  const getDocumentStatus = (fileName: string): "审理中" | "已结案" | "上诉中" | "侦查中" | "起诉中" => {
    if (fileName.includes('判决书')) return '已结案';
    if (fileName.includes('上诉')) return '上诉中';
    if (fileName.includes('侦查')) return '侦查中';
    if (fileName.includes('起诉书')) return '起诉中';
    return '审理中';
  };

  // 获取高亮类型的样式和图标
  const getHighlightStyle = (type: Highlight['type']) => {
    switch (type) {
      case 'inconsistency':
        return { 
          color: 'bg-red-100 text-red-800 border-red-200', 
          icon: <AlertTriangle className="h-4 w-4" /> 
        };
      case 'evidence':
        return { 
          color: 'bg-green-100 text-green-800 border-green-200', 
          icon: <CheckCircle2 className="h-4 w-4" /> 
        };
      case 'legal':
        return { 
          color: 'bg-blue-100 text-blue-800 border-blue-200', 
          icon: <BookMarked className="h-4 w-4" /> 
        };
      case 'timeline':
        return { 
          color: 'bg-amber-100 text-amber-800 border-amber-200', 
          icon: <History className="h-4 w-4" /> 
        };
      case 'note':
        return { 
          color: 'bg-purple-100 text-purple-800 border-purple-200', 
          icon: <MessageSquare className="h-4 w-4" /> 
        };
      default:
        return { 
          color: 'bg-gray-100 text-gray-800 border-gray-200', 
          icon: <HelpCircle className="h-4 w-4" /> 
        };
    }
  };

  if (!filePath) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center space-y-2">
          <FileText className="h-12 w-12 text-muted-foreground mx-auto" />
          <p className="text-muted-foreground">请从左侧选择一个文件查看</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {metadata && (
        <LegalDocumentHeader
          title={metadata.title}
          documentType={metadata.documentType}
          caseNumber={metadata.caseNumber}
          date={metadata.date}
          status={metadata.status}
        />
      )}
      
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <div className="border-b">
          <TabsList className="h-10">
            <TabsTrigger value="document" className="flex items-center gap-1">
              <BookOpen className="h-4 w-4" />
              <span>文档</span>
            </TabsTrigger>
            <TabsTrigger value="highlights" className="flex items-center gap-1">
              <Bookmark className="h-4 w-4" />
              <span>标注</span>
              {highlights.length > 0 && (
                <Badge variant="secondary" className="ml-1 h-5 w-5 p-0 flex items-center justify-center">
                  {highlights.length}
                </Badge>
              )}
            </TabsTrigger>
          </TabsList>
        </div>
        
        <TabsContent value="document" className="flex-1 p-0 m-0">
          <div 
            ref={contentRef}
            className="h-full"
            onMouseUp={handleTextSelection}
          >
            <ScrollArea className="h-full">
              <div className="p-4">
                {selectedText && (
                  <div className="sticky top-0 z-10 bg-background p-2 mb-4 border rounded-md shadow-sm">
                    <p className="text-sm mb-2">已选择文本："{selectedText.substring(0, 50)}..."</p>
                    <div className="flex gap-1">
                      <Button size="sm" variant="outline" onClick={() => addHighlight('inconsistency')}>
                        <AlertTriangle className="h-3.5 w-3.5 mr-1" />
                        标记为不一致
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => addHighlight('evidence')}>
                        <CheckCircle2 className="h-3.5 w-3.5 mr-1" />
                        标记为证据
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => addHighlight('legal')}>
                        <BookMarked className="h-3.5 w-3.5 mr-1" />
                        标记为法条
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => addHighlight('timeline')}>
                        <History className="h-3.5 w-3.5 mr-1" />
                        标记为时间点
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => setSelectedText('')}>
                        取消
                      </Button>
                    </div>
                  </div>
                )}
                
                <Highlighter
                  content={content}
                  highlights={highlights}
                  renderHighlight={(highlight) => {
                    const style = getHighlightStyle(highlight.type);
                    return (
                      <HighlighterItem
                        key={highlight.id}
                        highlight={highlight}
                        className={`border px-1 rounded ${style.color}`}
                      >
                        {highlight.text}
                      </HighlighterItem>
                    );
                  }}
                >
                  <div className="prose prose-sm max-w-none dark:prose-invert">
                    <ReactMarkdown
                      rehypePlugins={[rehypeRaw]}
                      remarkPlugins={[remarkGfm]}
                    >
                      {content}
                    </ReactMarkdown>
                  </div>
                </Highlighter>
              </div>
            </ScrollArea>
          </div>
        </TabsContent>
        
        <TabsContent value="highlights" className="flex-1 p-0 m-0">
          <ScrollArea className="h-full">
            <div className="p-4 space-y-4">
              {highlights.length === 0 ? (
                <div className="text-center py-8">
                  <Bookmark className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                  <p className="text-muted-foreground">暂无标注</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    在文档中选择文本并添加标注
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {highlights.map((highlight) => {
                    const style = getHighlightStyle(highlight.type);
                    return (
                      <Card key={highlight.id} className="overflow-hidden">
                        <CardContent className="p-3">
                          <div className="flex items-start gap-2">
                            <div className={`p-2 rounded-full ${style.color}`}>
                              {style.icon}
                            </div>
                            <div className="flex-1">
                              <div className="flex justify-between items-start">
                                <div className="font-medium">
                                  {highlight.type === 'inconsistency' && '不一致点'}
                                  {highlight.type === 'evidence' && '证据'}
                                  {highlight.type === 'legal' && '法律条文'}
                                  {highlight.type === 'timeline' && '时间点'}
                                  {highlight.type === 'note' && '笔记'}
                                </div>
                                <Badge variant="outline" className={style.color}>
                                  {highlight.type === 'inconsistency' && '不一致'}
                                  {highlight.type === 'evidence' && '证据'}
                                  {highlight.type === 'legal' && '法条'}
                                  {highlight.type === 'timeline' && '时间线'}
                                  {highlight.type === 'note' && '笔记'}
                                </Badge>
                              </div>
                              <p className="text-sm mt-1 border-l-2 pl-2 py-1 my-1 bg-muted/50 rounded-sm">
                                {highlight.text}
                              </p>
                              {highlight.note && (
                                <div className="mt-2 text-sm text-muted-foreground">
                                  <p className="font-medium text-xs mb-1">备注:</p>
                                  <p>{highlight.note}</p>
                                </div>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              )}
            </div>
          </ScrollArea>
        </TabsContent>
      </Tabs>
    </div>
  );
}

// 高亮组件
interface HighlighterProps {
  content: string;
  highlights: Highlight[];
  renderHighlight: (highlight: Highlight) => React.ReactNode;
  children: React.ReactNode;
}

function Highlighter({ content, highlights, renderHighlight, children }: HighlighterProps) {
  return children;
}

interface HighlighterItemProps {
  highlight: Highlight;
  className?: string;
  children: React.ReactNode;
}

function HighlighterItem({ highlight, className, children }: HighlighterItemProps) {
  return (
    <span className={className} title={highlight.note}>
      {children}
    </span>
  );
}
