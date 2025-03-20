from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(title="刑事案件文件分析系统API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入路由
from api.routes import router as api_router

# 注册路由
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "刑事案件文件分析系统API服务正在运行"}

if __name__ == "__main__":
    # 获取端口，默认为8000
    port = int(os.getenv("PORT", 8000))
    
    # 启动服务
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
