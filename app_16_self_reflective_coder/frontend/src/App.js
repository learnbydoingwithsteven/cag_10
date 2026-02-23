import React, { useState } from 'react';
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
