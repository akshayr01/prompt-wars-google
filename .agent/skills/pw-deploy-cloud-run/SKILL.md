---
name: pw-deploy-cloud-run
description: Use this skill when the user wants to deploy to Google Cloud Run, get a public URL, or ship the app for submission. Handles Dockerfile, gcloud build, service deployment, and URL verification end-to-end.
---

# pw-deploy-cloud-run

## Goal
Deploy to Cloud Run and get a publicly accessible URL in under 5 minutes.

## Instructions

### Step 1: Verify Dockerfile exists
If missing, generate based on project:

**Python/FastAPI:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
```

**Node.js:**
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 8080
CMD ["node", "server.js"]
```

**Static HTML (nginx):**
```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
```

nginx.conf for static:
```nginx
server {
    listen 8080;
    root /usr/share/nginx/html;
    index index.html;
    location / { try_files $uri $uri/ /index.html; }
    gzip on;
    gzip_types text/css application/javascript;
}
```

### Step 2: Test Docker Build Locally
```bash
docker build -t promptwars-app . && echo "BUILD OK"
docker run -p 8080:8080 --env-file .env promptwars-app &
curl http://localhost:8080/health
```

### Step 3: Deploy to Cloud Run
```bash
# Set project (replace with actual project ID)
export PROJECT_ID=$(gcloud config get-value project)

# Deploy directly from source (fastest)
gcloud run deploy promptwars-app \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 3 \
  --port 8080 \
  --set-env-vars GCP_PROJECT_ID=$PROJECT_ID

# Capture URL
export APP_URL=$(gcloud run services describe promptwars-app \
  --region us-central1 \
  --format 'value(status.url)')

echo "✅ Deployed: $APP_URL"
```

### Step 4: Verify Deployment
```bash
curl "$APP_URL/health"
# Should return: {"status":"ok","version":"1.0.0"}
```

### Step 5: README deploy section
Always add this to README.md:
```markdown
## Deploy

```bash
gcloud run deploy promptwars-app --source . --region us-central1 --allow-unauthenticated
```
Live URL: https://[YOUR-APP]-us-central1.a.run.app
```

## Constraints
- Always use `--allow-unauthenticated` (judges need public access)
- Region: `us-central1` unless specified
- Always verify the URL works before submitting
- If `gcloud run deploy --source` fails, use `gcloud builds submit` then `gcloud run deploy --image`
