import React, { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { 
  Megaphone, 
  Package, 
  Store, 
  Palette, 
  Globe, 
  Sparkles,
  ChevronRight,
  Check
} from 'lucide-react';
import { MarketingRequest, CampaignType, Language } from '../../types/marketing';
import { api } from '../../lib/api';
import { Product } from '../../types/retail';

interface CampaignWizardProps {
  onGenerate: (req: MarketingRequest) => void;
  isGenerating: boolean;
}

export function CampaignWizard({ onGenerate, isGenerating }: CampaignWizardProps) {
  const [campaignType, setCampaignType] = useState<CampaignType>('social');
  const [selectedProducts, setSelectedProducts] = useState<string[]>([]);
  const [selectedStore, setSelectedStore] = useState('migros_zh_stockerhof');
  const [theme, setTheme] = useState('Christmas');
  const [language, setLanguage] = useState<Language>('de');
  const [products, setProducts] = useState<Product[]>([]);
  const [stores, setStores] = useState<any[]>([]);

  useEffect(() => {
    api.getProducts().then(setProducts);
    api.getStores().then(setStores);
  }, []);

  const toggleProduct = (sku: string) => {
    setSelectedProducts(prev => 
      prev.includes(sku) ? prev.filter(s => s !== sku) : [...prev, sku]
    );
  };

  const handleSubmit = () => {
    onGenerate({
      campaignType,
      products: selectedProducts,
      storeId: selectedStore,
      theme,
      language,
    });
  };

  return (
    <div className="bento-card p-12 space-y-12">
      <div className="flex items-center gap-6 border-b border-slate-50 pb-10">
        <div className="w-16 h-16 bg-orange-50 text-migros-orange rounded-[1.5rem] flex items-center justify-center shadow-inner">
          <Megaphone className="w-8 h-8" />
        </div>
        <div>
          <h2 className="text-3xl font-black text-slate-900 italic uppercase tracking-tighter leading-none">Campaign Wizard</h2>
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] mt-2">AI-Powered Marketing Intelligence</p>
        </div>
      </div>

      <div className="space-y-12">
        {/* Campaign Type */}
        <div className="space-y-6">
          <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] flex items-center gap-3">
            <div className="w-1.5 h-1.5 bg-migros-orange rounded-full" />
            Kampagnentyp
          </label>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {(['social', 'banner', 'video', 'print', 'email'] as CampaignType[]).map(type => (
              <button
                key={type}
                onClick={() => setCampaignType(type)}
                className={`px-6 py-4 rounded-[1.5rem] text-[10px] font-black uppercase tracking-widest transition-all duration-300 border ${
                  campaignType === type 
                    ? 'bg-migros-orange text-white border-migros-orange shadow-2xl shadow-orange-500/30 scale-105' 
                    : 'bg-slate-50 text-slate-400 border-slate-100 hover:bg-slate-100 hover:text-slate-600'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        {/* Products */}
        <div className="space-y-6">
          <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] flex items-center gap-3">
            <div className="w-1.5 h-1.5 bg-migros-orange rounded-full" />
            Produkte auswählen
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[350px] overflow-y-auto pr-4 custom-scrollbar">
            {products.map(product => (
              <button
                key={product.sku}
                onClick={() => toggleProduct(product.sku)}
                className={`flex items-center gap-4 p-4 rounded-[1.5rem] border transition-all duration-300 text-left group ${
                  selectedProducts.includes(product.sku)
                    ? 'border-migros-orange bg-orange-50/50 shadow-lg shadow-orange-500/5'
                    : 'border-slate-100 bg-white hover:border-slate-200 hover:shadow-md'
                }`}
              >
                <div className="w-14 h-14 rounded-2xl overflow-hidden bg-slate-50 border border-slate-100 shrink-0">
                  <img src={product.imageUrl} alt={product.name} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-black text-slate-900 uppercase tracking-tight truncate">{product.name}</div>
                  <div className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-1">{product.category}</div>
                </div>
                <div className={`w-6 h-6 rounded-full flex items-center justify-center transition-all duration-300 ${
                  selectedProducts.includes(product.sku) ? 'bg-migros-orange text-white scale-110' : 'bg-slate-100 text-transparent'
                }`}>
                  <Check className="w-3.5 h-3.5" />
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Store */}
          <div className="space-y-4">
            <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] flex items-center gap-3">
              <div className="w-1.5 h-1.5 bg-migros-orange rounded-full" />
              Filiale
            </label>
            <div className="relative">
              <select 
                value={selectedStore}
                onChange={(e) => setSelectedStore(e.target.value)}
                className="w-full px-6 py-5 bg-slate-50 border border-slate-100 rounded-[1.5rem] text-[10px] font-black uppercase tracking-widest text-slate-900 focus:ring-4 focus:ring-migros-orange/10 focus:border-migros-orange/30 appearance-none transition-all"
              >
                {stores.map(store => (
                  <option key={store.id} value={store.id}>{store.name}</option>
                ))}
              </select>
              <div className="absolute right-6 top-1/2 -translate-y-1/2 pointer-events-none">
                <ChevronRight className="w-4 h-4 text-slate-400 rotate-90" />
              </div>
            </div>
          </div>

          {/* Theme */}
          <div className="space-y-4">
            <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] flex items-center gap-3">
              <div className="w-1.5 h-1.5 bg-migros-orange rounded-full" />
              Thema
            </label>
            <div className="relative">
              <select 
                value={theme}
                onChange={(e) => setTheme(e.target.value)}
                className="w-full px-6 py-5 bg-slate-50 border border-slate-100 rounded-[1.5rem] text-[10px] font-black uppercase tracking-widest text-slate-900 focus:ring-4 focus:ring-migros-orange/10 focus:border-migros-orange/30 appearance-none transition-all"
              >
                {['Christmas', 'Fondue', 'Summer BBQ', 'Organic', 'Easter'].map(t => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
              <div className="absolute right-6 top-1/2 -translate-y-1/2 pointer-events-none">
                <ChevronRight className="w-4 h-4 text-slate-400 rotate-90" />
              </div>
            </div>
          </div>

          {/* Language */}
          <div className="space-y-4">
            <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] flex items-center gap-3">
              <div className="w-1.5 h-1.5 bg-migros-orange rounded-full" />
              Sprache
            </label>
            <div className="flex gap-3">
              {(['de', 'fr', 'it'] as Language[]).map(lang => (
                <button
                  key={lang}
                  onClick={() => setLanguage(lang)}
                  className={`flex-1 py-5 rounded-[1.5rem] text-[10px] font-black uppercase tracking-widest transition-all duration-300 border ${
                    language === lang 
                      ? 'bg-migros-blue text-white border-migros-blue shadow-xl shadow-blue-500/20 scale-105' 
                      : 'bg-slate-50 text-slate-400 border-slate-100 hover:bg-slate-100'
                  }`}
                >
                  {lang}
                </button>
              ))}
            </div>
          </div>
        </div>

        <button
          onClick={handleSubmit}
          disabled={isGenerating || selectedProducts.length === 0}
          className={`w-full py-8 rounded-[2.5rem] font-black text-2xl flex items-center justify-center gap-6 transition-all duration-500 uppercase tracking-[0.2em] italic shadow-2xl ${
            isGenerating || selectedProducts.length === 0
              ? 'bg-slate-100 text-slate-300 cursor-not-allowed'
              : 'bg-migros-orange text-white shadow-orange-500/30 hover:scale-[1.02] active:scale-[0.98] hover:shadow-orange-500/50'
          }`}
        >
          {isGenerating ? (
            <>
              <div className="w-8 h-8 border-[5px] border-white/30 border-t-white rounded-full animate-spin" />
              Generieren...
            </>
          ) : (
            <>
              <Sparkles className="w-8 h-8" />
              🎨 Kampagne Generieren (90s)
            </>
          )}
        </button>
      </div>
    </div>
  );
}
