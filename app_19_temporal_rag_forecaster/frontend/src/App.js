import React, { useState } from 'react';
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
