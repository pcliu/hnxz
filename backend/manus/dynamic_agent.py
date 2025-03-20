import asyncio
import os
import sys
import json
import tempfile
import re
import time
from typing import Dict, Any, List, AsyncGenerator, Optional, Set, Tuple
from pathlib import Path
import logging

# 添加OpenManus到Python路径，确保路径正确
openmanus_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'openmanus')
sys.path.append(openmanus_path)

# 设置环境变量，让OpenManus知道配置文件位置
os.environ['OPENMANUS_CONFIG_DIR'] = os.path.join(openmanus_path, 'config')

# 导入OpenManus相关模块
try:
    from app.agent.manus import Manus
    from app.agent.planning import PlanningAgent
    from app.config import config
    from app.tool.str_replace_editor import StrReplaceEditor
    from app.tool.python_execute import PythonExecute
    from app.tool.planning import PlanningTool
    from app.schema import Message
    logging.info(f"成功导入OpenManus模块，配置目录: {os.environ.get('OPENMANUS_CONFIG_DIR')}")
except ImportError as e:
    logging.error(f"导入OpenManus模块失败: {str(e)}")
    logging.error(f"当前Python路径: {sys.path}")
    # 尝试直接从openmanus目录导入
    sys.path.append(os.path.join(openmanus_path, 'app'))
    try:
        from agent.manus import Manus
        from agent.planning import PlanningAgent
        from config import config
        from tool.str_replace_editor import StrReplaceEditor
        from tool.python_execute import PythonExecute
        from tool.planning import PlanningTool
        from schema import Message
        logging.info("使用替代路径成功导入OpenManus模块")
    except ImportError as e2:
        logging.error(f"尝试替代导入路径仍然失败: {str(e2)}")
        raise

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DynamicAgent")

