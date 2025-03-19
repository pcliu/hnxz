"use client";

import { FileText, Search, Filter, Download, Share2, Printer } from "lucide-react";
import { Button } from "./button";
import { Badge } from "./badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "./tooltip";

interface LegalDocumentHeaderProps {
  title: string;
  documentType?: string;
  caseNumber?: string;
  date?: string;
  status?: "审理中" | "已结案" | "上诉中" | "侦查中" | "起诉中";
}

export function LegalDocumentHeader({
  title,
  documentType,
  caseNumber,
  date,
  status = "审理中",
}: LegalDocumentHeaderProps) {
  const statusColors = {
    审理中: "bg-amber-100 text-amber-800 hover:bg-amber-200",
    已结案: "bg-green-100 text-green-800 hover:bg-green-200",
    上诉中: "bg-blue-100 text-blue-800 hover:bg-blue-200",
    侦查中: "bg-purple-100 text-purple-800 hover:bg-purple-200",
    起诉中: "bg-orange-100 text-orange-800 hover:bg-orange-200",
  };

  return (
    <div className="flex flex-col space-y-2 border-b pb-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-muted-foreground" />
          <h1 className="text-xl font-semibold">{title}</h1>
          {status && (
            <Badge variant="outline" className={statusColors[status]}>
              {status}
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-1">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <Search className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>搜索文档</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <Filter className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>筛选内容</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <Download className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>下载文档</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <Share2 className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>分享文档</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <Printer className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>打印文档</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </div>
      
      <div className="flex flex-wrap gap-x-6 gap-y-1 text-sm text-muted-foreground">
        {documentType && (
          <div className="flex items-center gap-1">
            <span className="font-medium">文档类型:</span>
            <span>{documentType}</span>
          </div>
        )}
        {caseNumber && (
          <div className="flex items-center gap-1">
            <span className="font-medium">案件编号:</span>
            <span>{caseNumber}</span>
          </div>
        )}
        {date && (
          <div className="flex items-center gap-1">
            <span className="font-medium">日期:</span>
            <span>{date}</span>
          </div>
        )}
      </div>
    </div>
  );
}
