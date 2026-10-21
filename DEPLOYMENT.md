# Render Deployment

DocuLens deploys as a FastAPI Docker service and a Next.js static site. The frontend is exported to `frontend/out`; it has no API routes, `getServerSideProps`, or server actions. The backend uses one worker and preloads the embedding and NLI models during the Docker build. The Render filesystem is ephemeral: SQLite records, uploaded files, and the FAISS index reset when the backend is redeployed or restarted. This Blueprint does not create PostgreSQL; configure `DATABASE_URL` manually only when a database is provisioned.

## Deploy with a Blueprint

1. Push the deployment files and source to the GitHub branch Render should deploy.
2. In the Render Dashboard, choose **New + → Blueprint**, connect the GitHub repository, select the branch, and apply `render.yaml`.
3. During the initial Blueprint prompt, set the backend environment values:
   - `HF_MODEL_ID`: `Abhimanyu125047/doculens-nli`.
   - `CORS_ORIGINS`: required; after creating the static site, set it to the exact frontend origin (scheme and host, no trailing slash). Multiple origins can be comma-separated.
   - `HF_TOKEN`: optional; leave unset for the public model or set a Hugging Face token if the model repository is private.
   - `MAX_UPLOAD_MB`: `10`.
   - `NLI_CONFIDENCE_THRESHOLD`: `0.85`.
   - `RETRIEVAL_TOP_K`: `5`.
   - `PYTHONUNBUFFERED`: `1`.
4. Create `doculens-frontend` as a Render Static Site from the Blueprint. Its build command is `npm ci && npm run build`, and its publish directory is `out`.
5. Set the frontend environment variable `NEXT_PUBLIC_API_URL` to `https://doculens-5.onrender.com` before its first build. This value is already configured in `render.yaml`, `frontend/.env.example`, and `frontend/.env.production`. Because Next.js inlines `NEXT_PUBLIC_*` variables at build time, redeploy the frontend after changing it.
6. Copy the frontend's deployed `https://...onrender.com` origin and set backend `CORS_ORIGINS` to that exact origin (no trailing slash). Add any additional allowed origins as comma-separated values.
7. Save and redeploy the backend after setting `CORS_ORIGINS`; redeploy the frontend after changing `NEXT_PUBLIC_API_URL`.

If the NLI model is private, `HF_TOKEN` as a service environment variable makes it available at runtime. To bake the private model into the Docker image as well, add a Render **secret file** named `HF_TOKEN` for the backend build with the same token. The Dockerfile reads it only through a BuildKit secret mount; do not pass the token as a Docker build argument or commit it. Render prompts for `sync: false` values during the initial Blueprint creation; add or update them later in the Dashboard.

## Render Settings to Confirm

- **Frontend Static Site**: build command `npm ci && npm run build`; publish directory `out`; environment variable `NEXT_PUBLIC_API_URL=https://doculens-5.onrender.com`.
- **Backend Web Service**: environment variable `CORS_ORIGINS=<your exact frontend origin>`; `HF_TOKEN` is optional for the public model and required only for a private model.
- No frontend start command or `NODE_VERSION` is needed for the static site.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Out of memory or repeated restarts | Keep the backend on the `1c-2g` plan, retain one worker, upload smaller PDFs, and avoid increasing the NLI batch size. Check backend memory and startup logs. |
| Browser CORS error | Set `CORS_ORIGINS` to the exact frontend origin, including `https://` and excluding a trailing slash; save and redeploy the backend. |
| 502 or unhealthy backend | Check Render logs for startup/model errors, verify `HF_MODEL_ID`, and confirm the service health check is `/health`. |
| Slow first request | Model files are baked into the image, but model initialization and cold starts still take time. Wait for the backend to become healthy; the UI shows a wait state and has a request timeout. |

## Post-deploy Checks

- Open `https://doculens-5.onrender.com/`; expect `{"service":"DocuLens API","status":"ok","docs":"/docs"}`.
- Open `https://doculens-5.onrender.com/health`; expect `{"status":"ok"}`.
- Open the frontend URL and confirm the backend status is online.
- Upload a small, text-based PDF under the configured size limit and confirm it appears in the document list.
- Run a semantic search and confirm matching document chunks are returned.
- Run an NLI analysis and confirm a label and confidence scores are displayed.
- Confirm a non-PDF upload returns HTTP 400 and an oversized PDF returns HTTP 413.
- Restart or redeploy the backend and confirm the UI remains usable; local SQLite/FAISS/upload data is ephemeral unless you configure persistent storage or PostgreSQL.