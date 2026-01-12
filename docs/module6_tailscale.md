# 模块 6：Tailscale 远程访问（最小改动版）
## 目标
在不暴露公网端口的前提下，通过 Tailscale 让 iPhone 访问 Mac 上的服务。

---

## macOS 安装与登录（中文）
1. 安装 Tailscale：打开 <https://tailscale.com/download> 下载并安装。
2. 登录：启动 Tailscale，使用同一账号登录（与 iPhone 保持一致）。

## macOS インストールとログイン（日本語）
1. Tailscale をインストール：<https://tailscale.com/download> からダウンロードしてインストール。
2. ログイン：Tailscale を起動し、iPhone と同一アカウントでログイン。

---

## iPhone 安装与登录（中文）
1. 从 App Store 安装 Tailscale。
2. 用与 Mac 相同的账号登录。

## iPhone インストールとログイン（日本語）
1. App Store から Tailscale をインストール。
2. Mac と同じアカウントでログイン。

---

## 确认 Mac 的 Tailscale IP / MagicDNS（中文）
1. 在 Mac 打开 Tailscale 客户端，查看分配的 100.x.x.x 地址。
2. 若启用 MagicDNS，可使用主机名（例如 `your-mac.tailnet-xxx.ts.net`）。

## Mac の Tailscale IP / MagicDNS 確認（日本語）
1. Mac の Tailscale クライアントで 100.x.x.x のアドレスを確認。
2. MagicDNS が有効ならホスト名（例：`your-mac.tailnet-xxx.ts.net`）を使用可能。

---

## 安全注意（中文）
- 不要把 8080 端口暴露到公网。
- AUTH_TOKEN 必须足够强。
- （可选）在 Tailscale ACL 中限制仅允许 iPhone 访问 Mac 的 8080 端口。

## セキュリティ注意（日本語）
- 8080 ポートをインターネットに公開しない。
- AUTH_TOKEN は十分に強いものを使用。
- （任意）Tailscale ACL で iPhone から Mac の 8080 へのアクセスだけを許可。

---

## 远程测试命令示例（中文）
将 `<MAC_TAILSCALE_IP>` 替换为 100.x.x.x 或 MagicDNS 名称。

### GET /status
```bash
curl -sS http://<MAC_TAILSCALE_IP>:8080/status \
  -H "Authorization: Bearer <AUTH_TOKEN>"
```

### POST /command（示例：sleep）
```bash
curl -sS -X POST http://<MAC_TAILSCALE_IP>:8080/command \
  -H "Authorization: Bearer <AUTH_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"action":"sleep","params":{"ms":1000}}'
```

### POST /stop
```bash
curl -sS -X POST http://<MAC_TAILSCALE_IP>:8080/stop \
  -H "Authorization: Bearer <AUTH_TOKEN>"
```

## リモート確認コマンド（日本語）
`<MAC_TAILSCALE_IP>` は 100.x.x.x または MagicDNS 名に置換。

### GET /status
```bash
curl -sS http://<MAC_TAILSCALE_IP>:8080/status \
  -H "Authorization: Bearer <AUTH_TOKEN>"
```

### POST /command（例：sleep）
```bash
curl -sS -X POST http://<MAC_TAILSCALE_IP>:8080/command \
  -H "Authorization: Bearer <AUTH_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"action":"sleep","params":{"ms":1000}}'
```

### POST /stop
```bash
curl -sS -X POST http://<MAC_TAILSCALE_IP>:8080/stop \
  -H "Authorization: Bearer <AUTH_TOKEN>"
```

---

## 常见问题排查（中文）
- 连不上：确认 iPhone 与 Mac 已登录同一 Tailscale 账号，且双方在线。
- 401：AUTH_TOKEN 不匹配或未传 Authorization。
- 超时：Mac 端服务未启动，或防火墙阻止 8080。

## よくあるトラブル（日本語）
- 接続できない：iPhone と Mac が同じ Tailscale アカウントでログインしているか確認。
- 401：AUTH_TOKEN が一致しない、または Authorization が未送信。
- タイムアウト：Mac 側のサービス未起動、または 8080 がファイアウォールで遮断。
