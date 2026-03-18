import React, { useState, useRef } from 'react';
import { Upload, X, File, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

interface UploadingFile {
  id: string;
  file: File;
  progress: number;
  status: 'uploading' | 'success' | 'error';
  error?: string;
}

import { Translation } from '../translations';

interface FileUploadZoneProps {
  onUploadComplete: (file: File, content?: string, fileData?: string) => void;
  onClose: () => void;
  t: Translation;
}

export const FileUploadZone: React.FC<FileUploadZoneProps> = ({ onUploadComplete, onClose, t }) => {
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFiles = (files: FileList | null) => {
    if (!files) return;

    const newFiles = Array.from(files).map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      progress: 0,
      status: 'uploading' as const
    }));

    setUploadingFiles(prev => [...prev, ...newFiles]);

    newFiles.forEach(uploadingFile => {
      simulateUpload(uploadingFile);
    });
  };

  const simulateUpload = (uploadingFile: UploadingFile) => {
    const { file, id } = uploadingFile;
    let progress = 0;
    
    const interval = setInterval(() => {
      progress += Math.random() * 30;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        
        // Process the file content
        const reader = new FileReader();
        
        if (file.type.startsWith('text/') || file.name.endsWith('.txt') || file.name.endsWith('.md')) {
          reader.onload = (event) => {
            const content = event.target?.result as string;
            onUploadComplete(file, content);
            updateFileStatus(id, 100, 'success');
          };
          reader.readAsText(file);
        } else if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
          reader.onload = (event) => {
            const fileData = event.target?.result as string;
            onUploadComplete(file, undefined, fileData);
            updateFileStatus(id, 100, 'success');
          };
          reader.readAsDataURL(file);
        } else {
          // Unsupported for preview but still "uploaded"
          onUploadComplete(file);
          updateFileStatus(id, 100, 'success');
        }
      } else {
        updateFileStatus(id, progress, 'uploading');
      }
    }, 200);
  };

  const updateFileStatus = (id: string, progress: number, status: 'uploading' | 'success' | 'error', error?: string) => {
    setUploadingFiles(prev => prev.map(f => 
      f.id === id ? { ...f, progress, status, error } : f
    ));
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = () => {
    setIsDragging(false);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  const removeFile = (id: string) => {
    setUploadingFiles(prev => prev.filter(f => f.id !== id));
  };

  return (
    <div className="space-y-6">
      <div 
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`
          relative border-2 border-dashed rounded-2xl p-12 transition-all cursor-pointer
          flex flex-col items-center justify-center text-center space-y-4
          ${isDragging ? 'border-brand-red bg-brand-red/5' : 'border-slate-200 hover:border-brand-red/50 hover:bg-slate-50'}
        `}
      >
        <input 
          type="file" 
          ref={fileInputRef}
          onChange={(e) => handleFiles(e.target.files)}
          multiple
          className="hidden"
        />
        
        <div className={`w-16 h-16 rounded-full flex items-center justify-center transition-colors ${isDragging ? 'bg-brand-red text-white' : 'bg-slate-100 text-slate-400'}`}>
          <Upload size={32} />
        </div>
        
        <div className="space-y-1">
          <p className="text-lg font-bold text-slate-800">{t.clickToUpload}</p>
          <p className="text-sm text-slate-500">{t.supportFiles}</p>
        </div>
      </div>

      <AnimatePresence>
        {uploadingFiles.length > 0 && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-3"
          >
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider">{t.uploadQueue}</h4>
              <button 
                onClick={() => setUploadingFiles([])}
                className="text-xs font-bold text-brand-red hover:underline"
              >
                {t.all}
              </button>
            </div>
            
            <div className="space-y-2 max-h-64 overflow-y-auto pr-2 custom-scrollbar">
              {uploadingFiles.map((file) => (
                <motion.div 
                  key={file.id}
                  layout
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className="bg-white border border-slate-100 rounded-xl p-4 flex items-center gap-4 shadow-sm"
                >
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    file.status === 'success' ? 'bg-emerald-50 text-emerald-500' : 
                    file.status === 'error' ? 'bg-red-50 text-red-500' : 'bg-slate-50 text-slate-400'
                  }`}>
                    {file.status === 'uploading' ? <Loader2 size={20} className="animate-spin" /> : 
                     file.status === 'success' ? <CheckCircle2 size={20} /> : <AlertCircle size={20} />}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-sm font-bold text-slate-800 truncate">{file.file.name}</p>
                      <span className="text-xs font-medium text-slate-400">
                        {file.status === 'uploading' ? `${Math.round(file.progress)}%` : 
                         file.status === 'success' ? t.done : t.off}
                      </span>
                    </div>
                    
                    <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${file.progress}%` }}
                        className={`h-full transition-all duration-300 ${
                          file.status === 'success' ? 'bg-emerald-500' : 
                          file.status === 'error' ? 'bg-red-500' : 'bg-brand-red'
                        }`}
                      />
                    </div>
                  </div>

                  <button 
                    onClick={() => removeFile(file.id)}
                    className="p-1.5 hover:bg-slate-100 rounded-lg text-slate-400 transition-colors"
                  >
                    <X size={16} />
                  </button>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
