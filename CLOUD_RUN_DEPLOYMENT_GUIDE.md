# 🚀 Lauyami App - Google Cloud Run Deployment Guide

Complete guide for deploying your Lauyami legal assistant app to Google Cloud Run with $300 free credits.

---

## 📋 PRE-DEPLOYMENT CHECKLIST

### ✅ Prerequisites
- [ ] Google Cloud account created with $300 free credits
- [ ] Project created: `lauyami-app` in GCP Console
- [ ] Billing enabled on the project
- [ ] Git repository up to date
- [ ] All API keys ready (see below)

### ✅ Required API Keys/URLs
Make sure you have these ready in your `backend/.env` file:

```bash
# Qdrant Vector Database
QDRANT__URL=https://your-qdrant-instance.cloud.qdrant.io
QDRANT__API_KEY=your_qdrant_api_key
QDRANT__COLLECTION_NAME=legal_documents_collection
QDRANT__DENSE_MODEL_NAME=BAAI/bge-base-en
QDRANT__SPARSE_MODEL_NAME=Qdrant/bm25

# Hugging Face (for embeddings)
HUGGING_FACE__API_KEY=hf_your_key_here

# OpenAI (for LLM)
OPENAI__API_KEY=sk-your_openai_key

# Modal Services (N-ATLaS AI)
MODAL__LLM_BASE_URL=https://your-workspace--natlas-vllm-serve.modal.run
MODAL__LLM_API_KEY=not-needed
MODAL__ASR_BASE_URL=https://your-workspace--natlas-asr-api-transcribe.modal.run

# YarnGPT TTS
YARNGPT__API_KEY=sk_live_your_yarngpt_key
YARNGPT__API_URL=https://yarngpt.ai/api/v1/tts

# CORS (will update after frontend deployment)
ALLOWED_ORIGINS=http://localhost:8080,http://localhost:3000
```

### ✅ Files Updated
- [x] `backend/deploy_fastapi.sh` - Updated with new env vars and service name
- [x] `backend/cloudbuild_fastapi.yaml` - Updated service name to "lauyami-backend"
- [x] `backend/Dockerfile` - Already configured correctly
- [x] `backend/pyproject.toml` - Project name already "lauyami-project"

---

## 🛠️ DEPLOYMENT METHOD 1: CLI (RECOMMENDED - 10 minutes)

This is the fastest and easiest method using your existing deployment script.

### Step 1: Install Google Cloud CLI

```bash
# For Ubuntu/WSL (your system)
curl https://sdk.cloud.google.com | bash

# Restart shell
exec -l $SHELL

# Verify installation
gcloud --version
```

### Step 2: Authenticate

```bash
# Login to your Google account
gcloud auth login

# This will open a browser - sign in with your Google account
# Select the account with $300 credits
```

### Step 3: Set Your Project

```bash
# Set active project
gcloud config set project lauyami-app

# Verify it's set
gcloud config get-value project
# Should output: lauyami-app
```

### Step 4: Enable Required APIs

```bash
# Enable Cloud Run, Cloud Build, and Container Registry
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com

# This takes 1-2 minutes
```

### Step 5: Verify Your .env File

```bash
cd /home/teehy/lauyami-app/backend

# Check that .env exists and has all required variables
cat .env | grep -E "QDRANT|MODAL|YARNGPT|OPENAI|HUGGING_FACE"

# Make sure all values are filled in (not empty)
```

### Step 6: Deploy Backend! 🚀

```bash
cd /home/teehy/lauyami-app/backend

# Make script executable (if not already)
chmod +x deploy_fastapi.sh

# Run deployment
./deploy_fastapi.sh
```

**What happens:**
1. Script loads your `.env` file ✅
2. Builds Docker image using Cloud Build ⏱️ (3-5 minutes)
3. Pushes image to Google Container Registry 📦
4. Deploys to Cloud Run with all environment variables 🚀
5. Gives you a URL: `https://lauyami-backend-xxx.run.app`

### Step 7: Test Your Backend

```bash
# Copy the URL from the deployment output
# Test health endpoint
curl https://lauyami-backend-xxx.run.app/health

# Should return: {"status":"healthy"}
```

### Step 8: Deploy Frontend to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Update frontend environment variable
cd /home/teehy/lauyami-app/frontend
echo "VITE_API_BASE_URL=https://lauyami-backend-xxx.run.app" > .env

