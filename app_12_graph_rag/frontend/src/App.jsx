
import React, { useState, useRef, useEffect } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import axios from 'axios';
import { Send, Loader2, Network } from 'lucide-react';

const App = () => {
  const [text, setText] = useState('');
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(false);
  const fgRef = useRef();

  const handleExtract = async () => {
    if (!text.trim()) return;
    setLoading(true);
    try {
      await axios.post('http://localhost:8012/extract', { text });
      const graphRes = await axios.get('http://localhost:8012/graph');
      setGraphData(graphRes.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-900 text-gray-100 font-sans overflow-hidden">
      {/* Sidebar */}
      <div className="w-1/3 min-w-[300px] bg-gray-800 p-6 flex flex-col gap-4 border-r border-gray-700 z-10 shadow-xl">
        <header className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-purple-600 rounded-lg shadow-lg shadow-purple-900/50"><Network className="w-6 h-6 text-white" /></div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">GraphRAG Explorer</h1>
            <p className="text-xs text-purple-300">Knowledge Graph Extraction</p>
          </div>
        </header>

        <div className="relative">
          <textarea
            className="w-full h-32 bg-gray-900 border border-gray-700 rounded-xl p-4 text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none resize-none shadow-inner text-gray-300 placeholder-gray-600 transition-all"
            placeholder="Enter text here to extract entities and relationships (triples)..."
            value={text}
            onChange={e => setText(e.target.value)}
          />
        </div>

        <button
          onClick={handleExtract}
          disabled={loading || !text.trim()}
          className="bg-purple-600 hover:bg-purple-500 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 rounded-xl flex items-center justify-center gap-2 font-medium transition-all shadow-lg active:scale-95"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          Extract To Graph
        </button>

        <div className="flex-1 flex flex-col bg-gray-900/30 rounded-xl border border-gray-700/50 overflow-hidden">
          <div className="p-4 border-b border-gray-700/50 bg-gray-800/50">
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Graph Statistics</h3>
          </div>

          <div className="p-4 grid grid-cols-2 gap-4">
            <div className="bg-gray-800/80 p-4 rounded-lg text-center border border-gray-700 shadow-sm">
              <div className="text-3xl font-bold text-purple-400">{graphData.nodes.length}</div>
              <div className="text-xs text-gray-500 font-medium mt-1">Nodes</div>
            </div>
            <div className="bg-gray-800/80 p-4 rounded-lg text-center border border-gray-700 shadow-sm">
              <div className="text-3xl font-bold text-blue-400">{graphData.links.length}</div>
              <div className="text-xs text-gray-500 font-medium mt-1">Relationships</div>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 pt-0">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Recent Entities</h3>
            <div className="flex flex-wrap gap-2">
              {graphData.nodes.length === 0 && <span className="text-xs text-gray-600 italic">No nodes yet...</span>}
              {graphData.nodes.slice(-15).reverse().map(n => (
                <span key={n.id} className="text-[10px] bg-gray-800 px-2 py-1 rounded-md border border-gray-700 text-gray-400 hover:text-white hover:border-gray-500 transition-colors cursor-default">
                  {n.label}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Graph Area */}
      <div className="flex-1 bg-black relative flex flex-col">
        <div className="absolute inset-0 z-0">
          <ForceGraph2D
            ref={fgRef}
            graphData={graphData}
            nodeLabel="label"
            nodeAutoColorBy="id"
            linkDirectionalArrowLength={3.5}
            linkDirectionalArrowRelPos={1}
            linkCurvature={0.25}
            backgroundColor="#050505"
            linkColor={() => "#444444"}
            nodeRelSize={6}
          />
        </div>

        <div className="absolute bottom-4 right-4 text-[10px] text-gray-700 pointer-events-none z-10 bg-black/50 px-2 py-1 rounded">
          Visualized with NetworkX & ForceGraph2D
        </div>
      </div>
    </div>
  );
};

export default App;
