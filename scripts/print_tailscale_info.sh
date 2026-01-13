#!/usr/bin/env bash
set -euo pipefail

if ! command -v tailscale >/dev/null 2>&1; then
  echo "tailscale 未安装。请先安装 Tailscale。"
  exit 1
fi

IPV4=$(tailscale ip -4 2>/dev/null | head -n 1 || true)
if [[ -z "${IPV4}" ]]; then
  echo "未获取到 Tailscale IPv4 地址，请确认已登录。"
  exit 1
fi

echo "Tailscale IPv4: ${IPV4}"
echo "Status URL: http://${IPV4}:8080/status"
