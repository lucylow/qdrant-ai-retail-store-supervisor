import React, { useState, useEffect } from 'react';
import { useAIStorefront } from '../hooks/useAIStorefront';
import { StorefrontRenderer } from '../components/storefront/StorefrontRenderer';
import { StorefrontSkeleton } from '../components/storefront/StorefrontSkeleton';
import { Language } from '../translations';
import { motion, AnimatePresence } from 'motion/react';
import { Search, Sparkles, ShoppingCart, ArrowLeft, AlertCircle } from 'lucide-react';

interface StorefrontPageProps {
  storeId: string;
  language: Language;
  onBack?: () => void;
}

export function StorefrontPage({ storeId, language, onBack }: StorefrontPageProps) {
  const [query, setQuery] = useState('');
  const [activeQuery, setActiveQuery] = useState('');
  
  // Get query from URL if present
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const chatParam = params.get('chat');
    if (chatParam) {
      setQuery(chatParam);
      setActiveQuery(chatParam);
    }
  }, []);

  const { storefront, loading, error } = useAIStorefront(activeQuery, storeId, language);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      setActiveQuery(query);
      // Update URL without reloading
      const newUrl = new URL(window.location.href);
      newUrl.searchParams.set('chat', query);
      window.history.pushState({}, '', newUrl);
    }
  };

  const handleAction = (action: any) => {
    console.log('Storefront Action:', action);
    // Handle actions like add-to-cart, twint-pay, etc.
    if (action.type === 'twint-pay') {
      alert(`Zahlung von CHF ${action.payload.totalChf.toFixed(2)} mit TWINT erfolgreich!`);
    } else if (action.type === 'add-to-cart') {
      alert(`${action.payload.name} zum Warenkorb hinzugefügt.`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50/50">
      {/* Search Bar / Navigation */}
      <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-100 px-4 py-4">
        <div className="max-w-7xl mx-auto flex items-center gap-4">
          {onBack && (
            <button 
              onClick={onBack}
              className="p-2 hover:bg-gray-100 rounded-xl transition-colors text-gray-500"
            >
              <ArrowLeft className="w-6 h-6" />
            </button>
          )}
          
          <form onSubmit={handleSearch} className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input 
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Was möchten Sie heute einkaufen? (z.B. 'Bio-Milch morgen 10h')"
              className="w-full pl-12 pr-4 py-3 bg-gray-100 border-transparent focus:bg-white focus:border-[#0066CC] focus:ring-4 focus:ring-blue-50 rounded-2xl transition-all outline-none text-gray-900"
            />
            <button 
              type="submit"
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-[#0066CC] text-white rounded-xl hover:bg-[#0052a3] transition-colors"
            >
              <Sparkles className="w-5 h-5" />
            </button>
          </form>
          
          <div className="hidden md:flex items-center gap-4">
            <button className="p-3 bg-white border border-gray-100 shadow-sm rounded-2xl text-gray-700 hover:bg-gray-50 transition-colors relative">
              <ShoppingCart className="w-6 h-6" />
              <span className="absolute -top-1 -right-1 bg-[#FF6C00] text-white text-[10px] font-bold w-5 h-5 rounded-full flex items-center justify-center border-2 border-white">
                3
              </span>
            </button>
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-[#0066CC] to-blue-400 flex items-center justify-center text-white font-bold shadow-lg shadow-blue-100">
              L
            </div>
          </div>
        </div>
      </nav>

      <main>
        <AnimatePresence mode="wait">
          {loading ? (
            <motion.div
              key="skeleton"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <StorefrontSkeleton />
            </motion.div>
          ) : error ? (
            <motion.div
              key="error"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="max-w-xl mx-auto mt-24 p-8 bg-white rounded-3xl border border-rose-100 shadow-xl text-center"
            >
              <div className="w-16 h-16 bg-rose-50 text-rose-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <AlertCircle className="w-8 h-8" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Hoppla!</h2>
              <p className="text-gray-500 mb-8">{error}</p>
              <button 
                onClick={() => setActiveQuery('')}
                className="px-8 py-3 bg-gray-900 text-white rounded-xl font-bold hover:bg-gray-800 transition-colors"
              >
                Zurück zum Start
              </button>
            </motion.div>
          ) : storefront ? (
            <motion.div
              key="content"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <StorefrontRenderer 
                payload={storefront} 
                onAction={handleAction} 
              />
            </motion.div>
          ) : null}
        </AnimatePresence>
      </main>
    </div>
  );
}
