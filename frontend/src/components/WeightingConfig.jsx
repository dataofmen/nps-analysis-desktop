import React, { useState, useEffect } from 'react';

const WeightingConfig = ({ columns, onConfigChange, dataVersion }) => {
    const [selectedColumns, setSelectedColumns] = useState([]);
    const [segments, setSegments] = useState([]);
    const [targets, setTargets] = useState({});
    const [isFetching, setIsFetching] = useState(false);
    const [popColumns, setPopColumns] = useState([]);
    const [selectedTargetCol, setSelectedTargetCol] = useState('');

    const [segmentationOptions, setSegmentationOptions] = useState([]);

    useEffect(() => {
        // Fetch population columns whenever dataVersion changes (new upload)
        const fetchPopColumns = async () => {
            try {
                const response = await fetch('http://localhost:8000/population-columns');
                const data = await response.json();
                setPopColumns(data.columns || []);
            } catch (error) {
                console.error("Error fetching population columns:", error);
            }
        };

        // Fetch Qualtrics columns for segmentation (ignore coding columns)
        const fetchQualtricsColumns = async () => {
            try {
                const response = await fetch('http://localhost:8000/columns/qualtrics');
                const data = await response.json();
                setSegmentationOptions(data.columns || []);
            } catch (error) {
                console.error("Error fetching qualtrics columns:", error);
            }
        };

        fetchPopColumns();
        fetchQualtricsColumns();
    }, [dataVersion]);

    useEffect(() => {
        if (selectedColumns.length > 0) {
            // Add a small delay to ensure backend has processed the file upload
            const timer = setTimeout(() => {
                fetchSegments();
            }, 500);
            return () => clearTimeout(timer);
        } else {
            setSegments([]);
            setTargets({}); // Clear targets if no columns are selected
            onConfigChange({ segment_columns: [], targets: {}, target_column: null });
        }
    }, [selectedColumns, dataVersion, selectedTargetCol]); // Re-fetch if target column changes

    const fetchSegments = async () => {
        setIsFetching(true);
        try {
            const response = await fetch('http://localhost:8000/preview-segments', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    segment_columns: selectedColumns,
                    target_column: selectedTargetCol || null
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to fetch segments');
            }

            const data = await response.json();
            setSegments(Array.isArray(data.segments) ? data.segments : []);

            // Auto-fill targets if suggested by backend (from uploaded Population data)
            if (data.suggested_targets && Object.keys(data.suggested_targets).length > 0) {
                setTargets(data.suggested_targets);
                onConfigChange({ segment_columns: selectedColumns, targets: data.suggested_targets, target_column: selectedTargetCol });
            } else {
                // Only reset targets if we don't have suggestions AND the segments have likely changed (implied by this fetch)
                // However, if we are just re-fetching due to dataVersion change and no new suggestions came,
                // we might want to preserve manual inputs?
                // For now, let's strictly follow the rule: if no suggestion, reset, UNLESS we want to preserve manual work.
                // But the user complaint is about auto-fill NOT working.

                // If we are here, it means no suggestions were found.
                // If this was triggered by Population upload, it means the upload didn't result in matches.
                // Let's keep the reset for now but ensure we log why.
                console.log("No suggested targets found.");

                // If segments changed, we must reset.
                // We can check if the new segments are different from current state 'segments'.
                // But 'segments' state might be stale in this closure? No, it's from useState.
                // Actually, let's just reset to be safe, or the UI will be mismatched.
                setTargets({});
                onConfigChange({ segment_columns: selectedColumns, targets: {}, target_column: selectedTargetCol });
            }
        } catch (error) {
            console.error(error);
            alert(`Error fetching segments: ${error.message}`);
            setSegments([]);
        } finally {
            setIsFetching(false);
        }
    };

    const handleTargetChange = (segment, value) => {
        const newTargets = { ...targets, [segment]: parseFloat(value) };
        setTargets(newTargets);
        onConfigChange({ segment_columns: selectedColumns, targets: newTargets, target_column: selectedTargetCol });
    };

    const handleColumnToggle = (col) => {
        const newCols = selectedColumns.includes(col)
            ? selectedColumns.filter(c => c !== col)
            : [...selectedColumns, col];
        setSelectedColumns(newCols);
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-brand-100 rounded-xl flex items-center justify-center text-brand-600 font-bold text-lg">2</div>
                <h2 className="text-xl font-bold text-slate-800">Weighting Configuration</h2>
            </div>

            <div className="bg-white rounded-2xl shadow-soft p-6">
                <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wide mb-4">Select Segmentation Columns</h3>
                <div className="flex flex-wrap gap-3">
                    {segmentationOptions.map(col => (
                        <button
                            key={col}
                            onClick={() => handleColumnToggle(col)}
                            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 border ${selectedColumns.includes(col)
                                ? 'bg-brand-50 border-brand-200 text-brand-700 shadow-sm'
                                : 'bg-white border-slate-200 text-slate-600 hover:border-brand-200 hover:text-brand-600'
                                }`}
                        >
                            <div className="flex items-center gap-2">
                                <div className={`w-4 h-4 rounded-full border flex items-center justify-center transition-colors ${selectedColumns.includes(col)
                                    ? 'bg-brand-500 border-brand-500'
                                    : 'border-slate-300'
                                    }`}>
                                    {selectedColumns.includes(col) && (
                                        <svg className="w-2.5 h-2.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                        </svg>
                                    )}
                                </div>
                                {col}
                            </div>
                        </button>
                    ))}
                </div>
            </div>

            {/* Target Column Selector */}
            {popColumns.length > 0 && (
                <div className="bg-white rounded-2xl shadow-soft p-6">
                    <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wide mb-4">Select Target Column (Optional)</h3>
                    <div className="max-w-xs">
                        <select
                            value={selectedTargetCol}
                            onChange={(e) => setSelectedTargetCol(e.target.value)}
                            className="w-full bg-slate-50 border border-slate-200 text-slate-700 text-sm rounded-xl focus:ring-brand-500 focus:border-brand-500 block p-2.5"
                        >
                            <option value="">Count Rows (Default)</option>
                            {popColumns.map(col => (
                                <option key={col} value={col}>{col}</option>
                            ))}
                        </select>
                        <p className="mt-2 text-xs text-slate-400">
                            Select a column from Population Data to use as weights (e.g., 'mem_rate'). If not selected, row counts will be used.
                        </p>
                    </div>
                </div>
            )}

            {isFetching && (
                <div className="flex items-center justify-center p-8 bg-white rounded-2xl shadow-soft">
                    <div className="w-6 h-6 border-2 border-brand-500 border-t-transparent rounded-full animate-spin mr-3"></div>
                    <span className="text-sm font-medium text-slate-500">Calculating segments and targets...</span>
                </div>
            )}

            {!isFetching && selectedColumns.length > 0 && segments.length === 0 && (
                <div className="bg-white rounded-2xl shadow-soft p-6 text-center text-slate-500 text-sm">
                    No segments found for the selected columns. Please try different columns or check your data.
                </div>
            )}

            {!isFetching && segments.length > 0 && (
                <div className="bg-white rounded-2xl shadow-soft p-6 animate-fade-in">
                    <div className="flex justify-between items-center mb-6">
                        <div className="flex items-center gap-2">
                            <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wide">Target Proportions (0-1)</h3>
                            <button
                                onClick={fetchSegments}
                                disabled={isFetching}
                                className="p-1 text-slate-400 hover:text-brand-600 transition-colors rounded-full hover:bg-brand-50"
                                title="Refresh Targets"
                            >
                                <svg className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                </svg>
                            </button>
                        </div>
                        <span className="text-xs font-medium bg-brand-50 text-brand-700 px-3 py-1 rounded-full">
                            {segments.length} Segments Identified
                        </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
                        {segments.map(seg => (
                            <div key={seg} className="flex items-center justify-between bg-slate-50 p-3 rounded-xl border border-slate-100 hover:border-brand-200 transition-colors group">
                                <span className="text-sm font-medium text-slate-700 truncate mr-3 flex-1" title={seg}>{seg}</span>
                                <div className="relative w-24">
                                    <input
                                        type="number"
                                        step="0.01"
                                        placeholder="0.0"
                                        value={targets[seg] || ''}
                                        className="w-full bg-white border border-slate-200 rounded-lg px-3 py-1.5 text-right text-sm font-mono focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all"
                                        onChange={(e) => handleTargetChange(seg, e.target.value)}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default WeightingConfig;
