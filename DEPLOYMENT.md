# Deployment

The frontend is a native Next.js application deployed on Vercel. The FastAPI backend is deployed separately on Render and remains configured by the root `render.yaml` Blueprint. The Render filesystem is ephemeral: SQLite records, uploaded files, and the FAISS index reset when the backend is redeployed or restarted. The Blueprint does not create PostgreSQL; configure `DATABASE_URL` manually only when a database is provisioned.

## Frontend on Vercel

1. Import the GitHub repository into Vercel.
2. Set **Root Directory** to `frontend` and **Framework Preset** to `Next.js`.
3. Add the environment variable `NEXT_PUBLIC_API_URL` with the value `https://doculens-5.onrender.com` for Production (and Preview if preview deployments should call the production API).
4. Deploy. Vercel uses the standard Next.js build; no `vercel.json` is required.
5. Copy the deployed Vercel URL, including its scheme and host.

`NEXT_PUBLIC_API_URL` is read at build time. If you change it in Vercel, redeploy the frontend. For local development, copy `frontend/.env.example` to `frontend/.env.local`; the checked-in example defaults to the deployed backend, while omitting the variable falls back to `http://localhost:8000`.

## Backend on Render

The backend is configured by the `doculens-backend` service in `render.yaml`. In its Render environment, set `CORS_ORIGINS` to the exact Vercel frontend origin (for example, `https://your-project.vercel.app`, without a trailing slash). Include any additional Vercel Preview origins as a comma-separated list. Save the variable and redeploy the backend.

The Blueprint also configures:

- `HF_MODEL_ID`: `Abhimanyu125047/doculens-nli`.
- `HF_TOKEN`: optional for the public model; required only if the model repository is private.
- `MAX_UPLOAD_MB`: `10`.
- `NLI_CONFIDENCE_THRESHOLD`: `0.85`.
- `RETRIEVAL_TOP_K`: `5`.
- `PYTHONUNBUFFERED`: `1`.

If the NLI model is private, set `HF_TOKEN` as a Render service environment variable. To bake the private model into the Docker image as well, add a Render secret file named `HF_TOKEN` for the backend build. The Dockerfile reads it through a BuildKit secret mount; do not pass the token as a Docker build argument or commit it.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Browser CORS error | Set backend `CORS_ORIGINS` to the exact Vercel origin, including `https://` and excluding a trailing slash; save and redeploy the backend. |
| 502 or unhealthy backend | Check Render logs for startup/model errors, verify `HF_MODEL_ID`, and confirm the service health check is `/health`. |
| Slow first request | Model initialization and backend cold starts can take time. The UI shows a wait state and has a request timeout. |
| Frontend calls the wrong backend | Confirm `NEXT_PUBLIC_API_URL` in the Vercel environment and redeploy; Next.js inlines this public variable during build. |

## Post-deploy Checks

- Open `https://doculens-5.onrender.com/`; expect `{"service":"DocuLens API","status":"ok","docs":"/docs"}`.
- Open `https://doculens-5.onrender.com/health`; expect `{"status":"ok"}`.
- Open the Vercel URL and confirm the backend status is online.
- Upload a small, text-based PDF under the configured size limit and confirm it appears in the document list.
- Run a semantic search and confirm matching document chunks are returned.
- Run an NLI analysis and confirm a label and confidence scores are displayed.
- Confirm a non-PDF upload returns HTTP 400 and an oversized PDF returns HTTP 413.