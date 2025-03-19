import React from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';

interface NavItem {
  label: string;
  href: string;
  active?: boolean;
}

interface PoliceNavProps {
  items?: NavItem[];
  className?: string;
}

export function PoliceNav({ items = defaultNavItems, className }: PoliceNavProps) {
  return (
    <nav className={cn("bg-blue-800 text-white", className)}>
      <div className="container mx-auto px-4">
        <ul className="flex items-center h-12">
          {items.map((item, index) => (
            <li key={index} className="relative">
              <Link 
                href={item.href} 
                className={cn(
                  "px-6 py-3 flex items-center h-full hover:bg-blue-700 transition-colors",
                  item.active && "bg-blue-700 font-medium"
                )}
              >
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}

const defaultNavItems: NavItem[] = [
  { label: '首 页', href: '/', active: true },
  { label: '机构设置', href: '/organization' },
  { label: '警务信息', href: '/info' },
  { label: '办事服务', href: '/services' },
  { label: '警民互动', href: '/interaction' },
];
