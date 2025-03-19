import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

// 递归获取文件夹中的所有文件
function getFilesRecursively(dir: string, basePath: string = ''): any[] {
  const files = fs.readdirSync(dir);
  
  return files.flatMap(file => {
    const filePath = path.join(dir, file);
    const relativePath = path.join(basePath, file);
    const stats = fs.statSync(filePath);
    
    if (stats.isDirectory()) {
      return {
        id: relativePath,
        name: file,
        type: 'directory',
        path: relativePath,
        children: getFilesRecursively(filePath, relativePath)
      };
    } else {
      return {
        id: relativePath,
        name: file,
        type: 'file',
        path: relativePath
      };
    }
  });
}

export async function GET() {
  try {
    const businessDir = path.join(process.cwd(), 'business');
    const files = getFilesRecursively(businessDir, 'business');
    
    return NextResponse.json(files);
  } catch (error) {
    console.error('获取文件列表失败:', error);
    return NextResponse.json(
      { error: '获取文件列表失败' },
      { status: 500 }
    );
  }
}
