#!/bin/bash

# 激活Python 3.12虚拟环境
source venv_py312/bin/activate

# 设置Python路径，确保OpenManus能够被正确导入
export PYTHONPATH=$PYTHONPATH:$(pwd)/..:$(pwd):$(pwd)/openmanus

# 启动后端服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
