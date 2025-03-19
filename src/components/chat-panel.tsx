"use client";

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { HistoryIcon, PlusIcon, TrashIcon, SendIcon } from 'lucide-react';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system' | 'thinking';
  content: string;
  timestamp: Date;
}

interface ChatHistory {
  id: string;
  title: string;
  timestamp: Date;
}

interface ChatPanelProps {
  filePath: string | null;
}

export function ChatPanel({ filePath }: ChatPanelProps) {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [chatHistories, setChatHistories] = useState<ChatHistory[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 提交消息
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    // 添加用户消息
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // 添加思考中的消息
    const thinkingMessage: Message = {
      id: 'thinking-' + Date.now().toString(),
      role: 'thinking',
      content: '正在分析问题...',
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, thinkingMessage]);

    try {
      // 模拟 AI 分析过程
      // 1. 分析问题并生成 TODO 列表
      setTimeout(() => {
        setMessages((prev) => {
          const updatedMessages = [...prev];
          const thinkingIndex = updatedMessages.findIndex(m => m.id === thinkingMessage.id);
          if (thinkingIndex !== -1) {
            updatedMessages[thinkingIndex] = {
              ...thinkingMessage,
              content: '分析问题: 正在生成任务列表...\n\n待办任务:\n1. 分析文件内容\n2. 检查证据链完整性\n3. 验证法律条文适用性',
            };
          }
          return updatedMessages;
        });
      }, 1000);

      // 2. 执行子任务1
      setTimeout(() => {
        setMessages((prev) => {
          const updatedMessages = [...prev];
          const thinkingIndex = updatedMessages.findIndex(m => m.id === thinkingMessage.id);
          if (thinkingIndex !== -1) {
            updatedMessages[thinkingIndex] = {
              ...thinkingMessage,
              content: '分析问题: 已生成任务列表\n\n待办任务:\n1. ✓ 分析文件内容\n2. 检查证据链完整性\n3. 验证法律条文适用性\n\n正在分析文件内容...',
            };
          }
          return updatedMessages;
        });
      }, 2000);

      // 3. 执行子任务2
      setTimeout(() => {
        setMessages((prev) => {
          const updatedMessages = [...prev];
          const thinkingIndex = updatedMessages.findIndex(m => m.id === thinkingMessage.id);
          if (thinkingIndex !== -1) {
            updatedMessages[thinkingIndex] = {
              ...thinkingMessage,
              content: '分析问题: 已生成任务列表\n\n待办任务:\n1. ✓ 分析文件内容\n2. ✓ 检查证据链完整性\n3. 验证法律条文适用性\n\n正在验证法律条文适用性...',
            };
          }
          return updatedMessages;
        });
      }, 3000);

      // 4. 完成所有子任务并返回结果
      setTimeout(() => {
        setMessages((prev) => {
          const updatedMessages = [...prev];
          const thinkingIndex = updatedMessages.findIndex(m => m.id === thinkingMessage.id);
          if (thinkingIndex !== -1) {
            // 移除思考消息
            updatedMessages.splice(thinkingIndex, 1);
          }
          
          // 添加 AI 回复
          const aiResponse: Message = {
            id: Date.now().toString(),
            role: 'assistant',
            content: `根据分析，我发现以下问题：\n\n1. **证据链不完整**：在《证据材料卷》中的物证与《侦查工作卷》中的描述存在不一致。详见[证据材料卷/前科证明.md](点击查看)\n\n2. **法律条文适用性问题**：根据《刑法》第232条关于故意杀人罪的规定，本案证据不足以支持该罪名。详见[故意杀人起诉 诉讼文书卷/判决书.md](点击查看)\n\n3. **时间线逻辑问题**：侦查时间与批捕时间存在超期情况，不符合刑事诉讼法规定的时限要求。`,
            timestamp: new Date(),
          };
          
          return [...updatedMessages, aiResponse];
        });
        setIsLoading(false);
      }, 4000);
    } catch (error) {
      console.error('发送消息失败:', error);
      setIsLoading(false);
      
      // 添加错误消息
      setMessages((prev) => {
        const updatedMessages = [...prev];
        const thinkingIndex = updatedMessages.findIndex(m => m.id === thinkingMessage.id);
        if (thinkingIndex !== -1) {
          updatedMessages.splice(thinkingIndex, 1);
        }
        
        return [...updatedMessages, {
          id: Date.now().toString(),
          role: 'system',
          content: '分析过程中出现错误，请稍后重试。',
          timestamp: new Date(),
        }];
      });
    }
  };

  // 清空聊天记录
  const handleClearChat = () => {
    setMessages([]);
  };

  // 创建新聊天
  const handleNewChat = () => {
    setMessages([]);
  };

  return (
    <Card className="flex flex-col h-full border-0 rounded-none shadow-none">
      <CardHeader className="flex flex-row items-center justify-between py-2 px-4 border-b">
        <CardTitle className="text-lg">聊天分析</CardTitle>
        <div className="flex items-center space-x-1">
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" title="历史记录">
                <HistoryIcon className="h-4 w-4" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right">
              <SheetHeader>
                <SheetTitle>历史记录</SheetTitle>
              </SheetHeader>
              <div className="py-4">
                {chatHistories.length === 0 ? (
                  <p className="text-sm text-muted-foreground">暂无历史记录</p>
                ) : (
                  <div className="space-y-2">
                    {chatHistories.map((history) => (
                      <div
                        key={history.id}
                        className="flex items-center justify-between p-2 rounded-md hover:bg-accent cursor-pointer"
                        onClick={() => {
                          // 加载历史记录
                        }}
                      >
                        <span className="text-sm truncate">{history.title}</span>
                        <span className="text-xs text-muted-foreground">
                          {history.timestamp.toLocaleDateString()}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </SheetContent>
          </Sheet>
          <Button variant="ghost" size="icon" onClick={handleNewChat} title="新建聊天">
            <PlusIcon className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" onClick={handleClearChat} title="清空聊天">
            <TrashIcon className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-muted-foreground text-center">
              你可以询问关于案件文件的任何问题，例如：<br />
              "这个案件的证据链是否完整？"<br />
              "有哪些法律条文适用性问题？"<br />
              "时间线是否存在逻辑问题？"
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : message.role === 'thinking'
                    ? 'bg-muted text-muted-foreground'
                    : message.role === 'system'
                    ? 'bg-destructive text-destructive-foreground'
                    : 'bg-accent'
                }`}
              >
                <div className="whitespace-pre-wrap">{message.content}</div>
                <div className="text-xs mt-1 opacity-70 text-right">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </CardContent>
      <CardFooter className="p-4 border-t">
        <form onSubmit={handleSubmit} className="flex w-full space-x-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="输入你的问题..."
            className="flex-1 min-h-[60px] max-h-[120px]"
            disabled={isLoading}
          />
          <Button type="submit" size="icon" disabled={isLoading || !input.trim()}>
            <SendIcon className="h-4 w-4" />
          </Button>
        </form>
      </CardFooter>
    </Card>
  );
}
