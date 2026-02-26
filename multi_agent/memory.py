"""
记忆系统 - Agent 的记忆和状态管理
"""

from typing import Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class MemoryEntry:
    """记忆条目"""
    content: Any
    entry_type: str = "general"  # general, message, task, observation
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)


class Memory:
    """
    Agent 记忆系统
    
    支持短期记忆和长期记忆
    """
    
    def __init__(self, agent_id: str, max_short_term: int = 100):
        self.agent_id = agent_id
        self.max_short_term = max_short_term
        
        # 短期记忆（最近的活动）
        self.short_term: list[MemoryEntry] = []
        
        # 长期记忆（重要信息）
        self.long_term: list[MemoryEntry] = []
    
    def add(self, content: Any, entry_type: str = "general", **metadata) -> None:
        """添加记忆"""
        entry = MemoryEntry(
            content=content,
            entry_type=entry_type,
            metadata=metadata,
        )
        self.short_term.append(entry)
        
        # 限制短期记忆大小
        if len(self.short_term) > self.max_short_term:
            # 将最旧的移入长期记忆
            oldest = self.short_term.pop(0)
            self.long_term.append(oldest)
    
    def add_message(self, message: Any) -> None:
        """添加消息到记忆"""
        self.add(
            content=message,
            entry_type="message",
        )
    
    def add_observation(self, observation: str) -> None:
        """添加观察"""
        self.add(
            content=observation,
            entry_type="observation",
        )
    
    def get_recent(self, n: int = 10) -> list[MemoryEntry]:
        """获取最近的记忆"""
        return self.short_term[-n:]
    
    def search(self, query: str) -> list[MemoryEntry]:
        """搜索记忆（简单字符串匹配）"""
        results = []
        for entry in self.short_term + self.long_term:
            if isinstance(entry.content, str) and query.lower() in entry.content.lower():
                results.append(entry)
            elif hasattr(entry.content, 'content'):
                if query.lower() in str(entry.content.content).lower():
                    results.append(entry)
        return results
    
    def clear_short_term(self) -> None:
        """清空短期记忆"""
        self.short_term.clear()
    
    def to_dict(self) -> dict:
        """导出为字典"""
        return {
            "agent_id": self.agent_id,
            "short_term": [
                {
                    "content": str(e.content),
                    "type": e.entry_type,
                    "timestamp": e.timestamp.isoformat(),
                }
                for e in self.short_term
            ],
            "long_term_count": len(self.long_term),
        }


class SharedMemory:
    """
    共享记忆
    
    用于多个 Agent 之间共享状态和信息
    """
    
    def __init__(self):
        self.data: dict[str, Any] = {}
        self.history: list[tuple[str, Any, datetime]] = []
    
    def set(self, key: str, value: Any) -> None:
        """设置共享数据"""
        self.data[key] = value
        self.history.append((key, value, datetime.now()))
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取共享数据"""
        return self.data.get(key, default)
    
    def update(self, updates: dict) -> None:
        """批量更新"""
        for key, value in updates.items():
            self.set(key, value)
    
    def delete(self, key: str) -> bool:
        """删除数据"""
        if key in self.data:
            del self.data[key]
            return True
        return False
    
    def keys(self) -> list[str]:
        """获取所有键"""
        return list(self.data.keys())
    
    def get_history(self, key: Optional[str] = None) -> list:
        """获取历史记录"""
        if key:
            return [(k, v, t) for k, v, t in self.history if k == key]
        return self.history.copy()
    
    def to_dict(self) -> dict:
        """导出为字典"""
        return {
            "data": self.data.copy(),
            "keys": self.keys(),
        }