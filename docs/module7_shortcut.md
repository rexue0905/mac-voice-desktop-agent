# モジュール7：iPhone ショートカット向け入力インターフェース

## 位置づけ（このモジュールの役割）
- iPhone（Siri / ショートカット）から Mac の Agent に安定した入力を送るための最小インターフェースを提供します。
- 本モジュールは **AI / LLM を実装しません**。自然言語は上流（ショートカットや将来の Agent）で **action + params** に変換する想定です。

---

## 推奨するショートカットの呼び出し方法
- HTTP POST を使用します。
- ヘッダに `Authorization: Bearer <token>` を必ず付けます。
- ボディは JSON（`action` と `params`）を送信します。

---

## 代表的なリクエスト例（curl）

### /command（sleep）
```bash
curl -sS -X POST http://<MAC_TAILSCALE_IP>:8080/command \
  -H "Authorization: Bearer <AUTH_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"action":"sleep","params":{"ms":1000}}'
```

### /command（open_url）
```bash
curl -sS -X POST http://<MAC_TAILSCALE_IP>:8080/command \
  -H "Authorization: Bearer <AUTH_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"action":"open_url","params":{"url":"https://example.com"}}'
```

### /command（ping）
```bash
curl -sS -X POST http://<MAC_TAILSCALE_IP>:8080/command \
  -H "Authorization: Bearer <AUTH_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"action":"ping","params":{}}'
```

### /command（noop）
```bash
curl -sS -X POST http://<MAC_TAILSCALE_IP>:8080/command \
  -H "Authorization: Bearer <AUTH_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"action":"noop","params":{}}'
```

### /command（stop）
```bash
curl -sS -X POST http://<MAC_TAILSCALE_IP>:8080/command \
  -H "Authorization: Bearer <AUTH_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"action":"stop","params":{}}'
```

### /status
```bash
curl -sS http://<MAC_TAILSCALE_IP>:8080/status \
  -H "Authorization: Bearer <AUTH_TOKEN>"
```

### /stop
```bash
curl -sS -X POST http://<MAC_TAILSCALE_IP>:8080/stop \
  -H "Authorization: Bearer <AUTH_TOKEN>"
```

---

## 現在の能力境界
- **AI エージェントではありません**。曖昧な指示や自然言語の解釈は行いません。
- `action` は明示的な文字列、`params` は構造化 JSON のみ受け付けます。
- 認証は `Authorization: Bearer <token>` のみです。新しい認証方式は追加しません。

---

## 最低限のアクション一覧
- sleep（待機 / STOP 動作確認用）
- stop（キュー停止）
- ping（到達確認）
- open_url（URL オープン）
- noop（デバッグ用・何もしない）
