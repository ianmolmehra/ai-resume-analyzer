import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react'
import clsx from 'clsx'

export default function DropZone({ onFileAccepted, isLoading }) {
  const [dragActive, setDragActive] = useState(false)
  const [error, setError] = useState(null)

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    setError(null)
    if (rejectedFiles.length > 0) {
      const err = rejectedFiles[0].errors[0]
      if (err.code === 'file-invalid-type') setError('Only PDF and DOCX files are supported.')
      else if (err.code === 'file-too-large') setError('File must be under 10MB.')
      else setError(err.message)
      return
    }
    if (acceptedFiles.length > 0) {
      onFileAccepted(acceptedFiles[0])
    }
  }, [onFileAccepted])

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 10 * 1024 * 1024,
    multiple: false,
    disabled: isLoading,
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false),
    onDropAccepted: () => setDragActive(false),
    onDropRejected: () => setDragActive(false),
  })

  const currentFile = acceptedFiles[0]

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={clsx(
          'relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300',
          isDragActive || dragActive
            ? 'border-brand-500 bg-brand-500/10 scale-[1.01]'
            : 'border-white/20 hover:border-brand-500/60 hover:bg-white/5',
          isLoading && 'opacity-50 cursor-not-allowed',
          currentFile && !isLoading && 'border-emerald-500/50 bg-emerald-500/5',
        )}
      >
        <input {...getInputProps()} />

        {/* Glow effect */}
        {(isDragActive || dragActive) && (
          <div className="absolute inset-0 rounded-2xl bg-brand-500/5 animate-pulse" />
        )}

        <div className="relative flex flex-col items-center gap-4">
          {currentFile && !isLoading ? (
            <>
              <div className="w-16 h-16 rounded-2xl bg-emerald-500/20 flex items-center justify-center">
                <CheckCircle size={32} className="text-emerald-400" />
              </div>
              <div>
                <p className="text-emerald-400 font-semibold text-lg">{currentFile.name}</p>
                <p className="text-slate-400 text-sm mt-1">
                  {(currentFile.size / 1024).toFixed(1)} KB · {currentFile.type.includes('pdf') ? 'PDF' : 'DOCX'}
                </p>
              </div>
              <p className="text-slate-500 text-sm">Drop another file to replace</p>
            </>
          ) : isLoading ? (
            <>
              <div className="w-16 h-16 rounded-2xl bg-brand-500/20 flex items-center justify-center">
                <div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
              </div>
              <p className="text-brand-400 font-semibold">Analyzing your resume...</p>
              <p className="text-slate-400 text-sm">Extracting information and skills</p>
            </>
          ) : (
            <>
              <div className={clsx(
                'w-16 h-16 rounded-2xl flex items-center justify-center transition-all duration-300',
                isDragActive ? 'bg-brand-500/30 scale-110' : 'bg-brand-500/20'
              )}>
                {isDragActive ? (
                  <FileText size={32} className="text-brand-400 animate-bounce" />
                ) : (
                  <Upload size={32} className="text-brand-400" />
                )}
              </div>
              <div>
                <p className="text-white font-semibold text-lg">
                  {isDragActive ? 'Drop it here!' : 'Drag & drop your resume'}
                </p>
                <p className="text-slate-400 mt-1">
                  or <span className="text-brand-400 font-medium">click to browse</span>
                </p>
              </div>
              <div className="flex items-center gap-4 text-xs text-slate-500">
                <span className="flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-slate-500 rounded-full" /> PDF
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-slate-500 rounded-full" /> DOCX
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-slate-500 rounded-full" /> Max 10MB
                </span>
              </div>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-3 flex items-center gap-2 text-red-400 text-sm">
          <AlertCircle size={16} />
          {error}
        </div>
      )}
    </div>
  )
}
