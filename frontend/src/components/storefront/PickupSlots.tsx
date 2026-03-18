import React from 'react';
import { motion } from 'motion/react';
import { Clock, Calendar, CheckCircle2, AlertTriangle } from 'lucide-react';
import { PickupWindow } from '../../types/retail';

interface PickupSlotsProps {
  title: string;
  subtitle?: string;
  content: (PickupWindow & { isRecommended?: boolean })[];
  onAction: (action: any) => void;
}

export function PickupSlots({ title, subtitle, content, onAction }: PickupSlotsProps) {
  return (
    <section className="mb-12">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
        {subtitle && <p className="text-gray-500">{subtitle}</p>}
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {content.map((window, i) => {
          const start = new Date(window.start);
          const end = new Date(window.end);
          const occupancy = (window.booked / window.capacity) * 100;
          const isFull = window.booked >= window.capacity;
          const isLow = window.capacity - window.booked <= 3;

          return (
            <motion.div
              key={window.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              onClick={() => !isFull && onAction({ type: 'select-slot', payload: window })}
              className={`
                relative p-4 rounded-2xl border-2 transition-all cursor-pointer overflow-hidden
                ${window.isRecommended 
                  ? 'border-[#0066CC] bg-blue-50/50' 
                  : 'border-gray-100 hover:border-gray-200 bg-white'
                }
                ${isFull ? 'opacity-50 cursor-not-allowed grayscale' : ''}
              `}
            >
              {window.isRecommended && (
                <div className="absolute top-0 right-0 bg-[#0066CC] text-white px-3 py-1 rounded-bl-xl text-xs font-bold flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" />
                  EMPFOHLEN
                </div>
              )}
              
              <div className="flex items-center gap-3 mb-4">
                <div className={`p-2 rounded-xl ${window.isRecommended ? 'bg-[#0066CC] text-white' : 'bg-gray-100 text-gray-500'}`}>
                  <Clock className="w-5 h-5" />
                </div>
                <div>
                  <div className="font-bold text-gray-900">
                    {start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - {end.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                  <div className="text-xs text-gray-500">
                    {start.toLocaleDateString([], { weekday: 'long', day: 'numeric', month: 'long' })}
                  </div>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-gray-500">Kapazität</span>
                  <span className={isFull ? 'text-rose-600' : isLow ? 'text-amber-600' : 'text-emerald-600'}>
                    {window.booked} / {window.capacity} gebucht
                  </span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: `${occupancy}%` }}
                    className={`h-full rounded-full ${isFull ? 'bg-rose-500' : isLow ? 'bg-amber-500' : 'bg-emerald-500'}`}
                  />
                </div>
              </div>
              
              {isLow && !isFull && (
                <div className="mt-3 flex items-center gap-1 text-xs font-bold text-amber-600">
                  <AlertTriangle className="w-3 h-3" />
                  Nur noch {window.capacity - window.booked} Plätze!
                </div>
              )}
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
