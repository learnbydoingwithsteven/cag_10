import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  CircularProgress,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  LinearProgress,
  Card,
  CardContent,
  Grid,
  Divider
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Send as SendIcon,
  Description as DescriptionIcon,
  Speed as SpeedIcon,
  Token as TokenIcon,
  Verified as VerifiedIcon
} from '@mui/icons-material';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const API_BASE_URL = 'http://localhost:8001';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [processSteps, setProcessSteps] = useState([]);
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/documents`);
      setDocuments(res.data);
    } catch (err) {
      console.error('Error fetching documents:', err);
    }
  };

  const handleAnalyze = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResponse(null);
    setProcessSteps([]);

    try {
      const res = await axios.post(`${API_BASE_URL}/analyze`, {
        query: query,
        context_limit: 5,
        temperature: 0.3,
        max_tokens: 1500
      });

      setResponse(res.data);
      setProcessSteps(res.data.process_visualization?.steps || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAnalyze();
    }
  };

  const renderProcessVisualization = () => {
    if (!processSteps.length) return null;

    return (
      <Card sx={{ mt: 3, bgcolor: '#f5f5f5' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Process Visualization
          </Typography>
          <Box sx={{ mt: 2 }}>
            {processSteps.map((step, index) => (
              <Box key={index} sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" fontWeight="bold">
                    {index + 1}. {step.name.replace(/_/g, ' ').toUpperCase()}
                  </Typography>
                  <Chip
                    label={`${step.duration_ms?.toFixed(2)}ms`}
                    size="small"
                    color={step.status === 'completed' ? 'success' : 'default'}
                  />
                </Box>
                <Typography variant="caption" color="text.secondary">
                  {step.description}
                </Typography>
                {step.details && (
                  <Box sx={{ mt: 1, pl: 2 }}>
                    {Object.entries(step.details).map(([key, value]) => (
                      <Typography key={key} variant="caption" display="block">
                        {key}: {typeof value === 'object' ? JSON.stringify(value) : value}
                      </Typography>
                    ))}
                  </Box>
                )}
                {index < processSteps.length - 1 && <Divider sx={{ mt: 2 }} />}
              </Box>
            ))}
          </Box>
        </CardContent>
      </Card>
    );
  };

  const renderMetrics = () => {
    if (!response) return null;

    return (
      <Grid container spacing={2} sx={{ mt: 2 }}>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <SpeedIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="body2" color="text.secondary">
                  Latency
                </Typography>
              </Box>
              <Typography variant="h6">
                {response.latency_ms.toFixed(2)}ms
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TokenIcon sx={{ mr: 1, color: 'success.main' }} />
                <Typography variant="body2" color="text.secondary">
                  Tokens Used
                </Typography>
              </Box>
              <Typography variant="h6">
                {response.token_usage.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <VerifiedIcon sx={{ mr: 1, color: 'info.main' }} />
                <Typography variant="body2" color="text.secondary">
                  Confidence
                </Typography>
              </Box>
              <Typography variant="h6">
                {(response.confidence_score * 100).toFixed(1)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <DescriptionIcon sx={{ mr: 1, color: 'warning.main' }} />
                <Typography variant="body2" color="text.secondary">
                  Citations
                </Typography>
              </Box>
              <Typography variant="h6">
                {response.citations.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderCitations = () => {
    if (!response?.citations?.length) return null;

    return (
      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Citations & Sources
        </Typography>
        {response.citations.map((citation, index) => (
          <Accordion key={index}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                <Chip
                  label={`[${index + 1}]`}
                  size="small"
                  color="primary"
                  sx={{ mr: 2 }}
                />
                <Typography variant="body2" sx={{ flexGrow: 1 }}>
                  {citation.source}
                </Typography>
                <Chip
                  label={`${(citation.relevance_score * 100).toFixed(1)}%`}
                  size="small"
                  color="success"
                  variant="outlined"
                />
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body2" color="text.secondary" paragraph>
                {citation.content}
              </Typography>
              {citation.metadata && Object.keys(citation.metadata).length > 0 && (
                <Box sx={{ mt: 2, p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
                  <Typography variant="caption" fontWeight="bold">
                    Metadata:
                  </Typography>
                  {Object.entries(citation.metadata).map(([key, value]) => (
                    <Typography key={key} variant="caption" display="block">
                      {key}: {typeof value === 'object' ? JSON.stringify(value) : value}
                    </Typography>
                  ))}
                </Box>
              )}
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>
    );
  };

  const renderReasoningSteps = () => {
    if (!response?.reasoning_steps?.length) return null;

    return (
      <Card sx={{ mt: 3, bgcolor: '#e3f2fd' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Reasoning Steps
          </Typography>
          <Box component="ol" sx={{ pl: 2 }}>
            {response.reasoning_steps.map((step, index) => (
              <Typography key={index} component="li" variant="body2" sx={{ mb: 1 }}>
                {step}
              </Typography>
            ))}
          </Box>
        </CardContent>
      </Card>
    );
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom align="center" color="primary">
          Legal Document Analyzer
        </Typography>
        <Typography variant="subtitle1" gutterBottom align="center" color="text.secondary">
          AI-powered legal analysis with RAG and citation tracking
        </Typography>

        <Box sx={{ mt: 4 }}>
          <TextField
            fullWidth
            multiline
            rows={4}
            variant="outlined"
            label="Enter your legal query"
            placeholder="e.g., What are the requirements for filing a motion to dismiss?"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
          />
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="caption" color="text.secondary">
              {documents.length} documents in knowledge base
            </Typography>
            <Button
              variant="contained"
              endIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
              onClick={handleAnalyze}
              disabled={loading || !query.trim()}
              size="large"
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </Button>
          </Box>
        </Box>

        {loading && (
          <Box sx={{ mt: 3 }}>
            <LinearProgress />
            <Typography variant="body2" align="center" sx={{ mt: 1 }}>
              Processing your query...
            </Typography>
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mt: 3 }}>
            {error}
          </Alert>
        )}

        {response && (
          <>
            {renderMetrics()}

            <Paper elevation={2} sx={{ mt: 3, p: 3, bgcolor: '#fafafa' }}>
              <Typography variant="h6" gutterBottom>
                Analysis Result
              </Typography>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                {response.answer}
              </Typography>
            </Paper>

            {renderCitations()}
            {renderReasoningSteps()}
            {renderProcessVisualization()}
          </>
        )}
      </Paper>

      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          Powered by Ollama (llama3) + ChromaDB + FastAPI
        </Typography>
      </Box>
    </Container>
  );
}

export default App;
