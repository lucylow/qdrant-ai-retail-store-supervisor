import React from 'react';
import { motion } from 'motion/react';
import { Sparkles, Shield, Zap, Database, ArrowRight, Bot, Globe, Layout } from 'lucide-react';

interface LandingPageProps {
  onLogin: () => void;
  t: any;
}

export function LandingPage({ onLogin, t }: LandingPageProps) {
  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900 overflow-x-hidden">
      {/* Navigation */}
      <nav className="h-20 bg-white/80 backdrop-blur-md border-b border-slate-200 flex items-center justify-between px-8 sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-[#DA291C] rounded-lg flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-red-500/20 relative overflow-hidden">
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-4 h-1 bg-white rounded-full" />
              <div className="h-4 w-1 bg-white rounded-full absolute" />
            </div>
          </div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Dynamic<span className="text-[#DA291C]">Vector</span>
          </h1>
        </div>
        <div className="flex items-center gap-6">
          <button className="text-sm font-bold text-slate-500 hover:text-slate-900 transition-colors">Features</button>
          <button className="text-sm font-bold text-slate-500 hover:text-slate-900 transition-colors">Enterprise</button>
          <button 
            onClick={onLogin}
            className="px-6 py-2.5 bg-[#FF6321] text-white rounded-xl font-bold shadow-lg shadow-orange-500/20 hover:bg-[#e5591e] transition-all flex items-center gap-2"
          >
            Login as Migros Supervisor
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-20 pb-32 px-8 overflow-hidden">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <motion.div 
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="space-y-8"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-red-50 border border-red-100 rounded-full text-[#DA291C] text-xs font-bold uppercase tracking-widest">
              <Sparkles className="w-4 h-4" />
              Next-Gen Enterprise AI
            </div>
            <h2 className="text-6xl font-black text-slate-900 leading-[1.1] tracking-tight">
              Your Data, <br />
              <span className="text-[#DA291C]">Intelligently</span> <br />
              Connected.
            </h2>
            <p className="text-xl text-slate-500 max-w-lg leading-relaxed">
              DynamicVector combines RAG, multi-modal analysis, and agentic workflows to transform your corporate knowledge into actionable insights.
            </p>
            <div className="flex items-center gap-4 pt-4">
              <button 
                onClick={onLogin}
                className="px-8 py-4 bg-slate-900 text-white rounded-2xl font-bold text-lg shadow-xl shadow-slate-900/20 hover:bg-slate-800 transition-all flex items-center gap-3"
              >
                Enter Platform
                <ArrowRight className="w-5 h-5" />
              </button>
              <button className="px-8 py-4 bg-white border border-slate-200 text-slate-700 rounded-2xl font-bold text-lg hover:bg-slate-50 transition-all">
                Request Demo
              </button>
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="relative"
          >
            <div className="relative z-10 bg-white p-8 rounded-[40px] shadow-2xl border border-slate-100">
              <div className="grid grid-cols-2 gap-6">
                {[
                  { icon: Database, label: 'RAG Engine', color: 'text-blue-500', bg: 'bg-blue-50' },
                  { icon: Bot, label: 'AI Agents', color: 'text-purple-500', bg: 'bg-purple-50' },
                  { icon: Shield, label: 'Governance', color: 'text-emerald-500', bg: 'bg-emerald-50' },
                  { icon: Zap, label: 'Real-time', color: 'text-amber-500', bg: 'bg-amber-50' },
                ].map((item, i) => (
                  <div key={i} className="p-6 bg-slate-50 rounded-3xl border border-slate-100 flex flex-col items-center text-center gap-4 hover:bg-white hover:shadow-xl hover:border-blue-100 transition-all cursor-default group">
                    <div className={`p-4 rounded-2xl ${item.bg} ${item.color} group-hover:scale-110 transition-transform`}>
                      <item.icon className="w-8 h-8" />
                    </div>
                    <span className="font-bold text-slate-900">{item.label}</span>
                  </div>
                ))}
              </div>
            </div>
            {/* Decorative elements */}
            <div className="absolute -top-20 -right-20 w-64 h-64 bg-red-500/10 rounded-full blur-3xl" />
            <div className="absolute -bottom-20 -left-20 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl" />
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="bg-white py-32 px-8">
        <div className="max-w-7xl mx-auto space-y-16">
          <div className="text-center space-y-4">
            <h3 className="text-4xl font-bold text-slate-900">Enterprise-Grade Capabilities</h3>
            <p className="text-slate-500 max-w-2xl mx-auto text-lg">Built for the most demanding corporate environments, ensuring security, compliance, and performance.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { title: 'Multi-Modal Analysis', desc: 'Process text, images, audio, and video with unified intelligence.', icon: Layout },
              { title: 'Swiss Data Sovereignty', desc: 'Compliant with Swiss FADP and GDPR regulations.', icon: Globe },
              { title: 'Seamless Integration', desc: 'Connect to your existing ERP, CRM, and data lakes.', icon: Database },
            ].map((f, i) => (
              <div key={i} className="p-8 rounded-3xl bg-slate-50 border border-slate-100 hover:border-red-200 transition-all group">
                <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center shadow-sm mb-6 group-hover:bg-[#DA291C] group-hover:text-white transition-all">
                  <f.icon className="w-6 h-6" />
                </div>
                <h4 className="text-xl font-bold text-slate-900 mb-2">{f.title}</h4>
                <p className="text-slate-500 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 py-20 px-8 text-white">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-12">
          <div className="col-span-2 space-y-6">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-[#DA291C] rounded-lg flex items-center justify-center text-white font-bold text-xl">
                <span className="relative z-10">+</span>
              </div>
              <h1 className="text-xl font-bold tracking-tight">
                DynamicVector
              </h1>
            </div>
            <p className="text-slate-400 max-w-sm">
              Empowering the modern enterprise with secure, scalable, and intelligent AI solutions.
            </p>
          </div>
          <div className="space-y-4">
            <h5 className="font-bold text-white uppercase tracking-widest text-xs">Product</h5>
            <ul className="space-y-2 text-slate-400 text-sm">
              <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Security</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
            </ul>
          </div>
          <div className="space-y-4">
            <h5 className="font-bold text-white uppercase tracking-widest text-xs">Company</h5>
            <ul className="space-y-2 text-slate-400 text-sm">
              <li><a href="#" className="hover:text-white transition-colors">About Us</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
            </ul>
          </div>
        </div>
        <div className="max-w-7xl mx-auto pt-20 border-t border-slate-800 mt-20 flex justify-between items-center text-slate-500 text-xs font-bold uppercase tracking-widest">
          <p>© 2026 DynamicVector AG. All rights reserved.</p>
          <div className="flex gap-8">
            <a href="#" className="hover:text-white transition-colors">LinkedIn</a>
            <a href="#" className="hover:text-white transition-colors">Twitter</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
