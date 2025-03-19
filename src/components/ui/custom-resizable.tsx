import React from "react";
import { ResizableHandle as OriginalResizableHandle } from "./resizable";

export const CustomResizableHandle: React.FC = () => {
  return (
    <OriginalResizableHandle className="group relative !w-4 !bg-transparent hover:!bg-transparent active:!bg-transparent">
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-0.5 h-16 bg-primary/50 group-hover:bg-primary/80 group-active:bg-primary transition-colors duration-200 rounded-full"></div>
      </div>
    </OriginalResizableHandle>
  );
};
