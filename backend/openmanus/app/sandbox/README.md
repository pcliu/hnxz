# Sandbox 模块

Sandbox 模块是 OpenManus 的安全执行环境，为代理系统提供隔离的执行空间，确保代码执行的安全性和可控性。

## 功能概述

Sandbox 模块提供以下核心功能：

- **安全执行**：在隔离环境中执行不可信代码
- **资源限制**：限制执行时间、内存使用等资源
- **环境管理**：提供统一的环境管理接口
- **状态追踪**：跟踪执行状态和结果
- **清理机制**：自动清理临时资源

## 主要组件

### SandboxClient

`SandboxClient` 是沙盒模块的主要接口，提供了与沙盒环境交互的方法：

- **执行代码**：在沙盒中执行代码
- **资源管理**：管理沙盒资源
- **状态查询**：查询执行状态
- **结果获取**：获取执行结果

### 执行环境

Sandbox 模块支持多种执行环境：

- **本地执行**：在本地进程中执行代码
- **容器执行**：在 Docker 容器中执行代码
- **远程执行**：在远程服务器上执行代码

## 使用示例

```python
from app.sandbox.client import SANDBOX_CLIENT

# 执行 Python 代码
async def execute_python(code):
    result = await SANDBOX_CLIENT.execute_python(code)
    return result

# 执行 Bash 命令
async def execute_bash(command):
    result = await SANDBOX_CLIENT.execute_bash(command)
    return result

# 清理资源
async def cleanup():
    await SANDBOX_CLIENT.cleanup()
```

## 安全考虑

Sandbox 模块采取了多种安全措施：

- **资源限制**：限制 CPU 时间、内存使用和磁盘访问
- **网络隔离**：限制网络访问
- **权限控制**：以最小权限运行代码
- **超时控制**：设置执行超时，防止无限循环

## 扩展指南

要添加新的执行环境，可以扩展 `SandboxClient` 类：

1. 创建新的执行方法
2. 实现资源限制和安全控制
3. 提供结果处理和错误处理机制

```python
class CustomSandboxClient(SandboxClient):
    async def execute_custom(self, code, **options):
        # 实现自定义执行逻辑
        pass
```
