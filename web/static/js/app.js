// Vue 3 应用
const { createApp, ref, computed, onMounted, nextTick } = Vue;

createApp({
    setup() {
        // 状态
        const wsConnected = ref(false);
        const agents = ref([]);
        const selectedAgent = ref(null);
        const messages = ref([]);
        const activityLogs = ref([]);
        
        // 表单
        const showCreateAgent = ref(false);
        const newAgent = ref({
            name: '',
            role: '',
            description: '',
            agent_type: 'basic'
        });
        
        // 消息
        const messageInput = ref('');
        const messageReceiver = ref('all');
        
        // 任务
        const taskInput = ref('');
        const taskAgent = ref('');
        
        // 编排器
        const orchestratorTask = ref('');
        const orchestratorStrategy = ref('auto');
        
        // WebSocket
        let ws = null;
        let reconnectInterval = null;

        // 连接 WebSocket
        const connectWebSocket = () => {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onopen = () => {
                wsConnected.value = true;
                addLog('system', 'WebSocket 已连接');
                if (reconnectInterval) {
                    clearInterval(reconnectInterval);
                    reconnectInterval = null;
                }
            };
            
            ws.onclose = () => {
                wsConnected.value = false;
                addLog('system', 'WebSocket 断开连接');
                
                // 自动重连
                if (!reconnectInterval) {
                    reconnectInterval = setInterval(() => {
                        if (!wsConnected.value) {
                            connectWebSocket();
                        }
                    }, 3000);
                }
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            };
            
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        };

        // 处理 WebSocket 消息
        const handleWebSocketMessage = (data) => {
            const { type, data: payload, timestamp } = data;
            
            switch (type) {
                case 'agent_created':
                    addLog('success', `Agent "${payload.name}" 已创建`);
                    fetchAgents();
                    break;
                    
                case 'agent_deleted':
                    addLog('info', `Agent "${payload.name}" 已删除`);
                    fetchAgents();
                    break;
                    
                case 'message_sent':
                    messages.value.push({
                        sender: payload.sender,
                        receiver: payload.receiver,
                        content: payload.content,
                        timestamp: payload.timestamp
                    });
                    scrollToBottom();
                    break;
                    
                case 'task_started':
                    addLog('task_started', `${payload.agent}: 开始执行任务`);
                    updateAgentState(payload.agent, 'working');
                    break;
                    
                case 'task_completed':
                    addLog('task_completed', `${payload.agent}: 任务完成`);
                    messages.value.push({
                        sender: payload.agent,
                        receiver: 'system',
                        content: `任务结果: ${payload.result}`,
                        timestamp: timestamp
                    });
                    updateAgentState(payload.agent, 'idle');
                    scrollToBottom();
                    break;
                    
                case 'task_failed':
                    addLog('task_failed', `${payload.agent}: 任务失败 - ${payload.error}`);
                    updateAgentState(payload.agent, 'error');
                    break;
                    
                case 'orchestrator_started':
                    addLog('info', `编排器开始执行: ${payload.task}`);
                    break;
                    
                case 'orchestrator_completed':
                    addLog('success', `编排器执行完成`);
                    messages.value.push({
                        sender: 'Orchestrator',
                        receiver: 'system',
                        content: `编排结果: ${payload.result}`,
                        timestamp: timestamp
                    });
                    scrollToBottom();
                    break;
            }
        };

        // 添加日志
        const addLog = (type, message) => {
            activityLogs.value.unshift({
                type,
                message,
                timestamp: new Date().toISOString()
            });
            
            // 保留最近 50 条
            if (activityLogs.value.length > 50) {
                activityLogs.value.pop();
            }
        };

        // 更新 Agent 状态
        const updateAgentState = (name, state) => {
            const agent = agents.value.find(a => a.name === name);
            if (agent) {
                agent.state = state;
            }
        };

        // 滚动到底部
        const scrollToBottom = async () => {
            await nextTick();
            const container = document.querySelector('.messages');
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        };

        // API 调用
        const api = {
            async get(url) {
                const response = await fetch(url);
                return response.json();
            },
            async post(url, data) {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                return response.json();
            },
            async delete(url) {
                const response = await fetch(url, { method: 'DELETE' });
                return response.json();
            }
        };

        // 获取 Agent 列表
        const fetchAgents = async () => {
            const data = await api.get('/api/agents');
            agents.value = data.agents || [];
        };

        // 选择 Agent
        const selectAgent = (name) => {
            selectedAgent.value = selectedAgent.value === name ? null : name;
            if (selectedAgent.value) {
                messageReceiver.value = name;
                taskAgent.value = name;
            }
        };

        // 创建 Agent
        const createAgent = async () => {
            if (!newAgent.value.name || !newAgent.value.role) {
                alert('请填写名称和角色');
                return;
            }
            
            const result = await api.post('/api/agents', newAgent.value);
            
            if (result.success) {
                showCreateAgent.value = false;
                newAgent.value = {
                    name: '',
                    role: '',
                    description: '',
                    agent_type: 'basic'
                };
            } else {
                alert(result.error || '创建失败');
            }
        };

        // 发送消息
        const sendMessage = async () => {
            if (!messageInput.value || !selectedAgent.value) {
                if (!selectedAgent.value) {
                    alert('请先选择一个 Agent');
                }
                return;
            }
            
            const result = await api.post('/api/messages', {
                sender: selectedAgent.value,
                receiver: messageReceiver.value,
                content: messageInput.value
            });
            
            if (result.success) {
                messageInput.value = '';
            }
        };

        // 执行任务
        const executeTask = async () => {
            if (!taskAgent.value || !taskInput.value) return;
            
            const result = await api.post('/api/tasks', {
                agent_name: taskAgent.value,
                task: taskInput.value
            });
            
            if (result.success) {
                taskInput.value = '';
            } else {
                alert(result.error || '执行失败');
            }
        };

        // 运行编排器
        const runOrchestrator = async () => {
            if (!orchestratorTask.value) return;
            
            const result = await api.post(
                `/api/orchestrator/run?task=${encodeURIComponent(orchestratorTask.value)}&strategy=${orchestratorStrategy.value}`
            );
            
            if (result.success) {
                orchestratorTask.value = '';
            } else {
                alert(result.error || '编排失败');
            }
        };

        // 格式化时间
        const formatTime = (timestamp) => {
            if (!timestamp) return '';
            const date = new Date(timestamp);
            return date.toLocaleTimeString('zh-CN', { 
                hour: '2-digit', 
                minute: '2-digit',
                second: '2-digit'
            });
        };

        // 初始化
        onMounted(() => {
            fetchAgents();
            connectWebSocket();
            
            // 定期刷新
            setInterval(fetchAgents, 30000);
        });

        return {
            // 状态
            wsConnected,
            agents,
            selectedAgent,
            messages,
            activityLogs,
            
            // 表单
            showCreateAgent,
            newAgent,
            
            // 消息
            messageInput,
            messageReceiver,
            
            // 任务
            taskInput,
            taskAgent,
            
            // 编排器
            orchestratorTask,
            orchestratorStrategy,
            
            // 方法
            selectAgent,
            createAgent,
            sendMessage,
            executeTask,
            runOrchestrator,
            formatTime
        };
    }
}).mount('#app');