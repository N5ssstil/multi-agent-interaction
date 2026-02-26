"""
展示如何将真实的 LLM Agent 接入框架
"""

import sys
sys.path.insert(0, '..')

import os
from multi_agent import MessageBus, Orchestrator
from multi_agent.llm_agent import (
    LLMAgent, 
    ToolEnabledAgent,
    create_researcher_agent,
    create_writer_agent,
    create_coder_agent,
)


def example_basic_llm_agent():
    """示例：基础 LLM Agent"""
    print("\n" + "="*50)
    print("示例：基础 LLM Agent")
    print("="*50)
    
    # 从环境变量获取 API Key
    api_key = os.getenv("OPENAI_API_KEY", "your-api-key")
    
    # 创建 LLM Agent
    agent = LLMAgent(
        name="Assistant",
        role="AI 助手",
        model="gpt-4",
        api_key=api_key,
        system_prompt="你是一个友好的 AI 助手。",
    )
    
    # 执行任务
    result = agent.execute_task("请用一句话介绍你自己")
    print(f"\n响应: {result}")


def example_tool_enabled_agent():
    """示例：支持工具调用的 Agent"""
    print("\n" + "="*50)
    print("示例：支持工具调用的 Agent")
    print("="*50)
    
    api_key = os.getenv("OPENAI_API_KEY", "your-api-key")
    
    agent = ToolEnabledAgent(
        name="Helper",
        role="智能助手",
        model="gpt-4",
        api_key=api_key,
    )
    
    # 注册自定义工具
    def get_weather(city: str) -> str:
        """获取天气信息"""
        # 这里可以接入真实的天气 API
        return f"{city} 今天晴天，温度 25°C"
    
    agent.register_tool("get_weather", get_weather, "获取指定城市的天气")
    
    # 执行任务
    result = agent.execute_task("北京今天天气怎么样？")
    print(f"\n响应: {result}")


def example_multi_agent_collaboration():
    """示例：多个 LLM Agent 协作"""
    print("\n" + "="*50)
    print("示例：多个 LLM Agent 协作")
    print("="*50)
    
    api_key = os.getenv("OPENAI_API_KEY", "your-api-key")
    
    # 创建消息总线
    bus = MessageBus()
    
    # 创建专业 Agent
    researcher = create_researcher_agent(api_key)
    researcher.message_bus = bus
    bus.register(researcher)
    
    writer = create_writer_agent(api_key)
    writer.message_bus = bus
    bus.register(writer)
    
    # 创建编排器
    orchestrator = Orchestrator(agents=[researcher, writer])
    
    # 执行协作任务
    print("\n执行协作任务：写一篇关于 AI 的短文")
    
    # 1. 研究员收集信息
    research_result = researcher.execute_task("研究 AI 的最新发展，列出 3 个关键点")
    print(f"\n[研究员] 研究结果:\n{research_result[:200]}...")
    
    # 2. 撰写者根据研究结果写作
    writer_task = f"根据以下研究结果写一段简短的介绍:\n{research_result}"
    article = writer.execute_task(writer_task)
    print(f"\n[撰写者] 文章:\n{article[:200]}...")


def example_custom_agent():
    """示例：自定义 Agent"""
    print("\n" + "="*50)
    print("示例：自定义 Agent")
    print("="*50)
    
    api_key = os.getenv("OPENAI_API_KEY", "your-api-key")
    
    class MyCustomAgent(LLMAgent):
        """自定义 Agent 示例"""
        
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.specialty = "Python 编程"
        
        def _do_task(self, task: str, **kwargs) -> str:
            # 添加自定义预处理
            enhanced_task = f"作为{self.specialty}专家，请回答：{task}"
            return super()._do_task(enhanced_task)
    
    agent = MyCustomAgent(
        name="PythonExpert",
        role="Python 专家",
        api_key=api_key,
    )
    
    result = agent.execute_task("什么是装饰器？")
    print(f"\n响应: {result[:200]}...")


def example_openclaw_integration():
    """
    示例：将 OpenClaw Agent 接入框架
    
    这个示例展示如何将你当前对话的 AI（OpenClaw）
    封装成一个 Agent 接入到框架中
    """
    print("\n" + "="*50)
    print("示例：OpenClaw Agent 集成方案")
    print("="*50)
    
    # 方案 1: 通过 API 代理
    print("""
方案 1: 通过 API 代理
    
    ┌─────────────┐      HTTP API      ┌─────────────┐
    │   框架中的   │ ──────────────────► │  OpenClaw   │
    │ LLMAgent    │                     │   Server    │
    └─────────────┘ ◄────────────────── └─────────────┘
    
    代码示例:
    
    agent = LLMAgent(
        name="OpenClaw",
        role="智能助手",
        model="custom",
        base_url="http://localhost:8080/v1",  # OpenClaw API 端点
        api_key="your-openclaw-token",
    )
    """)
    
    # 方案 2: 直接使用当前会话
    print("""
方案 2: 直接使用当前会话
    
    创建一个 OpenClawAgent 类，将当前会话的能力封装：
    
    class OpenClawAgent(Agent):
        def __init__(self, session_key: str):
            self.session_key = session_key
        
        def _do_task(self, task: str) -> str:
            # 调用 sessions_send 发送消息到 OpenClaw
            from openclaw import sessions_send
            return sessions_send(self.session_key, task)
    """)
    
    # 方案 3: 作为 Orchestrator 的中央大脑
    print("""
方案 3: 作为中央大脑
    
    你（OpenClaw）作为 Orchestrator 的决策中心：
    
    ┌────────────────────────────────────────┐
    │          OpenClaw (Orchestrator)        │
    │  - 理解用户意图                          │
    │  - 分配任务给专业 Agent                  │
    │  - 整合结果                              │
    └────────────────────────────────────────┘
            │           │           │
        ┌───▼───┐   ┌───▼───┐   ┌───▼───┐
        │Agent A│   │Agent B│   │Agent C│
        └───────┘   └───────┘   └───────┘
    """)


if __name__ == "__main__":
    print("\n🤖 LLM Agent 集成示例")
    print("=" * 50)
    
    # 检查 API Key
    if os.getenv("OPENAI_API_KEY"):
        # 有 API Key，运行真实示例
        example_basic_llm_agent()
        example_tool_enabled_agent()
        example_multi_agent_collaboration()
    else:
        # 无 API Key，显示集成方案
        print("\n⚠️ 未设置 OPENAI_API_KEY，显示集成方案...")
        example_openclaw_integration()
    
    print("\n\n✅ 示例完成！")