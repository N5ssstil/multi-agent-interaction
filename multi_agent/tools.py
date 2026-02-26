"""
工具系统 - Agent 可以使用的工具
"""

from typing import Callable, Any, Dict, List, Optional
from dataclasses import dataclass
import inspect


@dataclass
class Tool:
    """工具对象"""
    name: str
    function: Callable
    description: str
    parameters: Dict  # JSON Schema 格式的参数定义
    
    def execute(self, **kwargs) -> Any:
        """执行工具"""
        return self.function(**kwargs)
    
    def to_openai_format(self) -> Dict:
        """转换为 OpenAI Function Calling 格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }


class ToolRegistry:
    """
    工具注册表
    
    管理和调用 Agent 可用的工具
    """
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
    
    def register(
        self, 
        name: str, 
        function: Callable, 
        description: str = ""
    ) -> None:
        """注册工具"""
        # 自动从函数签名生成参数定义
        parameters = self._infer_parameters(function)
        
        self.tools[name] = Tool(
            name=name,
            function=function,
            description=description or function.__doc__ or "",
            parameters=parameters,
        )
        print(f"[ToolRegistry] 工具 '{name}' 已注册")
    
    def unregister(self, name: str) -> None:
        """注销工具"""
        if name in self.tools:
            del self.tools[name]
    
    def get(self, name: str) -> Optional[Tool]:
        """获取工具"""
        return self.tools.get(name)
    
    def execute(self, name: str, **kwargs) -> Any:
        """执行工具"""
        tool = self.get(name)
        if not tool:
            raise ValueError(f"工具 '{name}' 未找到")
        return tool.execute(**kwargs)
    
    def list_tools(self) -> List[str]:
        """列出所有工具"""
        return list(self.tools.keys())
    
    def to_openai_tools(self) -> List[Dict]:
        """转换为 OpenAI tools 格式"""
        return [tool.to_openai_format() for tool in self.tools.values()]
    
    def _infer_parameters(self, func: Callable) -> Dict:
        """从函数签名推断参数定义"""
        sig = inspect.signature(func)
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            param_info = {"type": "string"}  # 默认类型
            
            # 尝试从类型注解推断
            if param.annotation != inspect.Parameter.empty:
                type_map = {
                    str: "string",
                    int: "integer",
                    float: "number",
                    bool: "boolean",
                    list: "array",
                    dict: "object",
                }
                param_info["type"] = type_map.get(param.annotation, "string")
            
            properties[param_name] = param_info
            
            # 没有默认值的参数是必需的
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }
    
    def __repr__(self) -> str:
        return f"ToolRegistry(tools={self.list_tools()})"


# 预定义的通用工具
def create_default_tools() -> ToolRegistry:
    """创建默认工具集"""
    registry = ToolRegistry()
    
    @registry.register
    def search(query: str) -> str:
        """搜索互联网信息"""
        # 这里可以集成实际的搜索 API
        return f"搜索结果：{query}"
    
    @registry.register
    def calculate(expression: str) -> float:
        """计算数学表达式"""
        try:
            return eval(expression)
        except:
            return 0.0
    
    @registry.register
    def read_file(path: str) -> str:
        """读取文件内容"""
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"读取失败：{e}"
    
    return registry