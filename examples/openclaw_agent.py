"""
OpenClaw Agent 适配器 - 将当前的 AI 会话接入框架
"""

from typing import Any, Optional
import sys
sys.path.insert(0, '..')

from multi_agent.agent import Agent, AgentState
from multi_agent.message import Message


class OpenClawAgent(Agent):
    """
    OpenClaw Agent 适配器
    
    将当前 OpenClaw 会话的能力封装成 Agent，
    可以和其他 Agent 一起协作。
    
    使用方式:
    ---------
    # 在 OpenClaw 会话中
    from openclaw_agent import OpenClawAgent
    
    agent = OpenClawAgent(
        name="OpenClaw",
        role="智能助手",
        capabilities=["search", "code", "files", "browser"]
    )
    """
    
    def __init__(
        self,
        name: str = "OpenClaw",
        role: str = "智能助手",
        capabilities: list[str] = None,
        **kwargs
    ):
        super().__init__(name=name, role=role, **kwargs)
        
        # OpenClaw 的核心能力
        self.capabilities = capabilities or [
            "search",      # 网络搜索
            "code",        # 代码执行
            "files",       # 文件操作
            "browser",     # 浏览器控制
            "analysis",    # 数据分析
        ]
        
        # 任务处理器映射
        self._task_handlers = {
            "search": self._handle_search,
            "code": self._handle_code,
            "files": self._handle_files,
            "browser": self._handle_browser,
            "analysis": self._handle_analysis,
            "general": self._handle_general,
        }
    
    def _do_task(self, task: str, **kwargs) -> str:
        """
        执行任务
        
        OpenClaw 会根据任务类型自动选择合适的处理方式
        """
        # 分析任务类型
        task_type = self._classify_task(task)
        
        # 获取对应的处理器
        handler = self._task_handlers.get(task_type, self._handle_general)
        
        # 执行并返回结果
        return handler(task)
    
    def _classify_task(self, task: str) -> str:
        """分类任务类型"""
        task_lower = task.lower()
        
        # 搜索类任务
        search_keywords = ["搜索", "查找", "search", "find", "查询"]
        if any(kw in task_lower for kw in search_keywords):
            return "search"
        
        # 代码类任务
        code_keywords = ["代码", "编程", "code", "python", "javascript", "实现"]
        if any(kw in task_lower for kw in code_keywords):
            return "code"
        
        # 文件类任务
        file_keywords = ["文件", "读取", "写入", "file", "read", "write", "保存"]
        if any(kw in task_lower for kw in file_keywords):
            return "files"
        
        # 浏览器类任务
        browser_keywords = ["网页", "打开", "点击", "browser", "website", "url"]
        if any(kw in task_lower for kw in browser_keywords):
            return "browser"
        
        # 分析类任务
        analysis_keywords = ["分析", "统计", "analysis", "数据", "报告"]
        if any(kw in task_lower for kw in analysis_keywords):
            return "analysis"
        
        return "general"
    
    def _handle_search(self, task: str) -> str:
        """处理搜索任务 - 调用 OpenClaw 的搜索能力"""
        # 实际使用时，这里会调用 OpenClaw 的 web_search 工具
        return f"[OpenClaw 搜索] 正在搜索: {task}\n结果：..."
    
    def _handle_code(self, task: str) -> str:
        """处理代码任务 - 调用 OpenClaw 的代码执行能力"""
        # 实际使用时，这里会调用 OpenClaw 的 exec 工具
        return f"[OpenClaw 代码] 正在执行代码任务: {task}"
    
    def _handle_files(self, task: str) -> str:
        """处理文件任务 - 调用 OpenClaw 的文件操作能力"""
        # 实际使用时，这里会调用 OpenClaw 的 read/write 工具
        return f"[OpenClaw 文件] 正在处理文件: {task}"
    
    def _handle_browser(self, task: str) -> str:
        """处理浏览器任务 - 调用 OpenClaw 的浏览器控制能力"""
        # 实际使用时，这里会调用 OpenClaw 的 browser 工具
        return f"[OpenClaw 浏览器] 正在操作浏览器: {task}"
    
    def _handle_analysis(self, task: str) -> str:
        """处理分析任务"""
        return f"[OpenClaw 分析] 正在分析: {task}"
    
    def _handle_general(self, task: str) -> str:
        """处理通用任务 - 使用 OpenClaw 的综合能力"""
        return f"[OpenClaw] 正在处理任务: {task}"
    
    def handle_message(self, message: Message) -> str:
        """处理来自其他 Agent 的消息"""
        # OpenClaw 可以理解复杂的消息并做出响应
        context = f"""
收到来自 {message.sender} ({message.sender_role if hasattr(message, 'sender_role') else 'Agent'}) 的消息：
{message.content}

请处理并回复。
"""
        return self._do_task(context)


