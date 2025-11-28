import React, { useState } from 'react';

const FileUpload = ({ onUploadComplete }) => {
    const [status, setStatus] = useState({
        qualtrics: { status: 'idle', filename: '', rows: 0 },
        population: { status: 'idle', filename: '', rows: 0 },
        coding: { status: 'idle', filename: '', rows: 0 }
    });

    const handleUpload = async (type, file) => {
        const formData = new FormData();
        formData.append('file', file);

        setStatus(prev => ({
            ...prev,
            [type]: { ...prev[type], status: 'uploading', filename: file.name }
        }));

        try {
            const response = await fetch(`http://localhost:8000/upload/${type}`, {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                setStatus(prev => ({
                    ...prev,
                    [type]: {
                        status: 'uploaded',
                        filename: file.name,
                        rows: data.rows || 0
                    }
                }));
                onUploadComplete();
            } else {
                setStatus(prev => ({
                    ...prev,
                    [type]: { ...prev[type], status: 'error' }
                }));
            }
        } catch (error) {
            console.error(error);
            setStatus(prev => ({
                ...prev,
                [type]: { ...prev[type], status: 'error' }
            }));
        }
    };

    const UploadCard = ({ type, title, description, required }) => {
        const currentStatus = status[type] || { status: 'idle' };
        const isUploaded = currentStatus.status === 'uploaded';
        const isUploading = currentStatus.status === 'uploading';

        return (
            <div className={`group relative bg-white rounded-2xl p-6 transition-all duration-300 ${isUploaded
                ? 'shadow-soft ring-2 ring-green-500/20'
                : 'shadow-card hover:shadow-lg hover:-translate-y-1'
                }`}>
                <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                            <h3 className="text-lg font-bold text-slate-800 capitalize">{title}</h3>
                            {required && <span className="px-2 py-0.5 rounded-full bg-red-50 text-red-600 text-[10px] font-bold uppercase tracking-wider">Required</span>}
                        </div>
                        <p className="text-sm text-slate-500 leading-relaxed">{description}</p>
                    </div>
                    {isUploaded && (
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
                            onChange={(e) => handleUpload(type, e.target.files[0])}
                            className="hidden"
                        />
                        <div className={`relative overflow-hidden rounded-xl border-2 border-dashed transition-all duration-300 h-32 flex flex-col items-center justify-center ${isUploading
                            ? 'border-brand-200 bg-brand-50'
                            : isUploaded
                                ? 'border-green-200 bg-green-50/30'
                                : 'border-slate-200 bg-slate-50/50 group-hover/label:border-brand-400 group-hover/label:bg-brand-50/30'
                            }`}>
                            {isUploading ? (
                                <div className="flex flex-col items-center">
                                    <div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin mb-2"></div>
                                    <span className="text-xs font-medium text-brand-600">Uploading...</span>
                                </div>
                            ) : (
                                <>
                                    <div className={`mb-2 transition-transform duration-300 ${isUploaded ? 'scale-90' : 'group-hover/label:scale-110'}`}>
                                        {isUploaded ? (
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
                                        {isUploaded ? currentStatus.filename : 'Click to upload CSV'}
                                    </p>
                                </>
                            )}
                        </div>
                    </label>
                </div>

                {/* File Details Footer */}
                {isUploaded && (
                    <div className="mt-4 pt-4 border-t border-slate-100">
                        <div className="flex items-center justify-between text-xs">
                            <span className="text-slate-500 uppercase tracking-wide font-medium">Rows Loaded</span>
                            <span className="font-bold text-brand-600 bg-brand-50 px-2 py-1 rounded-md">
                                {currentStatus.rows.toLocaleString()}
                            </span>
                        </div>
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-brand-100 rounded-xl flex items-center justify-center text-brand-600 font-bold text-lg">1</div>
                <h2 className="text-xl font-bold text-slate-800">Upload Data Files</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <UploadCard
                    type="qualtrics"
                    title="Qualtrics Data"
                    description="Survey response data containing NPS scores."
                    required={true}
                />
                <UploadCard
                    type="population"
                    title="Population Data"
                    description="Demographic segments for weighting."
                    required={true}
                />
                <UploadCard
                    type="coding"
                    title="Coding Data"
                    description="Open-ended response categorization."
                    required={false}
                />
            </div>
        </div>
    );
};

export default FileUpload;
