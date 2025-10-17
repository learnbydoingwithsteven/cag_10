# Quick Start Guide - 10 Ollama CAG Applications

## 🚀 Get Started in 5 Minutes

### Prerequisites Check
```bash
# Check if Ollama is installed
ollama --version

# Check if Docker is installed
docker --version
docker-compose --version

# Check if Python is installed
python --version  # Should be 3.10+

# Check if Node.js is installed
node --version    # Should be 18+
```

### Step 1: Install Ollama (if not installed)
```bash
# Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download
```

### Step 2: Pull Required Models
```bash
# Essential models (run these first)
ollama pull llama3          # 4.7GB - General purpose
ollama pull mistral         # 4.1GB - Fast inference
ollama pull codellama       # 3.8GB - Code analysis
ollama pull nomic-embed-text # 274MB - Embeddings

# Optional specialized models
ollama pull meditron        # Medical domain
```

### Step 3: Clone and Setup
```bash
# Clone repository
git clone <your-repo-url>
cd cag_10

# Install shared dependencies
pip install -r shared/requirements.txt
```

### Step 4: Start Services with Docker
```bash
# Start all infrastructure services
docker-compose up -d

# Wait for services to be healthy (30-60 seconds)
docker-compose ps

# Check logs if needed
docker-compose logs -f
```

### Step 5: Run Your First App

#### Option A: Run All Apps (Recommended)
```bash
# Start all 10 applications
./start_all_apps.sh

# Or manually with Docker
docker-compose up -d app_legal_analyzer app_medical_assistant app_code_reviewer
```

#### Option B: Run Single App (Legal Analyzer)
```bash
cd app_01_legal_analyzer

# Start backend
cd backend
pip install -r requirements.txt
python main.py &

# Start frontend (new terminal)
cd frontend
npm install
npm start
```

### Step 6: Access Applications

Open your browser and visit:

- **Legal Analyzer**: http://localhost:8001
- **Medical Assistant**: http://localhost:8002
- **Code Reviewer**: http://localhost:8003
- **Support Agent**: http://localhost:8004
- **Financial Analyzer**: http://localhost:8005
- **Paper Summarizer**: http://localhost:8006
- **Product Recommender**: http://localhost:8007
- **Educational Tutor**: http://localhost:8008
- **Compliance Checker**: http://localhost:8009
- **Fact Checker**: http://localhost:8010

**Monitoring**:
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

---

## 🧪 Test Your Setup

### Test 1: Check Ollama
```bash
curl http://localhost:11434/api/tags
# Should return list of installed models
```

### Test 2: Check ChromaDB
```bash
curl http://localhost:8000/api/v1/heartbeat
# Should return heartbeat response
```

### Test 3: Test Legal Analyzer API
```bash
curl -X POST http://localhost:8001/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is a motion to dismiss?",
    "context_limit": 3,
    "temperature": 0.3,
    "max_tokens": 500
  }'
```

### Test 4: Upload Sample Document
```bash
curl -X POST http://localhost:8001/documents/upload \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sample Legal Document",
    "content": "This is a sample legal document about contract law...",
    "metadata": {"type": "contract"}
  }'
```

---

## 📊 Run Evaluation Pipeline

```bash
# Run comprehensive evaluation
python shared/evaluation/run_all_evaluations.py \
  --output-dir ./evaluation_results \
  --save-metrics

# View results
cat evaluation_results/summary.json

# Generate HTML report
python shared/evaluation/generate_report.py \
  --input-dir ./evaluation_results \
  --output report.html

# Open report in browser
open report.html  # Mac
xdg-open report.html  # Linux
start report.html  # Windows
```

---

## 🎯 Example Queries for Each App

### 1. Legal Document Analyzer
```
"What are the requirements for filing a motion to dismiss?"
"Explain the doctrine of res judicata"
"What is the statute of limitations for breach of contract?"
```

### 2. Medical Diagnosis Assistant
```
"Patient has fever, cough, and fatigue for 3 days. What could it be?"
"What are the symptoms of type 2 diabetes?"
"Explain the treatment options for hypertension"
```

### 3. Code Review Bot
```python
# Submit this code for review
def process_user_input(user_input):
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"
    return execute_query(query)
```

### 4. Customer Support Agent
```
"I can't log into my account"
"How do I reset my password?"
"My order hasn't arrived yet"
```

### 5. Financial Report Analyzer
```
"Analyze the Q3 2023 earnings report"
"What is the trend in profit margins over the last 3 years?"
"Compare revenue growth to industry average"
```

