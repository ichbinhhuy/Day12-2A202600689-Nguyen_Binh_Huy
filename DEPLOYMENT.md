# Deployment Information

## Public URL
> (ĐIỀN LINK CỦA BẠN VÀO ĐÂY, ví dụ: https://my-agent.up.railway.app)
https://my-agent-demo.up.railway.app

## Platform
Railway

## Test Commands

### Health Check (Kiểm tra liveness)
```bash
curl https://my-agent-demo.up.railway.app/health
# Expected: {"status": "ok", "uptime_seconds": ...}
```

### Readiness Check
```bash
curl https://my-agent-demo.up.railway.app/ready
# Expected: {"ready": true}
```

### API Test (với authentication)
```bash
curl -X POST https://my-agent-demo.up.railway.app/ask \
  -H "X-API-Key: secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"question": "Bạn tên là gì?", "user_id": "test_user_01"}'
```

## Environment Variables Set
Các biến môi trường đã được cài đặt trên Railway:
- `PORT=8000` (Thường do Railway tự cấp)
- `REDIS_URL=redis://...` (Link Redis do Railway cung cấp)
- `AGENT_API_KEY=secret-key-123`
- `LOG_LEVEL=INFO`
- `RATE_LIMIT_PER_MINUTE=10`
- `MONTHLY_BUDGET_USD=10.0`

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png) (Bạn hãy chụp ảnh up vào nhé)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)
