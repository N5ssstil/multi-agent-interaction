"""
Agent 基类 - 定义智能代理的核心接口
"""

from typing import Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid
import time

from .message import Message, MessageBus
from .memory import Memory
from .tools import ToolRegistry


class AgentState(Enum):
    """Agent 状态"""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"


@dataclass
class AgentConfig:
    """Agent 配置"""
    name: str
    role: str
    description: str = ""
    model: str = "gpt-4"
    max_tokens: int = 4096
    temperature: float = 0.7
    tools: list[str] = field(default_factory=list)


class Agent:
    """
    智能代理基类
    
    每个 Agent 都有：
    - 唯一标识
    - 角色和能力描述
    - 记忆系统
    - 工具集
    - 通信能力
    """
    
    def __init__(
        self,
        name: str,
        role: str,
        description: str = "",
        message_bus: Optional[MessageBus] = None,
        config: Optional[AgentConfig] = None,
    ):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.role = role
        self.description = description
        self.message_bus = message_bus
        self.state = AgentState.IDLE
        self.memory = Memory(agent_id=self.id)
        self.tools = ToolRegistry()
        self.inbox: list[Message] = []
        
        # 配置
        self.config = config or AgentConfig(
            name=name, 
            role=role, 
            description=description
        )
        
        # 注册到消息总线
        if self.message_bus:
            self.message_bus.register(self)
    
    def receive(self, message: Message) -> None:
        """接收消息"""
        self.inbox.append(message)
        self.memory.add_message(message)
        print(f"[{self.name}] 收到来自 {message.sender} 的消息")
    
    def send_to(self, target: str, content: Any, msg_type: str = "text") -> bool:
        """发送消息给指定 Agent"""
        if not self.message_bus:
            raise RuntimeError("未连接到消息总线")
        
        message = Message(
            sender=self.name,
            receiver=target,
            content=content,
            msg_type=msg_type,
        )
        self.message_bus.send(message)
        self.memory.add_message(message)
        return True
    
    def broadcast(self, content: Any, msg_type: str = "text") -> None:
        """广播消息给所有 Agent"""
        if not self.message_bus:
            raise RuntimeError("未连接到消息总线")
        
        message = Message(
            sender=self.name,
            receiver="all",
            content=content,
            msg_type=msg_type,
        )
        self.message_bus.broadcast(message)
    
    def process_inbox(self) -> list[Message]:
        """处理收件箱中的消息"""
        processed = []
        while self.inbox:
            msg = self.inbox.pop(0)
            response = self.handle_message(msg)
            processed.append(msg)
            if response:
                self.send_to(msg.sender, response)
        return processed
    
    def handle_message(self, message: Message) -> Any:
        """
        处理消息的入口点
        子类应该重写此方法实现具体逻辑
        """
        return f"[{self.name}] 已收到您的消息：{message.content}"
    
    def execute_task(self, task: str, **kwargs) -> Any:
        """
        执行任务
        子类应该重写此方法
        """
        self.state = AgentState.WORKING
        try:
            result = self._do_task(task, **kwargs)
            self.state = AgentState.IDLE
            return result
        except Exception as e:
            self.state = AgentState.ERROR
            raise e
    
    def _do_task(self, task: str, **kwargs) -> Any:
        """实际执行任务的内部方法"""
        raise NotImplementedError("子类需要实现 _do_task 方法")
    
    def register_tool(self, name: str, func: Callable, description: str = "") -> None:
        """注册工具"""
        self.tools.register(name, func, description)
    
    def __repr__(self) -> str:
        return f"Agent(name={self.name}, role={self.role}, state={self.state.value})"