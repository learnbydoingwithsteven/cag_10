#!/bin/bash

# Start All CAG Applications Script
# This script starts all 10 Ollama CAG applications

set -e

echo "=========================================="
echo "Starting 10 Ollama CAG Applications"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}Error: Ollama is not installed${NC}"
    echo "Install from: https://ollama.com/download"
    exit 1
fi
echo -e "${GREEN}✓ Ollama installed${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker installed${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose installed${NC}"

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${YELLOW}Starting Ollama service...${NC}"
    # Try to start Ollama (platform-specific)
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo systemctl start ollama
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        open -a Ollama
    fi
    sleep 5
fi
echo -e "${GREEN}✓ Ollama is running${NC}"

# Check required models
echo -e "${YELLOW}Checking required models...${NC}"
REQUIRED_MODELS=("llama3" "mistral" "codellama" "nomic-embed-text")

for model in "${REQUIRED_MODELS[@]}"; do
    if ollama list | grep -q "$model"; then
        echo -e "${GREEN}✓ Model $model is available${NC}"
    else
        echo -e "${YELLOW}Pulling model $model...${NC}"
        ollama pull "$model"
    fi
done

# Start infrastructure services
echo -e "${YELLOW}Starting infrastructure services...${NC}"
docker-compose up -d chromadb redis postgres mongodb neo4j elasticsearch

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Check service health
echo -e "${YELLOW}Checking service health...${NC}"

# ChromaDB
if curl -s http://localhost:8000/api/v1/heartbeat > /dev/null 2>&1; then
    echo -e "${GREEN}✓ ChromaDB is ready${NC}"
else
    echo -e "${RED}✗ ChromaDB is not responding${NC}"
fi

# Redis
if docker exec cag_redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis is ready${NC}"
else
    echo -e "${RED}✗ Redis is not responding${NC}"
fi

# Start all applications
echo -e "${YELLOW}Starting all 10 applications...${NC}"

APPS=(
    "app_legal_analyzer:8001:Legal Document Analyzer"
    "app_medical_assistant:8002:Medical Diagnosis Assistant"
    "app_code_reviewer:8003:Code Review Bot"
    "app_support_agent:8004:Customer Support Agent"
    "app_financial_analyzer:8005:Financial Report Analyzer"
    "app_paper_summarizer:8006:Research Paper Summarizer"
    "app_product_recommender:8007:E-commerce Product Recommender"
    "app_educational_tutor:8008:Educational Tutor"
    "app_compliance_checker:8009:Contract Compliance Checker"
    "app_fact_checker:8010:News Fact Checker"
)

for app_info in "${APPS[@]}"; do
    IFS=':' read -r app_name port display_name <<< "$app_info"
    echo -e "${YELLOW}Starting $display_name...${NC}"
    docker-compose up -d "$app_name" 2>/dev/null || echo -e "${RED}✗ Failed to start $display_name${NC}"
done

# Wait for apps to start
echo -e "${YELLOW}Waiting for applications to start...${NC}"
sleep 15

# Check application health
echo ""
echo "=========================================="
echo "Application Status"
echo "=========================================="

for app_info in "${APPS[@]}"; do
    IFS=':' read -r app_name port display_name <<< "$app_info"
    
    if curl -s "http://localhost:$port/" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $display_name - http://localhost:$port${NC}"
    else
        echo -e "${RED}✗ $display_name - Not responding${NC}"
    fi
done

# Start monitoring services
echo ""
echo -e "${YELLOW}Starting monitoring services...${NC}"
docker-compose up -d prometheus grafana

echo ""
echo "=========================================="
echo "Monitoring Services"
echo "=========================================="
echo -e "${GREEN}✓ Prometheus - http://localhost:9090${NC}"
echo -e "${GREEN}✓ Grafana - http://localhost:3000 (admin/admin)${NC}"

# Summary
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "All applications are now running. You can access them at:"
echo ""
echo "  Legal Document Analyzer:       http://localhost:8001"
echo "  Medical Diagnosis Assistant:   http://localhost:8002"
echo "  Code Review Bot:               http://localhost:8003"
echo "  Customer Support Agent:        http://localhost:8004"
echo "  Financial Report Analyzer:     http://localhost:8005"
echo "  Research Paper Summarizer:     http://localhost:8006"
echo "  E-commerce Recommender:        http://localhost:8007"
echo "  Educational Tutor:             http://localhost:8008"
echo "  Contract Compliance Checker:   http://localhost:8009"
echo "  News Fact Checker:             http://localhost:8010"
echo ""
echo "Monitoring:"
echo "  Grafana:                       http://localhost:3000"
echo "  Prometheus:                    http://localhost:9090"
echo ""
echo "To stop all services:"
echo "  docker-compose down"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f [service_name]"
echo ""
echo "=========================================="
