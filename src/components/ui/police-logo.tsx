import React from 'react';

export function PoliceLogo() {
  return (
    <div className="flex items-center gap-2">
      <div className="w-10 h-10 bg-red-600 rounded-full flex items-center justify-center">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="white"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="w-6 h-6"
        >
          <path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z" />
          <path d="M12 8v8" />
          <path d="M8 12h8" />
        </svg>
      </div>
      <div className="flex flex-col">
        <span className="font-bold text-base leading-tight">中华人民共和国公安部</span>
        <span className="text-xs text-gray-600 leading-tight">刑事案件文件分析系统</span>
      </div>
    </div>
  );
}
