"""
Web API - FastAPI 后端服务
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import asyncio
from datetime import datetime

# 导入核心模块
from multi_agent import Agent, MessageBus, Orchestrator
from multi_agent.llm_agent import LLMAgent, ToolEnabledAgent

app = FastAPI(title="Multi-Agent Interaction", version="0.1.0")

# 静态文件和模板
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# 全局状态
class AppState:
    def __init__(self):
        self.bus = MessageBus()
        self.agents: Dict[str, Agent] = {}
        self.orchestrator = Orchestrator()
        self.messages: List[Dict] = []
        self.websocket_clients: List[WebSocket] = []

state = AppState()


# ============ 数据模型 ============

class AgentCreate(BaseModel):
    name: str
    role: str
    description: Optional[str] = ""
    agent_type: Optional[str] = "basic"  # basic, llm


class MessageSend(BaseModel):
    sender: str
    receiver: str
    content: str


class TaskExecute(BaseModel):
    agent_name: str
    task: str


# ============ 页面路由 ============

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """主页"""
    return templates.TemplateResponse("index.html", {"request": request})


# ============ API 路由 ============

@app.get("/api/agents")
async def list_agents():
    """获取所有 Agent 列表"""
    result = []
    for name, agent in state.agents.items():
        result.append({
            "name": agent.name,
            "role": agent.role,
            "description": agent.description,
            "state": agent.state.value,
            "inbox_count": len(agent.inbox),
        })
    return {"agents": result}


@app.post("/api/agents")
async def create_agent(data: AgentCreate):
    """创建新 Agent"""
    if data.name in state.agents:
        return {"error": "Agent 名称已存在"}
    
    if data.agent_type == "llm":
        agent = LLMAgent(
            name=data.name,
            role=data.role,
            description=data.description,
            message_bus=state.bus,
        )
    else:
        agent = Agent(
            name=data.name,
            role=data.role,
            description=data.description,
            message_bus=state.bus,
        )
    
    state.agents[data.name] = agent
    state.orchestrator.add_agent(agent)
    
    await broadcast_event("agent_created", {
        "name": agent.name,
        "role": agent.role,
        "description": agent.description,
    })
    
    return {"success": True, "agent": {
        "name": agent.name,
        "role": agent.role,
    }}


@app.delete("/api/agents/{name}")
async def delete_agent(name: str):
    """删除 Agent"""
    if name not in state.agents:
        return {"error": "Agent 不存在"}
    
    del state.agents[name]
    state.bus.unregister(name)
    
    await broadcast_event("agent_deleted", {"name": name})
    
    return {"success": True}


@app.get("/api/agents/{name}/history")
async def get_agent_history(name: str):
    """获取 Agent 消息历史"""
    if name not in state.agents:
        return {"error": "Agent 不存在"}
    
    agent = state.agents[name]
    history = agent.memory.to_dict()
    
    return {"history": history}


@app.post("/api/messages")
async def send_message(data: MessageSend):
    """发送消息"""
    if data.sender not in state.agents:
        return {"error": "发送者不存在"}
    if data.receiver not in state.agents and data.receiver != "all":
        return {"error": "接收者不存在"}
    
    sender = state.agents[data.sender]
    
    if data.receiver == "all":
        sender.broadcast(data.content)
    else:
        sender.send_to(data.receiver, data.content)
    
    # 广播事件
    await broadcast_event("message_sent", {
        "sender": data.sender,
        "receiver": data.receiver,
        "content": data.content,
        "timestamp": datetime.now().isoformat(),
    })
    
    return {"success": True}


@app.post("/api/tasks")
async def execute_task(data: TaskExecute):
    """执行任务"""
    if data.agent_name not in state.agents:
        return {"error": "Agent 不存在"}
    
    agent = state.agents[data.agent_name]
    
    await broadcast_event("task_started", {
        "agent": data.agent_name,
        "task": data.task,
    })
    
    try:
        # 模拟异步执行
        result = agent.execute_task(data.task)
        
        await broadcast_event("task_completed", {
            "agent": data.agent_name,
            "task": data.task,
            "result": str(result)[:500],  # 限制长度
        })
        
        return {"success": True, "result": result}
    except Exception as e:
        await broadcast_event("task_failed", {
            "agent": data.agent_name,
            "task": data.task,
            "error": str(e),
        })
        return {"error": str(e)}


@app.get("/api/bus/history")
async def get_bus_history():
    """获取消息总线历史"""
    history = [msg.to_dict() for msg in state.bus.history[-50:]]  # 最近50条
    return {"history": history}


@app.get("/api/orchestrator/status")
async def get_orchestrator_status():
    """获取编排器状态"""
    status = state.orchestrator.get_status()
    return status


@app.post("/api/orchestrator/run")
async def run_orchestrator(task: str, strategy: str = "auto"):
    """通过编排器执行任务"""
    await broadcast_event("orchestrator_started", {"task": task})
    
    try:
        result = state.orchestrator.run(task, strategy)
        
        await broadcast_event("orchestrator_completed", {
            "task": task,
            "result": str(result)[:500],
        })
        
        return {"success": True, "result": result}
    except Exception as e:
        return {"error": str(e)}


# ============ WebSocket ============

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 连接 - 实时更新"""
    await websocket.accept()
    state.websocket_clients.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            # 处理客户端消息（心跳等）
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        state.websocket_clients.remove(websocket)


async def broadcast_event(event_type: str, data: Any):
    """广播事件到所有 WebSocket 客户端"""
    message = json.dumps({
        "type": event_type,
        "data": data,
        "timestamp": datetime.now().isoformat(),
    })
    
    for client in state.websocket_clients:
        try:
            await client.send_text(message)
        except:
            pass


# ============ 启动说明 ============

if __name__ == "__main__":
    import uvicorn
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║       Multi-Agent Interaction Web UI                  ║
    ╠═══════════════════════════════════════════════════════╣
    ║  启动后访问: http://localhost:8000                    ║
    ║  API 文档: http://localhost:8000/docs                  ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=8000)