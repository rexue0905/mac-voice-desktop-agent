# iPhone → Mac 远程 Agent 控制系统（学习项目）

本仓库实现一个可控、可中断、可审计的 Mac 端 Agent。当前已完成模块 5（最简单执行器）。

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
  -d '{"action":"sleep","params":{"ms":1000}}'
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

## 可用 Skills

- open_app(app_name): 仅允许白名单应用（Notes、Safari、Google Chrome、Terminal、Visual Studio Code）
- open_url(url): 仅允许 http/https
- notify(title, message): 系统通知（长度限制）
- screenshot(): 保存到 `./artifacts/screenshots/`
- sleep(ms): 演示队列与 STOP（上限 5000ms）
