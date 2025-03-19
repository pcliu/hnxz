"use client";

import { useState, useEffect } from "react";
import { ResizablePanel, ResizablePanelGroup } from "../components/ui/resizable";
import { CustomResizableHandle } from "../components/ui/custom-resizable";
import { Button } from "../components/ui/button";
import { FileTree } from "../components/file-tree";
import { FileViewer } from "../components/file-viewer";
import { ChatPanel } from "../components/chat-panel";
import { LegalFileTree } from "../components/ui/legal-file-tree";
import { LegalDocumentViewer } from "../components/ui/legal-document-viewer";
import { LegalChatPanel } from "../components/ui/legal-chat-panel";
import { MessageSquare, X, Scale, FileText, Gavel } from "lucide-react";

export default function Home() {
  const [files, setFiles] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>("");
  const [isChatOpen, setIsChatOpen] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // 加载文件列表
  useEffect(() => {
    // 这里应该从API获取文件列表，现在使用模拟数据
    setIsLoading(true);
    fetch('/api/files')
      .then(res => res.json())
      .then(data => {
        setFiles(data);
        setIsLoading(false);
      })
      .catch(err => {
        console.error('加载文件列表失败:', err);
        // 模拟数据
        const mockFiles = [
          {
            id: "case-files",
            name: "案件文件",
            type: "directory",
            path: "/案件文件",
            children: [
              {
                id: "indictment",
                name: "起诉书.md",
                type: "file",
                path: "/案件文件/起诉书.md",
                fileType: "indictment",
                metadata: {
                  date: "2023-01-15",
                  author: "检察官张某",
                  status: "已提交"
                }
              },
              {
                id: "evidence",
                name: "证据材料",
                type: "directory",
                path: "/案件文件/证据材料",
                children: [
                  {
                    id: "physical-evidence",
                    name: "物证清单.md",
                    type: "file",
                    path: "/案件文件/证据材料/物证清单.md",
                    fileType: "evidence"
                  },
                  {
                    id: "testimony",
                    name: "证人证言.md",
                    type: "file",
                    path: "/案件文件/证据材料/证人证言.md",
                    fileType: "testimony"
                  }
                ]
              },
              {
                id: "investigation",
                name: "侦查报告.md",
                type: "file",
                path: "/案件文件/侦查报告.md",
                fileType: "investigation"
              }
            ]
          },
          {
            id: "legal-documents",
            name: "法律文书",
            type: "directory",
            path: "/法律文书",
            children: [
              {
                id: "judgment",
                name: "判决书.md",
                type: "file",
                path: "/法律文书/判决书.md",
                fileType: "judgment"
              },
              {
                id: "legal-provisions",
                name: "适用法条.md",
                type: "file",
                path: "/法律文书/适用法条.md",
                fileType: "legal"
              }
            ]
          }
        ];
        setFiles(mockFiles);
        setIsLoading(false);
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
        // 模拟数据
        const fileName = filePath.split('/').pop() || '';
        let mockContent = '';
        
        if (fileName.includes('起诉书')) {
          mockContent = `# 起诉书

**案号**：刑事诉字[2023]01234号

## 被告人基本信息

被告人张某某，男，1985年5月出生，汉族，身份证号码：XXXXXXXXXXXXXXXXXX，住址：某市某区某街道。

## 指控事实

经查，2023年1月15日晚，被告人张某某在某市某区某酒吧内与被害人李某某因琐事发生口角，后被告人张某某使用随身携带的折叠刀对被害人李某某实施刺击，造成被害人李某某胸部重伤。经法医鉴定，被害人李某某所受伤害已构成重伤二级。

## 法律依据

被告人张某某的行为已触犯《中华人民共和国刑法》第二百三十四条，涉嫌故意伤害罪。案发后，被告人张某某主动向公安机关投案，并如实供述自己的犯罪事实，系自首。被告人张某某家属已与被害人李某某达成赔偿协议，并支付赔偿金人民币15万元。被害人李某某表示谅解。

## 处理意见

据此，依照《中华人民共和国刑事诉讼法》第一百七十二条之规定，提起公诉，请依法判处。`;
        } else if (fileName.includes('物证清单')) {
          mockContent = `# 物证清单

**案号**：刑事诉字[2023]01234号

| 序号 | 物证名称 | 数量 | 特征 | 发现地点 | 发现时间 |
| --- | --- | --- | --- | --- | --- |
| 1 | 血衣 | 1件 | 白色T恤，胸前有血迹 | 案发现场 | 2023-01-15 |
| 2 | 血迹样本 | 2份 | 被害人血迹 | 案发现场 | 2023-01-15 |
| 3 | 监控录像 | 1份 | 案发过程录像 | 酒吧监控室 | 2023-01-16 |

**备注**：未发现作案工具（折叠刀）`;
        } else if (fileName.includes('证人证言')) {
          mockContent = `# 证人证言

**案号**：刑事诉字[2023]01234号

## 证人王某某证言

时间：2023年1月16日

地点：某市公安局

内容：我是案发当晚在酒吧的服务员。大约晚上10点左右，我看到被告人张某某和被害人李某某发生争执。争执过程中，张某某突然从口袋里掏出一把折叠刀，向李某某胸部刺去。我立即报警并呼叫救护车。

## 证人赵某某证言

时间：2023年1月16日

地点：某市公安局

内容：我是案发当晚在酒吧的顾客。我看到张某某和李某某因为一点小事发生争执，两人都喝了不少酒。争执过程中，张某某情绪激动，掏出一把刀刺向李某某。我当时距离他们很近，看得很清楚。`;
        } else if (fileName.includes('侦查报告')) {
          mockContent = `# 侦查报告

**案号**：刑事诉字[2023]01234号

## 案件概述

2023年1月15日晚，接报警在某酒吧发生一起伤害案件。经初步侦查，嫌疑人张某某因琐事与被害人李某某发生口角，后用折叠刀将李某某刺伤。

## 侦查过程

1. 2023年1月15日23:30，接到报警后民警赶赴现场，将嫌疑人张某某控制。
2. 2023年1月16日凌晨，对现场进行勘查，提取血衣、血迹样本等物证。
3. 2023年1月16日上午，调取现场监控录像。
4. 2023年1月16日至17日，询问证人王某某、赵某某等人。
5. 2023年1月20日，对嫌疑人张某某进行讯问，其如实供述犯罪事实。

## 侦查结论

经侦查，嫌疑人张某某涉嫌故意伤害罪，建议批准逮捕。`;
        } else if (fileName.includes('判决书')) {
          mockContent = `# 判决书

**案号**：刑事判决字[2023]01234号

## 基本案情

被告人张某某因与被害人李某某发生口角，持折叠刀将李某某刺伤，致其重伤二级。案发后，被告人张某某主动投案，如实供述犯罪事实，并与被害人达成赔偿协议，取得被害人谅解。

## 法院认定

法院认为，被告人张某某的行为已构成故意伤害罪。鉴于被告人案发后自首，如实供述犯罪事实，积极赔偿被害人损失并取得谅解，依法可以从轻处罚。

## 判决结果

依照《中华人民共和国刑法》第二百三十四条、第六十七条第一款之规定，判决如下：

1. 被告人张某某犯故意伤害罪，判处有期徒刑三年，缓刑四年。
2. 缓刑考验期内，依法接受社区矫正，遵守相关规定。

如不服本判决，可在接到判决书的第二日起十日内，通过本院或者直接向上一级人民法院提出上诉。`;
        } else if (fileName.includes('适用法条')) {
          mockContent = `# 适用法条

**案号**：刑事诉字[2023]01234号

## 《中华人民共和国刑法》

### 第二百三十四条【故意伤害罪】

故意伤害他人身体的，处三年以下有期徒刑、拘役或者管制。

犯前款罪，致人重伤的，处三年以上十年以下有期徒刑；致人死亡或者以特别残忍手段致人重伤造成严重残疾的，处十年以上有期徒刑、无期徒刑或者死刑。

### 第六十七条【自首】

犯罪以后自动投案，如实供述自己的罪行的，是自首。对于自首的犯罪分子，可以从轻或者减轻处罚。其中，犯罪较轻的，可以免除处罚。

## 《中华人民共和国刑事诉讼法》

### 第一百七十二条【提起公诉的条件】

人民检察院认为犯罪嫌疑人的犯罪事实已经查清，证据确实、充分，依法应当追究刑事责任的，应当作出起诉决定，按照审判管辖的规定，向人民法院提起公诉。`;
        } else {
          mockContent = `# ${fileName}

这是一个示例文档内容，实际应用中应从后端获取真实内容。`;
        }
        
        setFileContent(mockContent);
      });
  };

  return (
    <div className="flex flex-col h-screen">
      {/* 头部标题栏 */}
      <header className="border-b p-4 flex justify-between items-center bg-card">
        <div className="flex items-center gap-2">
          <Scale className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-bold">刑事案件文件分析系统</h1>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            className="gap-1"
          >
            <Gavel className="h-4 w-4" />
            案件管理
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={() => setIsChatOpen(!isChatOpen)}
          >
            {isChatOpen ? <X className="h-4 w-4" /> : <MessageSquare className="h-4 w-4" />}
          </Button>
        </div>
      </header>

      {/* 主要内容区域 - 三面板布局 */}
      <ResizablePanelGroup direction="horizontal" className="flex-1">
        {/* 文件树面板 */}
        <ResizablePanel defaultSize={20} minSize={15}>
          <div className="h-full border-r border-black/30">
            {isLoading ? (
              <div className="flex items-center justify-center h-full">
                <div className="animate-pulse text-center">
                  <FileText className="h-10 w-10 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">加载文件中...</p>
                </div>
              </div>
            ) : (
              <LegalFileTree files={files} onSelectFile={loadFileContent} />
            )}
          </div>
        </ResizablePanel>

        <CustomResizableHandle />

        {/* 文件内容面板 */}
        <ResizablePanel defaultSize={isChatOpen ? 50 : 80}>
          <div className="h-full">
            <LegalDocumentViewer content={fileContent} filePath={selectedFile} />
          </div>
        </ResizablePanel>

        {/* 聊天面板 - 可以关闭 */}
        {isChatOpen && (
          <>
            <CustomResizableHandle />
            <ResizablePanel defaultSize={30}>
              <div className="h-full border-l border-black/30 overflow-y-auto">
                <LegalChatPanel filePath={selectedFile} />
              </div>
            </ResizablePanel>
          </>
        )}
      </ResizablePanelGroup>

      {/* 页脚 */}
      <footer className="border-t py-2 px-4 text-center text-sm text-muted-foreground flex items-center justify-between">
        <div>
          © 2025 河南公安 - 刑事案件文件分析系统
        </div>
        <div className="text-xs text-muted-foreground">
          版本 v1.0.0 | 最后更新: 2025-03-19
        </div>
      </footer>
    </div>
  );
}
