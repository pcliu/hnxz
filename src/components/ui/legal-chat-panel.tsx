"use client";

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  History as HistoryIcon, 
  Plus as PlusIcon, 
  Trash2 as TrashIcon, 
  Send as SendIcon,
  Paperclip as PaperclipIcon,
  Scale,
  FileText,
  Clock,
  CheckCircle2,
  AlertTriangle,
  X,
  MessageSquare,
  Bot,
  User,
  Sparkles
} from 'lucide-react';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';
import { sendChatMessage, getChatHistory, deleteChat } from '@/services/api';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system' | 'thinking';
  content: string;
  timestamp: Date;
  references?: {
    text: string;
    filePath: string;
    position: { start: number; end: number };
  }[];
}

interface ChatHistory {
  id: string;
  title: string;
  timestamp: Date;
  messageCount: number;
}

interface Task {
  id: string;
  description: string;
  status: 'pending' | 'completed' | 'failed';
  result?: string;
}

interface LegalChatPanelProps {
  filePath: string | null;
  className?: string;
  onMinimize?: () => void;
}

export function LegalChatPanel({ filePath, className, onMinimize }: LegalChatPanelProps) {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [chatHistories, setChatHistories] = useState<ChatHistory[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [activeTab, setActiveTab] = useState<string>('chat');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 初始化欢迎消息
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: Date.now().toString(),
          role: 'assistant',
          content: '您好，我是刑事案件分析助手。我可以帮助您分析案件文件，检查证据链完整性，验证法律条文适用性，以及检查时间线逻辑。请问有什么可以帮助您的？',
          timestamp: new Date(),
        }
      ]);
    }
  }, [messages.length]);

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

    // 创建任务列表
    const newTasks: Task[] = [
      { id: '1', description: '分析文件内容', status: 'pending' },
      { id: '2', description: '检查证据链完整性', status: 'pending' },
      { id: '3', description: '验证法律条文适用性', status: 'pending' }
    ];
    setTasks(newTasks);

    try {
      // 准备请求参数
      const chatRequest = {
        message: input,
        chat_id: messages.length > 1 ? messages[0].id : undefined,
        document_id: filePath || undefined
      };

      // 发送请求到后端API
      sendChatMessage(
        chatRequest,
        (data: any) => {
          // 处理流式响应数据
          if (data.type === 'message') {
            // 如果是最终消息，替换思考消息
            if (data.remove_thinking) {
              setMessages((prev) => {
                const updatedMessages = [...prev];
                const thinkingIndex = updatedMessages.findIndex(m => m.id === data.remove_thinking);
                if (thinkingIndex !== -1) {
                  updatedMessages.splice(thinkingIndex, 1);
                }
                return [...updatedMessages, {
                  id: data.content.id,
                  role: data.content.role,
                  content: data.content.content,
                  timestamp: new Date(data.content.timestamp),
                  references: data.content.references
                }];
              });
              setIsLoading(false);
            }
          } else if (data.type === 'thinking' || data.type === 'thinking_update') {
            // 更新思考消息
            setMessages((prev) => {
              const updatedMessages = [...prev];
              const thinkingIndex = updatedMessages.findIndex(m => m.id === data.thinking_id);
              if (thinkingIndex !== -1) {
                updatedMessages[thinkingIndex] = {
                  ...updatedMessages[thinkingIndex],
                  content: data.content,
                };
              }
              return updatedMessages;
            });

            // 解析内容中的任务状态更新
            const content = data.content;
            if (typeof content === 'string' && content.includes('✓')) {
              // 更新任务状态
              if (content.includes('✓ 分析文件内容')) {
                setTasks(prev => {
                  const updated = [...prev];
                  const taskIndex = updated.findIndex(t => t.id === '1');
                  if (taskIndex !== -1) {
                    updated[taskIndex] = {
                      ...updated[taskIndex],
                      status: 'completed',
                      result: '文件内容分析完成'
                    };
                  }
                  return updated;
                });
              }
              if (content.includes('✓ 检查证据链完整性')) {
                setTasks(prev => {
                  const updated = [...prev];
                  const taskIndex = updated.findIndex(t => t.id === '2');
                  if (taskIndex !== -1) {
                    updated[taskIndex] = {
                      ...updated[taskIndex],
                      status: 'completed',
                      result: '证据链分析完成'
                    };
                  }
                  return updated;
                });
              }
              if (content.includes('✓ 验证法律条文适用性')) {
                setTasks(prev => {
                  const updated = [...prev];
                  const taskIndex = updated.findIndex(t => t.id === '3');
                  if (taskIndex !== -1) {
                    updated[taskIndex] = {
                      ...updated[taskIndex],
                      status: 'completed',
                      result: '法律条文验证完成'
                    };
                  }
                  return updated;
                });
              }
            }
          } else if (data.type === 'error') {
            // 处理错误
            setMessages((prev) => {
              const updatedMessages = [...prev];
              const thinkingIndex = updatedMessages.findIndex(m => m.id === data.remove_thinking);
              if (thinkingIndex !== -1) {
                updatedMessages.splice(thinkingIndex, 1);
              }
              return [...updatedMessages, {
                id: Date.now().toString(),
                role: 'system',
                content: data.content.content || '分析过程中出现错误，请稍后重试。',
                timestamp: new Date(),
              }];
            });
            setIsLoading(false);
          }
        },
        (error: any) => {
          // 处理错误
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
              content: '连接服务器失败，请检查网络连接后重试。',
              timestamp: new Date(),
            }];
          });
        }
      );
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
    setTasks([]);
  };

  // 创建新聊天
  const handleNewChat = () => {
    // 保存当前聊天到历史记录
    if (messages.length > 1) {
      const newHistory: ChatHistory = {
        id: Date.now().toString(),
        title: messages.find(m => m.role === 'user')?.content.substring(0, 30) + '...' || '新对话',
        timestamp: new Date(),
        messageCount: messages.length
      };
      
      setChatHistories(prev => [newHistory, ...prev]);
    }
    
    // 清空当前聊天
    setMessages([]);
    setTasks([]);
  };

  // 加载历史聊天
  const loadChatHistory = async (historyId: string) => {
    try {
      // 从后端加载历史聊天记录
      const history = await getChatHistory(historyId);
      if (history && Array.isArray(history)) {
        // 转换时间戳为Date对象
        const formattedMessages = history.map(msg => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }));
        setMessages(formattedMessages);
      }
    } catch (error) {
      console.error('加载历史聊天失败:', error);
      // 显示错误消息
      setMessages([{
        id: Date.now().toString(),
        role: 'system',
        content: '加载历史聊天记录失败，请稍后重试。',
        timestamp: new Date(),
      }]);
    }
  };

  return (
    <div className="chat-panel flex flex-col h-full overflow-hidden">
      <div className="chat-header flex-none">
        <CardHeader className="flex flex-row items-center justify-between py-1 px-2 border-b">
          <CardTitle className="text-base font-semibold flex items-center gap-1 whitespace-nowrap">
            <MessageSquare className="h-4 w-4 text-blue-600" />
            <span className="text-blue-600">案件分析助手</span>
          </CardTitle>
          <div className="flex items-center">
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="h-7 w-7 p-1" title="历史记录">
                  <HistoryIcon className="h-3.5 w-3.5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="right">
                <SheetHeader>
                  <SheetTitle>历史对话记录</SheetTitle>
                </SheetHeader>
                <div className="py-4">
                  {chatHistories.length === 0 ? (
                    <div className="text-center py-8">
                      <HistoryIcon className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                      <p className="text-muted-foreground">暂无历史记录</p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {chatHistories.map((history) => (
                        <div
                          key={history.id}
                          className="flex items-center justify-between p-3 rounded-md hover:bg-accent cursor-pointer border"
                          onClick={() => loadChatHistory(history.id)}
                        >
                          <div className="flex flex-col">
                            <span className="text-sm font-medium truncate max-w-[200px]">{history.title}</span>
                            <span className="text-xs text-muted-foreground">
                              {history.messageCount}条消息 · {history.timestamp.toLocaleDateString()}
                            </span>
                          </div>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <FileText className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </SheetContent>
            </Sheet>
            <Button variant="ghost" size="icon" onClick={handleNewChat} className="h-7 w-7 p-1" title="新建聊天">
              <PlusIcon className="h-3.5 w-3.5" />
            </Button>
            <Button variant="ghost" size="icon" onClick={handleClearChat} className="h-7 w-7 p-1" title="清空聊天">
              <TrashIcon className="h-3.5 w-3.5" />
            </Button>
            {onMinimize && (
              <Button variant="ghost" size="icon" onClick={onMinimize} className="h-7 w-7 p-1" title="缩减面板">
                <X className="h-3.5 w-3.5" />
              </Button>
            )}
          </div>
        </CardHeader>
      </div>

      <div className="chat-body flex-1 overflow-y-auto">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
          <TabsList className="grid w-full grid-cols-2 px-4 py-2 bg-transparent">
            <TabsTrigger value="chat" className="text-sm">
              对话
            </TabsTrigger>
            <TabsTrigger value="tasks" className="text-sm">
              分析任务
              {tasks.length > 0 && (
                <Badge variant="secondary" className="ml-1.5">
                  {tasks.filter(t => t.status === 'completed').length}/{tasks.length}
                </Badge>
              )}
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="chat" className="flex-1 p-0 m-0 overflow-hidden">
            <ScrollArea className="flex-1 h-[calc(100%-60px)]">
              <div className="p-4 space-y-4">
                {messages.length === 0 ? (
                  <div className="flex items-center justify-center h-[300px]">
                    <div className="text-center space-y-3">
                      <Bot className="h-12 w-12 text-primary/50 mx-auto" />
                      <p className="text-muted-foreground text-center">
                        您可以询问关于案件文件的任何问题
                      </p>
                      <div className="flex flex-col gap-2 mt-4">
                        <Button variant="outline" className="justify-start text-sm" onClick={() => setInput("这个案件的证据链是否完整？")}>
                          <Scale className="h-4 w-4 mr-2" />
                          这个案件的证据链是否完整？
                        </Button>
                        <Button variant="outline" className="justify-start text-sm" onClick={() => setInput("有哪些法律条文适用性问题？")}>
                          <FileText className="h-4 w-4 mr-2" />
                          有哪些法律条文适用性问题？
                        </Button>
                        <Button variant="outline" className="justify-start text-sm" onClick={() => setInput("时间线是否存在逻辑问题？")}>
                          <Clock className="h-4 w-4 mr-2" />
                          时间线是否存在逻辑问题？
                        </Button>
                      </div>
                    </div>
                  </div>
                ) : (
                  messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${
                        message.role === 'user' ? 'justify-end' : 'justify-start'
                      }`}
                    >
                      {message.role !== 'user' && (
                        <Avatar className="h-8 w-8 mr-2">
                          <AvatarImage src="/ai-avatar.png" />
                          <AvatarFallback className="bg-primary text-primary-foreground">
                            {message.role === 'thinking' ? '思' : message.role === 'system' ? '系' : 'AI'}
                          </AvatarFallback>
                        </Avatar>
                      )}
                      
                      <div className="flex flex-col max-w-[80%]">
                        <div
                          className={cn(
                            "rounded-lg p-3",
                            message.role === 'user'
                              ? 'bg-primary text-primary-foreground rounded-tr-none'
                              : message.role === 'thinking'
                              ? 'bg-muted text-muted-foreground'
                              : message.role === 'system'
                              ? 'bg-destructive text-destructive-foreground'
                              : 'bg-accent rounded-tl-none'
                          )}
                        >
                          <div className="whitespace-pre-wrap">{message.content}</div>
                        </div>
                        
                        {message.references && message.references.length > 0 && (
                          <div className="mt-1 space-y-1">
                            <p className="text-xs text-muted-foreground ml-1">引用来源:</p>
                            {message.references.map((ref, index) => (
                              <div 
                                key={index}
                                className="text-xs bg-muted/50 p-1.5 rounded border border-border flex items-start"
                              >
                                <FileText className="h-3 w-3 mr-1 mt-0.5 flex-shrink-0" />
                                <div>
                                  <p className="font-medium">{ref.filePath}</p>
                                  <p className="text-muted-foreground line-clamp-1">{ref.text}</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                        
                        <div className="text-xs mt-1 opacity-70 text-right">
                          {message.timestamp.toLocaleTimeString()}
                        </div>
                      </div>
                      
                      {message.role === 'user' && (
                        <Avatar className="h-8 w-8 ml-2">
                          <AvatarImage src="/user-avatar.png" />
                          <AvatarFallback className="bg-muted">
                            <User className="h-4 w-4" />
                          </AvatarFallback>
                        </Avatar>
                      )}
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>
          </TabsContent>
          
          <TabsContent value="tasks" className="flex-1 p-0 m-0 overflow-hidden">
            <ScrollArea className="h-[calc(100%-60px)]">
              <div className="p-4 space-y-4">
                {tasks.length === 0 ? (
                  <div className="flex items-center justify-center h-[300px]">
                    <div className="text-center space-y-2">
                      <Sparkles className="h-12 w-12 text-primary/50 mx-auto" />
                      <p className="text-muted-foreground">尚未开始分析任务</p>
                      <p className="text-sm text-muted-foreground">
                        在对话中提问以开始分析
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {tasks.map((task) => (
                      <Card key={task.id} className="overflow-hidden">
                        <CardContent className="p-3">
                          <div className="flex items-start gap-2">
                            <div className={cn(
                              "p-2 rounded-full",
                              task.status === 'completed' 
                                ? "bg-green-100 text-green-800"
                                : task.status === 'failed'
                                ? "bg-red-100 text-red-800"
                                : "bg-amber-100 text-amber-800"
                            )}>
                              {task.status === 'completed' ? (
                                <CheckCircle2 className="h-4 w-4" />
                              ) : task.status === 'failed' ? (
                                <X className="h-4 w-4" />
                              ) : (
                                <Clock className="h-4 w-4" />
                              )}
                            </div>
                            <div className="flex-1">
                              <div className="flex justify-between items-start">
                                <div className="font-medium">{task.description}</div>
                                <Badge variant="outline" className={cn(
                                  task.status === 'completed' 
                                    ? "bg-green-100 text-green-800 border-green-200"
                                    : task.status === 'failed'
                                    ? "bg-red-100 text-red-800 border-red-200"
                                    : "bg-amber-100 text-amber-800 border-amber-200"
                                )}>
                                  {task.status === 'completed' ? '已完成' : task.status === 'failed' ? '失败' : '进行中'}
                                </Badge>
                              </div>
                              {task.result && (
                                <p className="text-sm mt-2">{task.result}</p>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </div>

      <div className="chat-footer flex-none">
        <CardFooter className="p-4 border-t mt-auto">
          <form onSubmit={handleSubmit} className="flex w-full space-x-2">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="输入你的问题..."
              className="flex-1 min-h-[60px] max-h-[120px] resize-y"
              disabled={isLoading}
            />
            <div className="flex flex-col gap-2">
              <Button type="button" size="icon" variant="outline" disabled={isLoading} title="附加文件">
                <PaperclipIcon className="h-4 w-4" />
              </Button>
              <Button type="submit" size="icon" disabled={isLoading || !input.trim()} className="bg-primary">
                <SendIcon className="h-4 w-4" />
              </Button>
            </div>
          </form>
        </CardFooter>
      </div>
    </div>
  );
}
