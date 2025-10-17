import React, { useState } from 'react';
import {
  Container, TextField, Button, Paper, Typography, Box,
  CircularProgress, Card, CardContent, Chip, Alert
} from '@mui/material';
import { Gavel } from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8009';

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

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Gavel sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
        <Typography variant="h3" component="h1" gutterBottom>
          Contract Compliance Checker
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Rule-based CAG
        </Typography>
        <Chip label="CAG Application" color="primary" sx={{ mt: 1 }} />
      </Box>

      <Paper elevation=3 sx={{ p: 4, mb: 3 }}>
        <TextField
          fullWidth
          multiline
          rows=4
          label="Enter Your Query"
          placeholder="Type your question here..."
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
          startIcon={loading ? <CircularProgress size={20} /> : <Gavel />}
        >
          {loading ? 'Processing...' : 'Submit'}
        </Button>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {result && (
        <>
          <Paper elevation=2 sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Response
            </Typography>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
              {result.response}
            </Typography>
          </Paper>

          <Paper elevation=2 sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Context Used
            </Typography>
            {result.context.map((ctx, idx) => (
              <Card key={idx} variant="outlined" sx={{ mb: 1 }}>
                <CardContent>
                  <Typography variant="body2">
                    {ctx.content}
                  </Typography>
                  <Chip
                    label={`Relevance: ${(ctx.relevance * 100).toFixed(0)}%`}
                    size="small"
                    sx={{ mt: 1 }}
                  />
                </CardContent>
              </Card>
            ))}
          </Paper>

          <Paper elevation=1 sx={{ p: 2, bgcolor: '#fafafa' }}>
            <Typography variant="caption" color="text.secondary">
              Model: {result.metadata.model} | Technique: {result.metadata.technique}
            </Typography>
          </Paper>
        </>
      )}
    </Container>
  );
}

export default App;
