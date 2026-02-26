"""
测试 Agent 基础功能
"""

import pytest
import sys
sys.path.insert(0, '..')

from multi_agent import Agent, MessageBus, Orchestrator


class TestAgent:
    """测试 Agent 类"""
    
    def test_agent_creation(self):
        """测试 Agent 创建"""
        agent = Agent(name="TestAgent", role="测试")
        assert agent.name == "TestAgent"
        assert agent.role == "测试"
    
    def test_agent_send_message(self):
        """测试 Agent 发送消息"""
        bus = MessageBus()
        alice = Agent(name="Alice", role="A", message_bus=bus)
        bob = Agent(name="Bob", role="B", message_bus=bus)
        
        alice.send_to("Bob", "Hello")
        assert len(bob.inbox) == 1
    
    def test_agent_broadcast(self):
        """测试 Agent 广播"""
        bus = MessageBus()
        agents = [
            Agent(name=f"Agent{i}", role="R", message_bus=bus)
            for i in range(3)
        ]
        
        agents[0].broadcast("广播消息")
        
        # 其他 Agent 应该收到消息
        assert len(agents[1].inbox) == 1
        assert len(agents[2].inbox) == 1


class TestMessageBus:
    """测试消息总线"""
    
    def test_message_bus_creation(self):
        """测试消息总线创建"""
        bus = MessageBus()
        assert len(bus.agents) == 0
    
    def test_agent_registration(self):
        """测试 Agent 注册"""
        bus = MessageBus()
        agent = Agent(name="Test", role="R")
        bus.register(agent)
        
        assert "Test" in bus.agents
    
    def test_message_history(self):
        """测试消息历史"""
        bus = MessageBus()
        alice = Agent(name="Alice", role="A", message_bus=bus)
        bob = Agent(name="Bob", role="B", message_bus=bus)
        
        alice.send_to("Bob", "Test message")
        
        history = bus.get_history()
        assert len(history) == 1


class TestOrchestrator:
    """测试编排器"""
    
    def test_orchestrator_creation(self):
        """测试编排器创建"""
        orc = Orchestrator()
        assert len(orc.agents) == 0
    
    def test_add_agent(self):
        """测试添加 Agent"""
        orc = Orchestrator()
        agent = Agent(name="Test", role="R")
        orc.add_agent(agent)
        
        assert "Test" in orc.agents
    
    def test_get_status(self):
        """测试获取状态"""
        orc = Orchestrator()
        agent = Agent(name="Test", role="R")
        orc.add_agent(agent)
        
        status = orc.get_status()
        assert "agents" in status
        assert "Test" in status["agents"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])