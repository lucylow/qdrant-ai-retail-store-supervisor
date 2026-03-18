import React, { useState, useEffect } from 'react';
import { api } from '../lib/api';
import { PickupWindow } from '../types/retail';
import { Calendar, Clock, Users, AlertCircle, ChevronLeft, ChevronRight, CheckCircle2 } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

export function PickupSchedule({ storeId, t, subView }: { storeId: string, t: any, subView?: string }) {
  const [windows, setWindows] = useState<PickupWindow[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDay, setSelectedDay] = useState(0); // 0 = today, 1 = tomorrow, etc.

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const results = await api.getPickupWindows(storeId, 7);
        setWindows(results);
        
        if (subView === 'schedule-today') {
          setSelectedDay(0);
        } else if (subView === 'schedule-tomorrow') {
          setSelectedDay(1);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [storeId, subView]);

  const days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date();
    d.setDate(d.getDate() + i);
    return d;
  });

  const filteredWindows = windows.filter(w => {
    const windowDate = new Date(w.start).toDateString();
    const selectedDate = days[selectedDay].toDateString();
    return windowDate === selectedDate;
  });

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">{t.pickupSchedule}</h2>
          <p className="text-slate-500 mt-1">Manage Swiss punctuality and pickup capacity.</p>
        </div>
        <div className="flex items-center gap-2 bg-white p-1 rounded-2xl border border-slate-200 shadow-sm">
          <button 
            onClick={() => setSelectedDay(Math.max(0, selectedDay - 1))}
            className="p-2 hover:bg-slate-50 rounded-xl transition-colors disabled:opacity-30"
            disabled={selectedDay === 0}
          >
            <ChevronLeft className="w-5 h-5 text-slate-600" />
          </button>
          <div className="px-4 py-2 text-sm font-bold text-slate-900 flex items-center gap-2">
            <Calendar className="w-4 h-4 text-blue-500" />
            {days[selectedDay].toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'long' })}
          </div>
          <button 
            onClick={() => setSelectedDay(Math.min(6, selectedDay + 1))}
            className="p-2 hover:bg-slate-50 rounded-xl transition-colors disabled:opacity-30"
            disabled={selectedDay === 6}
          >
            <ChevronRight className="w-5 h-5 text-slate-600" />
          </button>
        </div>
      </div>

      {/* Day Selector Tabs */}
      <div className="flex gap-4 overflow-x-auto pb-2 no-scrollbar">
        {days.map((day, i) => (
          <button
            key={i}
            onClick={() => setSelectedDay(i)}
            className={`px-6 py-4 rounded-2xl border transition-all flex flex-col items-center min-w-[120px] ${
              selectedDay === i 
                ? 'bg-blue-600 border-blue-600 text-white shadow-lg shadow-blue-500/20' 
                : 'bg-white border-slate-200 text-slate-600 hover:border-blue-200 hover:bg-blue-50/30'
            }`}
          >
            <span className="text-[10px] font-bold uppercase tracking-widest opacity-70 mb-1">
              {day.toLocaleDateString(undefined, { weekday: 'short' })}
            </span>
            <span className="text-xl font-bold">{day.getDate()}</span>
          </button>
        ))}
      </div>

      {/* Windows Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <AnimatePresence mode="popLayout">
          {loading ? (
            <div className="col-span-full p-12 text-center text-slate-400 animate-pulse">Loading schedule...</div>
          ) : filteredWindows.length > 0 ? (
            filteredWindows.map((window) => {
              const occupancy = (window.booked / window.capacity) * 100;
              const isFull = occupancy >= 100;
              const isHigh = occupancy >= 80;

              return (
                <motion.div
                  key={window.id}
                  layout
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className={`bg-white p-6 rounded-2xl border shadow-sm transition-all ${
                    isFull ? 'border-red-200 bg-red-50/30' : 'border-slate-200 hover:border-blue-200'
                  }`}
                >
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <div className={`p-3 rounded-xl ${isFull ? 'bg-red-100' : 'bg-blue-50'}`}>
                        <Clock className={`w-5 h-5 ${isFull ? 'text-red-600' : 'text-blue-600'}`} />
                      </div>
                      <div>
                        <p className="text-lg font-bold text-slate-900">
                          {new Date(window.start).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })} - {new Date(window.end).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}
                        </p>
                        <p className="text-xs text-slate-500 font-medium">Swiss Standard Window</p>
                      </div>
                    </div>
                    {isFull && <AlertCircle className="w-5 h-5 text-red-500" />}
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2 text-slate-600 font-medium">
                        <Users className="w-4 h-4" />
                        {window.booked} / {window.capacity} booked
                      </div>
                      <span className={`font-bold ${isFull ? 'text-red-600' : isHigh ? 'text-amber-600' : 'text-emerald-600'}`}>
                        {Math.round(occupancy)}%
                      </span>
                    </div>

                    <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${occupancy}%` }}
                        className={`h-full rounded-full ${
                          isFull ? 'bg-red-500' : isHigh ? 'bg-amber-500' : 'bg-emerald-500'
                        }`}
                      />
                    </div>

                    <div className="pt-4 flex items-center justify-between">
                      <div className="flex -space-x-2 overflow-hidden">
                        {[1, 2, 3].map((i) => (
                          <div key={i} className="inline-block h-6 w-6 rounded-full ring-2 ring-white bg-slate-200" />
                        ))}
                        <div className="inline-block h-6 w-6 rounded-full ring-2 ring-white bg-slate-100 flex items-center justify-center text-[8px] font-bold text-slate-400">
                          +{window.booked}
                        </div>
                      </div>
                      <button 
                        disabled={isFull}
                        className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                          isFull 
                            ? 'bg-slate-100 text-slate-400 cursor-not-allowed' 
                            : 'bg-blue-50 text-blue-600 hover:bg-blue-600 hover:text-white'
                        }`}
                      >
                        {isFull ? 'Full' : 'Manage'}
                      </button>
                    </div>
                  </div>
                </motion.div>
              );
            })
          ) : (
            <div className="col-span-full p-12 text-center bg-white rounded-2xl border border-dashed border-slate-200 text-slate-400">
              No pickup windows scheduled for this day.
            </div>
          )}
        </AnimatePresence>
      </div>

      {/* Capacity Summary Card */}
      <div className="bg-slate-900 p-8 rounded-3xl text-white flex flex-col md:flex-row items-center justify-between gap-8 shadow-xl shadow-slate-900/20">
        <div className="space-y-2 text-center md:text-left">
          <h3 className="text-xl font-bold flex items-center gap-2 justify-center md:justify-start">
            <CheckCircle2 className="text-emerald-400 w-6 h-6" />
            Daily Capacity Optimization
          </h3>
          <p className="text-slate-400 text-sm max-w-md">
            Our AI has optimized pickup windows based on historical Swiss holiday demand and staff availability.
          </p>
        </div>
        <div className="flex gap-8">
          <div className="text-center">
            <p className="text-3xl font-bold text-white">94%</p>
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">Punctuality</p>
          </div>
          <div className="w-px h-12 bg-slate-800" />
          <div className="text-center">
            <p className="text-3xl font-bold text-emerald-400">12h</p>
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">Wait Saved</p>
          </div>
        </div>
      </div>
    </div>
  );
}
