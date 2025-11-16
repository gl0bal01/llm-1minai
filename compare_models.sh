#!/bin/bash
# Compare different models for web search

echo "Setting up web_search for all models..."
llm 1min options set --model gpt-4o web_search true
llm 1min options set --model sonar web_search true
llm 1min options set --model sonar-reasoning web_search true

echo ""
echo "========================================"
echo "Testing GPT-4o with web_search"
echo "========================================"
llm -m 1min/gpt-4o "tell me about https://www.sowitty.com" 2>&1 | head -20

echo ""
echo "========================================"
echo "Testing Sonar with web_search"
echo "========================================"
llm -m 1min/sonar "tell me about https://www.sowitty.com" 2>&1 | head -20

echo ""
echo "========================================"
echo "Testing Sonar Reasoning with web_search"
echo "========================================"
llm -m 1min/sonar-reasoning "tell me about https://www.sowitty.com" 2>&1 | head -20
