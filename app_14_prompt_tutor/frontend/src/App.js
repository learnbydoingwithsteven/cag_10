import React, { useState } from 'react';
import {
    Container, TextField, Button, Paper, Typography, Box,
    CircularProgress, Card, CardContent, Chip, Alert, Divider, Accordion,
    AccordionSummary, AccordionDetails
} from '@mui/material';
import { School, ExpandMore, AutoAwesome, Psychology } from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8014';

function App() {
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const quickQuestions = [
        "How do I write a good few-shot prompt?",
        "What is chain-of-thought prompting?",
        "How can I get structured JSON output from an LLM?",
        "What are common prompt engineering mistakes?"
    ];

    const handleSubmit = async (q) => {
        const question = q || query;
        if (!question.trim()) {
            setError('Please ask a question about prompt engineering.');
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);
        if (q) setQuery(q);

        try {
            const response = await axios.post(`${API_BASE_URL}/learn`, {
                query: question
            });
            setResult(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get tutorial response');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container maxWidth="lg" sx={{ py: 4 }}>
            <Box sx={{ textAlign: 'center', mb: 4 }}>
                <School sx={{ fontSize: 60, color: 'secondary.main', mb: 2 }} />
                <Typography variant="h3" component="h1" gutterBottom>
                    Prompt Engineering Tutor
                </Typography>
                <Typography variant="subtitle1" color="text.secondary">
                    Learn how to craft effective prompts for LLMs — with examples and exercises
                </Typography>
                <Chip label="Pedagogical Scaffolding CAG" color="secondary" sx={{ mt: 1 }} />
            </Box>

            {/* Quick Questions */}
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, justifyContent: 'center', mb: 3 }}>
                {quickQuestions.map((q, idx) => (
                    <Chip
                        key={idx}
                        label={q}
                        variant="outlined"
                        color="primary"
                        clickable
                        onClick={() => handleSubmit(q)}
                        icon={<AutoAwesome />}
                        sx={{ fontSize: '0.85rem' }}
                    />
                ))}
            </Box>

            <Paper elevation={3} sx={{ p: 4, mb: 3 }}>
                <TextField
                    fullWidth
                    multiline
                    rows={3}
                    label="Ask about Prompt Engineering"
                    placeholder="e.g., How do I use chain-of-thought prompting to solve math problems?"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    variant="outlined"
                    sx={{ mb: 2 }}
                />
                <Button
                    variant="contained"
                    size="large"
                    onClick={() => handleSubmit()}
                    disabled={loading}
                    fullWidth
                    color="secondary"
                    startIcon={loading ? <CircularProgress size={20} /> : <Psychology />}
                >
                    {loading ? 'Thinking...' : 'Learn This Concept'}
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
                            <School color="secondary" sx={{ mr: 1 }} />
                            <Typography variant="h5">Lesson</Typography>
                        </Box>
                        <Divider sx={{ mb: 2 }} />
                        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
                            {result.response}
                        </Typography>
                    </Paper>

                    <Accordion>
                        <AccordionSummary expandIcon={<ExpandMore />}>
                            <Typography variant="h6">📚 Knowledge Sources Used</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            {result.context.map((ctx, idx) => (
                                <Card key={idx} variant="outlined" sx={{ mb: 1 }}>
                                    <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
                                        <Chip label={ctx.source} size="small" color="secondary" sx={{ mb: 0.5 }} />
                                        <Typography variant="body2">{ctx.content}</Typography>
                                        <Chip
                                            label={`Relevance: ${(ctx.relevance * 100).toFixed(0)}%`}
                                            size="small"
                                            variant="outlined"
                                            sx={{ mt: 0.5 }}
                                        />
                                    </CardContent>
                                </Card>
                            ))}
                        </AccordionDetails>
                    </Accordion>

                    <Paper elevation={1} sx={{ p: 2, mt: 2, bgcolor: '#fafafa' }}>
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
