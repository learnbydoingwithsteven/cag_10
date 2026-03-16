import React, { useState } from 'react';
import { Alert, Box, Button, Card, CardContent, CircularProgress, Container, Grid, Paper, TextField, Typography } from '@mui/material';
import { GppMaybe, Policy, PsychologyAlt, WarningAmber } from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8023';
const accent = '#ea580c';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!query.trim()) {
      setError('Please describe the AI system to red-team.');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/process`, { query, top_k: 5 });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate evaluation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', py: 5, background: 'linear-gradient(180deg, #fff7ed 0%, #fff1f2 45%, #f8fafc 100%)' }}>
      <Container maxWidth="lg">
        <Paper sx={{ p: 4, mb: 4, borderRadius: 5, background: 'linear-gradient(135deg, #1f2937 0%, #c2410c 100%)', color: 'white' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <GppMaybe sx={{ fontSize: 44 }} />
            <Box>
              <Typography variant="h3" fontWeight="bold">LLM Guardrail Red-Team Lab</Typography>
              <Typography variant="subtitle1" sx={{ opacity: 0.82 }}>
                Adversarial Evaluation CAG for prompt injection, leakage, and jailbreak risks.
              </Typography>
            </Box>
          </Box>
          <TextField fullWidth multiline minRows={3} label="Describe the AI system" value={query} onChange={(event) => setQuery(event.target.value)} sx={{ mb: 2, bgcolor: 'white', borderRadius: 2 }} />
          <Button variant="contained" size="large" onClick={handleSubmit} disabled={loading} startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <WarningAmber />} sx={{ bgcolor: '#fdba74', color: '#7c2d12', '&:hover': { bgcolor: '#fb923c' } }}>
            {loading ? 'Evaluating...' : 'Run Red-Team Review'}
          </Button>
        </Paper>
        {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
        {result && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card sx={{ borderRadius: 4, height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>Attack Playbook</Typography>
                  {result.context.map((item) => (
                    <Paper key={item.source} variant="outlined" sx={{ p: 2, mb: 2, borderRadius: 3 }}>
                      <Typography variant="subtitle2" fontWeight="bold">{item.title}</Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>{item.content}</Typography>
                    </Paper>
                  ))}
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={8}>
              <Paper sx={{ p: 4, borderRadius: 4, mb: 3, borderTop: `6px solid ${accent}` }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <PsychologyAlt sx={{ color: accent }} />
                  <Typography variant="h5" fontWeight="bold">Evaluation Report</Typography>
                </Box>
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>{result.response}</Typography>
              </Paper>
              <Paper sx={{ p: 3, borderRadius: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <Policy sx={{ color: accent }} />
                  <Typography variant="h6" fontWeight="bold">Process Steps</Typography>
                </Box>
                {result.process_steps.map((step) => (
                  <Typography key={step.step} variant="body2" sx={{ mb: 1.2 }}><strong>{step.step}</strong>: {step.description}</Typography>
                ))}
              </Paper>
            </Grid>
          </Grid>
        )}
      </Container>
    </Box>
  );
}

export default App;
