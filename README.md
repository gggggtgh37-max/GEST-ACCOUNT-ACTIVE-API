# FF Guest Activator — Vercel API

## Deploy karo (3 steps)

### Step 1 — Vercel CLI install karo
```bash
npm install -g vercel
```

### Step 2 — Login karo
```bash
vercel login
```

### Step 3 — Deploy karo (project folder ke andar se)
```bash
vercel --prod
```
Vercel ek live URL dega jaise:
```
https://ff-activator-xxxx.vercel.app
```

---

## Endpoints

### GET /
```
https://YOUR-URL.vercel.app/
```

### GET /health
```
https://YOUR-URL.vercel.app/health
```

### POST /activate
```bash
curl -X POST https://YOUR-URL.vercel.app/activate \
  -H "Content-Type: application/json" \
  -d '{"uid": "UID_YAHAN", "password": "PASS_YAHAN"}'
```

**Success:**
```json
{
  "success": true,
  "account_uid": "123456789",
  "region": "BD",
  "chat_server": "1.2.3.4:5678",
  "online_server": "1.2.3.4:9012",
  "chat_response": "OK",
  "online_response": "OK"
}
```

**Fail:**
```json
{
  "success": false,
  "error": "OAuth failed — invalid UID or password"
}
```

---

## File Structure
```
ff-vercel/
├── api/
│   └── index.py      ← FastAPI app (Vercel entry point)
├── requirements.txt  ← Python dependencies
├── vercel.json       ← Vercel routing config
└── README.md
```