# Deploy
vercel

# Follow prompts, then get your URL: https://lauyami.vercel.app
```

### Step 9: Update CORS (Important!)

```bash
# Go back to backend
cd /home/teehy/lauyami-app/backend

# Update .env with your Vercel URL
# Add this line:
ALLOWED_ORIGINS=http://localhost:8080,https://lauyami.vercel.app

# Redeploy backend with updated CORS
./deploy_fastapi.sh
```

### ✅ Done! Your app is live!
- Backend: `https://lauyami-backend-xxx.run.app`
- Frontend: `https://lauyami.vercel.app`

---

## 🖱️ DEPLOYMENT METHOD 2: GCP CONSOLE UI (20 minutes)

If you prefer clicking buttons instead of using CLI.

### Step 1: Access Cloud Run

1. Go to https://console.cloud.google.com
2. Make sure project `lauyami-app` is selected (top left dropdown)
3. In search bar, type "Cloud Run"
4. Click **Cloud Run** service
5. Click **"Enable API"** if prompted

### Step 2: Build Your Docker Image First

You need to build and push the image manually since we're not using CLI.

**Option A: Use Cloud Shell (Easiest)**
1. Click the **Cloud Shell** icon (>_) at top right
2. Run these commands:

```bash
# Clone your repo (if not already in Cloud Shell)
git clone https://github.com/YOUR_USERNAME/lauyami-app.git
cd lauyami-app/backend

# Build and push image
gcloud builds submit --tag gcr.io/lauyami-app/lauyami-backend

# This takes 5-10 minutes
```

**Option B: Use Cloud Build Manually**
1. Go to **Cloud Build** → **Triggers**
2. Click **"Create Trigger"**
3. Connect your GitHub repository
4. Configure:
   - Name: `lauyami-backend-build`
   - Branch: `main`
   - Build configuration: Cloud Build configuration file
   - Location: `backend/cloudbuild_fastapi.yaml`
5. Click **"Create"**
6. Click **"Run"** to start build

### Step 3: Create Cloud Run Service

1. Go back to **Cloud Run**
2. Click **"Create Service"**
3. Select **"Deploy one revision from an existing container image"**
4. Click **"Select"** → Choose: `gcr.io/lauyami-app/lauyami-backend`

### Step 4: Configure Service Settings

**Container Settings:**
- **Service name**: `lauyami-backend`
- **Region**: `europe-west6` (Zurich) or closest to you
- **Authentication**: ✅ Allow unauthenticated invocations

**Container, Variables & Secrets:**

Click the section to expand:

**Container Tab:**
- **Memory**: 2.5 GiB
- **CPU**: 1
- **Request timeout**: 300 seconds
- **Maximum concurrent requests**: 2
- **Execution environment**: Second generation

**Variables & Secrets Tab:**

Click **"Add Variable"** for each of these (copy from your `.env`):

```
HF_HOME=/tmp/huggingface
FASTEMBED_CACHE=/tmp/fastembed_cache
HUGGING_FACE__API_KEY=your_key
OPENAI__API_KEY=your_key
QDRANT__API_KEY=your_key
QDRANT__URL=your_url
QDRANT__COLLECTION_NAME=legal_documents_collection
QDRANT__DENSE_MODEL_NAME=BAAI/bge-base-en
QDRANT__SPARSE_MODEL_NAME=Qdrant/bm25
MODAL__LLM_BASE_URL=your_modal_url
MODAL__LLM_API_KEY=not-needed
MODAL__ASR_BASE_URL=your_modal_asr_url
YARNGPT__API_KEY=your_key
YARNGPT__API_URL=https://yarngpt.ai/api/v1/tts
ALLOWED_ORIGINS=http://localhost:8080,http://localhost:3000
```

**Autoscaling:**
- **Minimum instances**: 0 (scales to zero!)
- **Maximum instances**: 2

### Step 5: Deploy

1. Click **"Create"** at the bottom
2. Wait 2-3 minutes for deployment
3. Copy your service URL: `https://lauyami-backend-xxx.run.app`

### Step 6: Test Backend

```bash
curl https://lauyami-backend-xxx.run.app/health
# Should return: {"status":"healthy"}
```

### Step 7: Deploy Frontend (Same as CLI method)

Follow Step 8 from CLI method above to deploy frontend to Vercel.

### Step 8: Update CORS

