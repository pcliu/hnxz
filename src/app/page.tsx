"use client";

import { useState, useEffect } from "react";
import { ResizablePanel, ResizablePanelGroup } from "../components/ui/resizable";
import { CustomResizableHandle } from "../components/ui/custom-resizable";
import { Button } from "../components/ui/button";
import { FileTree } from "../components/file-tree";
import { FileViewer } from "../components/file-viewer";
import { ChatPanel } from "../components/chat-panel";
import { MessageSquare, X } from "lucide-react";

export default function Home() {
  const [files, setFiles] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>("");
  const [isChatOpen, setIsChatOpen] = useState<boolean>(true);

  // 加载文件列表
  useEffect(() => {
    // 这里应该从API获取文件列表，现在使用模拟数据
    fetch('/api/files')
      .then(res => res.json())
      .then(data => {
        setFiles(data);
      })
      .catch(err => {
        console.error('加载文件列表失败:', err);
      });
  }, []);

  // 加载文件内容
  const loadFileContent = (filePath: string) => {
    setSelectedFile(filePath);
    // 这里应该从API获取文件内容
    fetch(`/api/files/content?path=${encodeURIComponent(filePath)}`)
      .then(res => res.json())
      .then(data => {
        setFileContent(data.content);
      })
      .catch(err => {
        console.error('加载文件内容失败:', err);
      });
  };

  return (
    <div className="flex flex-col h-screen">
      {/* 头部标题栏 */}
      <header className="border-b p-4 flex justify-between items-center bg-card">
        <h1 className="text-2xl font-bold">刑事案件文件分析系统</h1>
        <Button
          variant="outline"
          size="icon"
          onClick={() => setIsChatOpen(!isChatOpen)}
        >
          {isChatOpen ? <X className="h-4 w-4" /> : <MessageSquare className="h-4 w-4" />}
        </Button>
      </header>

      {/* 主要内容区域 - 三面板布局 */}
      <ResizablePanelGroup direction="horizontal" className="flex-1">
        {/* 文件树面板 */}
        <ResizablePanel defaultSize={20} minSize={15}>
          <div className="h-full p-2 overflow-auto border-r">
            <FileTree files={files} onSelectFile={loadFileContent} />
          </div>
        </ResizablePanel>

        <CustomResizableHandle />

        {/* 文件内容面板 */}
        <ResizablePanel defaultSize={isChatOpen ? 50 : 80}>
          <div className="h-full overflow-auto p-4">
            <FileViewer content={fileContent} filePath={selectedFile} />
          </div>
        </ResizablePanel>

        {/* 聊天面板 - 可以关闭 */}
        {isChatOpen && (
          <>
            <CustomResizableHandle />
            <ResizablePanel defaultSize={30}>
              <div className="h-full border-l-2 border-black/30">
                <ChatPanel filePath={selectedFile} />
              </div>
            </ResizablePanel>
          </>
        )}
      </ResizablePanelGroup>

      {/* 页脚 */}
      <footer className="border-t p-2 text-center text-sm text-muted-foreground">
        © {new Date().getFullYear()} 河南公安 - 刑事案件文件分析系统
      </footer>
    </div>
  );
}
