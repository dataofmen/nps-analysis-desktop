import React, { useState, useEffect } from 'react';

const SelectField = ({ label, value, onChange, options = [] }) => (
    <div>
        <label className="block text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">{label}</label>
        <div className="relative">
            <select
                value={value}
                onChange={onChange}
                className="w-full appearance-none bg-white border border-slate-200 rounded-xl px-4 py-3 text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all cursor-pointer"
            >
                <option value="">Select Column</option>
                {options.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
            <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </div>
        </div>
    </div>
);

const MultiSelectField = ({ label, selectedValues, onChange, options = [] }) => {
    const handleToggle = (col) => {
        if (selectedValues.includes(col)) {
            onChange(selectedValues.filter(c => c !== col));
        } else {
            onChange([...selectedValues, col]);
        }
    };

    return (
        <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">{label}</label>
            <div className="bg-white border border-slate-200 rounded-xl p-2 max-h-48 overflow-y-auto custom-scrollbar">
                {options.map(col => (
                    <div
                        key={col}
                        onClick={() => handleToggle(col)}
                        className="flex items-center gap-3 p-2 hover:bg-slate-50 rounded-lg cursor-pointer transition-colors select-none"
                    >
                        <div className={`w-5 h-5 rounded border flex items-center justify-center transition-all ${selectedValues.includes(col) ? 'bg-brand-500 border-brand-500' : 'border-slate-300 bg-white'
                            }`}>
                            {selectedValues.includes(col) && (
                                <svg className="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                </svg>
                            )}
                        </div>
                        <span className="text-sm text-slate-700 font-medium">{col}</span>
                    </div>
                ))}
            </div>
            <p className="text-xs text-slate-400 mt-1 px-1">{selectedValues.length} columns selected</p>
        </div>
    );
};

const ScoreCard = ({ title, value, subtext, color, icon }) => {
    const colors = {
        blue: 'text-brand-600 bg-brand-50 border-brand-100',
        green: 'text-green-600 bg-green-50 border-green-100',
        purple: 'text-purple-600 bg-purple-50 border-purple-100',
    };
    const theme = colors[color] || colors.blue;

    return (
        <div className="bg-white rounded-2xl shadow-soft p-6 relative overflow-hidden group hover:shadow-lg transition-all duration-300">
            <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                {icon}
            </div>
            <p className="text-sm font-bold text-slate-500 uppercase tracking-wide">{title}</p>
            <div className="mt-4 flex items-baseline gap-2">
                <span className={`text-4xl font-black tracking-tight ${theme.split(' ')[0]}`}>
                    {value}
                </span>
            </div>
            {subtext && (
                <div className={`mt-3 inline-flex items-center text-xs font-bold px-2 py-1 rounded-lg ${theme}`}>
                    {subtext}
                </div>
            )}
        </div>
    );
};

const MultiResultCard = ({ title, data = {}, color, icon, subtext }) => {
    const colors = {
        green: 'text-green-600 bg-green-50 border-green-100 bar-green-500',
        purple: 'text-purple-600 bg-purple-50 border-purple-100 bar-purple-500',
    };
    const theme = colors[color] || colors.green;
    const barClass = theme.split(' ').find(c => c.startsWith('bar-'));
    const barColor = barClass ? barClass.replace('bar-', 'bg-') : 'bg-brand-500';

    return (
        <div className="bg-white rounded-2xl shadow-soft p-6 relative overflow-hidden group hover:shadow-lg transition-all duration-300">
            <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                {icon}
            </div>
            <p className="text-sm font-bold text-slate-500 uppercase tracking-wide mb-4">{title}</p>
            <div className="space-y-4 max-h-60 overflow-y-auto custom-scrollbar pr-2">
                {data && Object.keys(data).length > 0 ? (
                    Object.entries(data).map(([key, value]) => (
                        <div key={key}>
                            <div className="flex justify-between items-end mb-1">
                                <span className="text-xs font-medium text-slate-600 truncate max-w-[70%]">{key}</span>
                                <span className={`text-lg font-bold ${theme.split(' ')[0]}`}>{Number(value.percentage).toFixed(1)}%</span>
                            </div>
                            <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                                <div className={`h-full rounded-full ${barColor}`} style={{ width: `${Math.min(value.percentage || 0, 100)}%` }}></div>
                            </div>
                        </div>
                    ))
                ) : (
                    <p className="text-sm text-slate-400 italic">No data available</p>
                )}
            </div>
            {subtext && (
                <div className={`mt-4 inline-flex items-center text-xs font-bold px-2 py-1 rounded-lg ${theme.split(' ').slice(0, 3).join(' ')}`}>
                    {subtext}
                </div>
            )}
        </div>
    );
};

const NPSBreakdown = ({ breakdown }) => {
    if (!breakdown) return null;
    return (
        <div className="bg-white rounded-2xl shadow-soft p-6">
            <h4 className="text-sm font-bold text-slate-500 uppercase tracking-wide mb-4">NPS Breakdown</h4>
            <div className="flex h-8 rounded-full overflow-hidden">
                <div className="bg-green-500 h-full flex items-center justify-center text-white text-xs font-bold" style={{ width: `${breakdown.promoters}%` }} title={`Promoters: ${breakdown.promoters}%`}>
                    {breakdown.promoters > 5 && `${breakdown.promoters}%`}
                </div>
                <div className="bg-slate-300 h-full flex items-center justify-center text-slate-600 text-xs font-bold" style={{ width: `${breakdown.passives}%` }} title={`Passives: ${breakdown.passives}%`}>
                    {breakdown.passives > 5 && `${breakdown.passives}%`}
                </div>
                <div className="bg-red-500 h-full flex items-center justify-center text-white text-xs font-bold" style={{ width: `${breakdown.detractors}%` }} title={`Detractors: ${breakdown.detractors}%`}>
                    {breakdown.detractors > 5 && `${breakdown.detractors}%`}
                </div>
            </div>
            <div className="flex justify-between mt-3 text-xs font-medium text-slate-500">
                <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-green-500"></div>Promoters (9-10)</div>
                <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-slate-300"></div>Passives (7-8)</div>
                <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-red-500"></div>Detractors (0-6)</div>
            </div>
        </div>
    );
};

const NPSDistribution = ({ distribution }) => {
    if (!distribution) return null;

    // Helper to determine group and color
    const getGroupInfo = (score) => {
        if (score >= 9) return { label: 'Promoter', color: 'text-green-600 bg-green-50' };
        if (score >= 7) return { label: 'Passive', color: 'text-slate-600 bg-slate-50' };
        return { label: 'Detractor', color: 'text-red-600 bg-red-50' };
    };

    return (
        <div className="bg-white rounded-2xl shadow-soft p-6">
            <h4 className="text-sm font-bold text-slate-500 uppercase tracking-wide mb-4">Score Distribution (0-10)</h4>
            <div className="overflow-hidden rounded-xl border border-slate-200">
                <table className="w-full text-sm text-left text-slate-600">
                    <thead className="text-xs text-slate-700 uppercase bg-slate-50 border-b border-slate-200">
                        <tr>
                            <th className="px-4 py-3 font-bold text-center w-16">Score</th>
                            <th className="px-4 py-3 font-bold text-right">Count</th>
                            <th className="px-4 py-3 font-bold text-right">Percent</th>
                            <th className="px-4 py-3 font-bold text-center">Group</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {[...Array(11)].map((_, i) => {
                            const score = 10 - i; // Descending order (10 to 0) usually looks better in tables
                            const data = distribution[score.toString()] || { count: 0, percent: 0 };
                            const groupInfo = getGroupInfo(score);

                            return (
                                <tr key={score} className="hover:bg-slate-50/50 transition-colors">
                                    <td className="px-4 py-2 font-bold text-center text-slate-800">{score}</td>
                                    <td className="px-4 py-2 text-right font-mono">{Math.round(data.count)}</td>
                                    <td className="px-4 py-2 text-right font-mono font-medium">{Number(data.percent).toFixed(1)}%</td>
                                    <td className="px-4 py-2 text-center">
                                        <span className={`text-[10px] font-bold px-2 py-1 rounded-full ${groupInfo.color}`}>
                                            {groupInfo.label}
                                        </span>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

const Dashboard = ({ columns, weightingConfig, dataVersion }) => {
    const [npsCol, setNpsCol] = useState('');
    const [topBoxCols, setTopBoxCols] = useState([]);
    const [groupByCols, setGroupByCols] = useState([]); // Changed to array
    const [groupWeightingCols, setGroupWeightingCols] = useState([]);
    const [openEndCols, setOpenEndCols] = useState(['', '', '']); // Level 1, 2, 3
    const [openEndNpsCol, setOpenEndNpsCol] = useState('');

    const [activeTab, setActiveTab] = useState('quantitative'); // 'quantitative' or 'open-ended'

    const [qualtricsCols, setQualtricsCols] = useState([]);
    const [codingCols, setCodingCols] = useState([]);

    useEffect(() => {
        if (npsCol) {
            setOpenEndNpsCol(npsCol);
        }
    }, [npsCol]);

    useEffect(() => {
        const fetchColumns = async () => {
            try {
                const qRes = await fetch('http://localhost:8000/columns/qualtrics');
                const qData = await qRes.json();
                setQualtricsCols(qData.columns || []);

                const cRes = await fetch('http://localhost:8000/columns/coding');
                const cData = await cRes.json();
                setCodingCols(cData.columns || []);
            } catch (error) {
                console.error("Error fetching columns:", error);
            }
        };
        fetchColumns();
    }, [dataVersion]);

    // Auto-set group weighting columns when group by columns change
    useEffect(() => {
        if (groupByCols.length > 0 && weightingConfig?.segment_columns) {
            // Default: all weighting columns EXCEPT the ones used for grouping
            const defaults = weightingConfig.segment_columns.filter(col => !groupByCols.includes(col));
            setGroupWeightingCols(defaults);
        } else {
            setGroupWeightingCols([]);
        }
    }, [groupByCols, weightingConfig]);

    const [metricsResults, setMetricsResults] = useState(null);
    const [rrResults, setRrResults] = useState(null);

    const [loadingMetrics, setLoadingMetrics] = useState(false);
    const [loadingRR, setLoadingRR] = useState(false);

    const handleCalculateMetrics = async () => {
        if (!npsCol) {
            alert("Please select an NPS Column first.");
            return;
        }

        setLoadingMetrics(true);
        setMetricsResults(null);

        // Helper for logging
        const log = (msg) => {
            console.log(msg);
            try {
                if (window.require) {
                    const { ipcRenderer } = window.require('electron');
                    ipcRenderer.send('log-to-file', msg);
                }
            } catch (e) {
                // Ignore if not in Electron
            }
        };

        log(`Starting analysis for NPS Column: ${npsCol}`);

        try {
            const response = await fetch('http://localhost:8000/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    nps_column: npsCol,
                    top_box_columns: topBoxCols,
                    group_by_columns: groupByCols, // Pass array
                    group_weighting_columns: groupWeightingCols,
                    open_end_columns: [], // Not needed for metrics
                    weighting_config: weightingConfig
                }),
            });

            log(`Analysis response status: ${response.status}`);

            if (!response.ok) {
                const errorData = await response.json();
                const errorMsg = errorData.detail || 'Metrics analysis failed';
                log(`Analysis failed: ${errorMsg}`);
                throw new Error(errorMsg);
            }

            const data = await response.json();
            log(`Analysis success. Data keys: ${Object.keys(data).join(', ')}`);
            log(`NPS Data: ${JSON.stringify(data.nps)}`);

            setMetricsResults(data);
        } catch (error) {
            console.error(error);
            log(`Analysis Exception: ${error.message}`);
            alert(`Metrics Error: ${error.message}`);
        } finally {
            setLoadingMetrics(false);
        }
    };

    const handleCalculateResponseRates = async () => {
        const validCols = openEndCols.filter(c => c !== '');
        if (validCols.length === 0) {
            alert("Please select at least one Open End column.");
            return;
        }

        setLoadingRR(true);
        setRrResults(null);

        try {
            const response = await fetch('http://localhost:8000/analyze/response-rates', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    nps_column: openEndNpsCol, // Pass selected NPS column for segmentation
                    top_box_columns: [], // Not needed
                    open_end_columns: validCols,
                    weighting_config: weightingConfig // Pass config to enable exclusion logic
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Response rate analysis failed');
            }

            const data = await response.json();
            setRrResults(data);
        } catch (error) {
            console.error(error);
            alert(`Response Rate Error: ${error.message}`);
        } finally {
            setLoadingRR(false);
        }
    };

    const handleExportQuantitative = () => {
        if (!metricsResults) return;

        try {
            // 1. Overview Data
            let csvContent = "Metric,Value\n";
            csvContent += `NPS Score,${metricsResults.nps?.score !== undefined ? Number(metricsResults.nps.score).toFixed(1) : Number(metricsResults.nps).toFixed(1)}\n`;
            csvContent += `Promoters %,${metricsResults.nps?.breakdown?.promoters || 0}\n`;
            csvContent += `Passives %,${metricsResults.nps?.breakdown?.passives || 0}\n`;
            csvContent += `Detractors %,${metricsResults.nps?.breakdown?.detractors || 0}\n`;

            // Score Distribution
            if (metricsResults.nps?.distribution) {
                csvContent += "\nScore Distribution\n";
                csvContent += "Score,Count,Percent\n";
                // Sort 10 to 0
                [...Array(11)].forEach((_, i) => {
                    const score = 10 - i;
                    const data = metricsResults.nps.distribution[score.toString()] || { count: 0, percent: 0 };
                    csvContent += `${score},${data.count},${Number(data.percent).toFixed(1)}%\n`;
                });
                csvContent += "\n";
            }

            // Top Box
            Object.entries(metricsResults.top_box_3_percent).forEach(([col, score]) => {
                csvContent += `Top 3 Box % (${col}),${Number(score).toFixed(1)}\n`;
            });

            // 2. Segmented Results
            if (metricsResults.segmented_results && Object.keys(metricsResults.segmented_results).length > 0) {
                csvContent += "\n\nSegmented Analysis\n";

                // Get all Top Box columns
                const topBoxCols = Object.keys(metricsResults.top_box_3_percent);

                // Header
                csvContent += "Group Column,Group Value,NPS";
                topBoxCols.forEach(col => {
                    csvContent += `,Top Box % (${col})`;
                });
                csvContent += "\n";

                Object.entries(metricsResults.segmented_results).forEach(([groupCol, groupData]) => {
                    Object.entries(groupData).forEach(([groupVal, stats]) => {
                        // Escape commas in values
                        const safeGroupVal = `"${groupVal.replace(/"/g, '""')}"`;

                        csvContent += `"${groupCol}",${safeGroupVal},${Number(stats.nps).toFixed(1)}`;

                        // Add each Top Box column value
                        topBoxCols.forEach(col => {
                            const val = stats.top_box_3_percent[col];
                            csvContent += `,${val !== undefined ? Number(val).toFixed(1) + '%' : '-'}`;
                        });
                        csvContent += "\n";
                    });
                });
            }

            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'nps_analysis_quantitative.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Export error:', error);
            alert('Failed to export CSV file.');
        }
    };

    const handleExportOpenEndedCSV = () => {
        if (!rrResults) return;
        try {
            let csvContent = "Column,Segment,Total Count,Response Rate,Category,Count,Percentage\n";

            if (rrResults.response_rates) {
                Object.entries(rrResults.response_rates).forEach(([col, segments]) => {
                    Object.entries(segments).forEach(([segName, stats]) => {
                        // Base info for this segment
                        const baseInfo = `"${col}","${segName}",${stats.total_count},${stats.response_rate}%`;

                        if (stats.category_stats && Object.keys(stats.category_stats).length > 0) {
                            // Add a row for each category
                            Object.entries(stats.category_stats).forEach(([cat, val]) => {
                                // val is {count, percentage}
                                const percent = Number(val.percentage).toFixed(1);
                                const count = val.count;
                                csvContent += `${baseInfo},"${cat.replace(/"/g, '""')}",${count},${percent}%\n`;
                            });
                        } else {
                            // No categories, just segment info
                            csvContent += `${baseInfo},,,\n`;
                        }
                    });
                });
            }

            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'nps_analysis_open_ended.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Export error:', error);
            alert('Failed to export CSV file.');
        }
    };

    return (
        <div className="space-y-8">
            <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-brand-100 rounded-xl flex items-center justify-center text-brand-600 font-bold text-lg">3</div>
                <h2 className="text-xl font-bold text-slate-800">Analysis Dashboard</h2>
            </div>

            {/* Tab Navigation */}
            <div className="flex space-x-1 bg-slate-100 p-1 rounded-xl mb-6 w-fit">
                <button
                    onClick={() => setActiveTab('quantitative')}
                    className={`px-4 py-2 text-sm font-bold rounded-lg transition-all ${activeTab === 'quantitative'
                        ? 'bg-white text-brand-600 shadow-sm'
                        : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'
                        }`}
                >
                    Quantitative Metrics
                </button>
                <button
                    onClick={() => setActiveTab('open-ended')}
                    className={`px-4 py-2 text-sm font-bold rounded-lg transition-all ${activeTab === 'open-ended'
                        ? 'bg-white text-brand-600 shadow-sm'
                        : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'
                        }`}
                >
                    Open-Ended Analysis
                </button>
            </div>

            <div className="grid grid-cols-1 gap-8">
                {/* Section 1: Quantitative Metrics */}
                {activeTab === 'quantitative' && (
                    <div className="space-y-6 animate-fade-in">
                        <div className="bg-white rounded-2xl shadow-soft p-6 h-full flex flex-col">
                            <div className="flex items-center justify-between mb-6 border-b border-slate-100 pb-4">
                                <div className="flex items-center gap-2">
                                    <span className="text-2xl">📊</span>
                                    <h3 className="text-lg font-bold text-slate-800">Quantitative Metrics</h3>
                                </div>
                            </div>

                            <div className="space-y-6 flex-1">
                                <SelectField
                                    label="NPS Column"
                                    value={npsCol}
                                    onChange={e => setNpsCol(e.target.value)}
                                    options={qualtricsCols}
                                />
                                <MultiSelectField
                                    label="Top Box Columns (7-pt)"
                                    selectedValues={topBoxCols}
                                    onChange={setTopBoxCols}
                                    options={qualtricsCols}
                                />
                                <MultiSelectField
                                    label="Group By (Optional)"
                                    selectedValues={groupByCols}
                                    onChange={setGroupByCols}
                                    options={qualtricsCols}
                                />
                                {groupByCols.length > 0 && weightingConfig?.segment_columns?.length > 0 && (
                                    <MultiSelectField
                                        label="Weighting Variables for Grouping"
                                        selectedValues={groupWeightingCols}
                                        onChange={setGroupWeightingCols}
                                        options={weightingConfig.segment_columns}
                                    />
                                )}
                            </div>
                        </div>

                        <div className="mt-4">
                            <button
                                onClick={handleCalculateMetrics}
                                disabled={loadingMetrics}
                                className="w-full bg-brand-600 text-white py-3 rounded-xl font-bold shadow-lg shadow-brand-500/30 hover:bg-brand-700 hover:shadow-brand-500/40 active:scale-[0.99] disabled:bg-slate-200 disabled:text-slate-400 disabled:shadow-none transition-all duration-200 flex items-center justify-center gap-2"
                            >
                                {loadingMetrics ? (
                                    <>
                                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                        Calculating...
                                    </>
                                ) : (
                                    <>
                                        <span>⚡</span> Calculate Scores
                                    </>
                                )}
                            </button>
                        </div>


                        {/* Metrics Results */}
                        {metricsResults && (
                            <div className="space-y-6 animate-fade-in">
                                {metricsResults.excluded_count > 0 && (
                                    <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-center gap-3 text-amber-800 text-sm">
                                        <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                        </svg>
                                        <span>
                                            <strong>Note:</strong> {metricsResults.excluded_count} respondents were excluded from analysis due to missing weighting data.
                                        </span>
                                    </div>
                                )}
                                <div className="flex items-center justify-between">
                                    <h4 className="text-lg font-bold text-slate-800">Analysis Results</h4>
                                    <button
                                        onClick={handleExportQuantitative}
                                        className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-white bg-green-600 hover:bg-green-700 rounded-xl shadow-sm transition-all active:scale-95"
                                        title="Export to CSV"
                                    >
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                        </svg>
                                        Export CSV
                                    </button>
                                </div>
                                <ScoreCard
                                    title="NPS Score"
                                    value={metricsResults.nps?.score !== undefined ? Number(metricsResults.nps.score).toFixed(1) : Number(metricsResults.nps).toFixed(1)}
                                    subtext={metricsResults.weighted ? "Weighted Score" : "Raw Score"}
                                    color="blue"
                                    icon={<svg className="w-24 h-24" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-4h2v2h-2zm0-2h2V7h-2z" /></svg>}
                                />

                                {/* NPS Breakdown & Distribution */}
                                {metricsResults.nps?.breakdown && (
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <NPSBreakdown breakdown={metricsResults.nps.breakdown} />
                                        <NPSDistribution distribution={metricsResults.nps.distribution} />
                                    </div>
                                )}

                                {/* Top Box Scores */}
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                    {Object.entries(metricsResults.top_box_3_percent).map(([col, score]) => (
                                        <ScoreCard
                                            key={col}
                                            title={col}
                                            value={Number(score).toFixed(1)}
                                            subtext="Top 3 Box %"
                                            color="green"
                                            icon={null}
                                        />
                                    ))}
                                </div>

                                {/* Comparative Table for Segmented Results */}
                                {metricsResults.segmented_results && Object.keys(metricsResults.segmented_results).length > 0 && (
                                    <div className="space-y-6">
                                        {Object.entries(metricsResults.segmented_results).map(([groupCol, groupData]) => (
                                            <div key={groupCol} className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm overflow-hidden">
                                                <h4 className="text-lg font-bold text-slate-800 mb-4">Analysis by {groupCol}</h4>
                                                <div className="overflow-x-auto">
                                                    <table className="w-full text-sm text-left text-slate-600">
                                                        <thead className="text-xs text-slate-700 uppercase bg-slate-50 border-b border-slate-200">
                                                            <tr>
                                                                <th className="px-6 py-3 font-bold">Group</th>
                                                                <th className="px-6 py-3 font-bold text-blue-600">NPS</th>
                                                                {Object.keys(metricsResults.top_box_3_percent).map(col => (
                                                                    <th key={col} className="px-6 py-3 font-bold text-green-600">{col}</th>
                                                                ))}
                                                            </tr>
                                                        </thead>
                                                        <tbody>
                                                            {Object.entries(groupData).map(([group, stats], index) => (
                                                                <tr key={group} className={`border-b border-slate-100 hover:bg-slate-50 ${index % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'}`}>
                                                                    <td className="px-6 py-4 font-medium text-slate-900">{group}</td>
                                                                    <td className="px-6 py-4 font-bold text-blue-600">{Number(stats.nps).toFixed(1)}</td>
                                                                    {Object.keys(metricsResults.top_box_3_percent).map(col => (
                                                                        <td key={col} className="px-6 py-4 text-green-600">
                                                                            {stats.top_box_3_percent[col] !== undefined ? Number(stats.top_box_3_percent[col]).toFixed(1) : '-'}%
                                                                        </td>
                                                                    ))}
                                                                </tr>
                                                            ))}
                                                        </tbody>
                                                    </table>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}

                {/* Section 2: Open-Ended Analysis */}
                {activeTab === 'open-ended' && (
                    <div className="space-y-6 animate-fade-in">
                        <div className="bg-white rounded-2xl shadow-soft p-6 h-full flex flex-col">
                            <div className="flex items-center justify-between mb-6 border-b border-slate-100 pb-4">
                                <div className="flex items-center gap-2">
                                    <span className="text-2xl">📝</span>
                                    <h3 className="text-lg font-bold text-slate-800">Open-Ended Analysis</h3>
                                </div>
                            </div>

                            <div className="space-y-6 flex-1">
                                <SelectField
                                    label="NPS Column (Optional)"
                                    value={openEndNpsCol}
                                    onChange={e => setOpenEndNpsCol(e.target.value)}
                                    options={qualtricsCols}
                                />
                                <div>
                                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">Open End Columns</label>
                                    <div className="space-y-3 bg-slate-50 p-4 rounded-xl border border-slate-100">
                                        {[0, 1, 2].map((level) => (
                                            <div key={level}>
                                                <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Level {level + 1}</label>
                                                <div className="relative">
                                                    <select
                                                        value={openEndCols[level]}
                                                        onChange={e => {
                                                            const newCols = [...openEndCols];
                                                            newCols[level] = e.target.value;
                                                            setOpenEndCols(newCols);
                                                        }}
                                                        className="w-full appearance-none bg-white border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all cursor-pointer"
                                                    >
                                                        <option value="">Select Column</option>
                                                        {codingCols.map(c => <option key={c} value={c}>{c}</option>)}
                                                    </select>
                                                    <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">
                                                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                                        </svg>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            <div className="mt-4">
                                <button
                                    onClick={handleCalculateResponseRates}
                                    disabled={loadingRR}
                                    className="w-full bg-purple-600 text-white py-3 rounded-xl font-bold shadow-lg shadow-purple-500/30 hover:bg-purple-700 hover:shadow-purple-500/40 active:scale-[0.99] disabled:bg-slate-200 disabled:text-slate-400 disabled:shadow-none transition-all duration-200 flex items-center justify-center gap-2"
                                >
                                    {loadingRR ? (
                                        <>
                                            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                            Calculating...
                                        </>
                                    ) : (
                                        <>
                                            <span>📈</span> Calculate Rates
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>

                        {/* Response Rate Results */}
                        {rrResults && rrResults.response_rates && (
                            <div className="space-y-8 animate-fade-in">
                                {rrResults.excluded_count > 0 && (
                                    <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-center gap-3 text-amber-800 text-sm">
                                        <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                        </svg>
                                        <span>
                                            <strong>Note:</strong> {rrResults.excluded_count} respondents were excluded from analysis due to missing weighting data (e.g., missing gender or age).
                                        </span>
                                    </div>
                                )}

                                <div className="flex items-center justify-between mb-4">
                                    <h4 className="text-lg font-bold text-slate-800">Analysis Results</h4>
                                    <button
                                        onClick={handleExportOpenEndedCSV}
                                        className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-white bg-purple-600 hover:bg-purple-700 rounded-xl shadow-sm transition-all active:scale-95"
                                        title="Export to CSV"
                                    >
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                        </svg>
                                        Export CSV
                                    </button>
                                </div>

                                {Object.entries(rrResults.response_rates).map(([colName, segments]) => (
                                    <div key={colName} className="bg-slate-50 rounded-2xl p-6 border border-slate-200">
                                        <h4 className="text-md font-bold text-slate-700 mb-4 flex items-center gap-2">
                                            <span className="w-2 h-6 bg-brand-500 rounded-full"></span>
                                            {colName} Analysis
                                        </h4>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            {Object.entries(segments).map(([segName, stats]) => (
                                                <MultiResultCard
                                                    key={segName}
                                                    title={`${segName}`}
                                                    data={stats.category_stats}
                                                    color={segName.includes('Detractor') || segName.includes('At-Risk') ? 'purple' : 'green'}
                                                    icon={null}
                                                    subtext={`${Object.keys(stats.category_stats || {}).length} Categories`}
                                                />
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>

    );
};

export default Dashboard;
