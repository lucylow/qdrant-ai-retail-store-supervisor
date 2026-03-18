import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Sparkles, Zap, Palette, Video, Share2 } from 'lucide-react';

const STEPS = [
  { icon: <Palette />, text: 'Analyzing Migros Branding...', color: 'text-blue-500' },
  { icon: <Zap />, text: 'Compositing Product Assets...', color: 'text-orange-500' },
  { icon: <Sparkles />, text: 'AI Copywriting (DE/FR/IT)...', color: 'text-emerald-500' },
  { icon: <Video />, text: 'Rendering Video Motion...', color: 'text-purple-500' },
  { icon: <Share2 />, text: 'Optimizing for Meta & TikTok...', color: 'text-pink-500' },
];

export function GenerationSpinner() {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep(prev => (prev + 1) % STEPS.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center py-24 space-y-12">
      <div className="relative">
        <motion.div 
          animate={{ rotate: 360 }}
          transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
          className="w-48 h-48 border-8 border-gray-50 border-t-[#FF6C00] rounded-full shadow-2xl shadow-orange-500/10"
        />
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.div
            key={currentStep}
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 1.5, opacity: 0 }}
            className={`w-16 h-16 ${STEPS[currentStep].color}`}
          >
            {STEPS[currentStep].icon}
          </motion.div>
        </div>
      </div>

      <div className="text-center max-w-md">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -20, opacity: 0 }}
            className="space-y-4"
          >
            <h3 className="text-3xl font-black text-gray-900 italic uppercase tracking-tighter">
              {STEPS[currentStep].text}
            </h3>
            <p className="text-sm text-gray-400 font-bold uppercase tracking-widest">
              AI Marketing Studio &bull; 90s Generation
            </p>
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="flex gap-2">
        {STEPS.map((_, i) => (
          <div 
            key={i}
            className={`h-1.5 rounded-full transition-all duration-500 ${
              i === currentStep ? 'w-12 bg-[#FF6C00]' : 'w-4 bg-gray-100'
            }`}
          />
        ))}
      </div>
    </div>
  );
}
