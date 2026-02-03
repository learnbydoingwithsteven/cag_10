import { useEffect, useState } from 'react'
import { Activity, Play, Square, ExternalLink, RefreshCw, Server, AlertCircle } from 'lucide-react'
import AppCard from './components/AppCard'

const API_URL = 'http://localhost:8000';

function App() {
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefreshed, setLastRefreshed] = useState(new Date());

  const fetchApps = async () => {
    try {
      const res = await fetch(`${API_URL}/apps`);
      if (!res.ok) throw new Error('Failed to fetch apps');
      const data = await res.json();
      setApps(data);
      setError(null);
      setLastRefreshed(new Date());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApps();
    const interval = setInterval(fetchApps, 2000); // Poll every 2s
    return () => clearInterval(interval);
  }, []);

  const handleStart = async (id) => {
    try {
      await fetch(`${API_URL}/apps/${id}/start`, { method: 'POST' });
      // Immediate fetch to update UI state (optimistic or waiting)
      setTimeout(fetchApps, 500); 
    } catch (err) {
      console.error(err);
    }
  };

  const handleStop = async (id) => {
    try {
      await fetch(`${API_URL}/apps/${id}/stop`, { method: 'POST' });
      setTimeout(fetchApps, 500);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 font-sans selection:bg-blue-500 selection:text-white">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 h-16 bg-slate-800/80 backdrop-blur-md border-b border-slate-700 z-50 flex items-center justify-between px-6">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-2 rounded-lg shadow-lg shadow-blue-500/20">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
              CAG Dashboard
            </h1>
            <p className="text-xs text-slate-400">System Monitoring & Control</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <span className="text-xs text-slate-500 hidden sm:block">
            Last updated: {lastRefreshed.toLocaleTimeString()}
          </span>
          <button 
            onClick={fetchApps}
            className="p-2 rounded-full hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
            title="Refresh Status"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="pt-24 px-6 pb-12 max-w-7xl mx-auto">
        {error && (
          <div className="mb-8 bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-center gap-3 text-red-400">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <p>Connection Error: {error}. Is the backend running?</p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {apps.map(app => (
             <AppCard 
                key={app.id} 
                app={app} 
                onStart={() => handleStart(app.id)} 
                onStop={() => handleStop(app.id)} 
             />
          ))}
        </div>
        
        {apps.length === 0 && !loading && !error && (
            <div className="text-center text-slate-500 mt-20">
                <Server className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p>No apps found in configuration.</p>
            </div>
        )}
      </main>
    </div>
  )
}

export default App
