import React, { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { api } from '../lib/api';
import { Metrics, Product, PickupWindow } from '../types/retail';
import { TrendingUp, Package, Clock, ShieldCheck, AlertTriangle, Leaf, Zap } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export function Dashboard({ storeId, t, subView }: { storeId: string, t: any, subView?: string }) {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [lowStock, setLowStock] = useState<Product[]>([]);
  const [windows, setWindows] = useState<PickupWindow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [m, ls, w] = await Promise.all([
          api.getImpactMetrics(),
          api.getLowStockProducts(storeId),
          api.getPickupWindows(storeId, 1)
        ]);
        setMetrics(m);
        setLowStock(ls.slice(0, 3));
        setWindows(w);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [storeId]);

  if (loading) return <div className="p-8 animate-pulse text-slate-400">Loading dashboard...</div>;

  const kpis = [
    { label: t.stockoutsPrevented, value: metrics?.stockoutsPrevented, icon: Package, color: 'text-blue-600', bg: 'bg-blue-50' },
    { label: t.chfSaved, value: `CHF ${metrics?.chfSaved.toLocaleString()}`, icon: TrendingUp, color: 'text-emerald-600', bg: 'bg-emerald-50' },
    { label: t.co2Saved, value: `${metrics?.co2SavedKg} kg`, icon: Leaf, color: 'text-green-600', bg: 'bg-green-50' },
    { label: t.hoursReclaimed, value: `${metrics?.managerHoursReclaimed}h`, icon: Zap, color: 'text-amber-600', bg: 'bg-amber-50' },
  ];

  return (
    <div className="p-8 space-y-12 max-w-7xl mx-auto">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        {kpis.map((kpi, i) => (
          <motion.div 
            key={i} 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="bento-card p-8 flex flex-col gap-6 group"
          >
            <div className={`w-14 h-14 rounded-2xl ${kpi.bg} flex items-center justify-center transition-transform group-hover:scale-110 group-hover:rotate-3`}>
              <kpi.icon className={`w-7 h-7 ${kpi.color}`} />
            </div>
            <div>
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">{kpi.label}</p>
              <p className="text-3xl font-black text-slate-900 italic uppercase tracking-tighter">{kpi.value}</p>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Low Stock Alerts */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bento-card overflow-hidden flex flex-col"
        >
          <div className="p-8 border-b border-slate-50 flex items-center justify-between bg-slate-50/50">
            <div>
              <h3 className="text-xl font-black text-slate-900 italic uppercase tracking-tighter flex items-center gap-3">
                <AlertTriangle className="text-amber-500 w-6 h-6" />
                {t.lowStockAlerts}
              </h3>
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mt-1">Action Required Immediately</p>
            </div>
            <div className="px-4 py-1.5 bg-amber-100 text-amber-700 rounded-full text-[10px] font-black uppercase tracking-widest">
              {lowStock.length} Alerts
            </div>
          </div>
          <div className="divide-y divide-slate-50 flex-1">
            {lowStock.length > 0 ? lowStock.map((p, idx) => (
              <motion.div 
                key={p.sku} 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: idx * 0.1 }}
                className="p-6 flex items-center justify-between hover:bg-slate-50 transition-all group cursor-pointer"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-slate-100 rounded-xl overflow-hidden">
                    <img src={p.imageUrl} alt={p.name} className="w-full h-full object-cover group-hover:scale-110 transition-transform" />
                  </div>
                  <div>
                    <p className="font-black text-slate-900 italic uppercase tracking-tight">{p.name}</p>
                    <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">SKU: {p.sku}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-lg font-black italic ${p.stock < (p.safetyStock || 5) ? 'text-red-600' : 'text-amber-600'}`}>
                    {p.stock} Units
                  </p>
                  <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Safety: {p.safetyStock || 5}</p>
                </div>
              </motion.div>
            )) : (
              <div className="p-16 text-center text-slate-400 font-black uppercase tracking-widest text-xs italic">
                No critical stock alerts.
              </div>
            )}
          </div>
        </motion.div>

        {/* Pickup Capacity */}
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bento-card overflow-hidden flex flex-col"
        >
          <div className="p-8 border-b border-slate-50 flex items-center justify-between bg-slate-50/50">
            <div>
              <h3 className="text-xl font-black text-slate-900 italic uppercase tracking-tighter flex items-center gap-3">
                <Clock className="text-blue-500 w-6 h-6" />
                {t.pickupCapacity}
              </h3>
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mt-1">Real-time Store Throughput</p>
            </div>
            <div className="px-4 py-1.5 bg-blue-100 text-blue-700 rounded-full text-[10px] font-black uppercase tracking-widest">
              Live Today
            </div>
          </div>
          <div className="p-8 h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={windows}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis 
                  dataKey="start" 
                  tickFormatter={(val) => new Date(val).getHours() + ':00'} 
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 10, fill: '#94a3b8', fontWeight: 700 }}
                />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#94a3b8', fontWeight: 700 }} />
                <Tooltip 
                  cursor={{ fill: '#f8fafc' }}
                  contentStyle={{ borderRadius: '24px', border: 'none', boxShadow: '0 25px 50px -12px rgb(0 0 0 / 0.25)', padding: '16px' }}
                />
                <Bar dataKey="booked" radius={[8, 8, 0, 0]} barSize={40}>
                  {windows.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.booked >= entry.capacity ? '#DA291C' : '#004B91'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
