"""
编排器 - 协调多个 Agent 完成复杂任务
"""

from typing import Optional
from dataclasses import dataclass
from enum import Enum
import time

from .agent import Agent, AgentState
from .message import MessageBus


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """任务对象"""
    id: str
    description: str
    assigned_to: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    result: any = None
    error: Optional[str] = None


class Orchestrator:
    """
    任务编排器
    
    负责：
    - 任务分解
    - Agent 分配
    - 执行调度
    - 结果聚合
    """
    
    def __init__(self, agents: Optional[list[Agent]] = None):
        self.agents: dict[str, Agent] = {}
        self.message_bus = MessageBus()
        self.tasks: list[Task] = []
        
        # 注册 Agent
        if agents:
            for agent in agents:
                self.add_agent(agent)
    
    def add_agent(self, agent: Agent) -> None:
        """添加 Agent"""
        if not agent.message_bus:
            agent.message_bus = self.message_bus
        self.agents[agent.name] = agent
        self.message_bus.register(agent)
    
    def create_task(self, description: str, assign_to: Optional[str] = None) -> Task:
        """创建任务"""
        import uuid
        task = Task(
            id=str(uuid.uuid4())[:8],
            description=description,
            assigned_to=assign_to,
        )
        self.tasks.append(task)
        return task
    
    def run(self, task_description: str, strategy: str = "auto") -> any:
        """
        执行任务
        
        Args:
            task_description: 任务描述
            strategy: 执行策略
                - auto: 自动选择最合适的 Agent
                - round_robin: 轮询分配
                - broadcast: 广播给所有 Agent
        """
        print(f"\n[Orchestrator] 开始执行任务: {task_description}")
        
        if strategy == "broadcast":
            return self._broadcast_task(task_description)
        elif strategy == "round_robin":
            return self._round_robin_task(task_description)
        else:
            return self._auto_assign(task_description)
    
    def _auto_assign(self, task_description: str) -> any:
        """自动分配任务给最合适的 Agent"""
        # 简单实现：选择空闲的 Agent
        for agent in self.agents.values():
            if agent.state == AgentState.IDLE:
                print(f"[Orchestrator] 将任务分配给 {agent.name}")
                return agent.execute_task(task_description)
        
        print("[Orchestrator] 警告：没有可用的 Agent")
        return None
    
    def _round_robin_task(self, task_description: str) -> any:
        """轮询分配任务"""
        if not self.agents:
            return None
        
        # 简单轮询
        agent_names = list(self.agents.keys())
        last_idx = getattr(self, "_rr_index", 0)
        agent_name = agent_names[last_idx % len(agent_names)]
        self._rr_index = last_idx + 1
        
        agent = self.agents[agent_name]
        print(f"[Orchestrator] 轮询分配给 {agent.name}")
        return agent.execute_task(task_description)
    
    def _broadcast_task(self, task_description: str) -> dict:
        """广播任务给所有 Agent"""
        results = {}
        for name, agent in self.agents.items():
            print(f"[Orchestrator] 广播任务给 {name}")
            results[name] = agent.execute_task(task_description)
        return results
    
    def run_parallel(self, tasks: list[tuple[str, str]]) -> dict:
        """
        并行执行多个任务
        
        Args:
            tasks: [(agent_name, task_description), ...]
        """
        import concurrent.futures
        
        results = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {}
            for agent_name, task_desc in tasks:
                if agent_name in self.agents:
                    agent = self.agents[agent_name]
                    future = executor.submit(agent.execute_task, task_desc)
                    futures[future] = agent_name
            
            for future in concurrent.futures.as_completed(futures):
                agent_name = futures[future]
                try:
                    results[agent_name] = future.result()
                except Exception as e:
                    results[agent_name] = f"Error: {e}"
        
        return results
    
    def run_sequence(self, tasks: list[tuple[str, str]]) -> list:
        """
        顺序执行多个任务
        
        Args:
            tasks: [(agent_name, task_description), ...]
        """
        results = []
        for agent_name, task_desc in tasks:
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                result = agent.execute_task(task_desc)
                results.append((agent_name, result))
            else:
                results.append((agent_name, f"Error: Agent '{agent_name}' not found"))
        return results
    
    def get_status(self) -> dict:
        """获取编排器状态"""
        return {
            "agents": {
                name: {
                    "role": agent.role,
                    "state": agent.state.value,
                }
                for name, agent in self.agents.items()
            },
            "tasks_count": len(self.tasks),
            "message_history_count": len(self.message_bus.history),
        }
    
    def __repr__(self) -> str:
        return f"Orchestrator(agents={list(self.agents.keys())})"