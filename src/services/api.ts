// API服务，用于连接前端和后端

interface ChatMessage {
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

interface ChatRequest {
  message: string;
  chat_id?: string;
  document_id?: string;
}

interface AnalysisRequest {
  document_id: string;
  query: string;
}

// 基础API URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// 获取所有文档
export async function getAllDocuments() {
  try {
    const response = await fetch(`${API_BASE_URL}/documents`);
    if (!response.ok) {
      throw new Error(`获取文档列表失败: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('获取文档列表错误:', error);
    throw error;
  }
}

// 获取文档内容
export async function getDocumentContent(documentId: string) {
  try {
    const response = await fetch(`${API_BASE_URL}/documents/${documentId}`);
    if (!response.ok) {
      throw new Error(`获取文档内容失败: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('获取文档内容错误:', error);
    throw error;
  }
}

// 发送聊天消息（流式响应）
export async function sendChatMessage(request: ChatRequest, onMessage: (data: any) => void, onError: (error: any) => void) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`发送消息失败: ${response.status}`);
    }

    // 处理流式响应
    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('无法读取响应流');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    // 读取流数据
    const processStream = async () => {
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          // 解码二进制数据
          const chunk = decoder.decode(value, { stream: true });
          buffer += chunk;

          // 处理SSE格式的数据
          const lines = buffer.split('\n\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.substring(6));
                onMessage(data);
              } catch (e) {
                console.error('解析SSE数据错误:', e);
              }
            }
          }
        }
      } catch (error) {
        onError(error);
      }
    };

    processStream();
  } catch (error) {
    onError(error);
  }
}

// 获取聊天历史
export async function getChatHistory(chatId: string) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/${chatId}/history`);
    if (!response.ok) {
      throw new Error(`获取聊天历史失败: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('获取聊天历史错误:', error);
    throw error;
  }
}

// 删除聊天记录
export async function deleteChat(chatId: string) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/${chatId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error(`删除聊天记录失败: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('删除聊天记录错误:', error);
    throw error;
  }
}

// 分析文档
export async function analyzeDocument(request: AnalysisRequest) {
  try {
    const response = await fetch(`${API_BASE_URL}/analysis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      throw new Error(`分析文档失败: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('分析文档错误:', error);
    throw error;
  }
}

// 分析证据链
export async function analyzeEvidence(request: AnalysisRequest) {
  try {
    const response = await fetch(`${API_BASE_URL}/evidence-analysis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      throw new Error(`分析证据链失败: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('分析证据链错误:', error);
    throw error;
  }
}

// 验证法律条文
export async function verifyLegalProvisions(request: AnalysisRequest) {
  try {
    const response = await fetch(`${API_BASE_URL}/legal-verification`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      throw new Error(`验证法律条文失败: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('验证法律条文错误:', error);
    throw error;
  }
}

// 检查时间线
export async function checkTimeline(request: AnalysisRequest) {
  try {
    const response = await fetch(`${API_BASE_URL}/timeline-check`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      throw new Error(`检查时间线失败: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('检查时间线错误:', error);
    throw error;
  }
}
