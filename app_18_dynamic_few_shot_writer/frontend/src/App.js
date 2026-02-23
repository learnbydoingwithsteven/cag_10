import React, { useState } from 'react';
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
