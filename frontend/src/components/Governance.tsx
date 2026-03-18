import React, { useState, useEffect } from 'react';
import { api } from '../lib/api';
import { ComplianceScore } from '../types/retail';
import { ShieldCheck, AlertCircle, Lock, Eye, Terminal, Activity, ChevronRight, FileText, CheckCircle2 } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

export function Governance({ t, subView }: { t: any, subView?: string }) {
  const [score, setScore] = useState<ComplianceScore | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const s = await api.getComplianceScore();
        setScore(s);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <div className="p-8 animate-pulse text-slate-400">Loading governance data...</div>;

  const metrics = [
    { label: t.complianceScore, value: `${score?.overallScore}%`, icon: ShieldCheck, color: 'text-emerald-600', bg: 'bg-emerald-50' },
    { label: t.biasDrift, value: `${score?.biasDrift}%`, icon: Activity, color: 'text-blue-600', bg: 'bg-blue-50' },
    { label: t.privacyRisk, value: `${score?.privacyRisk}%`, icon: Lock, color: 'text-amber-600', bg: 'bg-amber-50' },
    { label: t.humanOverride, value: `${score?.humanOverrideRate}%`, icon: Eye, color: 'text-indigo-600', bg: 'bg-indigo-50' },
  ];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">{t.governance}</h2>
          <p className="text-slate-500 mt-1">AI compliance, bias monitoring, and audit logs.</p>
        </div>
        <div className="flex items-center gap-4">
          <button className="px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm font-bold text-slate-700 hover:bg-slate-50 transition-all flex items-center gap-2">
            <FileText className="w-4 h-4" />
            Audit Log
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-bold shadow-lg shadow-blue-500/20 hover:bg-blue-700 transition-all flex items-center gap-2">
            <ShieldCheck className="w-4 h-4" />
            Recertify System
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((m, i) => (
          <div key={i} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className={`p-3 rounded-xl ${m.bg}`}>
              <m.icon className={`w-6 h-6 ${m.color}`} />
            </div>
            <div>
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{m.label}</p>
              <p className="text-xl font-bold text-slate-900">{m.value}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Compliance Status */}
        <div className="lg:col-span-2 bg-white p-8 rounded-3xl border border-slate-200 shadow-sm space-y-8">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-900 flex items-center gap-2">
              <Terminal className="text-blue-500 w-5 h-5" />
              Real-time Model Monitoring
            </h3>
            <div className="flex items-center gap-2 text-emerald-600 bg-emerald-50 px-3 py-1 rounded-full text-xs font-bold">
              System Healthy
            </div>
          </div>

          <div className="space-y-6">
            {[
              { label: 'Data Privacy (GDPR/Swiss FADP)', status: 'Compliant', score: 98 },
              { label: 'Algorithmic Fairness', status: 'Healthy', score: 95 },
              { label: 'Explainability Index', status: 'High', score: 92 },
              { label: 'Human-in-the-loop Rate', status: 'Optimal', score: 88 },
            ].map((item, i) => (
              <div key={i} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="font-bold text-slate-700">{item.label}</span>
                  <span className="font-bold text-blue-600">{item.status} ({item.score}%)</span>
                </div>
                <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: `${item.score}%` }}
                    className="h-full bg-blue-600 rounded-full"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Audit Summary */}
        <div className="bg-slate-900 p-8 rounded-3xl text-white space-y-8 flex flex-col justify-between shadow-xl shadow-slate-900/20">
          <div className="space-y-2">
            <h3 className="text-xl font-bold flex items-center gap-2">
              <CheckCircle2 className="text-emerald-400 w-6 h-6" />
              Last Audit Summary
            </h3>
            <p className="text-slate-400 text-sm">Automated compliance check completed on {score?.lastAuditDate}.</p>
          </div>

          <div className="space-y-4">
            <div className="bg-slate-800/50 p-4 rounded-2xl border border-slate-700">
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Findings</p>
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-amber-400 shrink-0" />
                <p className="text-sm text-slate-300">Minor drift detected in 'BBQ Season' demand forecasting model. Recalibration recommended.</p>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl">
              <div className="flex items-center gap-3">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                <span className="text-sm font-bold text-emerald-400">Swiss FADP Verified</span>
              </div>
              <ChevronRight className="w-4 h-4 text-emerald-400" />
            </div>
          </div>

          <button className="w-full py-4 bg-white text-slate-900 font-bold rounded-2xl transition-all hover:bg-slate-100">
            Download Certificate
          </button>
        </div>
      </div>
    </div>
  );
}
