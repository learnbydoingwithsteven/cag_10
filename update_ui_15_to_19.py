import os

APPS_UI_DATA = {
    15: '''import React, { useState } from 'react';
import {
  Container, TextField, Button, Paper, Typography, Box,
  CircularProgress, Card, CardContent, Chip, Alert, Grid, Avatar
} from '@mui/material';
import { GroupWork, Person, Psychology, FactCheck } from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8015';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/process`, {
        query: query,
        top_k: 5
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process query');
    } finally {
      setLoading(false);
    }
  };

  const getPersonaIcon = (type) => {
    if (type.includes("optimist")) return <Person sx={{bgcolor:"#4caf50", color:"white", p:1, borderRadius:"50%"}}/>;
    if (type.includes("pessimist")) return <Psychology sx={{bgcolor:"#f44336", color:"white", p:1, borderRadius:"50%"}}/>;
    if (type.includes("analyst")) return <FactCheck sx={{bgcolor:"#2196f3", color:"white", p:1, borderRadius:"50%"}}/>;
    return <GroupWork />;
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <GroupWork sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
        <Typography variant="h3" component="h1" gutterBottom fontWeight="bold">
          Multi-Agent Strategy Debater
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Multi-Agent Debate CAG Simulation
        </Typography>
      </Box>

      <Paper elevation={3} sx={{ p: 4, mb: 4, borderRadius: 3 }}>
        <TextField
          fullWidth multiline rows={3}
          label="What business proposition should we debate?"
          value={query} onChange={(e) => setQuery(e.target.value)}
          variant="outlined" sx={{ mb: 2 }}
        />
        <Button variant="contained" size="large" onClick={handleSubmit} disabled={loading} fullWidth startIcon={loading ? <CircularProgress size={20} /> : <GroupWork />}>
          {loading ? 'Agents are debating...' : 'Start Debate'}
        </Button>
      </Paper>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {result && (
        <Box>
          <Typography variant="h5" sx={{mb: 2, fontWeight: "bold"}}>Debate Perspectives</Typography>
          <Grid container spacing={3} sx={{mb:4}}>
            {result.context.slice(0, 2).map((ctx, idx) => (
              <Grid item xs={12} md={6} key={idx}>
                <Card sx={{height: '100%', borderRadius: 3, boxShadow: 3, borderTop: `5px solid ${ctx.type.includes('optimist') ? '#4caf50' : '#f44336'}`}}>
                  <CardContent>
                    <Box sx={{display:'flex', alignItems:'center', mb:2}}>
                      {getPersonaIcon(ctx.type)}
                      <Typography variant="h6" sx={{ml:2, textTransform: 'capitalize'}}>{ctx.type.replace('_', ' ')}</Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{whiteSpace: 'pre-wrap'}}>{ctx.content}</Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
          
          <Paper elevation={4} sx={{ p: 4, borderRadius: 3, borderLeft: '5px solid #2196f3', bgcolor: '#f8fbff' }}>
            <Box sx={{display:'flex', alignItems:'center', mb:2}}>
              {getPersonaIcon('analyst')}
              <Typography variant="h5" sx={{ml:2, fontWeight:"bold"}}>Final Analyst Synthesis</Typography>
            </Box>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
              {result.response}
            </Typography>
          </Paper>
        </Box>
      )}
    </Container>
  );
}

export default App;
''',
    16: '''import React, { useState } from 'react';
import {
  Container, TextField, Button, Paper, Typography, Box,
  CircularProgress, Alert, Stepper, Step, StepLabel, StepContent
} from '@mui/material';
import { Engineering, Code, BugReport, AutoFixHigh } from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8016';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!query.trim()) { setError('Please enter a query'); return; }
    setLoading(true); setError(null); setResult(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/process`, { query, top_k: 5 });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process query');
    } finally {
      setLoading(false);
    }
  };

  const getStepIcon = (type) => {
    if (type.includes("initial")) return <Code color="primary" />;
    if (type.includes("critique")) return <BugReport color="error" />;
    return <AutoFixHigh color="success" />;
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Engineering sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
        <Typography variant="h3" fontWeight="bold" gutterBottom>Self-Reflective Code Generator</Typography>
        <Typography variant="subtitle1" color="text.secondary">Reflexion-based CAG with Code Self-Evaluation</Typography>
      </Box>

      <Paper elevation={3} sx={{ p: 4, mb: 4, borderRadius: 3 }}>
        <TextField fullWidth multiline rows={3} label="Describe the code you want to generate" value={query} onChange={(e) => setQuery(e.target.value)} sx={{ mb: 2 }} />
        <Button variant="contained" size="large" onClick={handleSubmit} disabled={loading} fullWidth startIcon={loading ? <CircularProgress size={20} /> : <Engineering />}>
          {loading ? 'Reflecting and Coding...' : 'Generate Code'}
        </Button>
      </Paper>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {result && (
        <Box>
          <Typography variant="h5" sx={{mb: 3, fontWeight: "bold"}}>Reflexion Process</Typography>
          <Paper elevation={2} sx={{p:3, borderRadius: 3, mb: 4}}>
            <Stepper orientation="vertical" activeStep={result.context.length}>
              {result.context.map((ctx, idx) => (
                <Step key={idx} expanded={true}>
                  <StepLabel icon={getStepIcon(ctx.type)}>
                    <Typography variant="h6" sx={{textTransform: 'capitalize'}}>{ctx.type.replace('_', ' ')}</Typography>
                  </StepLabel>
                  <StepContent>
                    <Box sx={{ bgcolor: '#1e1e1e', color: '#d4d4d4', p: 2, borderRadius: 2, fontFamily: 'monospace', overflowX: 'auto', mt: 1 }}>
                      <pre style={{ margin: 0 }}>{ctx.content}</pre>
                    </Box>
                  </StepContent>
                </Step>
              ))}
            </Stepper>
          </Paper>
        </Box>
      )}
    </Container>
  );
}

export default App;
''',
    17: '''import React, { useState } from 'react';
import {
  Container, TextField, Button, Paper, Typography, Box,
  CircularProgress, Alert, Card, CardContent, Grid, Divider
} from '@mui/material';
import { AccountTree, EmojiObjects, Assessment, DoneAll } from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8017';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!query.trim()) { setError('Please enter a query'); return; }
    setLoading(true); setError(null); setResult(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/process`, { query, top_k: 5 });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <AccountTree sx={{ fontSize: 60, color: '#9c27b0', mb: 2 }} />
        <Typography variant="h3" fontWeight="bold" gutterBottom>Tree of Thoughts Solver</Typography>
        <Typography variant="subtitle1" color="text.secondary">Explore Multiple Reasoning Paths</Typography>
      </Box>

      <Paper elevation={3} sx={{ p: 4, mb: 4, borderRadius: 3 }}>
        <TextField fullWidth multiline rows={3} label="State your complex logic or math problem" value={query} onChange={(e) => setQuery(e.target.value)} sx={{ mb: 2 }} />
        <Button variant="contained" color="secondary" size="large" onClick={handleSubmit} disabled={loading} fullWidth startIcon={loading ? <CircularProgress size={20} /> : <AccountTree />}>
          {loading ? 'Searching Tree...' : 'Solve Problem'}
        </Button>
      </Paper>

      {error && <Alert severity="error">{error}</Alert>}

      {result && (
        <Box>
          <Grid container spacing={3}>
            {result.context.map((ctx, idx) => (
              <Grid item xs={12} key={idx}>
                <Card sx={{boxShadow: 2, borderRadius: 2, borderLeft: `5px solid ${idx === 0 ? '#ff9800' : '#2196f3'}`}}>
                  <CardContent>
                    <Box sx={{display: 'flex', alignItems: 'center', mb: 1}}>
                      {idx === 0 ? <EmojiObjects sx={{color: '#ff9800', mr:1}}/> : <Assessment sx={{color: '#2196f3', mr:1}}/>}
                      <Typography variant="h6" sx={{textTransform: 'capitalize'}}>{ctx.type}</Typography>
                    </Box>
                    <Typography variant="body2" sx={{whiteSpace: 'pre-wrap', color: 'text.secondary'}}>{ctx.content}</Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
            <Grid item xs={12}>
                <Paper elevation={4} sx={{ p: 4, borderRadius: 3, border: '2px solid #4caf50', bgcolor: '#f1f8e9' }}>
                  <Box sx={{display: 'flex', alignItems: 'center', mb: 2}}>
                    <DoneAll sx={{color: '#4caf50', mr:1, fontSize: 30}}/>
                    <Typography variant="h5" fontWeight="bold" color="#2e7d32">Final Optimal Execution</Typography>
                  </Box>
                  <Divider sx={{mb:2}}/>
                  <Typography variant="body1" sx={{whiteSpace: 'pre-wrap'}}>{result.response}</Typography>
                </Paper>
            </Grid>
          </Grid>
        </Box>
      )}
    </Container>
  );
}

export default App;
''',
    18: '''import React, { useState } from 'react';
import {
  Container, TextField, Button, Paper, Typography, Box,
  CircularProgress, Alert, Chip, Card, CardContent
} from '@mui/material';
import { Create, AutoAwesome, HistoryEdu } from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8018';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!query.trim()) { setError('Please enter a query'); return; }
    setLoading(true); setError(null); setResult(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/process`, { query, top_k: 5 });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Create sx={{ fontSize: 60, color: '#e91e63', mb: 2 }} />
        <Typography variant="h3" fontWeight="bold" gutterBottom>Dynamic Few-Shot Copywriter</Typography>
        <Typography variant="subtitle1" color="text.secondary">Data-Driven Ad Copy Generation</Typography>
      </Box>

      <Paper elevation={3} sx={{ p: 4, mb: 4, borderRadius: 3 }}>
        <TextField fullWidth multiline rows={3} label="What product do you need copy for?" value={query} onChange={(e) => setQuery(e.target.value)} sx={{ mb: 2 }} />
        <Button variant="contained" sx={{bgcolor: '#e91e63', '&:hover': {bgcolor: '#c2185b'}}} size="large" onClick={handleSubmit} disabled={loading} fullWidth startIcon={loading ? <CircularProgress size={20} /> : <AutoAwesome />}>
          {loading ? 'Crafting Copy...' : 'Generate High-Converting Copy'}
        </Button>
      </Paper>

      {error && <Alert severity="error">{error}</Alert>}

      {result && (
        <Box>
          <Box sx={{mb:4}}>
            <Typography variant="h6" fontWeight="bold" sx={{mb: 2, display:'flex', alignItems:'center'}}>
              <HistoryEdu sx={{mr:1}}/> Dynamically Selected Template
            </Typography>
            {result.context.map((ctx, idx) => (
               <Card key={idx} sx={{mb: 4, borderRadius: 2, bgcolor: '#f5f5f5', borderStyle: 'dashed', borderWidth: 2, borderColor: '#bdbdbd'}}>
                <CardContent>
                  <Chip label={ctx.type.replace(/_/g, ' ')} color="primary" size="small" sx={{textTransform: 'uppercase', mb: 1, fontWeight: 'bold'}}/>
                  <Typography variant="body1" fontStyle="italic">"{ctx.content}"</Typography>
                </CardContent>
               </Card>
            ))}
          </Box>

          <Paper elevation={4} sx={{ p: 4, borderRadius: 3, background: 'linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%)' }}>
            <Typography variant="h5" fontWeight="bold" color="#e65100" sx={{mb: 2}}>Final Ad Copy</Typography>
            <Typography variant="h6" sx={{whiteSpace: 'pre-wrap', lineHeight: 1.6, color: '#3e2723'}}>{result.response}</Typography>
          </Paper>
        </Box>
      )}
    </Container>
  );
}

export default App;
''',
    19: '''import React, { useState } from 'react';
import {
  Container, TextField, Button, Paper, Typography, Box,
  CircularProgress, Alert, Stepper, Step, StepLabel, StepContent, Grid
} from '@mui/material';
import { Timeline, EventNote, TrendingUp } from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8019';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!query.trim()) { setError('Please enter a query'); return; }
    setLoading(true); setError(null); setResult(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/process`, { query, top_k: 5 });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Timeline sx={{ fontSize: 60, color: '#009688', mb: 2 }} />
        <Typography variant="h3" fontWeight="bold" gutterBottom>Temporal Market Forecaster</Typography>
        <Typography variant="subtitle1" color="text.secondary">Time-Aware RAG Pattern</Typography>
      </Box>

      <Paper elevation={3} sx={{ p: 4, mb: 4, borderRadius: 3 }}>
        <TextField fullWidth multiline rows={2} label="Enter market query (e.g. AI sector outlook)" value={query} onChange={(e) => setQuery(e.target.value)} sx={{ mb: 2 }} />
        <Button variant="contained" sx={{bgcolor: '#009688', '&:hover': {bgcolor: '#00796b'}}} size="large" onClick={handleSubmit} disabled={loading} fullWidth startIcon={loading ? <CircularProgress size={20} /> : <TrendingUp />}>
          {loading ? 'Forecasting...' : 'Forecast Trend'}
        </Button>
      </Paper>

      {error && <Alert severity="error">{error}</Alert>}

      {result && (
        <Grid container spacing={4}>
          <Grid item xs={12} md={5}>
            <Typography variant="h6" fontWeight="bold" sx={{mb: 2, color: '#00796b'}}>Chronological Events Timeline</Typography>
            <Stepper orientation="vertical" activeStep={result.context.length}>
              {result.context.map((ctx, idx) => {
                const parts = ctx.content.split('] ');
                const date = parts[0].replace('[', '');
                const desc = parts[1];
                return (
                  <Step key={idx} expanded={true}>
                    <StepLabel icon={<EventNote />}>
                      <Typography variant="subtitle2" fontWeight="bold">{date}</Typography>
                    </StepLabel>
                    <StepContent>
                      <Typography variant="body2" color="text.secondary">{desc}</Typography>
                    </StepContent>
                  </Step>
                );
              })}
            </Stepper>
          </Grid>
          <Grid item xs={12} md={7}>
            <Paper elevation={5} sx={{ p: 4, borderRadius: 3, height: '100%', bgcolor: '#e0f2f1', borderTop: '5px solid #009688' }}>
              <Box sx={{display: 'flex', alignItems: 'center', mb: 2}}>
                <TrendingUp sx={{mr: 1, color: '#00796b', fontSize: 32}}/>
                <Typography variant="h5" fontWeight="bold" color="#00695c">Future Market Forecast</Typography>
              </Box>
              <Typography variant="body1" sx={{whiteSpace: 'pre-wrap', lineHeight: 1.8, color: '#004d40'}}>
                {result.response}
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      )}
    </Container>
  );
}

export default App;
'''
}

base_dir = os.path.dirname(os.path.abspath(__file__))

for app_num, content in APPS_UI_DATA.items():
    app_dir_name = None
    for d in os.listdir(base_dir):
        if d.startswith(f"app_{app_num:02d}_"):
            app_dir_name = d
            break
            
    if app_dir_name:
        file_path = os.path.join(base_dir, app_dir_name, "frontend", "src", "App.js")
        if os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Updated UI for {app_dir_name}")
        else:
            print(f"Warning: {file_path} not found")

print("Successfully updated App 15-19 UIs!")
