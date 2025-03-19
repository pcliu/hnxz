"use client";

import React, { ReactNode } from 'react';

interface Highlight {
  id: string;
  text: string;
  position: { start: number; end: number };
  type: string;
  note?: string;
}

interface HighlighterProps {
  content: string;
  highlights: Highlight[];
  renderHighlight: (highlight: Highlight) => React.ReactNode;
  children: React.ReactNode;
}

export function Highlighter({ content, highlights, renderHighlight, children }: HighlighterProps) {
  // 在实际实现中，这里应该解析内容并插入高亮
  // 这里简化处理，直接返回子组件
  return <>{children}</>;
}

interface HighlighterItemProps {
  highlight: Highlight;
  className?: string;
  children: React.ReactNode;
}

export function HighlighterItem({ highlight, className, children }: HighlighterItemProps) {
  return (
    <span className={className} title={highlight.note}>
      {children}
    </span>
  );
}
