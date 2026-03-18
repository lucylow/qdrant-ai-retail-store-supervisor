import React, { useState, useEffect, useRef } from 'react';
import { 
  Layout, 
  Search, 
  ShoppingBag, 
  Clock, 
  Zap, 
  Database, 
  Shield, 
  Settings, 
  FileText, 
  Globe, 
  User, 
  LogOut, 
  ChevronDown, 
  Menu, 
  X,
  TrendingUp,
  Leaf,
  Sparkles,
  Bot,
  CreditCard,
  QrCode,
  Megaphone,
  MapPin
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { Dashboard } from './components/Dashboard';
import { ProductSearch } from './components/ProductSearch';
import { Orders } from './components/Orders';
import { PickupSchedule } from './components/PickupSchedule';
import { AIQuery } from './components/AIQuery';
import { Metrics } from './components/Metrics';
import { Governance } from './components/Governance';
import { LandingPage } from './components/LandingPage';
import { StorefrontPage } from './pages/Storefront';
import MarketingStudio from './pages/MarketingStudio';
import StoreLocator from './pages/StoreLocator';
import { translations, Language } from './translations';
import { RAGDocument, Agent, INITIAL_AGENTS } from './types';

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(() => {
    return sessionStorage.getItem('migros_is_logged_in') === 'true';
  });
  const [view, setView] = useState<'dashboard' | 'products' | 'orders' | 'schedule' | 'ai-query' | 'metrics' | 'governance' | 'builder' | 'rag' | 'storefront' | 'marketing' | 'stores-map'>(() => {
    if (window.location.pathname === '/storefront' || window.location.search.includes('chat=')) {
      return 'storefront';
    }
    return 'dashboard';
  });
  const [language, setLanguage] = useState<Language>(() => {
    const saved = localStorage.getItem('migros_supervisor_lang');
    return (saved as Language) || 'en';
  });
  const [tenant, setTenant] = useState((import.meta as any).env.VITE_DEFAULT_TENANT || 'migros');
  const [store, setStore] = useState((import.meta as any).env.VITE_DEFAULT_STORE || 'migros_zh_stockerhof');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isUserModalOpen, setIsUserModalOpen] = useState(false);
  
  const t = translations[language];
  const userEmail = "low.lucyy@gmail.com";

  useEffect(() => {
    localStorage.setItem('migros_supervisor_lang', language);
  }, [language]);

  useEffect(() => {
    sessionStorage.setItem('migros_is_logged_in', isLoggedIn.toString());
  }, [isLoggedIn]);

  const handleLogin = () => {
    setIsLoggedIn(true);
    setView('dashboard');
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    sessionStorage.removeItem('migros_is_logged_in');
  };

  if (!isLoggedIn && view !== 'storefront') {
    return <LandingPage onLogin={handleLogin} t={t} />;
  }

  if (view === 'storefront') {
    return (
      <StorefrontPage 
        storeId={store} 
        language={language} 
        onBack={isLoggedIn ? () => setView('dashboard') : undefined} 
      />
    );
  }

  const sidebarItems = [
    { 
      id: 'dashboard', 
      label: t.dashboard, 
      icon: Layout 
    },
    {
      id: 'storefront',
      label: 'AI Storefront',
      icon: Sparkles,
      subItems: [
        { id: 'storefront', label: 'Dynamic View' },
        { id: 'storefront', label: 'Personalized' },
      ]
    },
    {
      id: 'marketing',
      label: 'Marketing Studio',
      icon: Megaphone,
      subItems: [
        { id: 'marketing', label: 'Campaign Wizard' },
        { id: 'marketing', label: 'Asset Library' },
        { id: 'marketing', label: 'Analytics' },
      ]
    },
    {
      id: 'stores-map',
      label: 'Store Locator',
      icon: MapPin,
      subItems: [
        { id: 'stores-map', label: 'Zürich Map' },
        { id: 'stores-map', label: 'Capacity Heat' },
      ]
    },
    { 
      id: 'products', 
      label: t.productSearch, 
      icon: Search,
      subItems: [
        { id: 'products', label: t.searchBrowse },
        { id: 'products', label: t.lowStockAlerts },
        { id: 'products', label: t.categoryOverview },
      ]
    },
    { 
      id: 'orders', 
      label: t.ordersCheckout, 
      icon: ShoppingBag,
      subItems: [
        { id: 'orders', label: t.newOrder },
        { id: 'orders', label: t.orderHistory },
        { id: 'orders', label: t.paymentStatus + ' (TWINT)' },
      ]
    },
    { 
      id: 'schedule', 
      label: t.pickupSchedule, 
      icon: Clock,
      subItems: [
        { id: 'schedule', label: t.dailyWindows },
        { id: 'schedule', label: t.capacityOptimization },
      ]
    },
    { 
      id: 'ai-query', 
      label: t.aiQuery, 
      icon: Bot,
      subItems: [
        { id: 'ai-query', label: t.askRetailBot },
        { id: 'ai-query', label: t.dataVisualizer },
      ]
    },
    { 
      id: 'metrics', 
      label: t.metricsImpact, 
      icon: TrendingUp,
      subItems: [
        { id: 'metrics', label: t.financialRoi },
        { id: 'metrics', label: t.sustainability },
      ]
    },
    { 
      id: 'governance', 
      label: t.governance, 
      icon: Shield,
      subItems: [
        { id: 'governance', label: t.aiCompliance },
        { id: 'governance', label: t.modelMonitoring },
      ]
    },
  ];

  const settingsItems = [
    { id: 'builder', label: t.agentBuilder, icon: Zap },
    { id: 'rag', label: t.ragManager, icon: Database },
  ];

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden font-sans text-slate-900">
      {/* Sidebar */}
      <AnimatePresence mode="wait">
        {isSidebarOpen && (
          <motion.aside
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 280, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            className="bg-migros-blue text-white flex flex-col z-30 shadow-2xl relative"
          >
            {/* Migros Logo Area */}
            <div className="p-8 flex items-center gap-4">
              <div className="w-12 h-12 bg-migros-orange rounded-2xl flex items-center justify-center shadow-lg shadow-orange-500/20">
                <span className="text-3xl font-black text-white italic">M</span>
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-tight">MIGROS</h1>
                <p className="text-[10px] font-bold text-blue-200 uppercase tracking-[0.2em]">Supervisor Pro</p>
              </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto custom-scrollbar">
              {sidebarItems.map((item) => (
                <div key={item.id} className="space-y-1">
                  <button
                    onClick={() => setView(item.id as any)}
                    className={`w-full flex items-center gap-4 px-4 py-3 rounded-2xl transition-all group ${
                      view === item.id 
                        ? 'bg-white/10 text-white shadow-inner' 
                        : 'text-blue-100 hover:bg-white/5 hover:text-white'
                    }`}
                  >
                    <item.icon className={`w-5 h-5 transition-transform group-hover:scale-110 ${view === item.id ? 'text-migros-orange' : 'text-blue-300'}`} />
                    <span className="text-sm font-bold tracking-wide">{item.label}</span>
                    {view === item.id && (
                      <motion.div layoutId="active-pill" className="ml-auto w-1.5 h-1.5 bg-migros-orange rounded-full" />
                    )}
                  </button>
                  
                  {item.subItems && view === item.id && (
                    <div className="ml-12 space-y-1 pb-2">
                      {item.subItems.map((sub, idx) => (
                        <button
                          key={idx}
                          onClick={() => setView(sub.id as any)}
                          className="w-full text-left px-4 py-1.5 text-[11px] font-bold text-blue-300 hover:text-white transition-colors"
                        >
                          • {sub.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}

              <div className="pt-8 pb-4">
                <p className="px-4 text-[10px] font-bold text-blue-300 uppercase tracking-[0.2em] mb-2">{t.settings}</p>
                {settingsItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => setView(item.id as any)}
                    className={`w-full flex items-center gap-4 px-4 py-3.5 rounded-2xl transition-all group ${
                      view === item.id 
                        ? 'bg-white/10 text-white shadow-inner' 
                        : 'text-blue-100 hover:bg-white/5 hover:text-white'
                    }`}
                  >
                    <item.icon className={`w-5 h-5 transition-transform group-hover:scale-110 ${view === item.id ? 'text-migros-orange' : 'text-blue-300'}`} />
                    <span className="text-sm font-bold tracking-wide">{item.label}</span>
                  </button>
                ))}
              </div>
            </nav>

            {/* Sidebar Footer */}
            <div className="p-6 border-t border-white/10 space-y-4">
              <div className="flex items-center gap-3 px-2">
                <div className="w-8 h-8 rounded-full bg-blue-400/20 flex items-center justify-center border border-white/10">
                  <User className="w-4 h-4 text-blue-200" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-bold truncate">Lucy Low</p>
                  <p className="text-[10px] text-blue-300 truncate">Store Manager</p>
                </div>
                <button 
                  onClick={handleLogout}
                  className="p-2 hover:bg-white/10 rounded-xl transition-colors text-blue-300 hover:text-white"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-20 bg-white/80 backdrop-blur-xl border-b border-slate-200 flex items-center justify-between px-8 z-20 shadow-sm">
          <div className="flex items-center gap-6">
            <button 
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2.5 hover:bg-slate-100 rounded-xl transition-all text-slate-500 active:scale-95"
            >
              {isSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            
            <div className="flex items-center gap-4">
              <div className="flex flex-col">
                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest leading-none mb-1">Store Location</span>
                <div className="flex items-center gap-2">
                  <h2 className="text-lg font-black text-slate-900 italic uppercase tracking-tighter">Zürich HB (Stockerhof)</h2>
                  <div className="px-2 py-0.5 bg-emerald-100 text-emerald-600 rounded-full text-[10px] font-black uppercase tracking-wider">
                    Live
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-6">
            {/* Selectors */}
            <div className="hidden xl:flex items-center gap-3 bg-slate-50 p-1.5 rounded-2xl border border-slate-200">
              <div className="relative">
                <select 
                  value={tenant}
                  onChange={(e) => setTenant(e.target.value)}
                  className="h-9 bg-white border border-slate-200 rounded-xl pl-3 pr-8 text-xs font-bold text-slate-600 appearance-none cursor-pointer hover:border-slate-300 transition-all focus:outline-none"
                >
                  <option value="migros">Migros</option>
                  <option value="retail-corp">Retail Corp</option>
                  <option value="coop">Coop</option>
                </select>
                <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400 pointer-events-none" />
              </div>
              <div className="relative">
                <select 
                  value={store}
                  onChange={(e) => setStore(e.target.value)}
                  className="h-9 bg-white border border-slate-200 rounded-xl pl-3 pr-8 text-xs font-bold text-slate-600 appearance-none cursor-pointer hover:border-slate-300 transition-all focus:outline-none"
                >
                  <option value="migros_zh_stockerhof">Zürich HB (Stockerhof)</option>
                  <option value="migros_be_bahnhof">Bern HB</option>
                  <option value="migros_appenzell">Appenzell (Rural)</option>
                  <option value="migros_vs_sion">Valais Sion</option>
                  <option value="migros_ge_carouge">Geneva Carouge</option>
                </select>
                <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400 pointer-events-none" />
              </div>
            </div>

            {/* Language */}
            <div className="relative hidden md:block">
              <select 
                value={language}
                onChange={(e) => setLanguage(e.target.value as Language)}
                className="h-10 bg-slate-50 border border-slate-200 rounded-2xl pl-4 pr-10 text-xs font-bold text-slate-700 appearance-none cursor-pointer hover:bg-slate-100 transition-all focus:outline-none"
              >
                {(['en', 'de', 'fr', 'it', 'rm'] as Language[]).map(lang => (
                  <option key={lang} value={lang}>
                    {translations[lang].langName} ({lang.toUpperCase()})
                  </option>
                ))}
              </select>
              <Globe className="absolute right-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
            </div>

            <div className="w-px h-8 bg-slate-200" />

            <button className="flex items-center gap-3 group px-4 py-2 hover:bg-slate-50 rounded-2xl transition-all">
              <div className="text-right hidden sm:block">
                <p className="text-xs font-black text-slate-900 italic uppercase tracking-tighter">CHF 24,567.00</p>
                <p className="text-[10px] font-black text-emerald-500 uppercase tracking-widest">Today's Revenue</p>
              </div>
              <div className="w-10 h-10 rounded-2xl bg-slate-100 flex items-center justify-center group-hover:bg-slate-200 transition-all shadow-sm">
                <TrendingUp className="w-5 h-5 text-slate-600" />
              </div>
            </button>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-hidden relative flex flex-col">
          <div className="flex-1 overflow-y-auto custom-scrollbar">
            <AnimatePresence mode="wait">
              <motion.div
                key={view}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className="h-full"
              >
                {view.startsWith('dashboard') && <Dashboard storeId={store} t={t} subView={view} />}
                {view.startsWith('products') && <ProductSearch tenant={tenant} storeId={store} t={t} subView={view} />}
                {view.startsWith('orders') && <Orders storeId={store} t={t} subView={view} />}
                {view.startsWith('schedule') && <PickupSchedule storeId={store} t={t} subView={view} />}
                {view.startsWith('ai-query') && <AIQuery tenant={tenant} storeId={store} t={t} subView={view} />}
                {view.startsWith('metrics') && <Metrics t={t} subView={view} />}
                {view.startsWith('governance') && <Governance t={t} subView={view} />}
                {view === 'marketing' && <MarketingStudio />}
                {view === 'stores-map' && <StoreLocator />}
                
                {(view === 'builder' || view === 'rag') && (
                  <div className="p-12 text-center space-y-6">
                    <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mx-auto">
                      <Settings className="w-10 h-10 text-slate-300" />
                    </div>
                    <div className="space-y-2">
                      <h3 className="text-2xl font-bold text-slate-900">Admin Settings</h3>
                      <p className="text-slate-500">The {view === 'builder' ? 'Agent Builder' : 'RAG Manager'} is restricted to regional directors.</p>
                    </div>
                    <button onClick={() => setView('dashboard')} className="px-8 py-3 bg-slate-900 text-white font-bold rounded-2xl hover:bg-slate-800 transition-all">
                      Back to Dashboard
                    </button>
                  </div>
                )}
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Footer Ticker */}
          <footer className="h-10 bg-slate-900 text-white flex items-center overflow-hidden whitespace-nowrap border-t border-slate-800">
            <div className="flex items-center animate-marquee whitespace-nowrap">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="flex items-center gap-8 px-8">
                  <span className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest">
                    <TrendingUp className="w-3 h-3 text-emerald-400" />
                    CHF 24,567 Saved Today
                  </span>
                  <span className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest">
                    <Leaf className="w-3 h-3 text-emerald-400" />
                    18.2k Tons CO₂ Reduced
                  </span>
                  <span className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest">
                    <Clock className="w-3 h-3 text-blue-400" />
                    94% Punctuality Rate
                  </span>
                  <span className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest">
                    <Zap className="w-3 h-3 text-amber-400" />
                    58% TWINT Market Share
                  </span>
                </div>
              ))}
            </div>
          </footer>
        </main>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes marquee {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        .animate-marquee {
          animation: marquee 30s linear infinite;
        }
        .no-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .no-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #e2e8f0;
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #cbd5e1;
        }
      `}} />
    </div>
  );
}
