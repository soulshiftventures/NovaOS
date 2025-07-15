#!/usr/bin/env bash
docker-compose down --remove-orphans
docker-compose up --build -d

echo "✅ NovaOS live."

deploy_team() {
  idea="$1"
  docker exec nova-core \
    sh -c "python -u agents/NOVA-CORE/main.py <<< 'New Idea R&D: $idea'"
  echo "🚀 Deployed R&D team for: $idea"
}

echo "Use: deploy_team 'Your Idea'"
