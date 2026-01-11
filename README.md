# iPhone → Mac 远程 Agent 控制系统（学习项目）

本仓库实现一个可控、可中断、可审计的 Mac 端 Agent。当前已完成模块 4（Queue + STOP）。

## 快速开始

### 1) 启动服务

```bash
export AUTH_TOKEN="your-strong-token"
python src/server.py
```

### 2) 发送指令（入队）

```bash
curl -sS -X POST http://127.0.0.1:8080/command \
  -H "Authorization: Bearer your-strong-token" \
  -H "Content-Type: application/json" \
  -d '{"action":"ping","params":{}}'
```

### 3) 查看队列状态

```bash
curl -sS http://127.0.0.1:8080/status \
  -H "Authorization: Bearer your-strong-token"
```

### 4) 查看结构化日志

```bash
curl -sS http://127.0.0.1:8080/logs \
  -H "Authorization: Bearer your-strong-token"
```

### 5) STOP（中断队列与正在执行任务）

```bash
curl -sS -X POST http://127.0.0.1:8080/stop \
  -H "Authorization: Bearer your-strong-token"
```

## 最小可运行测试

```bash
python -m unittest discover -s tests -v
```
