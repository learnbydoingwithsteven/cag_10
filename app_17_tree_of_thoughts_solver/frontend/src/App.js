import React, { useState } from 'react';
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
