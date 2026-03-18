import React from 'react';
import { motion } from 'motion/react';
import { Smartphone, ShieldCheck, Zap, Info } from 'lucide-react';

interface TWINTCheckoutZoneProps {
  title: string;
  subtitle?: string;
  content: {
    totalChf: number;
    qrCodeUrl: string;
  };
  onAction: (action: any) => void;
}

export function TWINTCheckoutZone({ title, subtitle, content, onAction }: TWINTCheckoutZoneProps) {
  return (
    <section className="mb-16 bg-gradient-to-br from-[#00A859]/10 to-emerald-50 p-10 rounded-[3rem] border border-[#00A859]/20 shadow-xl shadow-emerald-900/5">
      <div className="flex flex-col lg:flex-row items-center gap-16">
        <div className="flex-1">
          <div className="flex items-center gap-4 mb-8">
            <div className="p-3 bg-[#00A859] text-white rounded-2xl shadow-lg shadow-emerald-500/30">
              <Smartphone className="w-8 h-8" />
            </div>
            <div>
              <h2 className="text-3xl font-black text-gray-900 tracking-tight uppercase italic">{title}</h2>
              {subtitle && <p className="text-gray-500 font-medium">{subtitle}</p>}
            </div>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 mb-12">
            <div className="flex items-start gap-4">
              <div className="p-2 bg-emerald-100 text-emerald-600 rounded-xl">
                <Zap className="w-6 h-6" />
              </div>
              <div>
                <div className="font-black text-gray-900 uppercase text-sm tracking-wider">Blitzschnell</div>
                <div className="text-sm text-gray-500 leading-relaxed">58% schneller als herkömmliche Kartenzahlung.</div>
              </div>
            </div>
            
            <div className="flex items-start gap-4">
              <div className="p-2 bg-emerald-100 text-emerald-600 rounded-xl">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <div>
                <div className="font-black text-gray-900 uppercase text-sm tracking-wider">Sicher</div>
                <div className="text-sm text-gray-500 leading-relaxed">Verschlüsselt nach Schweizer Bankenstandard.</div>
              </div>
            </div>
          </div>
          
          <div className="p-8 bg-white rounded-3xl border border-emerald-100 shadow-sm">
            <div className="flex justify-between items-center mb-6">
              <span className="text-gray-400 font-bold uppercase tracking-widest text-xs">Gesamtbetrag</span>
              <span className="text-4xl font-black text-gray-900 tracking-tighter italic">CHF {content.totalChf.toFixed(2)}</span>
            </div>
            <button 
              onClick={() => onAction({ type: 'twint-pay', payload: content })}
              className="w-full py-5 bg-[#00A859] hover:bg-[#008f4b] text-white rounded-2xl font-black text-xl flex items-center justify-center gap-4 transition-all hover:scale-[1.02] active:scale-[0.98] shadow-xl shadow-emerald-500/20 uppercase tracking-widest"
            >
              <Smartphone className="w-7 h-7" />
              TWINT bezahlen
            </button>
          </div>
        </div>
        
        <div className="flex-shrink-0">
          <motion.div 
            whileHover={{ scale: 1.05, rotate: 2 }}
            className="p-10 bg-white rounded-[3rem] border-4 border-[#00A859]/10 shadow-2xl relative"
          >
            <div className="absolute -top-5 left-1/2 -translate-x-1/2 bg-[#00A859] text-white px-6 py-2 rounded-full text-xs font-black tracking-[0.2em] shadow-lg">
              SCAN & PAY
            </div>
            <div className="bg-gray-50 p-4 rounded-2xl">
              <img 
                src={content.qrCodeUrl} 
                alt="TWINT QR Code" 
                className="w-64 h-64 object-contain mix-blend-multiply"
                referrerPolicy="no-referrer"
              />
            </div>
            <div className="mt-8 flex items-center justify-center gap-3 text-gray-400 font-bold text-xs uppercase tracking-widest">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Live QR Code
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
