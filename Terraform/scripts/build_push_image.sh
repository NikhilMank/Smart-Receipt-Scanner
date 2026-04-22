#!/usr/bin/env bash
set -euo pipefail

REGION="$1"
REPO_URL="$2"
IMAGE_URI="$3"
CONTEXT_DIR="$4"

aws ecr get-login-password --region "$REGION" \
    | docker login --username AWS --password-stdin "$REPO_URL"

docker build -t "$IMAGE_URI" "$CONTEXT_DIR"
docker push "$IMAGE_URI"