1. Go back to Cloud Run service in console
2. Click **"Edit & Deploy New Revision"**
3. Go to **"Variables & Secrets"**
4. Find `ALLOWED_ORIGINS`
5. Update value to include your Vercel URL:
   ```
   http://localhost:8080,https://lauyami.vercel.app
   ```
6. Click **"Deploy"**

---

## 🔍 TROUBLESHOOTING

### Issue: "Permission denied" when running gcloud commands

**Solution:**
```bash
gcloud auth login
gcloud config set project lauyami-app
```

### Issue: "API not enabled" error

**Solution:**
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Issue: Build fails with "uv not found"

**Solution:** Your Dockerfile is correct, this shouldn't happen. Check that you're in the `backend` directory when deploying.

### Issue: Service responds with 500 error

**Solution:** Check Cloud Run logs:
1. Go to Cloud Run console
2. Click your service
3. Click **"Logs"** tab
4. Look for error messages
5. Common issues:
   - Missing environment variables
   - Modal endpoints not accessible
   - Qdrant connection failed

### Issue: CORS error in frontend

**Solution:** Update `ALLOWED_ORIGINS` to include your Vercel URL and redeploy.

### Issue: Cold starts are slow

**Solution:** Set `min-instances` to 1 (costs ~$5-10/month):
```bash
gcloud run services update lauyami-backend \
  --region europe-west6 \
  --min-instances 1
```

---

## 💰 COST MONITORING

### Check Your Spending

1. Go to https://console.cloud.google.com/billing
2. Select your billing account
3. Go to **"Reports"**
4. Filter by project: `lauyami-app`
5. See daily/monthly costs

### Expected Costs (with $300 credits)

**First 6 months:**
- Months 1-3: $0 (covered by credits)
- Months 4-6: $0-5 (within free tier)

**After credits (realistic for hackathon):**
- Cloud Run: $0-2/month (low traffic, scales to zero)
- Cloud Build: $0 (120 builds/day free)
- Container Registry: $0 (first 0.5GB free)

**Total: $0-2/month for low traffic** 💰

### Set Budget Alerts

1. Go to **Billing** → **Budgets & alerts**
2. Click **"Create Budget"**
3. Set budget: $10/month
4. Set alert at: 50%, 90%, 100%
5. Add your email
6. Click **"Finish"**

---

## 🎉 POST-DEPLOYMENT CHECKLIST

- [ ] Backend URL works: `https://lauyami-backend-xxx.run.app/health`
- [ ] Frontend deployed: `https://lauyami.vercel.app`
- [ ] Can upload a document and get analysis
- [ ] Voice query works
- [ ] TTS (Listen) works
- [ ] PDF report downloads
- [ ] CORS configured correctly
- [ ] Budget alerts set up
- [ ] URLs shared with hackathon judges

---

## 🗑️ CLEANUP (After Hackathon)

To avoid any charges after your demo:

### Delete Cloud Run Service

**CLI:**
```bash
gcloud run services delete lauyami-backend --region europe-west6
```

**Console:**
1. Go to Cloud Run
2. Select `lauyami-backend`
3. Click **"Delete"**

### Delete Container Images

```bash
gcloud container images delete gcr.io/lauyami-app/lauyami-backend
```

### Delete Vercel Project

1. Go to https://vercel.com/dashboard
2. Select your project
3. Settings → Delete Project

**Total cleanup time: 2 minutes**

---

## 📞 NEED HELP?

Common commands for debugging:

```bash
# View logs
gcloud run services logs read lauyami-backend --region europe-west6

# Check service details
gcloud run services describe lauyami-backend --region europe-west6

# List all services
gcloud run services list

# Update environment variable
gcloud run services update lauyami-backend \
  --region europe-west6 \
  --update-env-vars NEW_VAR=value
```

---

## ✅ QUICK REFERENCE

**Your Project Details:**
- Project ID: `lauyami-app`
- Service Name: `lauyami-backend`
- Region: `europe-west6` (Zurich)
- Image: `gcr.io/lauyami-app/lauyami-backend`

**Useful URLs:**
- GCP Console: https://console.cloud.google.com
- Cloud Run: https://console.cloud.google.com/run
- Billing: https://console.cloud.google.com/billing

**Quick Deploy Command:**
```bash
cd /home/teehy/lauyami-app/backend && ./deploy_fastapi.sh
```

---

Good luck with your hackathon! 🚀

