
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import {
  Bot,
  Send,
  Loader2,
  BrainCircuit,
  Search,
  Lightbulb,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

const AgenticChat = () => {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [steps, setSteps] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (result) scrollToBottom();
  }, [result, steps]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setResult(null);
    setSteps([]); // Clear previous steps

    // Simulate steps streaming (since standard streaming isn't in backend yet)
    // In a real app, SSE would be better.
    const interval = setInterval(() => {
      setSteps(prev => {
        const nextId = prev.length + 1;
        if (nextId === 1) return [{ id: 1, name: 'Planning', desc: 'Decomposing query...', status: 'running' }];
        if (nextId === 2) return [{ id: 1, name: 'Planning', desc: 'Plan created.', status: 'done' }, { id: 2, name: 'Retrieval', desc: 'Searching knowledge base...', status: 'running' }];
        if (nextId === 3) return [...prev.slice(0, 1), { id: 2, name: 'Retrieval', desc: 'Context retrieved.', status: 'done' }, { id: 3, name: 'Reasoning', desc: 'Synthesizing answer...', status: 'running' }];
        if (nextId === 4) return [...prev.slice(0, 2), { id: 3, name: 'Reasoning', desc: 'Draft generated.', status: 'done' }, { id: 4, name: 'Reflection', desc: 'Critiquing response...', status: 'running' }];
        return prev;
      });
    }, 1500);

    try {
      const { data } = await axios.post('http://localhost:8011/research', { query });
      clearInterval(interval);
      setResult(data);
      // Use actual steps from backend
      setSteps(data.steps.map((s, i) => ({
        id: i + 1,
        name: s.name,
        desc: s.description,
        status: 'done',
        thought: s.thought_process,
        result: s.result
      })));
    } catch (err) {
      clearInterval(interval);
      console.error(err);
      setSteps(prev => [...prev, { id: 99, name: 'Error', desc: 'Failed to process.', status: 'error' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col font-sans">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 p-4 shadow-lg sticky top-0 z-10">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600 rounded-lg shadow-blue-500/20 shadow-md">
              <BrainCircuit className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white">Agentic Research Assistant</h1>
              <div className="flex items-center gap-2 text-xs text-blue-400">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                </span>
                SOTA Reasoning Engine Active
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-5xl w-full mx-auto p-4 flex flex-col md:flex-row gap-6">

        {/* Left: Chat & Input */}
        <section className="flex-1 flex flex-col gap-4">
          {/* Result Area */}
          <div className="flex-1 bg-gray-800/50 rounded-xl border border-gray-700 p-6 min-h-[400px] shadow-inner overflow-y-auto">
            {!result && !loading && (
              <div className="h-full flex flex-col items-center justify-center text-gray-500 gap-4">
                <Bot className="w-16 h-16 opacity-20" />
                <p>Ask a complex question to start the agentic workflow.</p>
                <div className="flex gap-2 text-sm">
                  <span className="bg-gray-800 px-3 py-1 rounded-full border border-gray-700">Planning</span>
                  <span className="bg-gray-800 px-3 py-1 rounded-full border border-gray-700">Retrieval</span>
                  <span className="bg-gray-800 px-3 py-1 rounded-full border border-gray-700">Reflection</span>
                </div>
              </div>
            )}

            {result && (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                {/* User Query */}
                <div className="flex gap-4">
                  <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center shrink-0">
                    <span className="font-bold text-xs">YOU</span>
                  </div>
                  <div className="bg-gray-700/50 rounded-2xl rounded-tl-sm p-4 text-gray-200">
                    {result.query}
                  </div>
                </div>

                {/* Agent Answer */}
                <div className="flex gap-4">
                  <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center shrink-0 shadow-lg shadow-blue-900/50">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div className="space-y-4 flex-1">
                    <div className="bg-blue-900/20 border border-blue-800/50 rounded-2xl rounded-tr-sm p-6 text-gray-50 prose prose-invert max-w-none shadow-sm">
                      <p className="whitespace-pre-wrap leading-relaxed">{result.answer}</p>
                    </div>

                    {/* Critique Box */}
                    {result.critique && (
                      <div className="bg-amber-900/20 border border-amber-800/30 rounded-lg p-4 text-sm flex gap-3 text-amber-200/80">
                        <Lightbulb className="w-5 h-5 shrink-0 text-amber-500" />
                        <div>
                          <p className="font-semibold text-amber-500 mb-1">Self-Reflection (Score: {result.critique.score}/10)</p>
                          <p className="italic">"{result.critique.critique}"</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Input Area */}
          <form onSubmit={handleSubmit} className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="E.g., What are the implications of quantum computing for cryptography? Investigate via multiple angles."
              className="w-full bg-gray-800 border border-gray-700 rounded-xl py-4 pl-6 pr-14 text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-lg transition-all"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="absolute right-2 top-2 bottom-2 p-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg text-white transition-colors aspect-square flex items-center justify-center shadow-md"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            </button>
          </form>
        </section>

        {/* Right: Reasoning Log (SOTA Feature) */}
        <aside className="w-full md:w-80 shrink-0">
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-4 h-full sticky top-24 shadow-lg overflow-hidden flex flex-col">
            <div className="flex items-center gap-2 mb-4 pb-4 border-b border-gray-700">
              <Search className="w-4 h-4 text-emerald-400" />
              <h2 className="font-semibold text-gray-200">Reasoning Engine</h2>
            </div>

            <div className="space-y-4 overflow-y-auto flex-1 pr-2 custom-scrollbar">
              {steps.length === 0 && !loading && (
                <div className="text-sm text-gray-500 text-center py-10 opacity-60">
                  Ready to analyze...
                </div>
              )}

              {steps.map((step) => (
                <div key={step.id} className="relative pl-6 pb-2 group">
                  {/* Connector Line */}
                  {step.id !== steps.length && (
                    <div className="absolute left-[11px] top-6 bottom-[-16px] w-0.5 bg-gray-700 group-last:hidden"></div>
                  )}

                  {/* Status Dot */}
                  <div className={`absolute left-0 top-1 w-6 h-6 rounded-full border-2 flex items-center justify-center bg-gray-800 z-10 transition-colors duration-300
                                ${step.status === 'done' ? 'border-emerald-500 text-emerald-500' :
                      step.status === 'error' ? 'border-red-500 text-red-500' :
                        'border-blue-500 text-blue-500 animate-pulse'}`}>
                    {step.status === 'done' ? <CheckCircle2 className="w-3 h-3" /> :
                      step.status === 'error' ? <AlertCircle className="w-3 h-3" /> :
                        <div className="w-2 h-2 bg-blue-500 rounded-full" />}
                  </div>

                  {/* Content */}
                  <div>
                    <h3 className={`text-sm font-medium ${step.status === 'running' ? 'text-blue-400' : 'text-gray-300'}`}>
                      {step.name}
                    </h3>
                    <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                      {step.desc}
                    </p>

                    {/* Detailed Thought Expandable (Simulated here) */}
                    {step.thought && (
                      <div className="mt-2 bg-gray-900/50 p-2 rounded text-[10px] font-mono text-gray-400 border border-gray-700/50">
                        &gt; {step.thought}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </main>
    </div>
  );
};

export default AgenticChat;
