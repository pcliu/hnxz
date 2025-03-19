import React from 'react';
import { Search } from 'lucide-react';

export function PoliceSearch() {
  return (
    <div className="relative flex items-center">
      <input
        type="text"
        placeholder="输入关键字搜索"
        className="h-8 pl-3 pr-10 rounded-full text-sm border border-gray-300 focus:outline-none focus:border-blue-500"
      />
      <button className="absolute right-0 top-0 h-full px-3 flex items-center justify-center text-gray-500 hover:text-blue-600">
        <Search className="h-4 w-4" />
      </button>
    </div>
  );
}
