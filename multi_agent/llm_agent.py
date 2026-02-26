"""
LLM Agent 实现 - 接入真实的 LLM API
"""

import os
import json
from typing import Any, Optional, Callable, List, Dict
from dataclasses import dataclass

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

from .agent import Agent, AgentConfig, AgentState
from .message import Message
from .tools import Tool


@dataclass
class LLMAgentConfig(AgentConfig):
    """LLM Agent 配置"""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    system_prompt: str = ""


class LLMAgent(Agent):
    """
    LLM Agent - 连接真实的大语言模型
    
    支持:
    - OpenAI API (GPT-4, GPT-3.5)
    - Anthropic API (Claude)
    - 自定义 API 端点
    """
    
    def __init__(
        self,
        name: str,
        role: str,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        super().__init__(name=name, role=role, **kwargs)
        
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url
        self.system_prompt = system_prompt or f"你是{name}，一个{role}。"
        
        # 初始化客户端
        self._client = None
        self._init_client()
        
        # 对话历史
        self.conversation_history: List[Dict] = []
    
    def _init_client(self):
        """初始化 LLM 客户端"""
        if "claude" in self.model.lower():
            if HAS_ANTHROPIC and self.api_key:
                self._client = anthropic.Anthropic(api_key=self.api_key)
                self._provider = "anthropic"
        else:
            if HAS_OPENAI:
                client_kwargs = {"api_key": self.api_key}
                if self.base_url:
                    client_kwargs["base_url"] = self.base_url
                self._client = OpenAI(**client_kwargs)
                self._provider = "openai"
    
    def _do_task(self, task: str, **kwargs) -> str:
        """执行任务 - 调用 LLM"""
        if not self._client:
            return f"[{self.name}] 错误：LLM 客户端未初始化"
        
        # 构建消息
        messages = self._build_messages(task)
        
        try:
            if self._provider == "anthropic":
                response = self._client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=self.system_prompt,
                    messages=messages,
                )
                result = response.content[0].text
            else:
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                )
                result = response.choices[0].message.content
            
            # 保存到对话历史
            self.conversation_history.append({"role": "user", "content": task})
            self.conversation_history.append({"role": "assistant", "content": result})
            
            return result
            
        except Exception as e:
            return f"[{self.name}] 调用 LLM 失败: {e}"
    
    def _build_messages(self, user_input: str) -> List[Dict]:
        """构建消息列表"""
        messages = []
        
        # 添加历史对话（保留最近 10 轮）
        for msg in self.conversation_history[-20:]:
            messages.append(msg)
        
        # 添加当前输入
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    def handle_message(self, message: Message) -> str:
        """处理收到的消息"""
        # 将消息转换为任务
        task = f"收到来自 {message.sender} 的消息: {message.content}"
        return self._do_task(task)
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history.clear()
    
    def set_system_prompt(self, prompt: str):
        """设置系统提示"""
        self.system_prompt = prompt


class ToolEnabledAgent(LLMAgent):
    """
    支持工具调用的 LLM Agent
    
    可以调用注册的工具来完成任务
    """
    
    def _do_task(self, task: str, **kwargs) -> str:
        """执行任务 - 支持工具调用"""
        if not self._client or self._provider != "openai":
            return super()._do_task(task)
        
        messages = self._build_messages(task)
        
        # 获取工具定义
        tools = self.tools.to_openai_tools() if self.tools.tools else None
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
            )
            
            message = response.choices[0].message
            
            # 检查是否需要调用工具
            if message.tool_calls:
                # 执行工具调用
                tool_results = []
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    # 执行工具
                    result = self.tools.execute(tool_name, **tool_args)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_name,
                        "content": str(result),
                    })
                
                # 将工具结果发回 LLM
                messages.append(message)
                messages.extend(tool_results)
                
                # 获取最终响应
                final_response = self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                )
                return final_response.choices[0].message.content
            
            return message.content
            
        except Exception as e:
            return f"[{self.name}] 执行失败: {e}"


# 预定义的专家 Agent 模板
def create_researcher_agent(api_key: str, model: str = "gpt-4") -> ToolEnabledAgent:
    """创建研究员 Agent"""
    agent = ToolEnabledAgent(
        name="Researcher",
        role="研究员",
        model=model,
        api_key=api_key,
        system_prompt="""你是一个专业的研究员。你的职责是：
1. 搜索和收集相关信息
2. 分析和整理数据
3. 提供客观的研究报告

请始终保持专业和客观。""",
    )
    
    # 注册工具
    def search_tool(query: str) -> str:
        return f"搜索结果：{query}"
    
    agent.register_tool("search", search_tool, "搜索互联网信息")
    
    return agent


def create_writer_agent(api_key: str, model: str = "gpt-4") -> LLMAgent:
    """创建撰写者 Agent"""
    return LLMAgent(
        name="Writer",
        role="撰写者",
        model=model,
        api_key=api_key,
        system_prompt="""你是一个专业的内容撰写者。你的职责是：
1. 根据研究材料撰写文章
2. 确保内容清晰、有逻辑
3. 使用恰当的语言风格

请创作高质量的内容。""",
    )


def create_coder_agent(api_key: str, model: str = "gpt-4") -> ToolEnabledAgent:
    """创建程序员 Agent"""
    agent = ToolEnabledAgent(
        name="Coder",
        role="程序员",
        model=model,
        api_key=api_key,
        system_prompt="""你是一个专业的程序员。你的职责是：
1. 编写高质量代码
2. 解决技术问题
3. 代码审查和优化

请遵循最佳实践。""",
    )
    
    # 注册代码执行工具
    def run_code(code: str) -> str:
        try:
            exec_globals = {}
            exec(code, exec_globals)
            return "代码执行成功"
        except Exception as e:
            return f"执行错误: {e}"
    
    agent.register_tool("run_code", run_code, "执行 Python 代码")
    
    return agent