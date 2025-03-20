#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import os
import logging
import inspect
from pathlib import Path

# 设置日志级别为DEBUG以获取更多信息
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestDynamicAgent")

# 添加项目根目录到Python路径
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
logger.info(f"添加项目根目录到Python路径: {root_dir}")

# 设置OpenManus配置目录环境变量
openmanus_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'openmanus')
config_dir = os.path.join(openmanus_path, 'config')
os.environ['OPENMANUS_CONFIG_DIR'] = config_dir
logger.info(f"设置OpenManus配置目录: {config_dir}")

# 检查配置文件
config_file = os.path.join(config_dir, 'config.toml')
if os.path.exists(config_file):
    logger.info(f"找到配置文件: {config_file}")
    # 打印配置文件内容（不包括API密钥）
    with open(config_file, 'r') as f:
        content = f.read()
        # 替换API密钥为占位符
        content = content.replace(content.split('api_key = ')[1].split('\n')[0], '"[API_KEY_HIDDEN]"')
        logger.debug(f"配置文件内容预览:\n{content[:500]}...")
else:
    logger.error(f"配置文件不存在: {config_file}")

# 添加OpenManus到Python路径
sys.path.append(openmanus_path)
logger.info(f"添加OpenManus路径: {openmanus_path}")

# 检查Python路径和模块可见性
logger.debug(f"Python路径: {sys.path}")

# 尝试导入核心模块
try:
    from app.config import config
    logger.info("成功导入OpenManus config模块")
    # 检查config对象
    if hasattr(config, 'llm'):
        # 安全地检查config.llm的属性
        try:
            logger.info(f"Config llm类型: {type(config.llm)}")
            
            # 获取config.llm的属性
            llm_attrs = [attr for attr in dir(config.llm) if not attr.startswith('_')]
            logger.info(f"Config llm属性: {llm_attrs}")
            
            # 尝试安全访问model
            if hasattr(config.llm, 'default'):
                logger.info(f"默认LLM模型: {getattr(config.llm.default, 'model', '未找到')}")
            else:
                logger.warning("config.llm没有default属性")
                
            # 尝试打印整个config.llm对象
            logger.info(f"Config llm: {config.llm}")
        except Exception as e:
            logger.error(f"访问config.llm属性时出错: {str(e)}")
    else:
        logger.warning("config对象没有llm属性")
        
    # 检查整个config对象
    logger.info(f"Config类型: {type(config)}")
    config_attrs = [attr for attr in dir(config) if not attr.startswith('_')]
    logger.info(f"Config属性: {config_attrs}")
except ImportError as e:
    logger.error(f"导入OpenManus config模块失败: {str(e)}")
    logger.info("尝试使用替代路径...")
    sys.path.append(os.path.join(openmanus_path, 'app'))
    try:
        from config import config
        logger.info("使用替代路径成功导入config模块")
    except ImportError as e2:
        logger.error(f"使用替代路径仍然失败: {str(e2)}")

# 检查app包结构
try:
    import app
    logger.info(f"app包路径: {app.__file__}")
    
    # 检查app包内容
    app_contents = dir(app)
    logger.info(f"app包内容: {[item for item in app_contents if not item.startswith('_')]}")
    
    # 检查app.agent包
    try:
        import app.agent
        logger.info(f"app.agent包路径: {app.agent.__file__}")
        agent_contents = dir(app.agent)
        logger.info(f"app.agent包内容: {[item for item in agent_contents if not item.startswith('_')]}")
    except ImportError as e:
        logger.error(f"导入app.agent包失败: {str(e)}")
except ImportError as e:
    logger.error(f"导入app包失败: {str(e)}")

# 现在导入DynamicLegalAgent
try:
    logger.info("尝试导入DynamicLegalAgent...")
    from backend.manus.dynamic_agent import DynamicLegalAgent
    logger.info("成功导入DynamicLegalAgent")
    # 检查DynamicLegalAgent的实现
    source_file = inspect.getsourcefile(DynamicLegalAgent)
    logger.info(f"DynamicLegalAgent源文件: {source_file}")
except ImportError as e:
    logger.error(f"导入DynamicLegalAgent失败: {str(e)}")
    sys.exit(1)

async def test_dynamic_agent():
    """测试DynamicLegalAgent的功能"""
    logger.info("开始测试DynamicLegalAgent...")
    
    # 创建DynamicLegalAgent实例
    try:
        agent = DynamicLegalAgent()
        logger.info("成功创建DynamicLegalAgent实例")
    except Exception as e:
        logger.error(f"创建DynamicLegalAgent实例失败: {str(e)}")
        return
    
    # 测试用户查询
    test_query = "分析张某故意伤害案的证据链是否完整，法律适用是否正确？"
    
    logger.info(f"测试查询: {test_query}")
    
    # 追踪分析过程
    step_count = 0
    try:
        async for response in agent.analyze_query(test_query):
            logger.info(f"步骤 {step_count}: {response['status']}")
            
            if response['status'] == 'planning':
                logger.info(f"计划内容: {response.get('plan', '无计划内容')[:200]}...")
            
            elif response['status'] == 'processing':
                logger.info(f"正在处理步骤: {response.get('step', '未知步骤')} "
                          f"({response.get('progress', '进度未知')})")
            
            elif response['status'] == 'step_completed':
                step_result = response.get('result', {})
                documents = step_result.get('documents', [])
                logger.info(f"步骤完成: {response.get('step', '未知步骤')}")
                logger.info(f"使用的文档: {', '.join(documents) if documents else '无文档'}")
            
            elif response['status'] == 'completed':
                final_result = response.get('result', {})
                elapsed_time = response.get('elapsed_time', 0)
                logger.info(f"分析完成，耗时: {elapsed_time:.2f}秒")
                logger.info(f"完成步骤数: {final_result.get('steps_completed', 0)}/{final_result.get('steps_total', 0)}")
                
                # 打印最终结果的一部分
                content = final_result.get('content', '')
                logger.info(f"分析结果预览: {content[:500]}..." if len(content) > 500 else content)
            
            elif response['status'] == 'error':
                logger.error(f"错误: {response.get('message', '未知错误')}")
            
            step_count += 1
    except Exception as e:
        logger.error(f"执行analyze_query时出错: {str(e)}")
    
    # 清理资源
    try:
        agent.cleanup()
        logger.info("成功清理资源")
    except Exception as e:
        logger.error(f"清理资源时出错: {str(e)}")
    
    logger.info("测试完成")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_dynamic_agent()) 