import React, { useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  Grid,
  Paper,
  TextField,
  Typography,
} from '@mui/material';
import { AutoGraph, Flag, Insights, RocketLaunch } from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8020';
const accent = '#0f766e';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!query.trim()) {
      setError('Please enter a launch scenario.');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/process`, { query, top_k: 5 });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate plan');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', background: 'linear-gradient(180deg, #f4fbfa 0%, #eef2ff 100%)', py: 5 }}>
      <Container maxWidth="lg">
        <Paper sx={{ p: 4, borderRadius: 5, mb: 4, background: 'linear-gradient(135deg, #0f172a 0%, #134e4a 100%)', color: 'white' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <RocketLaunch sx={{ fontSize: 44 }} />
            <Box>
              <Typography variant="h3" fontWeight="bold">Constraint-Aware Launch Planner</Typography>
              <Typography variant="subtitle1" sx={{ opacity: 0.82 }}>
                Constraint-Satisfaction CAG for shipping SOTA MVPs under real-world limits.
              </Typography>
            </Box>
          </Box>
          <TextField
            fullWidth
            multiline
            minRows={3}
            label="Describe the launch challenge"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            sx={{ mb: 2, bgcolor: 'white', borderRadius: 2 }}
          />
          <Button
            variant="contained"
            size="large"
            onClick={handleSubmit}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <AutoGraph />}
            sx={{ bgcolor: '#f59e0b', color: '#111827', '&:hover': { bgcolor: '#d97706' } }}
          >
            {loading ? 'Planning...' : 'Generate Launch Plan'}
          </Button>
        </Paper>

        {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

        {result && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card sx={{ borderRadius: 4, height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>Retrieved Planning Context</Typography>
                  {result.context.map((item) => (
                    <Paper key={item.source} variant="outlined" sx={{ p: 2, mb: 2, borderRadius: 3 }}>
                      <Typography variant="subtitle2" fontWeight="bold">{item.title}</Typography>
                      <Chip size="small" label={`${Math.round(item.relevance * 100)}% match`} sx={{ mt: 1, mb: 1, bgcolor: '#ccfbf1', color: accent }} />
                      <Typography variant="body2" color="text.secondary">{item.content}</Typography>
                    </Paper>
                  ))}
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={8}>
              <Paper sx={{ p: 4, borderRadius: 4, mb: 3, borderTop: `6px solid ${accent}` }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <Flag sx={{ color: accent }} />
                  <Typography variant="h5" fontWeight="bold">Execution Plan</Typography>
                </Box>
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
                  {result.response}
                </Typography>
              </Paper>
              <Paper sx={{ p: 3, borderRadius: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <Insights sx={{ color: accent }} />
                  <Typography variant="h6" fontWeight="bold">Pipeline Steps</Typography>
                </Box>
                {result.process_steps.map((step) => (
                  <Chip key={step.step} label={step.description} sx={{ mr: 1, mb: 1, bgcolor: '#ecfeff', color: '#155e75' }} />
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
