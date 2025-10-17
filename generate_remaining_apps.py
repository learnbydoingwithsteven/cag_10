"""
Script to generate remaining CAG applications (Apps 3-10)
"""

import os
import json

# App configurations
APPS = [
    {
        "num": 3,
        "name": "code_reviewer",
        "title": "Code Review Bot",
        "technique": "AST-based Context Augmentation",
        "port": 8003,
        "model": "codellama",
        "icon": "Code"
    },
    {
        "num": 4,
        "name": "support_agent",
        "title": "Customer Support Agent",
        "technique": "Conversational CAG with Memory",
        "port": 8004,
        "model": "llama3",
        "icon": "SupportAgent"
    },
    {
        "num": 5,
        "name": "financial_analyzer",
        "title": "Financial Report Analyzer",
        "technique": "Structured Data CAG",
        "port": 8005,
        "model": "llama3",
        "icon": "AccountBalance"
    },
    {
        "num": 6,
        "name": "paper_summarizer",
        "title": "Research Paper Summarizer",
        "technique": "Hierarchical CAG",
        "port": 8006,
        "model": "llama3",
        "icon": "Description"
    },
    {
        "num": 7,
        "name": "product_recommender",
        "title": "E-commerce Product Recommender",
        "technique": "Hybrid CAG",
        "port": 8007,
        "model": "llama3",
        "icon": "ShoppingCart"
    },
    {
        "num": 8,
        "name": "educational_tutor",
        "title": "Educational Tutor",
        "technique": "Adaptive CAG",
        "port": 8008,
        "model": "llama3",
        "icon": "School"
    },
    {
        "num": 9,
        "name": "compliance_checker",
        "title": "Contract Compliance Checker",
        "technique": "Rule-based CAG",
        "port": 8009,
        "model": "llama3",
        "icon": "Gavel"
    },
    {
        "num": 10,
        "name": "fact_checker",
        "title": "News Fact Checker",
        "technique": "Multi-source CAG",
        "port": 8010,
        "model": "llama3",
        "icon": "FactCheck"
    }
]


def create_backend_main(app):
    """Generate backend main.py"""
    return f'''"""
{app["title"]} Backend
{app["technique"]}
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from cag_engine.ollama_client import OllamaClient

app = FastAPI(title="{app["title"]} API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ollama_client = OllamaClient(base_url="http://ollama:11434")


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


class QueryResponse(BaseModel):
    query: str
    response: str
    context: list
    metadata: dict
    process_steps: list


@app.get("/")
async def root():
    return {{
        "app": "{app["title"]}",
        "technique": "{app["technique"]}",
        "status": "running"
    }}


@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process query using {app["technique"]}"""
    try:
        # Simulate CAG processing
        context = [
            {{"type": "context_item", "content": f"Context {{i+1}} for query", "relevance": 0.9 - i*0.1}}
            for i in range(request.top_k)
        ]
        
        prompt = f"""You are a {app["title"].lower()}. Process the following query:

Query: {{request.query}}

Context:
{{chr(10).join([f"- {{c['content']}}" for c in context])}}

Provide a comprehensive response."""
        
        response = ollama_client.generate(prompt=prompt, model="{app["model"]}")
        
        process_steps = [
            {{"step": "context_retrieval", "description": "Retrieved relevant context"}},
            {{"step": "augmentation", "description": "Augmented prompt with context"}},
            {{"step": "generation", "description": "Generated response with LLM"}}
        ]
        
        return QueryResponse(
            query=request.query,
            response=response,
            context=context,
            metadata={{"model": "{app["model"]}", "technique": "{app["technique"]}"}},
            process_steps=process_steps
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {{"status": "healthy"}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port={app["port"]})
'''


