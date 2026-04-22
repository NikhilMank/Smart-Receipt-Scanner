#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:?repo root required (arg1)}"
BUCKET_NAME="${2:?bucket name required (arg2)}"
API_BASE_URL="${3:?API base URL required (arg3)}"

FRONTEND_DIR="$REPO_ROOT/../frontend"
BUILD_DIR="$FRONTEND_DIR/build"

echo "==> Repo root: $REPO_ROOT"
echo "==> Bucket name: $BUCKET_NAME"
echo "==> API base URL: $API_BASE_URL"
echo "==> Frontend directory: $FRONTEND_DIR"
echo "==> Build directory: $BUILD_DIR"

cd "$FRONTEND_DIR"

echo "REACT_APP_API_URL=$API_BASE_URL" > .env

echo "==> Installing frontend dependencies..."
if [ -f package-lock.json ]; then
  echo "==> Building frontend with existing node_modules..."
  npm run build
else
  npm install
  echo "==> Building frontend..."
  npm run build
fi

echo "==> Uploading build to S3 bucket..."

aws s3 cp "${BUILD_DIR}/index.html" "s3://${BUCKET_NAME}/index.html" \
  --cache-control "no-cache"

aws s3 cp "${BUILD_DIR}/asset-manifest.json" "s3://${BUCKET_NAME}/asset-manifest.json" \
  --cache-control "no-cache"

aws s3 sync "${BUILD_DIR}/static" "s3://${BUCKET_NAME}/static" --delete \
  --cache-control "public,max-age=31536000,immutable"

echo "✅ Done"