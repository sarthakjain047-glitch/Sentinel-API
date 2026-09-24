#!/usr/bin/env bash
set -euo pipefail
payload='{"spec_url":"http://127.0.0.1:8001/openapi.json","target_base_url":"http://127.0.0.1:8001","auth_tokens":{"userA":"token-a","userB":"token-b"},"checks":["bola","data_exposure","auth_misconfig","rate_limit"],"authorization_confirmed":true}'
scan=$(curl -fsS -X POST http://127.0.0.1:8000/api/scans -H 'Content-Type: application/json' -d "$payload")
id=$(printf '%s' "$scan" | sed -n 's/.*"id":"\([^"]*\)".*/\1/p')
[ -n "$id" ]
echo "scan_id=$id"
for i in $(seq 1 40); do
  status=$(curl -fsS "http://127.0.0.1:8000/api/scans/$id")
  printf '%s\n' "$status" | grep -q '"status":"completed"' && break
  printf '%s\n' "$status" | grep -q '"status":"failed"' && { echo "$status"; exit 1; }
  sleep 0.25
done
findings=$(curl -fsS "http://127.0.0.1:8000/api/scans/$id/findings")
echo "$status"
echo "$findings"
for klass in 'BOLA/IDOR' 'Data Exposure' 'Auth Misconfiguration' 'Rate Limit'; do
  printf '%s' "$findings" | grep -q "$klass" || { echo "missing finding class: $klass"; exit 1; }
done
echo 'e2e-scan-ok'
