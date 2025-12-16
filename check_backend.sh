#!/bin/bash
# Script to check backend status and get Cloud Run URL

PROJECT_ID="lauyami-app"
SERVICE_NAME="lauyami-backend"
REGION="europe-west6"

echo "🔍 Checking Cloud Run service status..."
echo ""

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)' 2>/dev/null)

if [ -z "$SERVICE_URL" ]; then
    echo "❌ Could not find Cloud Run service: $SERVICE_NAME"
    echo "   Make sure you're logged in: gcloud auth login"
    exit 1
fi

echo "✅ Backend URL: $SERVICE_URL"
echo ""
echo "📋 To configure frontend, set this environment variable:"
echo "   VITE_API_BASE_URL=$SERVICE_URL"
echo ""
echo "🧪 Testing backend health..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" "$SERVICE_URL/docs" || echo "❌ Backend not reachable"
echo ""
echo "📊 Viewing recent logs (last 20 lines)..."
echo "   Run this to see full logs:"
echo "   gcloud run services logs read $SERVICE_NAME --region=$REGION --limit=50"

