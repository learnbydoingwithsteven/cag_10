import React, { useState } from 'react';
import {
  Container, TextField, Button, Paper, Typography, Box,
  CircularProgress, Stepper, Step, StepLabel, Card, CardContent,
  Chip, Alert, Grid, Accordion, AccordionSummary, AccordionDetails
} from '@mui/material';
import {
  LocalHospital, Psychology, Medication, ExpandMore, Warning
} from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8002';

function App() {
  const [symptoms, setSymptoms] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleDiagnose = async () => {
    if (!symptoms.trim()) {
      setError('Please describe your symptoms');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/diagnose`, {
        symptoms: symptoms,
        top_k: 5
      });

      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get diagnosis');
    } finally {
      setLoading(false);
    }
  };

  const renderProcessSteps = () => {
    if (!result) return null;

    return (
      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Psychology /> Multi-Hop Reasoning Process
        </Typography>
        <Stepper activeStep={result.process_steps.length} alternativeLabel sx={{ mt: 2 }}>
          {result.process_steps.map((step, index) => (
            <Step key={index} completed>
              <StepLabel>{step.step.replace(/_/g, ' ').toUpperCase()}</StepLabel>
            </Step>
          ))}
        </Stepper>
        <Box sx={{ mt: 2 }}>
          {result.process_steps.map((step, index) => (
            <Chip
              key={index}
              label={step.description}
              sx={{ m: 0.5 }}
              size="small"
              color="primary"
              variant="outlined"
            />
          ))}
        </Box>
      </Paper>
    );
  };

  const renderContextByHop = () => {
    if (!result || !result.context) return null;

    const hop1 = result.context.filter(c => c.hop === 1);
    const hop2 = result.context.filter(c => c.hop === 2);
    const hop3 = result.context.filter(c => c.hop === 3);

    return (
      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Knowledge Graph Reasoning Path
        </Typography>

        {hop1.length > 0 && (
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                Hop 1: Symptom → Disease Matching ({hop1.length} matches)
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                {hop1.map((item, index) => (
                  <Grid item xs={12} md={6} key={index}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="body2" color="text.secondary">
                          Symptom: <strong>{item.symptom}</strong>
                        </Typography>
                        <Typography variant="body1" sx={{ mt: 1 }}>
                          → Disease: <strong>{item.disease}</strong>
                        </Typography>
                        <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                          <Chip
                            label={`Probability: ${(item.probability * 100).toFixed(0)}%`}
                            size="small"
                            color="primary"
                          />
                          <Chip
                            label={`Severity: ${item.severity}`}
                            size="small"
                            color={item.severity === 'severe' ? 'error' : 'warning'}
                          />
                          <Chip
                            label={item.category}
                            size="small"
                            variant="outlined"
                          />
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </AccordionDetails>
          </Accordion>
        )}

        {hop2.length > 0 && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                Hop 2: Complete Disease Profiles ({hop2.length} symptoms)
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                {hop2.map((item, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="body2" color="primary" sx={{ fontWeight: 'bold' }}>
                          {item.disease}
                        </Typography>
                        <Typography variant="body2" sx={{ mt: 1 }}>
                          {item.symptom}
                        </Typography>
                        <Chip
                          label={`${(item.probability * 100).toFixed(0)}%`}
                          size="small"
                          sx={{ mt: 1 }}
                        />
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </AccordionDetails>
          </Accordion>
        )}

        {hop3.length > 0 && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                Hop 3: Treatment Options ({hop3.length} treatments)
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                {hop3.map((item, index) => (
                  <Grid item xs={12} md={6} key={index}>
                    <Card variant="outlined">
                      <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Medication color="primary" />
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            For: <strong>{item.disease}</strong>
                          </Typography>
                          <Typography variant="body1" sx={{ mt: 0.5 }}>
                            {item.treatment}
                          </Typography>
                          <Chip
                            label={item.treatment_type}
                            size="small"
                            sx={{ mt: 1 }}
                            variant="outlined"
                          />
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </AccordionDetails>
          </Accordion>
        )}
      </Paper>
    );
  };

  const renderDiagnosis = () => {
    if (!result) return null;

    return (
      <Paper elevation={3} sx={{ p: 3, mb: 3, bgcolor: '#f5f5f5' }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <LocalHospital color="primary" /> Diagnosis
        </Typography>
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
          {result.diagnosis}
        </Typography>
        <Alert severity="warning" sx={{ mt: 2 }} icon={<Warning />}>
          <strong>Medical Disclaimer:</strong> This is an AI-powered educational tool and should not replace professional medical advice. 
          Always consult with a qualified healthcare provider for medical diagnosis and treatment.
        </Alert>
      </Paper>
    );
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <LocalHospital sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
        <Typography variant="h3" component="h1" gutterBottom>
          Medical Diagnosis Assistant
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Multi-hop Reasoning with Medical Knowledge Graph
        </Typography>
        <Chip label="CAG Technique: Multi-hop Reasoning" color="primary" sx={{ mt: 1 }} />
      </Box>

      <Paper elevation={3} sx={{ p: 4, mb: 3 }}>
        <TextField
          fullWidth
          multiline
          rows={4}
          label="Describe Your Symptoms"
          placeholder="Example: I have a fever, cough, and feel very tired. I also have body aches."
          value={symptoms}
          onChange={(e) => setSymptoms(e.target.value)}
          variant="outlined"
          sx={{ mb: 2 }}
        />
        <Button
          variant="contained"
          size="large"
          onClick={handleDiagnose}
          disabled={loading}
          fullWidth
          startIcon={loading ? <CircularProgress size={20} /> : <Psychology />}
        >
          {loading ? 'Analyzing Symptoms...' : 'Get Diagnosis'}
        </Button>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {renderProcessSteps()}
      {renderContextByHop()}
      {renderDiagnosis()}

      {result && (
        <Paper elevation={1} sx={{ p: 2, bgcolor: '#fafafa' }}>
          <Typography variant="caption" color="text.secondary">
            <strong>Metadata:</strong> Model: {result.metadata.model} | 
            Technique: {result.metadata.technique} | 
            Knowledge Source: {result.metadata.knowledge_source} | 
            Reasoning Hops: {result.metadata.hops}
          </Typography>
        </Paper>
      )}
    </Container>
  );
}

export default App;
