import React, { useState } from 'react';
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