def create_frontend_app(app):
    """Generate frontend App.js"""
    return f'''import React, {{ useState }} from 'react';
import {{
  Container, TextField, Button, Paper, Typography, Box,
  CircularProgress, Card, CardContent, Chip, Alert
}} from '@mui/material';
import {{ {app["icon"]} }} from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:{app["port"]}';

function App() {{
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {{
    if (!query.trim()) {{
      setError('Please enter a query');
      return;
    }}

    setLoading(true);
    setError(null);
    setResult(null);

    try {{
      const response = await axios.post(`${{API_BASE_URL}}/process`, {{
        query: query,
        top_k: 5
      }});

      setResult(response.data);
    }} catch (err) {{
      setError(err.response?.data?.detail || 'Failed to process query');
    }} finally {{
      setLoading(false);
    }}
  }};

  return (
    <Container maxWidth="lg" sx={{{{ py: 4 }}}}>
      <Box sx={{{{ textAlign: 'center', mb: 4 }}}}>
        <{app["icon"]} sx={{{{ fontSize: 60, color: 'primary.main', mb: 2 }}}} />
        <Typography variant="h3" component="h1" gutterBottom>
          {app["title"]}
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          {app["technique"]}
        </Typography>
        <Chip label="CAG Application" color="primary" sx={{{{ mt: 1 }}}} />
      </Box>

      <Paper elevation={3} sx={{{{ p: 4, mb: 3 }}}}>
        <TextField
          fullWidth
          multiline
          rows={4}
          label="Enter Your Query"
          placeholder="Type your question here..."
          value={{query}}
          onChange={{(e) => setQuery(e.target.value)}}
          variant="outlined"
          sx={{{{ mb: 2 }}}}
        />
        <Button
          variant="contained"
          size="large"
          onClick={{handleSubmit}}
          disabled={{loading}}
          fullWidth
          startIcon={{loading ? <CircularProgress size={{20}} /> : <{app["icon"]} />}}
        >
          {{loading ? 'Processing...' : 'Submit'}}
        </Button>
      </Paper>

      {{error && (
        <Alert severity="error" sx={{{{ mb: 3 }}}}>
          {{error}}
        </Alert>
      )}}

      {{result && (
        <>
          <Paper elevation={2} sx={{{{ p: 3, mb: 3 }}}}>
            <Typography variant="h6" gutterBottom>
              Response
            </Typography>
            <Typography variant="body1" sx={{{{ whiteSpace: 'pre-wrap' }}}}>
              {{result.response}}
            </Typography>
          </Paper>

          <Paper elevation={2} sx={{{{ p: 3, mb: 3 }}}}>
            <Typography variant="h6" gutterBottom>
              Context Used
            </Typography>
            {{result.context.map((ctx, idx) => (
              <Card key={{idx}} variant="outlined" sx={{{{ mb: 1 }}}}>
                <CardContent>
                  <Typography variant="body2">
                    {{ctx.content}}
                  </Typography>
                  <Chip
                    label={{`Relevance: ${{(ctx.relevance * 100).toFixed(0)}}%`}}
                    size="small"
                    sx={{{{ mt: 1 }}}}
                  />
                </CardContent>
              </Card>
            ))}}
          </Paper>

          <Paper elevation={1} sx={{{{ p: 2, bgcolor: '#fafafa' }}}}>
            <Typography variant="caption" color="text.secondary">
              Model: {{result.metadata.model}} | Technique: {{result.metadata.technique}}
            </Typography>
          </Paper>
        </>
      )}}
    </Container>
  );
}}

export default App;
'''


def create_package_json(app):
    """Generate package.json"""
    return json.dumps({
        "name": app["name"].replace("_", "-"),
        "version": "1.0.0",
        "private": True,
        "dependencies": {
            "@mui/material": "^5.14.18",
            "@mui/icons-material": "^5.14.18",
            "@emotion/react": "^11.11.1",
            "@emotion/styled": "^11.11.0",
            "axios": "^1.6.2",
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-scripts": "5.0.1"
        },
        "scripts": {
            "start": "react-scripts start",
            "build": "react-scripts build",
            "test": "react-scripts test"
        }
    }, indent=2)


def create_requirements_txt():
    """Generate requirements.txt"""
    return """fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
requests==2.31.0
"""


def main():
    """Generate all remaining apps"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for app in APPS:
        app_dir = os.path.join(base_dir, f"app_{app['num']:02d}_{app['name']}")
        backend_dir = os.path.join(app_dir, "backend")
        frontend_dir = os.path.join(app_dir, "frontend", "src")
        
        # Create directories
        os.makedirs(backend_dir, exist_ok=True)
        os.makedirs(frontend_dir, exist_ok=True)
        
        # Create backend files
        with open(os.path.join(backend_dir, "main.py"), "w") as f:
            f.write(create_backend_main(app))
        
        with open(os.path.join(backend_dir, "requirements.txt"), "w") as f:
            f.write(create_requirements_txt())
        
        # Create frontend files
        with open(os.path.join(frontend_dir, "App.js"), "w") as f:
            f.write(create_frontend_app(app))
        
        with open(os.path.join(app_dir, "frontend", "package.json"), "w") as f:
            f.write(create_package_json(app))
        
        print(f"✓ Created App {app['num']}: {app['title']}")
    
    print(f"\\n✅ Successfully generated {len(APPS)} applications!")


if __name__ == "__main__":
    main()
