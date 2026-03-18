import React from 'react';
import { motion } from 'motion/react';
import { ShoppingCart, Info } from 'lucide-react';

interface HeroSectionProps {
  title: string;
  subtitle?: string;
  content: {
    imageUrl: string;
    ctaText: string;
  };
  onAction: (action: any) => void;
}

export function HeroSection({ title, subtitle, content, onAction }: HeroSectionProps) {
  return (
    <motion.section 
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      className="relative h-[500px] rounded-[2.5rem] overflow-hidden mb-12 shadow-2xl shadow-blue-900/10"
    >
      <img 
        src={content.imageUrl} 
        alt={title} 
        className="absolute inset-0 w-full h-full object-cover"
        referrerPolicy="no-referrer"
      />
      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent flex flex-col justify-end p-10 md:p-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="max-w-3xl"
        >
          <h1 className="text-5xl md:text-7xl font-black text-white mb-6 leading-[0.9] tracking-tighter italic uppercase">
            {title}
          </h1>
          {subtitle && (
            <p className="text-xl md:text-2xl text-white/80 mb-10 font-medium leading-relaxed">
              {subtitle}
            </p>
          )}
          <div className="flex flex-wrap gap-4">
            <button 
              onClick={() => onAction({ type: 'hero-cta', payload: content })}
              className="bg-[#FF6C00] hover:bg-[#e66100] text-white px-10 py-4 rounded-2xl font-black text-lg flex items-center gap-3 transition-all hover:scale-105 active:scale-95 shadow-xl shadow-orange-500/30 uppercase tracking-wider"
            >
              <ShoppingCart className="w-6 h-6" />
              {content.ctaText}
            </button>
            <button className="bg-white/10 hover:bg-white/20 backdrop-blur-xl text-white px-10 py-4 rounded-2xl font-bold text-lg flex items-center gap-3 transition-all border border-white/20">
              <Info className="w-6 h-6" />
              Details
            </button>
          </div>
        </motion.div>
      </div>
    </motion.section>
  );
}
