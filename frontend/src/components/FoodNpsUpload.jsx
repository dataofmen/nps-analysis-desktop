import React, { useState, useEffect } from 'react';

const FoodNpsUpload = ({ onUploadComplete }) => {
  const [uploadStatus, setUploadStatus] = useState({
    qualtrics: { uploaded: false, loading: false, filename: '', rows: 0 },
    population: { uploaded: false, loading: false, filename: '', segments: 0 },
    coding: { uploaded: false, loading: false, filename: '', rows: 0 }
  });

  const [autoAnalyze, setAutoAnalyze] = useState(true);

  useEffect(() => {
    const initStatus = async () => {
      const status = await checkUploadStatus();
      setUploadStatus(prev => ({
        qualtrics: {
          ...prev.qualtrics,
          uploaded: status.qualtrics_uploaded,
          rows: status.qualtrics_rows || 0,
          filename: status.qualtrics_uploaded ? 'Existing Data' : ''
        },
        population: {
          ...prev.population,
          uploaded: status.population_uploaded,
          rows: status.population_segments || 0,
          filename: status.population_uploaded ? 'Existing Data' : ''
        },
        coding: {
          ...prev.coding,
          uploaded: status.coding_uploaded,
          rows: status.coding_rows || 0,
          filename: status.coding_uploaded ? 'Existing Data' : ''
        }
      }));

      // Auto-trigger analysis if files are already uploaded
      if (status.qualtrics_uploaded && status.population_uploaded && onUploadComplete) {
        onUploadComplete();
      }
    };
    initStatus();
  }, []);

  const handleFileUpload = async (type, file) => {
    if (!file) return;

    setUploadStatus(prev => ({
      ...prev,
      [type]: { ...prev[type], loading: true, filename: file.name }
    }));

    const formData = new FormData();
    formData.append('file', file);

    const endpoints = {
      qualtrics: '/food-nps/upload/qualtrics',
      population: '/food-nps/upload/population',
      coding: '/food-nps/upload/coding'
    };

    try {
      const response = await fetch(`http://localhost:8000${endpoints[type]}`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || '업로드 실패');
      }

      const data = await response.json();

      setUploadStatus(prev => ({
        ...prev,
        [type]: {
          uploaded: true,
          loading: false,
          filename: file.name,
          rows: data.rows || data.segments || 0,
          ...(type === 'qualtrics' && { valid_nps_scores: data.valid_nps_scores }),
          ...(type === 'population' && { total_weight: data.total_weight }),
          ...(type === 'coding' && { unique_categories: data.unique_categories })
        }
      }));

      // 자동 분석: Qualtrics와 Population이 모두 업로드되면 자동 분석 실행
      if (autoAnalyze && onUploadComplete) {
        const status = await checkUploadStatus();
        if (status.qualtrics_uploaded && status.population_uploaded) {
          setTimeout(() => onUploadComplete(), 500);
        }
      }

    } catch (error) {
      alert(`${type} 업로드 오류: ${error.message}`);
      setUploadStatus(prev => ({
        ...prev,
        [type]: { ...prev[type], loading: false, uploaded: false }
      }));
    }
  };

  const checkUploadStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/food-nps/status');
      return await response.json();
    } catch (error) {
      console.error('상태 확인 오류:', error);
      return { qualtrics_uploaded: false, population_uploaded: false, coding_uploaded: false };
    }
  };

  const FileUploadCard = ({ type, title, description, required, status }) => (
    <div className={`group relative bg-white rounded-2xl p-6 transition-all duration-300 ${status.uploaded
        ? 'shadow-soft ring-2 ring-green-500/20'
        : 'shadow-card hover:shadow-lg hover:-translate-y-1'
      }`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-lg font-bold text-slate-800">{title}</h3>
            {required && <span className="px-2 py-0.5 rounded-full bg-red-50 text-red-600 text-[10px] font-bold uppercase tracking-wider">Required</span>}
          </div>
          <p className="text-sm text-slate-500 leading-relaxed">{description}</p>
        </div>
        {status.uploaded && (
          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center text-green-600">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        )}
      </div>

      <div className="mt-6">
        <label className="block w-full cursor-pointer group/label">
          <input
            type="file"
            accept=".csv"
            onChange={(e) => handleFileUpload(type, e.target.files[0])}
            disabled={status.loading}
            className="hidden"
          />
          <div className={`relative overflow-hidden rounded-xl border-2 border-dashed transition-all duration-300 h-32 flex flex-col items-center justify-center ${status.loading
              ? 'border-brand-200 bg-brand-50'
              : status.uploaded
                ? 'border-green-200 bg-green-50/30'
                : 'border-slate-200 bg-slate-50/50 group-hover/label:border-brand-400 group-hover/label:bg-brand-50/30'
            }`}>
            {status.loading ? (
              <div className="flex flex-col items-center">
                <div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin mb-2"></div>
                <span className="text-xs font-medium text-brand-600">Uploading...</span>
              </div>
            ) : (
              <>
                <div className={`mb-2 transition-transform duration-300 ${status.uploaded ? 'scale-90' : 'group-hover/label:scale-110'}`}>
                  {status.uploaded ? (
                    <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  ) : (
                    <svg className="w-8 h-8 text-slate-400 group-hover/label:text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  )}
                </div>
                <p className="text-xs font-medium text-slate-600">
                  {status.uploaded ? status.filename : 'Click to upload CSV'}
                </p>
              </>
            )}
          </div>
        </label>

        {status.uploaded && (
          <div className="mt-4 pt-4 border-t border-slate-100">
            <div className="grid grid-cols-2 gap-2">
              {type === 'qualtrics' && (
                <>
                  <div className="bg-slate-50 p-2 rounded-lg text-center">
                    <p className="text-[10px] text-slate-500 uppercase tracking-wide">Total Rows</p>
                    <p className="text-sm font-bold text-slate-700">{status.rows.toLocaleString()}</p>
                  </div>
                  <div className="bg-slate-50 p-2 rounded-lg text-center">
                    <p className="text-[10px] text-slate-500 uppercase tracking-wide">Valid NPS</p>
                    <p className="text-sm font-bold text-brand-600">{status.valid_nps_scores?.toLocaleString()}</p>
                  </div>
                </>
              )}
              {type === 'population' && (
                <>
                  <div className="bg-slate-50 p-2 rounded-lg text-center">
                    <p className="text-[10px] text-slate-500 uppercase tracking-wide">Segments</p>
                    <p className="text-sm font-bold text-slate-700">{status.rows.toLocaleString()}</p>
                  </div>
                  <div className="bg-slate-50 p-2 rounded-lg text-center">
                    <p className="text-[10px] text-slate-500 uppercase tracking-wide">Total Weight</p>
                    <p className="text-sm font-bold text-brand-600">{status.total_weight?.toFixed(2)}</p>
                  </div>
                </>
              )}
              {type === 'coding' && (
                <>
                  <div className="bg-slate-50 p-2 rounded-lg text-center">
                    <p className="text-[10px] text-slate-500 uppercase tracking-wide">Rows</p>
                    <p className="text-sm font-bold text-slate-700">{status.rows.toLocaleString()}</p>
                  </div>
                  <div className="bg-slate-50 p-2 rounded-lg text-center">
                    <p className="text-[10px] text-slate-500 uppercase tracking-wide">Categories</p>
                    <p className="text-sm font-bold text-brand-600">{status.unique_categories}</p>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const canAnalyze = uploadStatus.qualtrics.uploaded && uploadStatus.population.uploaded;

  return (
    <div className="space-y-8">
      <div className="bg-gradient-to-r from-brand-50 to-white border border-brand-100 rounded-2xl p-6">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 bg-brand-100 rounded-xl flex items-center justify-center flex-shrink-0 text-brand-600">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-brand-900">Data Upload Requirements</h3>
            <div className="mt-2 text-sm text-brand-700 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 bg-brand-500 rounded-full"></span>
                Qualtrics: Must include Q1_1 (NPS)
              </div>
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 bg-brand-500 rounded-full"></span>
                Population: 241 demographic segments
              </div>
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 bg-brand-500 rounded-full"></span>
                Coding: Optional open-end categorization
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between bg-white rounded-2xl shadow-soft p-4 px-6">
        <div className="flex items-center gap-3">
          <div className="relative flex items-center">
            <input
              type="checkbox"
              id="autoAnalyze"
              checked={autoAnalyze}
              onChange={(e) => setAutoAnalyze(e.target.checked)}
              className="peer h-5 w-5 cursor-pointer appearance-none rounded-md border border-slate-300 transition-all checked:border-brand-500 checked:bg-brand-500 hover:border-brand-400"
            />
            <svg className="pointer-events-none absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-white opacity-0 peer-checked:opacity-100" width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M10 3L4.5 8.5L2 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <label htmlFor="autoAnalyze" className="text-sm font-medium text-slate-700 cursor-pointer select-none">
            Auto-run analysis after upload
          </label>
        </div>

        {canAnalyze && !autoAnalyze && (
          <button
            onClick={onUploadComplete}
            className="px-6 py-2.5 bg-brand-600 text-white text-sm font-bold rounded-xl hover:bg-brand-700 active:scale-95 transition-all shadow-lg shadow-brand-500/30"
          >
            Run Analysis
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <FileUploadCard
          type="qualtrics"
          title="Qualtrics Data"
          description="Survey response data containing NPS scores and demographics."
          required={true}
          status={uploadStatus.qualtrics}
        />

        <FileUploadCard
          type="population"
          title="Population Weights"
          description="Demographic segments for weighting calculation (241 segments)."
          required={true}
          status={uploadStatus.population}
        />

        <FileUploadCard
          type="coding"
          title="Coding Data"
          description="Open-ended response categorization data (Optional)."
          required={false}
          status={uploadStatus.coding}
        />
      </div>
    </div>
  );
};

export default FoodNpsUpload;
