# GEST ACT API — Render + Railway

## Deploy on Render
1. Extract this ZIP and push the folder contents to a GitHub repository.
2. In Render, choose **New + → Blueprint** and select the repository.
3. Render reads `render.yaml` and builds the included Dockerfile.
4. After deployment, test `https://YOUR-SERVICE.onrender.com/health`.

## Deploy on Railway
1. Extract this ZIP and push the folder contents to a GitHub repository.
2. In Railway, choose **New Project → Deploy from GitHub Repo**.
3. Select the repository. Railway builds using `Dockerfile`.
4. Test `https://YOUR-SERVICE.up.railway.app/health`.

## API routes
- `GET /` — API information
- `GET /health` — health check
- `POST /activate` — JSON body: `{"uid":"...","password":"..."}`
- `GET /bind?uid=...&password=...&region=BD`
- `GET /docs` — interactive API docs

The service listens on the platform-provided `PORT`. Do not commit account passwords,
API keys, or other secrets to the repository. A successful deploy only confirms that
the web service started; it does not guarantee that an external game service will
accept an activation request.
