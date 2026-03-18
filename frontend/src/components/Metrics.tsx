import React, { useState, useEffect } from 'react';
import { api } from '../lib/api';
import { Metrics as RetailMetrics } from '../types/retail';
import { TrendingUp, Leaf, Zap, Clock, ShieldCheck, AlertCircle, ChevronRight, Tag, BarChart3, PieChart, LineChart } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';

export function Metrics({ t, subView }: { t: any, subView?: string }) {
  const [metrics, setMetrics] = useState<RetailMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const m = await api.getImpactMetrics();
        setMetrics(m);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <div className="p-8 animate-pulse text-slate-400">Loading metrics...</div>;

  const data = [
    { name: 'Jan', value: 4000 },
    { name: 'Feb', value: 3000 },
    { name: 'Mar', value: 2000 },
    { name: 'Apr', value: 2780 },
    { name: 'May', value: 1890 },
    { name: 'Jun', value: 2390 },
    { name: 'Jul', value: 3490 },
  ];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">{t.metricsImpact}</h2>
          <p className="text-slate-500 mt-1">ROI, CO₂ savings, and operational efficiency.</p>
        </div>
        <div className="flex items-center gap-4">
          <button className="px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm font-bold text-slate-700 hover:bg-slate-50 transition-all flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            Export PDF
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-bold shadow-lg shadow-blue-500/20 hover:bg-blue-700 transition-all flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            Generate Report
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main ROI Chart */}
        <div className="lg:col-span-2 bg-white p-8 rounded-3xl border border-slate-200 shadow-sm space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-900 flex items-center gap-2">
              <TrendingUp className="text-blue-500 w-5 h-5" />
              Financial ROI (CHF)
            </h3>
            <div className="flex items-center gap-2 text-emerald-600 bg-emerald-50 px-3 py-1 rounded-full text-xs font-bold">
              +12.5% vs Last Month
            </div>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} />
                <Tooltip 
                  contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                />
                <Area type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorValue)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Sustainability Impact */}
        <div className="bg-slate-900 p-8 rounded-3xl text-white space-y-8 flex flex-col justify-between shadow-xl shadow-slate-900/20">
          <div className="space-y-2">
            <h3 className="text-xl font-bold flex items-center gap-2">
              <Leaf className="text-emerald-400 w-6 h-6" />
              Sustainability Impact
            </h3>
            <p className="text-slate-400 text-sm">Real-time CO₂ reduction from optimized logistics.</p>
          </div>
          
          <div className="space-y-6">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Monthly Goal</span>
                <span className="font-bold text-emerald-400">85%</span>
              </div>
              <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: '85%' }}
                  className="h-full bg-emerald-400 rounded-full"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div>
                <p className="text-2xl font-bold text-white">{metrics?.co2SavedKg} kg</p>
                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">CO₂ Saved</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{metrics?.pickupEfficiency}%</p>
                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">Efficiency</p>
              </div>
            </div>
          </div>

          <button className="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-2xl transition-all flex items-center justify-center gap-2">
            <ShieldCheck className="w-5 h-5" />
            Verify ESG Data
          </button>
        </div>
      </div>

      {/* Operational Efficiency Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: 'TWINT Conversion', value: `${metrics?.twintConversion}%`, icon: Zap, color: 'text-blue-600', bg: 'bg-blue-50' },
          { label: 'Manager Hours', value: `${metrics?.managerHoursReclaimed}h`, icon: Clock, color: 'text-amber-600', bg: 'bg-amber-50' },
          { label: 'Stock Accuracy', value: '99.2%', icon: ShieldCheck, color: 'text-emerald-600', bg: 'bg-emerald-50' },
          { label: 'System Uptime', value: '99.99%', icon: Zap, color: 'text-indigo-600', bg: 'bg-indigo-50' },
        ].map((item, i) => (
          <div key={i} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className={`p-3 rounded-xl ${item.bg}`}>
              <item.icon className={`w-6 h-6 ${item.color}`} />
            </div>
            <div>
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{item.label}</p>
              <p className="text-xl font-bold text-slate-900">{item.value}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
