"use client";

import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import remarkGfm from 'remark-gfm';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface FileViewerProps {
  content: string;
  filePath: string | null;
}

export function FileViewer({ content, filePath }: FileViewerProps) {
  if (!filePath) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-muted-foreground">请从左侧选择一个文件查看</p>
      </div>
    );
  }

  const fileName = filePath.split('/').pop() || '';

  return (
    <Card className="h-full border-0 shadow-none">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-medium">{fileName}</CardTitle>
      </CardHeader>
      <CardContent className="markdown-content">
        <div className="prose prose-sm max-w-none dark:prose-invert">
          <ReactMarkdown
            rehypePlugins={[rehypeRaw]}
            remarkPlugins={[remarkGfm]}
          >
            {content}
          </ReactMarkdown>
        </div>
      </CardContent>
    </Card>
  );
}