class DynamicLegalAgent:
    """
    动态规划法律文档分析Agent
    
    基于OpenManus的PlanningAgent实现，通过动态规划方式处理法律文档分析任务。
    根据用户查询和文档内容自动规划分析步骤，可以在执行过程中动态加载相关文档。
    使用临时文件记录分析过程中的中间结果，实现更灵活的文档分析流程。
    """
    
    def __init__(self):
        """初始化动态法律文档分析Agent"""
        # 检查OpenManus配置是否正确加载
        logger.info(f"OpenManus配置目录: {os.environ.get('OPENMANUS_CONFIG_DIR', '未设置')}")
        config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'openmanus', 'config', 'config.toml')
        if os.path.exists(config_file):
            logger.info(f"找到配置文件: {config_file}")
        else:
            logger.warning(f"配置文件不存在: {config_file}")
            
        # 获取OpenManus的WORKSPACE_ROOT
        import backend.openmanus.app.config as app_config
        self.openmanus_workspace = app_config.WORKSPACE_ROOT
        logger.info(f"OpenManus工作目录: {self.openmanus_workspace}")
        
        # 设置源文件目录
        self.source_workspace = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'business')
        logger.info(f"源文件目录: {self.source_workspace}")
        
        # 将business目录中的文件复制到OpenManus工作目录
        self._copy_files_to_workspace()
        
        # 检查API配置
        try:
            # 安全地访问LLMSettings对象的属性
            if hasattr(config, 'llm') and 'default' in config.llm:
                llm_config = config.llm['default']
                api_type = llm_config.api_type if hasattr(llm_config, 'api_type') else 'unknown'
                model = llm_config.model if hasattr(llm_config, 'model') else 'unknown'
                base_url = llm_config.base_url if hasattr(llm_config, 'base_url') else 'unknown'
                api_key = "已配置" if hasattr(llm_config, 'api_key') and llm_config.api_key else "未配置"
                
                logger.info(f"API配置: 类型={api_type}, 模型={model}, API密钥={api_key}")
                if base_url.endswith('/'):
                    logger.warning("base_url末尾有斜杠，可能导致API调用问题")
            else:
                logger.warning("未找到默认LLM配置")
        except Exception as e:
            logger.error(f"获取API配置信息失败: {str(e)}")
        
        # 初始化OpenManus的Manus Agent
        self.manus_agent = Manus()
        
        # 创建规划Agent (Planning Agent)
        self.planning_agent = PlanningAgent()
        
        # 已处理的文档缓存
        self.processed_documents = set()
        
        # 文档内容缓存
        self.document_cache = {}
        
        # 文档目录缓存
        self.document_directory = None
        
        # 当前任务上下文和计划ID
        self.current_task_context = {}
        self.current_plan_id = None
        
        # 创建临时文件目录用于存储中间结果
        self.temp_dir = tempfile.mkdtemp(prefix="legal_analysis_")
        logger.info(f"创建临时目录: {self.temp_dir}")
        
        # 检查PlanningAgent初始化状态
        if not hasattr(self.planning_agent, 'available_tools') or not self.planning_agent.available_tools or "planning" not in self.planning_agent.available_tools.tool_map:
            logger.error("PlanningAgent初始化失败，无法使用规划功能")
        
        # 初始化时扫描文档目录
        asyncio.create_task(self._scan_document_directory())
        
    def _copy_files_to_workspace(self):
        """将business目录中的文件复制到OpenManus工作目录"""
        try:
            import shutil
            
            # 确保目标目录存在
            os.makedirs(self.openmanus_workspace, exist_ok=True)
            
            # 统计文件数
            copied_files = 0
            
            # 递归遍历源目录
            for root, dirs, files in os.walk(self.source_workspace):
                # 计算目标目录路径
                rel_path = os.path.relpath(root, self.source_workspace)
                target_dir = os.path.join(self.openmanus_workspace, rel_path)
                
                # 创建目标子目录
                os.makedirs(target_dir, exist_ok=True)
                
                # 复制文件
                for file in files:
                    source_file = os.path.join(root, file)
                    target_file = os.path.join(target_dir, file)
                    
                    # 如果目标文件已存在，则先删除
                    if os.path.exists(target_file):
                        os.remove(target_file)
                        
                    # 复制文件
                    shutil.copy2(source_file, target_file)
                    copied_files += 1
            
            logger.info(f"成功将 {copied_files} 个文件从 {self.source_workspace} 复制到 {self.openmanus_workspace}")
        except Exception as e:
            logger.error(f"复制文件到工作目录时出错: {str(e)}")
        
    async def analyze_query(self, query: str, document_id: Optional[str] = None,
                         document_content: Optional[str] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """使用动态规划方式分析用户查询，基于文档内容生成分析计划并执行"""
        # 记录开始时间
        start_time = time.time()
        
        # 确保文档目录已扫描
        if self.document_directory is None:
            await self._scan_document_directory()
            
        # 首先返回初始状态
        yield {
            "status": "started",
            "message": "开始分析用户查询，准备创建动态分析计划"
        }
        
        # 如果提供了文档ID和内容，将其添加到缓存
        if document_id and document_content:
            self.processed_documents.add(document_id)
            self.document_cache[document_id] = document_content
            
            # 创建初始中间文件记录该文档
            await self._save_to_temp_file("initial_document.md", 
                                        f"# 初始文档: {document_id}\n\n{document_content[:2000]}...")
        
        # 构建文档清单
        document_list = await self._generate_document_list()
        document_list_text = "\n".join([f"- {doc['name']} (类别: {doc['category']})" for doc in document_list[:20]])
        
        # 将文档清单保存到临时文件
        await self._save_to_temp_file("document_list.md", f"# 可用文档清单\n\n{document_list_text}")
        
        # 创建规划提示，用于指导规划过程
        planning_prompt = f"""分析以下用户询问，并创建一个动态分析计划来处理法律文档分析任务。

用户询问: {query}

可用文档清单:
{document_list_text}

请创建一个详细的计划，包括以下方面的分析:
1. 理解用户需求，确定核心问题
2. 识别需要分析的文档和信息
3. 提取关键信息和证据
4. 验证法律适用性
5. 生成综合分析结果

你的计划应该是动态的，允许在执行过程中根据发现的信息调整后续步骤。
每个步骤都应该足够具体，包括需要查询的文档类型和关注的问题点。"""
        
        # 创建初始计划
        try:
            # 使用PlanningAgent创建初始计划
            self.current_plan_id = f"plan_{int(time.time())}"
            
            # 检查 planning_agent.available_tools 是否正确初始化
            if not hasattr(self.planning_agent, 'available_tools') or not self.planning_agent.available_tools or "planning" not in self.planning_agent.available_tools.tool_map:
                logger.error("PlanningAgent.available_tools 初始化失败，无法执行计划创建")
                yield {
                    "status": "error",
                    "message": "规划工具初始化失败，无法创建分析计划"
                }
                return
                
            # 尝试执行计划创建
            try:
                # 使用create_initial_plan方法创建初始计划
                await self.planning_agent.create_initial_plan(planning_prompt)
                # 使用planning_agent的active_plan_id
                self.current_plan_id = self.planning_agent.active_plan_id
                
                # 获取计划内容
                plan_result = await self.planning_agent.available_tools.execute(
                    name="planning",
                    tool_input={"command": "get", "plan_id": self.current_plan_id}
                )
                
                plan_content = plan_result.output if hasattr(plan_result, 'output') else str(plan_result)
                
                # 检查计划内容是否有效
                if not plan_content or plan_content == "None":
                    logger.error(f"plan_content 无效: {plan_content}")
                    # 使用硬编码的计划内容作为备选方案
                    plan_content = f"""
                    分析计划: {query[:30]}...
                    
                    步骤:
                    1. 扫描文档目录，确定需要分析的关键文档
                    2. 提取相关证据和信息
                    3. 分析证据链完整性
                    4. 检查法律条文适用性
                    5. 验证时间线逻辑
                    6. 生成综合分析报告
                    """
                    logger.info("使用备选计划内容")
                    
                    # 尝试使用PlanningTool直接创建计划
                    await self.planning_agent.available_tools.execute(
                        name="planning",
                        tool_input={
                            "command": "create", 
                            "plan_id": self.current_plan_id,
                            "title": f"分析计划: {query[:30]}...",
                            "steps": [
                                "扫描文档目录，确定需要分析的关键文档",
                                "提取相关证据和信息",
                                "分析证据链完整性",
                                "检查法律条文适用性",
                                "验证时间线逻辑",
                                "生成综合分析报告"
                            ]
                        }
                    )
            except Exception as e:
                logger.error(f"执行计划创建时出错: {str(e)}")
                yield {
                    "status": "error",
                    "message": f"创建分析计划时出错: {str(e)}"
                }
                return
            
            # 保存计划到临时文件
            await self._save_to_temp_file("analysis_plan.md", f"# 动态分析计划\n\n{plan_content}")
            
            # 返回计划创建状态
            yield {
                "status": "planning",
                "plan": plan_content,
                "message": "已创建动态分析计划"
            }
            
            # 执行计划中的步骤
            step_results = []
            current_step_index = 0
            
            # 检查plan_content是否为None
            if plan_content is None:
                logger.error("plan_content 为 None，无法执行计划")
                yield {
                    "status": "error",
                    "message": "分析过程中发生错误: 无法获取有效的计划内容"
                }
                return
                
            # 计算总步骤数
            try:
                total_steps = plan_content.count('[ ]')
            except Exception as e:
                logger.error(f"计算步骤数时出错: {str(e)}")
                total_steps = 0
            
            # 逐步执行计划
            while current_step_index < total_steps:
                # 获取当前步骤
                step_info = await self._get_current_step(self.current_plan_id)
                if not step_info or 'step' not in step_info:
                    break
                    
                current_step = step_info['step']
                step_index = step_info.get('index', current_step_index)
                
                # 返回当前步骤状态
                yield {
                    "status": "processing",
                    "step_index": step_index,
                    "step": current_step,
                    "progress": f"{step_index + 1}/{total_steps}"
                }
                
                # 执行当前步骤
                step_result = await self._execute_step(current_step, query, step_index)
                step_results.append(step_result)
                
                # 标记步骤完成
                await self.planning_agent.available_tools.execute(
                    name="planning",
                    tool_input={
                        "command": "mark_step",
                        "plan_id": self.current_plan_id,
                        "step_index": step_index,
                        "step_status": "completed"
                    }
                )
                
                # 返回步骤完成状态
                yield {
                    "status": "step_completed",
                    "step_index": step_index,
                    "step": current_step,
                    "result": step_result
                }
                
                # 更新步骤索引
                current_step_index = step_index + 1
            
            # 合并所有步骤结果
            final_result = await self._combine_results(step_results)
            
            # 计算耗时
            elapsed_time = time.time() - start_time
            
            # 返回最终结果
            yield {
                "status": "completed",
                "result": final_result,
                "elapsed_time": elapsed_time,
                "message": f"分析完成，总耗时: {elapsed_time:.2f}秒"
            }
            
        except Exception as e:
            error_message = f"分析过程中发生错误: {str(e)}"
            logger.error(error_message)
            yield {"status": "error", "message": error_message}
            
    async def _get_current_step(self, plan_id: str) -> Dict[str, Any]:
        """获取当前计划中待执行的步骤"""
        try:
            # 检查计划是否存在
            planning_tool = self.planning_agent.available_tools.tool_map.get("planning")
            if not planning_tool or plan_id not in planning_tool.plans:
                logger.error(f"计划 {plan_id} 不存在")
                # 尝试使用API方式获取
                result = await self.planning_agent.available_tools.execute(
                    name="planning",
                    tool_input={"command": "get", "plan_id": plan_id}
                )
                plan_content = result.output if hasattr(result, 'output') else str(result)
                
                # 解析计划内容找到首个未完成步骤
                lines = plan_content.splitlines()
                steps_section = False
                
                for i, line in enumerate(lines):
                    if line.strip() == "Steps:":
                        steps_section = True
                        continue
                        
                    if steps_section and ('[ ]' in line or '[→]' in line):
                        # 提取步骤描述
                        step_match = re.search(r'(?:\[ \]|\[→\])\s*(.*?)\s*(?:\(|$)', line)
                        if step_match:
                            step_description = step_match.group(1).strip()
                            # 获取步骤索引
                            step_index = -1
                            for j, l in enumerate(lines):
                                if l.strip() == "Steps:":
                                    for k, sl in enumerate(lines[j+1:]):
                                        if '[ ]' in sl or '[→]' in sl or '[x]' in sl:
                                            if sl == line:
                                                step_index = k
                                                break
                                    break
                            
                            return {"step": step_description, "index": step_index}
                
                return {}
            
            # 直接访问计划数据（更可靠的方法）
            plan_data = planning_tool.plans[plan_id]
            steps = plan_data.get("steps", [])
            step_statuses = plan_data.get("step_statuses", [])
            
            # 查找第一个未完成的步骤
            for i, (step, status) in enumerate(zip(steps, step_statuses)):
                if status in ["not_started", "in_progress"]:
                    return {"step": step, "index": i}
            
            return {}
        except Exception as e:
            logger.error(f"获取当前步骤时出错: {str(e)}")
            return {}
            
    async def _execute_step(self, step: str, query: str, step_index: int) -> Dict[str, Any]:
        """执行单个计划步骤，让Agent自行决定需要加载的文档"""
        try:
            # 首先获取文档列表，但不加载内容
            document_list = await self._generate_document_list()
            doc_list_text = "\n".join([f"- {doc['name']}" for doc in document_list])
            
            # 构建步骤执行提示，包含文档列表，让Agent自行决定需要哪些文档
            step_prompt = f"""请执行以下分析步骤：

步骤描述: {step}

用户查询: {query}

## 可用文档列表
{doc_list_text}

请先分析当前步骤需要哪些文档，然后从中选择最相关的文档进行分析。
首先输出：【文档选择】，然后列出你需要的文档名称（每行一个）。
然后输出：【分析开始】，接着进行你的分析。
"""
            
            # 将步骤提示添加到Agent上下文
            self.manus_agent.memory.add_message(Message.user_message(step_prompt))
            
            # 使用Manus Agent执行步骤
            await self.manus_agent.step()

            # 获取Agent的响应
            last_message = self.manus_agent.memory.messages[-1].content if self.manus_agent.memory.messages else ""
            
            # 从Agent响应中提取所需文档
            selected_docs = []
            if last_message and "【文档选择】" in last_message:
                # 提取文档选择部分
                doc_selection_match = re.search(r'【文档选择】\s*\n([\s\S]*?)(?:【分析开始】|$)', last_message)
                if doc_selection_match:
                    selected_doc_text = doc_selection_match.group(1).strip()
                    selected_doc_names = [line.strip().strip('- ') for line in selected_doc_text.split('\n') if line.strip()]
                    
                    # 根据名称找到对应的文档
                    for doc_name in selected_doc_names:
                        for doc in document_list:
                            if doc_name.lower() in doc['name'].lower() and doc not in selected_docs:
                                selected_docs.append(doc)
                                break
            
            # 加载Agent选择的文档（从OpenManus工作目录加载）
            loaded_docs = await self._load_documents(selected_docs)
            
            # 如果Agent选择了文档，将文档内容发送给Agent继续分析
            if loaded_docs:
                docs_content = ""
                for doc in loaded_docs:
                    docs_content += f"\n## {doc['name']}\n{doc['content']}\n"
                
                # 构建新的提示，包含文档内容
                continue_prompt = f"""以下是你请求的文档内容，请继续你的分析：

{docs_content}
"""
                
                # 将文档内容添加到Agent上下文
                self.manus_agent.memory.add_message(Message.user_message(continue_prompt))
                
                # 使用Manus Agent继续分析
                await self.manus_agent.step()
                
                # 获取更新后的响应
                last_message = self.manus_agent.memory.messages[-1].content if self.manus_agent.memory.messages else ""
            
            # 将结果保存到临时文件
            step_filename = f"step_{step_index+1}_result.md"
            step_content = f"# 步骤 {step_index+1}: {step}\n\n{last_message}\n\n## 使用的文档\n"
            for doc in loaded_docs:
                step_content += f"- {doc['name']}\n"
            
            await self._save_to_temp_file(step_filename, step_content)
            
            # 返回步骤执行结果
            return {
                "description": step,
                "analysis": last_message,
                "documents": [doc["name"] for doc in loaded_docs]
            }
        
        except Exception as e:
            logger.error(f"执行步骤时出错: {str(e)}")
            return {"description": step, "error": str(e)}
    
    async def _scan_document_directory(self) -> None:
        """扫描文档目录，只收集文件名清单供大模型判断"""
        try:
            # 使用固定的business目录路径
            document_dir = self.source_workspace
            document_list = []
            
            if not os.path.exists(document_dir):
                logger.error(f"文档目录不存在: {document_dir}")
                self.document_directory = []
                return
                
            # 遍历文档目录
            for root, dirs, files in os.walk(document_dir):
                for file in files:
                    if file.endswith(".md") or file.endswith(".txt") or file.endswith(".pdf") or file.endswith(".docx"):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, document_dir)
                        
                        # 使用相对路径作为文档名称，更有可读性
                        doc_name = rel_path
                        
                        # 不再预先分类，由大模型自行判断
                        document_list.append({
                            "name": doc_name,
                            "path": file_path,
                            "relative_path": rel_path,
                            "category": "unknown"  # 不预先分类
                        })
            
            self.document_directory = document_list
            logger.info(f"已扫描文档目录，共找到 {len(document_list)} 个文档文件")
        except Exception as e:
            logger.error(f"扫描文档目录时出错: {str(e)}")
            self.document_directory = []
            
    async def _generate_document_list(self) -> List[Dict[str, Any]]:
        """获取可用的文档列表，包括分类信息"""
        document_list = []
        
        try:
            # 检查目录是否存在
            if not os.path.exists(self.source_workspace):
                logger.warning(f"工作目录不存在: {self.source_workspace}")
                return document_list
            
            # 遍历工作目录中的文件和文件夹
            logger.info(f"扫描工作目录: {self.source_workspace}")
            
            for root, dirs, files in os.walk(self.source_workspace):
                # 排除隐藏目录
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                # 处理文件
                for file in files:
                    # 排除隐藏文件和非文本文件
                    if file.startswith('.') or not file.endswith(('.md', '.txt', '.json')):
                        continue
                    
                    # 构建完整路径
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.source_workspace)
                    
                    # 确定文档分类（基于目录结构）
                    category = os.path.basename(os.path.dirname(full_path))
                    if category == os.path.basename(self.source_workspace):
                        category = "一般文档"
                    
                    # 添加到文档列表
                    document_list.append({
                        'id': rel_path,  # 使用相对路径作为ID
                        'name': file,
                        'path': rel_path,
                        'category': category
                    })
            
            # 按分类排序
            document_list.sort(key=lambda x: (x['category'], x['name']))
            logger.info(f"找到 {len(document_list)} 个可用文档")
        
        except Exception as e:
            logger.error(f"生成文档列表时出错: {str(e)}")
        
        return document_list
        
    async def _load_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """加载文档内容，并缓存已处理过的文档"""
        loaded_docs = []
        for doc in documents:
            # 如果已经在缓存中，直接使用缓存内容
            if doc['id'] in self.document_cache:
                loaded_docs.append({
                    'id': doc['id'],
                    'name': doc['name'],
                    'content': self.document_cache[doc['id']]
                })
                continue
                
            # 构建文档路径（使用OpenManus工作目录）
            doc_path = os.path.join(self.openmanus_workspace, doc['path'])
            
            # 确保路径正确
            logger.info(f"加载文档路径: {doc_path}")
            
            # 检查文件是否存在
            if not os.path.exists(doc_path):
                logger.warning(f"文档不存在: {doc_path}")
                # 尝试源工作目录
                source_doc_path = os.path.join(self.source_workspace, doc['path'])
                if os.path.exists(source_doc_path):
                    doc_path = source_doc_path
                    logger.info(f"在源目录找到文档: {doc_path}")
                else:
                    continue
                
            try:
                # 读取文档内容
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 缓存文档内容
                self.document_cache[doc['id']] = content
                self.processed_documents.add(doc['id'])
                
                # 添加到加载文档列表
                loaded_docs.append({
                    'id': doc['id'],
                    'name': doc['name'],
                    'content': content
                })
                
                # 记录加载成功
                logger.info(f"成功加载文档: {doc['name']}")
            except Exception as e:
                logger.error(f"加载文档 {doc['name']} 时出错: {str(e)}")
                
        return loaded_docs
        
    async def _save_to_temp_file(self, filename: str, content: str) -> str:
        """保存内容到临时文件"""
        try:
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return file_path
        except Exception as e:
            logger.error(f"保存临时文件时出错 {filename}: {str(e)}")
            return ""
        
    async def _combine_results(self, step_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """合并所有步骤结果，生成最终分析结果"""
        if not step_results:
            return {"content": "未能获取有效分析结果", "references": []}
            
        # 收集所有步骤的分析内容和引用的文档
        analysis_parts = []
        used_documents = set()
        steps_completed = 0
        errors = []
        
        for i, result in enumerate(step_results):
            step_num = i + 1
            description = result.get("description", f"步骤 {step_num}")
            
            # 检查是否有错误
            if "error" in result:
                errors.append({"step": step_num, "error": result["error"]})
                analysis_parts.append(f"## 步骤 {step_num}: {description}\n\n*执行出错: {result['error']}*\n")
                continue
                
            # 获取步骤分析结果
            analysis = result.get("analysis", "")
            if analysis:
                # 处理分析结果，移除【文档选择】和【分析开始】标记
                cleaned_analysis = analysis
                if "【文档选择】" in analysis and "【分析开始】" in analysis:
                    # 提取分析开始后的内容
                    analysis_match = re.search(r'【分析开始】\s*\n([\s\S]*?)$', analysis)
                    if analysis_match:
                        cleaned_analysis = analysis_match.group(1).strip()
                
                analysis_parts.append(f"## 步骤 {step_num}: {description}\n\n{cleaned_analysis}\n")
                steps_completed += 1
                
            # 记录使用的文档
            for doc in result.get("documents", []):
                used_documents.add(doc)
        
        # 构建最终结果
        final_content = ""
        
        # 添加摘要部分
        if steps_completed > 0:
            summary = f"# 法律文件分析结果\n\n完成了 {steps_completed} 个分析步骤"
            if errors:
                summary += f"，其中 {len(errors)} 个步骤执行出错"
            summary += "。\n\n"
            
            # 添加使用的文档列表
            if used_documents:
                summary += "## 引用文档\n\n"
                for doc in sorted(list(used_documents)):
                    summary += f"- {doc}\n"
                summary += "\n"
                
            final_content = summary + "\n" + "\n".join(analysis_parts)
        else:
            final_content = "# 法律文件分析结果\n\n未能完成任何分析步骤，请检查日志了解详情。\n"
            if errors:
                final_content += "\n## 错误信息\n\n"
                for err in errors:
                    final_content += f"- 步骤 {err['step']}: {err['error']}\n"
        
        # 将最终结果保存到临时文件
        await self._save_to_temp_file("final_analysis.md", final_content)
        
        return {
            "content": final_content,
            "references": list(used_documents),
            "steps_completed": steps_completed,
            "steps_total": len(step_results),
            "errors": errors
        }
    
    def cleanup(self):
        """清理临时文件和资源"""
        try:
            # 清理临时目录
            if os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
                logger.info(f"已清理临时目录: {self.temp_dir}")
                
            # 清理缓存
            self.document_cache.clear()
            self.processed_documents.clear()
            
        except Exception as e:
            logger.error(f"清理资源时出错: {str(e)}")
