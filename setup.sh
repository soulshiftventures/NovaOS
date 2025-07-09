#!/bin/bash

echo "🔧 Setting up NovaOS file structure..."

mkdir -p Agents/CEO-VISION
mkdir -p Agents/CTO-AUTO
mkdir -p Agents/NOVA-CORE
mkdir -p Logs
mkdir -p Prompts
mkdir -p Output
mkdir -p agents/core
mkdir -p agents/blueprints

touch .env.example
echo "OPENAI_API_KEY=your-openai-key-here" > .env.example

echo "✅ File structure created and .env.example initialized."


