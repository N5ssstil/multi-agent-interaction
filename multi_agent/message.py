"""
消息系统 - Agent 之间的通信机制
"""

from typing import Any, Optional, List, Dict, Callable, List, Dict, Callable
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Message:
    """
    消息对象
    
    用于 Agent 之间的通信
    """
    sender: str
    receiver: str
    content: Any
    msg_type: str = "text"  # text, task, result, control
    metadata: dict = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "type": self.msg_type,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        return cls(
            id=data.get("id"),
            sender=data["sender"],
            receiver=data["receiver"],
            content=data["content"],
            msg_type=data.get("type", "text"),
            metadata=data.get("metadata", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


class MessageBus:
    """
    消息总线
    
    负责 Agent 之间的消息路由
    """
    
    def __init__(self):
        self.agents: Dict[str, "Agent"] = {}  # type: ignore
        self.history: List[Message] = []
        self.hooks: List[Callable] = []
    
    def register(self, agent: "Agent") -> None:  # type: ignore
        """注册 Agent"""
        self.agents[agent.name] = agent
        print(f"[MessageBus] Agent '{agent.name}' 已注册")
    
    def unregister(self, agent_name: str) -> None:
        """注销 Agent"""
        if agent_name in self.agents:
            del self.agents[agent_name]
            print(f"[MessageBus] Agent '{agent_name}' 已注销")
    
    def send(self, message: Message) -> bool:
        """发送消息给指定 Agent"""
        self.history.append(message)
        
        # 触发钩子
        for hook in self.hooks:
            hook(message)
        
        if message.receiver in self.agents:
            self.agents[message.receiver].receive(message)
            return True
        
        print(f"[MessageBus] 警告：未找到接收者 '{message.receiver}'")
        return False
    
    def broadcast(self, message: Message) -> None:
        """广播消息给所有 Agent（除发送者外）"""
        self.history.append(message)
        
        for hook in self.hooks:
            hook(message)
        
        for name, agent in self.agents.items():
            if name != message.sender:
                agent.receive(message)
    
    def add_hook(self, hook: Callable) -> None:
        """添加消息钩子"""
        self.hooks.append(hook)
    
    def get_history(self, agent_name: Optional[str] = None) -> List[Message]:
        """获取消息历史"""
        if agent_name:
            return [
                m for m in self.history 
                if m.sender == agent_name or m.receiver == agent_name
            ]
        return self.history.copy()
    
    def clear_history(self) -> None:
        """清空消息历史"""
        self.history.clear()
    
    def __repr__(self) -> str:
        return f"MessageBus(agents={list(self.agents.keys())})"