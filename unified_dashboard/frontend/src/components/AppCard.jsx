import React from 'react';
import { Play, Square, ExternalLink, Activity, Globe } from 'lucide-react';

const AppCard = ({ app, onStart, onStop }) => {
    const isRunning = app.status === 'running';

    return (
        <div className={`
      relative group overflow-hidden rounded-2xl border transition-all duration-300
      ${isRunning
                ? 'bg-slate-800/40 border-slate-700 hover:border-blue-500/50 hover:shadow-lg hover:shadow-blue-500/10'
                : 'bg-slate-800/20 border-slate-800 hover:border-slate-700'
            }
    `}>
            {/* Status Bar */}
            <div className={`absolute top-0 left-0 w-1 h-full transition-colors duration-300 ${isRunning ? 'bg-green-500' : 'bg-slate-600'}`} />

            <div className="p-5 pl-7">
                <div className="flex justify-between items-start mb-3">
                    <div>
                        <h3 className="font-semibold text-lg text-slate-100 group-hover:text-blue-400 transition-colors">
                            {app.name}
                        </h3>
                        <p className="text-sm text-slate-400 line-clamp-2 h-10">
                            {app.description}
                        </p>
                    </div>
                    <div className={`
            w-2 h-2 rounded-full mt-2
            ${isRunning ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)] animate-pulse' : 'bg-slate-600'}
          `} />
                </div>

                {/* Info & Stats (Placeholder) */}
                <div className="flex items-center gap-4 text-xs text-slate-500 mb-6 font-mono">
                    <span className="flex items-center gap-1">
                        <Globe className="w-3 h-3" />
                        :{app.frontend_port}
                    </span>
                    <span className="flex items-center gap-1">
                        <Activity className="w-3 h-3" />
                        :{app.backend_port}
                    </span>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 mt-auto">
                    {isRunning ? (
                        <>
                            <a
                                href={`http://localhost:${app.frontend_port}`}
                                target="_blank"
                                rel="noreferrer"
                                className="flex-1 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white py-2 rounded-lg text-sm font-medium transition-colors"
                            >
                                <ExternalLink className="w-4 h-4" />
                                Open App
                            </a>
                            <button
                                onClick={onStop}
                                className="p-2 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500 hover:text-white transition-colors border border-red-500/20"
                                title="Stop App"
                            >
                                <Square className="w-4 h-4" />
                            </button>
                        </>
                    ) : (
                        <button
                            onClick={onStart}
                            className="flex-1 flex items-center justify-center gap-2 bg-slate-700 hover:bg-blue-600 text-white py-2 rounded-lg text-sm font-medium transition-all group-hover:bg-slate-600 group-hover:hover:bg-blue-600"
                        >
                            <Play className="w-4 h-4" />
                            Start App
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AppCard;