### 6. Research Paper Summarizer
```
"Summarize this paper on transformer architectures"
"What are the key findings of this study?"
"Explain the methodology used in this research"
```

### 7. E-commerce Product Recommender
```
"Recommend products similar to wireless headphones"
"What should I buy based on my purchase history?"
"Show me trending products in electronics"
```

### 8. Educational Tutor
```
"Explain the Pythagorean theorem"
"Help me understand calculus derivatives"
"What is the difference between mitosis and meiosis?"
```

### 9. Contract Compliance Checker
```
"Check this employment contract for GDPR compliance"
"Verify if this NDA meets legal requirements"
"Identify missing clauses in this service agreement"
```

### 10. News Fact Checker
```
"Verify: The unemployment rate decreased by 2% last month"
"Check this claim about climate change statistics"
"Is this news article factually accurate?"
```

---

## 🐛 Troubleshooting

### Issue: Ollama not responding
```bash
# Check if Ollama is running
ps aux | grep ollama

# Restart Ollama
systemctl restart ollama  # Linux
# Or restart the Ollama app on Mac/Windows

# Check logs
journalctl -u ollama -f  # Linux
```

### Issue: ChromaDB connection error
```bash
# Check if ChromaDB container is running
docker ps | grep chromadb

# Restart ChromaDB
docker-compose restart chromadb

# Check logs
docker logs cag_chromadb
```

### Issue: Port already in use
```bash
# Find process using port 8001
lsof -i :8001  # Mac/Linux
netstat -ano | findstr :8001  # Windows

# Kill process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows

# Or change port in app config
```

### Issue: Out of memory
```bash
# Check memory usage
docker stats

# Reduce concurrent apps
docker-compose stop app_medical_assistant app_code_reviewer

# Or increase Docker memory limit
# Docker Desktop > Settings > Resources > Memory
```

### Issue: Slow response times
```bash
# Check if models are loaded
ollama list

# Use smaller models
ollama pull llama3:8b  # Instead of llama3:70b

# Reduce context_limit in queries
# Change from context_limit: 10 to context_limit: 3
```

---

## 📈 Performance Optimization

### 1. Use Model Quantization
```bash
# Pull quantized models (faster, less memory)
ollama pull llama3:8b-q4_0
ollama pull mistral:7b-q4_0
```

### 2. Enable Caching
```python
# In your app config
ENABLE_CACHE = True
CACHE_TTL = 3600  # 1 hour
```

### 3. Batch Requests
```python
# Process multiple queries together
results = await process_batch([query1, query2, query3])
```

### 4. Optimize Context Size
```python
# Reduce context chunks
context_limit = 3  # Instead of 10

# Reduce chunk size
chunk_size = 300  # Instead of 500
```

---

## 🔐 Security Best Practices

### 1. Set Environment Variables
```bash
# Create .env file
cat > .env << EOF
OLLAMA_HOST=http://localhost:11434
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/db
EOF
```

### 2. Enable Authentication
```python
# Add to FastAPI app
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/analyze")
async def analyze(request: Request, token: str = Depends(security)):
    # Verify token
    pass
```

### 3. Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/analyze")
@limiter.limit("10/minute")
async def analyze(request: Request):
    pass
```

---

## 📚 Next Steps

### 1. Customize Applications
- Modify prompts in `*_rag.py` files
- Adjust temperature and max_tokens
- Add custom evaluation metrics

### 2. Add Your Own Data
```bash
# Upload documents via API
curl -X POST http://localhost:8001/documents/upload-file \
  -F "file=@your_document.pdf"
```

### 3. Deploy to Production
```bash
# Build Docker images
docker-compose build

# Push to registry
docker-compose push

# Deploy with Kubernetes
kubectl apply -f k8s/
```

### 4. Monitor Performance
- Set up Grafana dashboards
- Configure alerts
- Track metrics over time

### 5. Contribute
- Fork the repository
- Add new CAG techniques
- Submit pull requests

---

## 🆘 Getting Help

- **Documentation**: See `COMPLETE_IMPLEMENTATION_GUIDE.md`
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@example.com

---

## ✅ Checklist

- [ ] Ollama installed and running
- [ ] Required models downloaded
- [ ] Docker services started
- [ ] At least one app running
- [ ] Test query successful
- [ ] Monitoring accessible
- [ ] Evaluation pipeline tested

**Congratulations! You're ready to use the CAG applications! 🎉**
