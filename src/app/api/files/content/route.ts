import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const filePath = searchParams.get('path');
    
    if (!filePath) {
      return NextResponse.json(
        { error: '缺少文件路径参数' },
        { status: 400 }
      );
    }
    
    // 确保文件路径在项目根目录下
    const fullPath = path.join(process.cwd(), filePath);
    
    // 安全检查：确保文件路径不超出项目根目录
    const relativePath = path.relative(process.cwd(), fullPath);
    if (relativePath.startsWith('..') || path.isAbsolute(relativePath)) {
      return NextResponse.json(
        { error: '无效的文件路径' },
        { status: 403 }
      );
    }
    
    // 检查文件是否存在
    if (!fs.existsSync(fullPath)) {
      return NextResponse.json(
        { error: '文件不存在' },
        { status: 404 }
      );
    }
    
    // 检查是否为文件
    const stats = fs.statSync(fullPath);
    if (!stats.isFile()) {
      return NextResponse.json(
        { error: '请求的路径不是文件' },
        { status: 400 }
      );
    }
    
    // 读取文件内容
    const content = fs.readFileSync(fullPath, 'utf-8');
    
    return NextResponse.json({ content });
  } catch (error) {
    console.error('获取文件内容失败:', error);
    return NextResponse.json(
      { error: '获取文件内容失败' },
      { status: 500 }
    );
  }
}
