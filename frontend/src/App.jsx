import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import WeightingConfig from './components/WeightingConfig';
import Dashboard from './components/Dashboard';
import Modal from './components/Modal';

function App() {
  const [columns, setColumns] = useState([]);
  const [weightingConfig, setWeightingConfig] = useState(null);
  const [dataVersion, setDataVersion] = useState(0); // For data updates (columns)
  const [resetKey, setResetKey] = useState(0); // For forcing component reset

  // Modal States
  const [isResetModalOpen, setIsResetModalOpen] = useState(false);
  const [isSuccessModalOpen, setIsSuccessModalOpen] = useState(false);

  const fetchColumns = async () => {
    try {
      const response = await fetch('http://localhost:8000/columns');
      const data = await response.json();
      setColumns(data.columns);
      setDataVersion(v => v + 1); // Update data version for dependent components
    } catch (error) {
      console.error(error);
    }
  };

  class ErrorBoundary extends React.Component {
    constructor(props) {
      super(props);
      this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
      return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
      console.error("Uncaught error:", error, errorInfo);
      try {
        if (window.require) {
          const { ipcRenderer } = window.require('electron');
          ipcRenderer.send('log-to-file', `React Error: ${error.toString()}`);
          ipcRenderer.send('log-to-file', `Component Stack: ${errorInfo.componentStack}`);
        }
      } catch (e) {
        // Ignore
      }
    }

    render() {
      if (this.state.hasError) {
        return (
          <div className="p-6 bg-red-50 border border-red-200 rounded-xl text-red-700">
            <h2 className="text-lg font-bold mb-2">Something went wrong.</h2>
            <p className="text-sm">{this.state.error && this.state.error.toString()}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-bold"
            >
              Reload App
            </button>
          </div>
        );
      }

      return this.props.children;
    }
  }

  const handleReset = async () => {
    try {
      await fetch('http://localhost:8000/reset', { method: 'POST' });
      setColumns([]);
      setWeightingConfig(null);
      setDataVersion(v => v + 1);
      setResetKey(k => k + 1); // Force reset of upload components

      setIsResetModalOpen(false);
      setIsSuccessModalOpen(true);
    } catch (error) {
      console.error('Reset failed:', error);
      alert('Failed to reset data. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex font-sans text-slate-900">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-slate-200 fixed h-full z-10 hidden md:flex flex-col">
        <div className="p-6 border-b border-slate-100">
          <h1 className="text-xl font-bold text-brand-600 flex items-center gap-2">
            <span className="text-2xl">⚡</span> NPS Analysis
          </h1>
          <p className="text-xs text-slate-500 mt-1">Automated Insights System</p>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          <button
            className="w-full flex items-center gap-3 px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 bg-brand-50 text-brand-700 shadow-sm"
          >
            <span>📊</span> Generic Analysis
          </button>
        </nav>

        <div className="p-4 border-t border-slate-100">
          <div className="bg-slate-50 rounded-xl p-4">
            <p className="text-xs font-medium text-slate-500 mb-2">System Status</p>
            <div className="flex items-center gap-2 text-xs text-green-600">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              All Systems Operational
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 md:ml-64 min-h-screen transition-all duration-300">
        <div className="max-w-7xl mx-auto p-6 md:p-10">
          <header className="mb-8 flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-slate-800">
                Generic NPS Analysis
              </h2>
              <p className="text-slate-500 mt-1">
                Analyze standard NPS data with customizable weighting
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsResetModalOpen(true)}
                className="px-4 py-2 text-sm font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
              >
                Reset Data
              </button>
              <span className="text-sm text-slate-500">Last updated: Today</span>

            </div>
          </header>

          <div className="animate-fade-in space-y-8">
            <FileUpload key={resetKey} onUploadComplete={fetchColumns} />
            {columns.length > 0 && (
              <>
                <WeightingConfig columns={columns} onConfigChange={setWeightingConfig} dataVersion={dataVersion} />
                <ErrorBoundary>
                  <Dashboard columns={columns} weightingConfig={weightingConfig} dataVersion={dataVersion} />
                </ErrorBoundary>
              </>
            )}
          </div>
        </div>
      </main>

      {/* Reset Confirmation Modal */}
      <Modal
        isOpen={isResetModalOpen}
        onClose={() => setIsResetModalOpen(false)}
        title="Reset All Data?"
        footer={
          <>
            <button
              onClick={() => setIsResetModalOpen(false)}
              className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleReset}
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors shadow-sm"
            >
              Yes, Reset Everything
            </button>
          </>
        }
      >
        <p>
          This will clear all uploaded data and analysis results. This action cannot be undone.
        </p>
      </Modal>

      {/* Success Modal */}
      <Modal
        isOpen={isSuccessModalOpen}
        onClose={() => setIsSuccessModalOpen(false)}
        title="Data Reset Complete"
        footer={
          <button
            onClick={() => setIsSuccessModalOpen(false)}
            className="px-4 py-2 text-sm font-medium text-white bg-brand-600 hover:bg-brand-700 rounded-lg transition-colors shadow-sm"
          >
            OK
          </button>
        }
      >
        <div className="flex flex-col items-center text-center py-4">
          <div className="w-12 h-12 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-4">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <p className="text-lg font-medium text-slate-800">All data has been cleared.</p>
          <p className="text-sm text-slate-500 mt-1">You can now start a new analysis.</p>
        </div>
      </Modal>
    </div>
  );
}

export default App;
