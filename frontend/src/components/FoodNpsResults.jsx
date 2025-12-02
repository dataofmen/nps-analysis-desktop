import React, { useState, useEffect } from 'react';

const FoodNpsResults = ({ triggerAnalysis }) => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (triggerAnalysis) {
      runAnalysis();
    }
  }, [triggerAnalysis]);

  const runAnalysis = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/food-nps/analyze', {
        method: 'POST'
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || '분석 실패');
      }

      const data = await response.json();
      setResults(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-soft p-12 text-center">
        <div className="inline-block relative">
          <div className="w-16 h-16 border-4 border-brand-100 rounded-full"></div>
          <div className="w-16 h-16 border-4 border-brand-500 border-t-transparent rounded-full animate-spin absolute top-0 left-0"></div>
        </div>
        <h3 className="text-xl font-bold text-slate-800 mt-6">Calculating Weighted NPS</h3>
        <p className="text-slate-500 mt-2">Processing demographic segments and applying weights...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-100 rounded-2xl p-6 flex items-start gap-4">
        <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0 text-red-600">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-bold text-red-900">Analysis Error</h3>
          <p className="text-red-700 mt-1">{error}</p>
          <button
            onClick={runAnalysis}
            className="mt-4 px-4 py-2 bg-red-600 text-white text-sm font-bold rounded-lg hover:bg-red-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="bg-white rounded-2xl shadow-soft p-12 text-center border-2 border-dashed border-slate-200">
        <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mx-auto text-slate-300 mb-6">
          <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <h3 className="text-lg font-bold text-slate-700">Ready for Analysis</h3>
        <p className="text-slate-500 mt-2">Upload data files to see the weighted NPS breakdown.</p>
        <button
          onClick={runAnalysis}
          className="mt-6 px-6 py-2.5 bg-brand-600 text-white font-bold rounded-xl hover:bg-brand-700 transition-all shadow-lg shadow-brand-500/30"
        >
          Run Analysis Manually
        </button>
      </div>
    );
  }

  const getNpsColor = (nps) => {
    if (nps >= 50) return 'text-green-600';
    if (nps >= 0) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Score Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-2xl shadow-soft p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10">
            <svg className="w-24 h-24" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-4h2v2h-2zm0-2h2V7h-2z" /></svg>
          </div>
          <p className="text-sm font-bold text-slate-500 uppercase tracking-wide">Weighted NPS</p>
          <div className="mt-4 flex items-baseline gap-2">
            <span className={`text-5xl font-black tracking-tight ${getNpsColor(results.nps_score)}`}>
              {results.nps_score.toFixed(1)}
            </span>
            <span className="text-sm font-medium text-slate-400">Score</span>
          </div>
          <div className="mt-4 flex flex-col gap-2">
            <div className="flex items-center gap-2 text-xs font-medium text-slate-500 bg-slate-50 w-fit px-2 py-1 rounded-lg">
              <span>Actual Respondents:</span>
              <span className="text-slate-700 font-bold">{results.total_responses.toLocaleString()}</span>
            </div>
            <div className="flex items-center gap-2 text-xs font-medium text-slate-500 bg-slate-50 w-fit px-2 py-1 rounded-lg">
              <span>Scale Factor:</span>
              <span className="text-slate-700">{results.scale_factor.toFixed(4)}</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-soft p-6 border-b-4 border-green-500">
          <p className="text-sm font-bold text-slate-500 uppercase tracking-wide">Promoters</p>
          <div className="mt-4">
            <span className="text-4xl font-bold text-slate-800">{results.promoters_pct.toFixed(1)}%</span>
            <p className="text-xs text-green-600 font-medium mt-1">Score 9-10</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-soft p-6 border-b-4 border-yellow-500">
          <p className="text-sm font-bold text-slate-500 uppercase tracking-wide">Passives</p>
          <div className="mt-4">
            <span className="text-4xl font-bold text-slate-800">{results.passives_pct.toFixed(1)}%</span>
            <p className="text-xs text-yellow-600 font-medium mt-1">Score 7-8</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-soft p-6 border-b-4 border-red-500">
          <p className="text-sm font-bold text-slate-500 uppercase tracking-wide">Detractors</p>
          <div className="mt-4">
            <span className="text-4xl font-bold text-slate-800">{results.detractors_pct.toFixed(1)}%</span>
            <p className="text-xs text-red-600 font-medium mt-1">Score 0-6</p>
          </div>
        </div>
      </div>

      {/* Demographic Table */}
      {results.demographic_breakdown && results.demographic_breakdown.length > 0 && (
        <div className="bg-white rounded-2xl shadow-soft overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex justify-between items-center">
            <h3 className="text-lg font-bold text-slate-800">Demographic Breakdown</h3>
            <span className="text-xs font-medium bg-slate-100 text-slate-600 px-3 py-1 rounded-full">
              Top 20 Segments
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50/50 text-xs font-bold text-slate-500 uppercase tracking-wider border-b border-slate-100">
                  <th className="px-6 py-4">Gender</th>
                  <th className="px-6 py-4">Age Group</th>
                  <th className="px-6 py-4">Region</th>
                  <th className="px-6 py-4">Club</th>
                  {results.demographic_breakdown[0].division && <th className="px-6 py-4">Division</th>}
                  <th className="px-6 py-4 text-right">NPS</th>
                  <th className="px-6 py-4 text-right">Count</th>
                  <th className="px-6 py-4 text-right">Weight</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {results.demographic_breakdown.slice(0, 20).map((segment, index) => (
                  <tr key={index} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-6 py-3 text-sm font-medium text-slate-700">{segment.gender}</td>
                    <td className="px-6 py-3 text-sm text-slate-600">{segment.age_group}</td>
                    <td className="px-6 py-3 text-sm text-slate-600">{segment.rgn_nm}</td>
                    <td className="px-6 py-3 text-sm text-slate-600">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${segment.bmclub === '구독' ? 'bg-brand-50 text-brand-700' : 'bg-slate-100 text-slate-600'}`}>
                        {segment.bmclub}
                      </span>
                    </td>
                    {segment.division && <td className="px-6 py-3 text-sm text-slate-600">{segment.division}</td>}
                    <td className={`px-6 py-3 text-sm font-bold text-right ${getNpsColor(segment.nps)}`}>
                      {segment.nps.toFixed(1)}
                    </td>
                    <td className="px-6 py-3 text-sm text-slate-500 text-right font-mono">{segment.count}</td>
                    <td className="px-6 py-3 text-sm text-slate-500 text-right font-mono">{segment.weight.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Category Analysis */}
      {results.category_analysis && (
        <div className="bg-white rounded-2xl shadow-soft p-6">
          <h3 className="text-lg font-bold text-slate-800 mb-6">Key Drivers by NPS Group</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {['Promoter', 'Passive', 'Detractor'].map((group) => {
              const data = results.category_analysis[group];
              if (!data) return null;

              const colors = {
                Promoter: { bg: 'bg-green-50', text: 'text-green-800', border: 'border-green-100', bar: 'bg-green-500' },
                Passive: { bg: 'bg-yellow-50', text: 'text-yellow-800', border: 'border-yellow-100', bar: 'bg-yellow-500' },
                Detractor: { bg: 'bg-red-50', text: 'text-red-800', border: 'border-red-100', bar: 'bg-red-500' }
              }[group];

              return (
                <div key={group} className={`rounded-xl p-5 ${colors.bg} border ${colors.border}`}>
                  <h4 className={`font-bold ${colors.text} mb-4 flex items-center gap-2`}>
                    {group}s
                    <span className="text-xs font-normal opacity-70">Top 5 Categories</span>
                  </h4>
                  <div className="space-y-3">
                    {data.slice(0, 5).map((cat, idx) => (
                      <div key={idx} className="bg-white/60 rounded-lg p-3 backdrop-blur-sm">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm font-medium text-slate-700 truncate pr-2">{cat.category}</span>
                          <span className={`text-sm font-bold ${colors.text}`}>{cat.response_rate.toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-black/5 rounded-full h-1.5 overflow-hidden">
                          <div className={`h-full rounded-full ${colors.bar}`} style={{ width: `${Math.min(cat.response_rate, 100)}%` }}></div>
                        </div>
                        <div className="mt-1 text-[10px] text-slate-500 text-right">
                          n={cat.count}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default FoodNpsResults;