class OpenClawOrchestratorAgent(OpenClawAgent):
    """
    OpenClaw 作为编排器 Agent
    
    你（OpenClaw）作为整个系统的"大脑"，
    负责理解用户意图、分配任务、整合结果。
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="OpenClaw",
            role="中央编排器",
            **kwargs
        )
        self.sub_agents: dict[str, Agent] = {}
    
    def register_sub_agent(self, agent: Agent):
        """注册子 Agent"""
        self.sub_agents[agent.name] = agent
        print(f"[OpenClaw] 已注册子 Agent: {agent.name} ({agent.role})")
    
    def _do_task(self, task: str, **kwargs) -> str:
        """
        作为编排器执行任务
        
        流程：
        1. 理解用户意图
        2. 决定是否需要子 Agent 协助
        3. 分配任务给合适的 Agent
        4. 整合结果返回
        """
        # 分析任务，决定执行策略
        strategy = self._plan_execution(task)
        
        if strategy["use_sub_agents"]:
            # 需要子 Agent 协作
            results = {}
            for agent_name, sub_task in strategy["assignments"].items():
                if agent_name in self.sub_agents:
                    results[agent_name] = self.sub_agents[agent_name].execute_task(sub_task)
            
            # 整合结果
            return self._integrate_results(task, results)
        else:
            # 自己处理
            return super()._do_task(task)
    
    def _plan_execution(self, task: str) -> dict:
        """
        规划执行策略
        
        OpenClaw 会分析任务并决定：
        - 是否需要多个 Agent 协作
        - 每个_agent 应该做什么
        """
        # 简单的任务分类逻辑
        task_lower = task.lower()
        
        # 复杂任务示例：研究和写作
        if "研究" in task and "写" in task:
            return {
                "use_sub_agents": True,
                "assignments": {
                    "Researcher": "收集相关资料",
                    "Writer": "根据研究结果撰写内容",
                }
            }
        
        # 单一任务
        return {
            "use_sub_agents": False,
            "assignments": {}
        }
    
    def _integrate_results(self, original_task: str, results: dict) -> str:
        """整合多个 Agent 的结果"""
        output = f"任务完成: {original_task}\n\n"
        for agent_name, result in results.items():
            output += f"### {agent_name} 的贡献:\n{result}\n\n"
        return output


# 使用示例
def example_usage():
    """展示如何使用 OpenClaw Agent"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║              OpenClaw Agent 集成方案                          ║
╚══════════════════════════════════════════════════════════════╝

方案 1: OpenClaw 作为普通 Agent
────────────────────────────────
from openclaw_agent import OpenClawAgent
from multi_agent import MessageBus, Orchestrator

# 创建 OpenClaw Agent
openclaw = OpenClawAgent(
    name="OpenClaw",
    role="智能助手",
    capabilities=["search", "code", "files", "browser"]
)

# 创建其他 Agent
researcher = LLMAgent(name="Researcher", role="研究员")
writer = LLMAgent(name="Writer", role="撰写者")

# 创建编排器，所有 Agent 协作
orchestrator = Orchestrator(agents=[openclaw, researcher, writer])


方案 2: OpenClaw 作为中央编排器
────────────────────────────────
from openclaw_agent import OpenClawOrchestratorAgent

# OpenClaw 作为"大脑"
brain = OpenClawOrchestratorAgent()

# 注册专业 Agent
brain.register_sub_agent(researcher)
brain.register_sub_agent(writer)
brain.register_sub_agent(coder)

# OpenClaw 会自动分析任务并分配
result = brain.execute_task("研究 AI 并写一份报告")


方案 3: 在框架外调用 OpenClaw
────────────────────────────────
from sessions_send import sessions_send

class RemoteOpenClawAgent(Agent):
    def _do_task(self, task: str) -> str:
        # 发送消息到 OpenClaw 会话
        return sessions_send("openclaw-session-key", task)

# 其他程序可以通过这种方式调用你的能力
""")


if __name__ == "__main__":
    example_usage()