# モジュール8：LLMによる自然言語→action変換

## 目的
- 中国語（簡体）または日本語の自然言語を、既存の `action + params` に変換します。
- 本モジュールは**実行しません**。出力は `validate_command` に渡され、既存のホワイトリストとキューで処理されます。

---

## 対応する入力例（中国語 / 日本語）
同じ意図は同じ action に正規化されます。

- 「暂停一下」 / 「ちょっと止めて」 → `{"action":"stop","params":{}}`
- 「等一秒」 / 「1秒待って」 → `{"action":"sleep","params":{"ms":1000}}`
- 「测试一下」 / 「テストして」 → `{"action":"ping","params":{}}`
- 「什么都别做」 / 「何もしないで」 → `{"action":"noop","params":{}}`

---

## 非対応の例
次のような指示は **拒否** されます（曖昧または対象外）。

- 「ブラウザを開いて」 / 「打开网页」 → `{"error":"unsupported_or_ambiguous_request"}`
- 「買い物して」 / 「支付」 → `{"error":"unsupported_or_ambiguous_request"}`
- 「パスワードを入力して」 / 「输入密码」 → `{"error":"unsupported_or_ambiguous_request"}`

---

## 安全境界
- LLM は **action の提案のみ** を行います。
- 実行の可否は既存の `validate_command` とキュー/Executor が決定します。
- LLM は **直接実行しません**。曖昧な指示は拒否します。

---

## なぜモデルが直接実行できないのか
- 安全上の理由で、LLM の出力は必ずホワイトリスト検証を通す必要があります。
- 直接実行は誤動作や不正操作の原因になるため、禁止します。
