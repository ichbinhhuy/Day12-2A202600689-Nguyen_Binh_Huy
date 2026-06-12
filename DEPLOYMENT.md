# Deployment Information

## Public URL
https://day12-2a202600689-nguyenbinhhuy-production.up.railway.app

## Platform
Railway

## Test Commands

### Health Check (Kiểm tra liveness)
```bash
curl https://day12-2a202600689-nguyenbinhhuy-production.up.railway.app/health
# Expected: {"status": "ok", "uptime_seconds": ...}
```

### Readiness Check
```bash
curl https://day12-2a202600689-nguyenbinhhuy-production.up.railway.app/ready
# Expected: {"ready": true}
```

### API Test (với authentication)
```bash
curl -X POST https://day12-2a202600689-nguyenbinhhuy-production.up.railway.app/ask \
  -H "X-API-Key: my-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello", "user_id": "test_user_01"}'
```

### Rate Limiting Test
```bash
# Gửi 15 request liên tục, từ request thứ 11 sẽ bị chặn
for i in $(seq 1 15); do
  curl -s -X POST https://day12-2a202600689-nguyenbinhhuy-production.up.railway.app/ask \
    -H "X-API-Key: my-secret-key-123" \
    -H "Content-Type: application/json" \
    -d '{"question": "test"}'
  echo ""
done
# Expected: Từ request thứ 11 trả về 429 "Rate limit exceeded"
```

## Environment Variables Set
Các biến môi trường đã được cài đặt trên Railway:
- `PORT` (Do Railway tự cấp, giá trị 8080)
- `REDIS_URL` (Link Redis nội bộ do Railway cung cấp)
- `AGENT_API_KEY=my-secret-key-123`
- `JWT_SECRET` (Đã cấu hình)
- `ENVIRONMENT=production`
- `RATE_LIMIT_PER_MINUTE=10`
- `DAILY_BUDGET_USD=10.0`

## Test Results
- Health Check: ✅ 200 OK — `{"status":"ok","environment":"production"}`
- Auth (no key): ✅ 401 — `"Invalid or missing API key"`
- Auth (valid key): ✅ 200 OK — Agent trả lời thành công
- Rate Limiting: ✅ 429 — Chặn từ request thứ 11 trở đi

## Screenshots
- Bảng điều khiển Railway: App "Online" màu xanh lá
- Kết quả test API thành công trên Terminal
