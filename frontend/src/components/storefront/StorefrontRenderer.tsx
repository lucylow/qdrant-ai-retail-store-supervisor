import React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { AIStorefrontPayload } from '../../types/storefront';
import { AISection } from './AISection';
import { ShoppingCart, ArrowRight, Sparkles, MapPin } from 'lucide-react';

interface StorefrontRendererProps {
  payload: AIStorefrontPayload;
  onAction: (action: any) => void;
}

export function StorefrontRenderer({ payload, onAction }: StorefrontRendererProps) {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Dynamic Header */}
      <header className="mb-16 flex flex-col md:flex-row md:items-center justify-between gap-8">
        <div className="flex-1">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-3 text-[#FF6C00] font-black text-xs uppercase tracking-[0.3em] mb-4"
          >
            <div className="w-8 h-1 bg-[#FF6C00] rounded-full" />
            <Sparkles className="w-4 h-4" />
            AI-Personalized for you
          </motion.div>
          <h1 className="text-5xl md:text-6xl font-black text-gray-900 tracking-tighter italic uppercase leading-[0.9]">
            {payload.title}
          </h1>
          <p className="text-xl text-gray-500 mt-6 max-w-2xl font-medium leading-relaxed">
            {payload.description}
          </p>
        </div>
        
        <div className="flex flex-col items-end gap-4">
          <div className="p-4 bg-white rounded-[2rem] border border-gray-100 shadow-xl shadow-blue-900/5 flex items-center gap-4 min-w-[280px]">
            <div className="w-12 h-12 bg-blue-50 text-[#0066CC] rounded-2xl flex items-center justify-center">
              <MapPin className="w-6 h-6" />
            </div>
            <div>
              <div className="text-[10px] text-gray-400 font-black uppercase tracking-widest">Ihre Filiale</div>
              <div className="text-base font-black text-gray-900 italic uppercase">Migros Zürich HB</div>
            </div>
          </div>
          <div className="flex items-center gap-2 text-[10px] font-black text-emerald-500 uppercase tracking-widest bg-emerald-50 px-4 py-2 rounded-full">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            Live Stock Sync Active
          </div>
        </div>
      </header>
      
      {/* Dynamic Sections */}
      <div className="space-y-24">
        <AnimatePresence mode="wait">
          {payload.sections.map((section, i) => (
            <AISection 
              key={`${section.type}-${i}`} 
              section={section} 
              onAction={onAction} 
            />
          ))}
        </AnimatePresence>
      </div>
      
      {/* Primary Floating CTA (Mobile) */}
      {payload.primaryAction && (
        <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 md:hidden w-[calc(100%-2rem)]">
          <button 
            onClick={() => onAction({ type: 'primary-action', payload: payload.primaryAction })}
            className="w-full py-5 bg-[#FF6C00] text-white rounded-[2rem] font-black text-xl shadow-2xl shadow-orange-500/40 flex items-center justify-center gap-4 hover:scale-105 transition-transform active:scale-95 uppercase tracking-widest italic"
          >
            {payload.primaryAction.type === 'twint-checkout' ? <Smartphone className="w-7 h-7" /> : <ArrowRight className="w-7 h-7" />}
            {payload.primaryAction.text}
          </button>
        </div>
      )}
      
      {/* Footer Info */}
      <footer className="mt-32 pt-16 border-t border-gray-100">
        <div className="flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-[#FF6321] rounded-2xl flex items-center justify-center shadow-lg shadow-orange-500/20">
              <span className="text-2xl font-black text-white italic">M</span>
            </div>
            <div className="text-left">
              <div className="text-lg font-black text-gray-900 italic uppercase tracking-tighter">Migros Online</div>
              <div className="text-xs text-gray-400 font-bold uppercase tracking-widest">Einfach besser leben</div>
            </div>
          </div>
          
          <div className="flex gap-8">
            <div className="text-center md:text-right">
              <div className="text-xs text-gray-400 font-bold uppercase tracking-widest mb-2">Sicherheit</div>
              <div className="flex items-center gap-2 text-gray-900 font-black text-sm uppercase italic">
                <ShieldCheck className="w-4 h-4 text-emerald-500" />
                SSL Verschlüsselt
              </div>
            </div>
            <div className="text-center md:text-right">
              <div className="text-xs text-gray-400 font-bold uppercase tracking-widest mb-2">Zahlung</div>
              <div className="flex items-center gap-2 text-gray-900 font-black text-sm uppercase italic text-[#00A859]">
                <Smartphone className="w-4 h-4" />
                TWINT Ready
              </div>
            </div>
          </div>
        </div>
        <div className="mt-12 text-center text-[10px] text-gray-300 font-bold uppercase tracking-[0.3em]">
          &copy; 2026 Migros-Genossenschafts-Bund. Alle Rechte vorbehalten.
        </div>
      </footer>
    </div>
  );
}

function Smartphone({ className }: { className?: string }) {
  return (
    <svg 
      className={className} 
      xmlns="http://www.w3.org/2000/svg" 
      width="24" 
      height="24" 
      viewBox="0 0 24 24" 
      fill="none" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    >
      <rect width="14" height="20" x="5" y="2" rx="2" ry="2" />
      <path d="M12 18h.01" />
    </svg>
  );
}

function ShieldCheck({ className }: { className?: string }) {
  return (
    <svg 
      className={className} 
      xmlns="http://www.w3.org/2000/svg" 
      width="24" 
      height="24" 
      viewBox="0 0 24 24" 
      fill="none" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    >
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  );
}
