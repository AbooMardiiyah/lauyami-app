#!/bin/bash
# -----------------------
# FastAPI Backend Deployment to Cloud Run
# -----------------------

# Exit immediately if a command exits with a non-zero status
set -e

#-----------------------
# Load environment variables
#-----------------------

if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    exit 1
fi

set -o allexport
source .env
set +o allexport

echo "✅ Environment variables loaded."

PROJECT_ID="lauyami-project"
SERVICE_NAME="lauyami-backend"
REGION="europe-west6" #europe-west1 "europe-west6"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"


echo "🔧 Setting GCP project to $PROJECT_ID..."
gcloud config set project "$PROJECT_ID"

echo "🔧 Enabling required GCP services..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com


echo "🐳 Building and pushing Docker image..."
gcloud builds submit --config cloudbuild_fastapi.yaml \
    --substitutions=_SERVICE_NAME=$SERVICE_NAME

echo "🚀 Deploying $SERVICE_NAME to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
--image "$IMAGE_NAME" \
--platform managed \
--region "$REGION" \
--allow-unauthenticated \
--memory 2.5Gi \
--cpu 1 \
--timeout 300 \
--concurrency 2 \
--min-instances 0 \
--max-instances 2 \
--execution-environment gen2 \
--cpu-boost \
--set-env-vars HF_HOME=/tmp/huggingface \
--set-env-vars FASTEMBED_CACHE=/tmp/fastembed_cache \
--set-env-vars HUGGING_FACE__API_KEY=$HUGGING_FACE__API_KEY \
--set-env-vars OPENAI__API_KEY=$OPENAI__API_KEY \
--set-env-vars QDRANT__API_KEY=$QDRANT__API_KEY \
--set-env-vars QDRANT__URL=$QDRANT__URL \
--set-env-vars QDRANT__COLLECTION_NAME=$QDRANT__COLLECTION_NAME \
--set-env-vars QDRANT__DENSE_MODEL_NAME=$QDRANT__DENSE_MODEL_NAME \
--set-env-vars QDRANT__SPARSE_MODEL_NAME=$QDRANT__SPARSE_MODEL_NAME \
--set-env-vars MODAL__LLM_BASE_URL=$MODAL__LLM_BASE_URL \
--set-env-vars MODAL__LLM_API_KEY=$MODAL__LLM_API_KEY \
--set-env-vars MODAL__ASR_BASE_URL=$MODAL__ASR_BASE_URL \
--set-env-vars YARNGPT__API_KEY=$YARNGPT__API_KEY \
--set-env-vars YARNGPT__API_URL=$YARNGPT__API_URL \
--set-env-vars "^@^ALLOWED_ORIGINS=$ALLOWED_ORIGINS@" \

echo "✅ Allowed origins set to: $ALLOWED_ORIGINS"

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')
echo "Deployment complete!"
echo "Service URL: $SERVICE_URL"
