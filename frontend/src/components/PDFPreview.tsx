import React, { useEffect, useRef, useState } from 'react';
import * as pdfjsLib from 'pdfjs-dist';
import { Loader2, AlertCircle } from 'lucide-react';

// Set worker source to a CDN for simplicity in this environment
pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.mjs`;

import { Translation } from '../translations';

interface PDFPreviewProps {
  fileData: string;
  t: Translation;
}

export const PDFPreview: React.FC<PDFPreviewProps> = ({ fileData, t }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const renderPDF = async () => {
      setLoading(true);
      setError(null);

      try {
        // Convert base64 to Uint8Array
        const binaryString = window.atob(fileData.split(',')[1] || fileData);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }

        const loadingTask = pdfjsLib.getDocument({ data: bytes });
        const pdf = await loadingTask.promise;

        if (!isMounted) return;

        const page = await pdf.getPage(1);
        const viewport = page.getViewport({ scale: 1.5 });

        if (!isMounted || !canvasRef.current) return;

        const canvas = canvasRef.current;
        const context = canvas.getContext('2d');
        if (!context) throw new Error('Could not get canvas context');

        canvas.height = viewport.height;
        canvas.width = viewport.width;

        const renderContext: any = {
          canvasContext: context,
          viewport: viewport,
        };

        await page.render(renderContext).promise;
        if (isMounted) setLoading(false);
      } catch (err) {
        console.error('Error rendering PDF:', err);
        if (isMounted) {
          setError(t.pdfPreviewNotAvailable);
          setLoading(false);
        }
      }
    };

    renderPDF();

    return () => {
      isMounted = false;
    };
  }, [fileData, t]);

  return (
    <div className="relative w-full flex flex-col items-center justify-center bg-slate-100 rounded-xl overflow-hidden min-h-[400px]">
      {loading && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-50/80 z-10">
          <Loader2 className="w-8 h-8 text-brand-red animate-spin mb-2" />
          <p className="text-sm text-slate-500 font-medium">{t.renderingPdf}</p>
        </div>
      )}
      
      {error ? (
        <div className="p-8 text-center space-y-4">
          <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center text-red-500 mx-auto">
            <AlertCircle size={32} />
          </div>
          <p className="text-sm text-slate-600 max-w-xs">{error}</p>
        </div>
      ) : (
        <canvas ref={canvasRef} className="max-w-full h-auto shadow-lg" />
      )}
    </div>
  );
};
