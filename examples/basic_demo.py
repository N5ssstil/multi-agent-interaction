"""
Multi-Agent 交互示例
演示如何创建和使用多个 Agent 进行协作
"""

import sys
sys.path.insert(0, '..')

from multi_agent import Agent, Orchestrator, MessageBus


class ResearcherAgent(Agent):
    """研究员 Agent - 负责收集信息"""
    
    def _do_task(self, task: str, **kwargs) -> str:
        print(f"[{self.name}] 正在研究: {task}")
        # 这里可以集成实际的搜索/研究逻辑
        result = f"关于'{task}'的研究结果：\n1. 核心概念...\n2. 相关技术...\n3. 应用场景..."
        return result


class WriterAgent(Agent):
    """撰写者 Agent - 负责内容创作"""
    
    def _do_task(self, task: str, **kwargs) -> str:
        print(f"[{self.name}] 正在撰写: {task}")
        # 这里可以集成实际的写作逻辑
        result = f"文章草稿：\n\n# {task}\n\n基于研究结果，本文将探讨..."
        return result


class ReviewerAgent(Agent):
    """审核者 Agent - 负责审核和改进"""
    
    def _do_task(self, task: str, **kwargs) -> str:
        print(f"[{self.name}] 正在审核: {task[:50]}...")
        # 这里可以集成实际的审核逻辑
        feedback = f"审核反馈：\n- 结构清晰\n- 建议增加实例\n- 结论需要加强"
        return feedback


def example_basic_communication():
    """示例1：基础 Agent 通信"""
    print("\n" + "="*50)
    print("示例1：基础 Agent 通信")
    print("="*50)
    
    # 创建消息总线
    bus = MessageBus()
    
    # 创建两个 Agent
    alice = Agent(name="Alice", role="助手", message_bus=bus)
    bob = Agent(name="Bob", role="分析师", message_bus=bus)
    
    # Alice 发送消息给 Bob
    alice.send_to("Bob", "你好，请帮我分析一下今天的任务")
    
    # Bob 处理收件箱
    bob.process_inbox()
    
    print(f"\n消息历史: {len(bus.history)} 条消息")


def example_task_orchestration():
    """示例2：任务编排"""
    print("\n" + "="*50)
    print("示例2：任务编排")
    print("="*50)
    
    # 创建专业 Agent
    researcher = ResearcherAgent(
        name="Researcher",
        role="研究员",
        description="负责收集和分析信息"
    )
    
    writer = WriterAgent(
        name="Writer",
        role="撰写者", 
        description="负责内容创作"
    )
    
    reviewer = ReviewerAgent(
        name="Reviewer",
        role="审核者",
        description="负责内容审核"
    )
    
    # 创建编排器
    orchestrator = Orchestrator(agents=[researcher, writer, reviewer])
    
    # 查看状态
    print(f"\n编排器状态: {orchestrator.get_status()}")
    
    # 执行顺序任务流
    print("\n--- 顺序执行任务流 ---")
    results = orchestrator.run_sequence([
        ("Researcher", "AI Agent 框架"),
        ("Writer", "基于研究结果撰写文章"),
        ("Reviewer", "审核文章质量"),
    ])
    
    for agent_name, result in results:
        print(f"\n[{agent_name}] 结果:\n{result[:100]}...")


def example_parallel_tasks():
    """示例3：并行任务执行"""
    print("\n" + "="*50)
    print("示例3：并行任务执行")
    print("="*50)
    
    # 创建多个研究员
    researchers = [
        ResearcherAgent(name=f"Researcher{i}", role="研究员")
        for i in range(1, 4)
    ]
    
    # 创建编排器
    orchestrator = Orchestrator(agents=researchers)
    
    # 并行执行多个研究任务
    tasks = [
        ("Researcher1", "机器学习基础"),
        ("Researcher2", "深度学习应用"),
        ("Researcher3", "自然语言处理"),
    ]
    
    print("\n并行执行研究任务...")
    results = orchestrator.run_parallel(tasks)
    
    for agent, result in results.items():
        print(f"\n[{agent}] 完成: {result[:50]}...")


def example_broadcast():
    """示例4：广播消息"""
    print("\n" + "="*50)
    print("示例4：广播消息")
    print("="*50)
    
    bus = MessageBus()
    
    # 创建多个 Agent
    agents = [
        Agent(name=f"Agent{i}", role="成员", message_bus=bus)
        for i in range(1, 4)
    ]
    
    # Agent1 广播消息
    agents[0].broadcast("大家好，会议将在 10 分钟后开始！")
    
    # 所有 Agent 处理消息
    for agent in agents[1:]:
        agent.process_inbox()


if __name__ == "__main__":
    print("\n🤖 Multi-Agent Interaction 演示")
    print("=" * 50)
    
    # 运行所有示例
    example_basic_communication()
    example_task_orchestration()
    example_parallel_tasks()
    example_broadcast()
    
    print("\n\n✅ 演示完成！")