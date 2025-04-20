from llm.base_model import LanguageModel
from memory.memory import Memory
from tool.base_tool import Tool
from callback.callback import CallbackHandler
from rag.rag import RAG
from tool.Calculator import Calculator
from tool.Weather import Weather
import re
from typing import Dict, TypeVar, Any, Optional, Union, List
from functools import lru_cache
import json
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from datetime import datetime
import logging



# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

T = TypeVar('T', bound='Tool')  # 工具类型泛型

class ToolExecutionError(Exception):
    """工具执行错误"""
    pass

class SimpleAgent:
    """一个简单的智能代理，能够使用工具、记忆对话和检索增强生成"""
    
    def __init__(self, name: str, llm_model: str = "DeepSeek-R1"):
        """
        初始化智能代理
        Args:
            name: 代理名称
            llm_model: 使用的语言模型名称
        """
        self.name = name
        self.language_model = LanguageModel(llm_model)
        self.memory = Memory()
        self.callback = CallbackHandler(name="AgentCallback")
        self.rag_agent = RAG()
        self._tools: Dict[str, Tool] = {}
        self._executor = ThreadPoolExecutor(max_workers=4)  # 工具执行线程池
        self._init_tools()
        
    def greet(self) -> str:
        """发送欢迎消息"""
        greeting = f"你好，我是{self.name}，很高兴为你服务！"
        print(greeting)
        return greeting
    
    def rag(self, file_path: str, prompt: str) -> str:
        """
        使用RAG检索增强生成回答
        Args:
            file_path: 文档文件路径
            prompt: 用户提问
            
        Returns:
            生成的回答
        """
        logger.info(f"开始处理RAG请求，文件: {file_path}")
        self.callback.on_rag_start(file_path, prompt)
        try:
            self.rag_agent.load_document(file_path)
            result = self.rag_agent.retrieve_and_generate(prompt)
            self.callback.on_rag_end(result)
            return result
        except Exception as e:
            logger.error(f"RAG处理失败: {str(e)}")
            self.callback.on_rag_error(e)
            return f"处理文档时出错: {str(e)}"
    def generate_response(self, prompt: str, use_memory: bool = False) -> str:
        """
        生成自然语言响应
        Args:
            prompt: 输入提示
            use_memory: 是否使用记忆
        Returns:
            生成的响应文本
        """
        self.callback.on_llm_start(prompt)
        try:
            # 如果需要，可以从记忆中获取上下文
            
            response = self.language_model.generate_text(prompt)
            
            if use_memory:
                self.memory.save_history(prompt, response)
                
            self.callback.on_llm_end(response)
            return response
        except Exception as e:
            logger.error(f"生成响应失败: {str(e)}")
            self.callback.on_llm_error(e)
            return "抱歉，我无法生成回答。请稍后再试。"
    def _init_tools(self) -> None:
        """初始化默认工具集"""
        # 预加载核心工具
        self.register_tool("calculator", Calculator(), is_core=True)
        self.register_tool("weather", Weather(), is_core=True)

    @property
    def available_tools(self) -> Dict[str, str]:
        """获取可用工具清单（名称: 描述）"""
        return {
            name: tool.__doc__.split('\n')[0].strip() if tool.__doc__ else "无描述"
            for name, tool in self._tools.items()
        }

    def register_tool(self, name: str, tool_instance: Tool, *, 
                     is_core: bool = False, overwrite: bool = False) -> None:
        """
        注册新工具
        
        Args:
            name: 工具标识名
            tool_instance: 工具实例
            is_core: 是否为核心工具（不可卸载）
            overwrite: 是否允许覆盖已有工具
            
        Raises:
            ValueError: 当工具名已存在且不允许覆盖时
            TypeError: 当工具类型不正确时
        """
        if not isinstance(tool_instance, Tool):
            raise TypeError(f"工具必须继承自Tool类，获取 {type(tool_instance)}")
            
        if name in self._tools and not overwrite:
            if self._tools[name]._is_core and not is_core:
                raise ValueError(f"核心工具 {name} 不能被非核心版本覆盖")
            raise ValueError(f"工具 {name} 已存在，使用 overwrite=True 强制覆盖")
            
        tool_instance._is_core = is_core
        self._tools[name] = tool_instance
        logger.info(f"注册工具: {name} (核心: {is_core})")
        
    def unregister_tool(self, name: str) -> bool:
        """
        卸载工具
        
        Args:
            name: 工具名
            
        Returns:
            bool: 是否成功卸载
            
        Raises:
            ValueError: 当尝试卸载核心工具时
        """
        if name not in self._tools:
            return False
            
        if self._tools[name]._is_core:
            raise ValueError(f"不能卸载核心工具 {name}")
            
        del self._tools[name]
        logger.info(f"已卸载工具: {name}")
        return True
        
    @lru_cache(maxsize=32)
    def get_tool(self, name: str, tool_type: Optional[type[T]] = None) -> T:
        """
        安全获取工具实例
        Args:
            name: 工具名
            tool_type: 期望的工具类型  
        Returns:
            工具实例 
        Raises:
            ValueError: 当工具不存在或类型不匹配时
        """
        if name not in self._tools:
            raise ValueError(
                f"工具 {name} 未注册。可用工具: {list(self._tools.keys())}"
            ) 
        tool = self._tools[name]
        
        if tool_type and not isinstance(tool, tool_type):
            raise ValueError(
                f"工具 {name} 类型不符，期望 {tool_type} 但获取 {type(tool)}")  
                
        return tool
    def tool_use(self, tool_name: str, params: Union[str, dict], *args, **kwargs) -> Any: 
        """
        安全执行工具调用
        
        Args:
            tool_name: 工具名称
            params: 工具参数(可以是字符串或字典)
            *args: 工具位置参数
            **kwargs: 工具关键字参数   
        Returns:
            工具执行结果   
            
        Raises:
            ToolExecutionError: 工具执行失败时
            TimeoutError: 工具执行超时时
        """
        try:
            tool = self.get_tool(tool_name)
            self.callback.on_tool_start(tool_name, params)
            # 如果参数是字符串，尝试解析为字典
            if isinstance(params, str):
                try:
                    params = json.loads(params)
                except json.JSONDecodeError:
                    # 如果不是JSON，作为单一参数处理
                    params =params
            
            # 执行工具（带超时控制）
            result = tool.use(params)
            
            self.callback.on_tool_end(tool_name, result)
            return result
            
        except Exception as e:
            logger.error(f"工具 {tool_name} 执行失败: {str(e)}", exc_info=True)
            self.callback.on_tool_error(tool_name, e)
            raise ToolExecutionError(f"工具 {tool_name} 执行失败: {str(e)}")
        
    def llm_tool_dispatcher(self, prompt: str, file_path: Optional[str] = None) -> str:
        """
        主调度方法，根据用户输入决定使用工具或直接响应
        Args:
            prompt: 用户输入
        Returns:
            生成的响应文本
        """
        logger.info(f"用户输入: {prompt}")
        if file_path :
            return self.rag(file_path, prompt)
        tool_choice = self._llm_analyze_intent(prompt)
        if not tool_choice or tool_choice["action"] == "direct_response":
            return self.generate_response(prompt)
        try:
            result = self.tool_use(
                tool_name=tool_choice["tool"],
                params=tool_choice["params"]
            )
            return self._format_tool_result(
                tool_name=tool_choice["tool"],
                result=result,
                original_query=prompt
            ) 
        except ToolExecutionError as e:
            logger.error(f"工具调度失败: {str(e)}")
            # 失败时尝试直接回答
            return self.generate_response(f"用户问题: {prompt}\n工具执行失败: {str(e)}\n请直接回答用户问题")  
    def _llm_analyze_intent(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        使用LLM分析用户意图，决定是否使用工具
        
        Args:
            prompt: 用户输入
            
        Returns:
            包含工具选择信息的字典，或None
        """
        logger.info("分析用户意图...")
        tools_list = "\n".join(
            f"- {name}: {tool.__doc__.splitlines()[0] if tool.__doc__ else '无描述'}"
            for name, tool in self._tools.items()
        )
        prompt_template = f"""
        请分析用户意图并选择操作。可用工具：
        {tools_list}
        用户输入：{prompt}
        
        请返回严格的JSON格式：
        {{
            "tool": "工具名" | null,
            "action": "use" | "direct_response",
            "params": "参数" | null,
        }}
        """
        response = self.generate_response(prompt_template, use_memory=False)
        
        try:
            # 更健壮的JSON提取
            json_str = re.search(r'\{.*\}', response, re.DOTALL)
            if json_str:
                result = json.loads(json_str.group())
                # 验证结果结构
                if all(key in result for key in ["tool", "action", "params"]):
                    return result
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"解析意图失败: {str(e)}")
            
        return None 
    def _format_tool_result(self, tool_name: str, result: Any, 
                          original_query: str) -> str:
        """
        将工具执行结果格式化为自然语言回复
        
        Args:
            tool_name: 工具名称
            result: 工具执行结果
            original_query: 原始问题
        Returns:
            格式化的自然语言回复
        """
        logger.info(f"格式化工具 {tool_name} 的结果")
        prompt = f"""
        工具 {tool_name} 执行完成。
        原始问题：{original_query}
        执行结果：{result}
        
        请生成友好的自然语言回复，直接回答用户的问题:
        """
        return self.generate_response(prompt)
    
if __name__ == "__main__":
    # 示例用法
    agent = SimpleAgent("Agent007")
    agent.greet()   
    # print(agent.llm_tool_dispatcher("查询北京的天气"))
    print(agent.llm_tool_dispatcher("请计算3+5等于多少"))
    
    # print(agent.generate_response("你是谁"))
    # answer = agent.rag("D:\\learn_AI\\small_agent\\rag\\南瓜书.pdf", "南瓜书的作者是谁？")
    # print(answer) 