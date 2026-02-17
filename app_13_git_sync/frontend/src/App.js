import React, { useState } from 'react';
import {
  Container, TextField, Button, Paper, Typography, Box,
  CircularProgress, Card, CardContent, Chip, Alert, Divider
} from '@mui/material';
import { Sync, Terminal, Code } from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8013';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!query.trim()) {
      setError('Please describe your git situation.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/analyze`, {
        query: query
      });

      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze git scenario');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Sync sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
        <Typography variant="h3" component="h1" gutterBottom>
          Git Sync Assistant
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Expert advice for git synchronization, conflicts, and workflows
        </Typography>
        <Chip label="SOTA CAG Application" color="secondary" sx={{ mt: 1 }} />
      </Box>

      <Paper elevation={3} sx={{ p: 4, mb: 3 }}>
        <TextField
          fullWidth
          multiline
          rows={4}
          label="Describe your Git Situation"
          placeholder="e.g., I have a merge conflict in main.py, or I forgot to pull before pushing..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          variant="outlined"
          sx={{ mb: 2 }}
        />
        <Button
          variant="contained"
          size="large"
          onClick={handleSubmit}
          disabled={loading}
          fullWidth
          startIcon={loading ? <CircularProgress size={20} /> : <Terminal />}
        >
          {loading ? 'Analyzing Repository State...' : 'Get Expert Advice'}
        </Button>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {result && (
        <>
          <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Code color="action" sx={{ mr: 1 }} />
                <Typography variant="h5">
                  Expert Recommendation
                </Typography>
            </Box>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '1.1rem' }}>
              {result.response}
            </Typography>
          </Paper>

          <Paper elevation={2} sx={{ p: 3, mb: 3, bgcolor: '#f5f5f5' }}>
            <Typography variant="h6" gutterBottom>
              Relevant Guidelines
            </Typography>
            {result.context.map((ctx, idx) => (
              <Card key={idx} variant="outlined" sx={{ mb: 1 }}>
                <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
                  <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                    {ctx.source}
                  </Typography>
                  <Typography variant="body2">
                    {ctx.content}
                  </Typography>
                </CardContent>
              </Card>
            ))}
          </Paper>

          <Paper elevation={1} sx={{ p: 2, bgcolor: '#fafafa' }}>
            <Typography variant="caption" color="text.secondary" display="block">
              CAG Steps: {result.process_steps?.map(s => `${s.step} (${s.duration?.toFixed(1)}ms)`).join(' → ')}
            </Typography>
          </Paper>
        </>
      )}
    </Container>
  );
}

export default App;
